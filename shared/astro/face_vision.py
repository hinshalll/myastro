"""
shared.astro/face_vision.py
============================
Accuracy-first face vision math engine for Vedic face reading (Mukha Samudrika).

Mirrors the philosophy of palm_vision.py: produce ONLY deterministic, reliable
signals from MediaPipe Face Mesh (468/478 landmarks), and let the VLM (Gemini)
do the qualitative visual judgement (moles, complexion, expression) and the
final synthesis.

WHAT THIS DOES (deterministic geometry only):
  - MediaPipe Face Mesh landmark detection (refine_landmarks=True → iris too)
  - Image prep reused from palm_vision (EXIF, resize, gray-world, CLAHE, quality gate)
  - Frontal-pose gate (rejects turned/tilted faces so measurements are valid)
  - Face-shape classification → Pancha Bhoota element (with ratios + confidence)
  - Three-zone proportions (forehead / mid-face / lower) and dominant zone
  - Eye spacing (wide/close-set) and canthal tilt (up/down-turned)
  - Nose length & width ratios; jaw strength; mouth width; lip fullness (approx)
  - Facial symmetry score
  - Region crops (forehead / eyes / nose / mouth-chin) for VLM input
  - Clean landmark overlay for the UI

WHAT THIS DELIBERATELY DOES NOT DO:
  - Forehead "line" reading (faint, unreliable from one photo — like palm lines)
  - Mole detection (the VLM does that from the image; we only interpret position)
  - Eyebrow thickness / skin texture (qualitative — left to the VLM)

Classifications are TENTATIVE hints. The VLM receives them plus the photo and
confirms/refines (especially face shape, whose boundaries are inherently fuzzy).
"""

import io
import cv2
import numpy as np
import PIL.Image
import PIL.ImageOps
import mediapipe as mp

# Reuse the proven image-prep + quality gate from the palm engine (pure image
# functions — no hand-specific logic). Keeps a single source of truth.
from shared.astro.palm_vision import (
    _resize_to_width, _gray_world_balance, enhance_for_vlm, _assess_quality, CFG,
)


# ── Lazy Face Mesh init (same pattern as palm_vision's hands detector) ─────────
_face_mesh = None


def _get_face_mesh():
    global _face_mesh
    if _face_mesh is None:
        try:
            _face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,      # adds iris → 478 pts, better eye metrics
                min_detection_confidence=0.5,
            )
        except AttributeError as e:
            raise RuntimeError(
                "MediaPipe is installed but `mp.solutions.face_mesh` is unavailable. "
                "Align local version with the pinned wheel: "
                "`pip install -r requirements.txt --upgrade`. "
                f"(Original error: {e})"
            ) from e
    return _face_mesh


# ── Canonical Face Mesh landmark indices we rely on ────────────────────────────
LM = {
    "forehead_top": 10, "chin": 152,
    "cheek_l": 234, "cheek_r": 454,        # zygomatic (face) width
    "jaw_l": 172, "jaw_r": 397,            # lower jaw width
    "temple_l": 21, "temple_r": 251,       # upper-face / forehead width
    "glabella": 9, "nose_bridge": 168, "nose_tip": 1, "nose_base": 2,
    "ala_l": 129, "ala_r": 358,            # nostril width
    "eye_l_out": 33, "eye_l_in": 133, "eye_l_top": 159, "eye_l_bot": 145,
    "eye_r_in": 362, "eye_r_out": 263, "eye_r_top": 386, "eye_r_bot": 374,
    "brow_l_peak": 105, "brow_r_peak": 334,
    "mouth_l": 61, "mouth_r": 291,
    "lip_top": 0, "lip_inner_top": 13, "lip_inner_bot": 14, "lip_bot": 17,
}


def _d(p, q):
    return float(np.hypot(p[0] - q[0], p[1] - q[1]))


# ══════════════════════════════════════════════════════════════════════════════
# POSE GATE — ensure the face is frontal enough for measurements to be valid
# ══════════════════════════════════════════════════════════════════════════════

def _pose_check(L):
    """Estimate yaw (left/right turn), roll (tilt), and pitch (vertical nod) from landmarks.

    yaw: nose tip should sit midway between the two cheek edges. Off-centre → turned.
    roll: the eye line should be horizontal. Angled → tilted head.
    pitch: relative vertical position of the nose tip between eye line and mouth line.
    Returns (issues_list, metrics).
    """
    nose = L["nose_tip"]; cl = L["cheek_l"]; cr = L["cheek_r"]
    face_w = abs(cr[0] - cl[0]) or 1
    # 0 = perfectly centred; +/- = turned toward one side
    yaw = (nose[0] - (cl[0] + cr[0]) / 2) / face_w
    
    # eye-line angle in degrees
    el = L["eye_l_out"]; er = L["eye_r_out"]
    roll = float(np.degrees(np.arctan2(er[1] - el[1], er[0] - el[0])))
    
    # pitch estimation: relative nose tip y-position compared to eye and mouth y-positions
    eye_y = (L["eye_l_out"][1] + L["eye_r_out"][1]) / 2.0
    mouth_y = (L["mouth_l"][1] + L["mouth_r"][1]) / 2.0
    nose_y = L["nose_tip"][1]
    
    denom = (mouth_y - eye_y) or 1.0
    pitch = (nose_y - eye_y) / denom
    
    issues = []
    if abs(yaw) > 0.16:
        issues.append("Face looks turned to one side — please look straight at the camera.")
    if abs(roll) > 12:
        issues.append("Head looks tilted — please hold it level.")
    if pitch < 0.35:
        issues.append("Head looks tilted upward — please look straight at the camera.")
    elif pitch > 0.60:
        issues.append("Head looks tilted downward — please look straight at the camera.")
        
    return issues, {"yaw": round(yaw, 3), "roll_deg": round(roll, 1), "pitch": round(pitch, 3)}


# ══════════════════════════════════════════════════════════════════════════════
# METRICS
# ══════════════════════════════════════════════════════════════════════════════

def _face_shape(L):
    length = _d(L["forehead_top"], L["chin"])
    cheek_w = _d(L["cheek_l"], L["cheek_r"]) or 1
    fore_w = _d(L["temple_l"], L["temple_r"])
    jaw_w = _d(L["jaw_l"], L["jaw_r"])
    aspect = length / cheek_w
    fw = fore_w / cheek_w
    jw = jaw_w / cheek_w

    # Best-effort decision tree → (shape, element). Boundaries are fuzzy; the VLM
    # confirms. Element keys match face_knowledge.json.
    if fw - jw >= 0.12 and aspect < 1.5:
        shape, conf = "tapering", "medium"          # forehead wider than jaw → Fire
    elif aspect >= 1.32 and fw < 0.92 and jw < 0.92:
        shape, conf = "oval", "medium"              # longer than wide, tapered both ends → Air
    elif aspect < 1.18 and jw >= 0.9:
        shape, conf = "square", "medium"            # width≈length, strong jaw → Earth
    elif aspect < 1.22 and jw < 0.9 and fw < 0.95:
        shape, conf = "round", "medium"             # soft, width-dominant → Water
    elif jw < fw and fw < 1.0 and 1.1 <= aspect < 1.32:
        shape, conf = "inverted_pot", "low"         # cheek-widest diamond-ish → Ether
    else:
        shape, conf = "oval", "low"
    element = {"square": "earth", "round": "water", "tapering": "fire",
               "oval": "air", "inverted_pot": "ether"}[shape]
    return {
        "primary": shape, "element": element, "confidence": conf,
        "aspect_ratio": round(aspect, 3),
        "forehead_to_cheek": round(fw, 3),
        "jaw_to_cheek": round(jw, 3),
    }


def _zones(L):
    top = L["forehead_top"][1]
    brow = (L["brow_l_peak"][1] + L["brow_r_peak"][1]) / 2
    nbase = L["nose_base"][1]
    chin = L["chin"][1]
    total = (chin - top) or 1
    upper = (brow - top) / total
    mid = (nbase - brow) / total
    lower = (chin - nbase) / total
    parts = {"upper_forehead": upper, "mid_nose": mid, "lower_mouth": lower}
    dominant = max(parts, key=parts.get)
    return {
        "upper": round(upper, 3), "mid": round(mid, 3), "lower": round(lower, 3),
        "dominant": dominant,
        "note": "Upper zone uses the visible forehead top (Face Mesh has no hairline point), so it reads conservatively.",
    }


def _eyes(L):
    lw = _d(L["eye_l_out"], L["eye_l_in"])
    rw = _d(L["eye_r_in"], L["eye_r_out"])
    eye_w = (lw + rw) / 2 or 1
    inter = _d(L["eye_l_in"], L["eye_r_in"])
    spacing_ratio = inter / eye_w
    spacing = "wide_set" if spacing_ratio > 1.08 else ("close_set" if spacing_ratio < 0.92 else "average")
    # canthal tilt: outer corner higher (smaller y) than inner → upturned
    tilt_l = L["eye_l_in"][1] - L["eye_l_out"][1]
    tilt_r = L["eye_r_in"][1] - L["eye_r_out"][1]
    tilt = (tilt_l + tilt_r) / 2 / eye_w
    tilt_label = "upturned" if tilt > 0.06 else ("downturned" if tilt < -0.06 else "neutral")
    # openness
    open_l = _d(L["eye_l_top"], L["eye_l_bot"]) / (lw or 1)
    open_r = _d(L["eye_r_top"], L["eye_r_bot"]) / (rw or 1)
    openness = (open_l + open_r) / 2
    size = "large_bright" if openness > 0.45 else ("small_narrow" if openness < 0.3 else "average")
    return {
        "spacing": spacing, "spacing_ratio": round(spacing_ratio, 3),
        "tilt": tilt_label, "tilt_ratio": round(tilt, 3),
        "size": size, "openness_ratio": round(openness, 3),
    }


def _nose(L):
    length = _d(L["nose_bridge"], L["nose_base"])
    width = _d(L["ala_l"], L["ala_r"])
    face_len = _d(L["forehead_top"], L["chin"]) or 1
    cheek_w = _d(L["cheek_l"], L["cheek_r"]) or 1
    len_ratio = length / face_len
    wid_ratio = width / cheek_w
    return {
        "length": "long" if len_ratio > 0.30 else ("short" if len_ratio < 0.24 else "medium"),
        "width": "wide_fleshy" if wid_ratio > 0.27 else ("narrow" if wid_ratio < 0.21 else "medium"),
        "length_ratio": round(len_ratio, 3), "width_ratio": round(wid_ratio, 3),
    }


def _lips_chin(L):
    mouth_w = _d(L["mouth_l"], L["mouth_r"])
    cheek_w = _d(L["cheek_l"], L["cheek_r"]) or 1
    lip_h = _d(L["lip_top"], L["lip_bot"])
    face_len = _d(L["forehead_top"], L["chin"]) or 1
    jaw_w = _d(L["jaw_l"], L["jaw_r"])
    mw = mouth_w / cheek_w
    lh = lip_h / face_len
    jw = jaw_w / cheek_w
    return {
        "mouth_width": "wide" if mw > 0.4 else ("small" if mw < 0.32 else "average"),
        "lip_fullness": "full" if lh > 0.14 else ("thin" if lh < 0.09 else "average"),
        "jaw": "broad_strong_jaw" if jw > 0.92 else ("weak_receding" if jw < 0.78 else "average"),
        "mouth_ratio": round(mw, 3), "lip_ratio": round(lh, 3), "jaw_ratio": round(jw, 3),
    }


def _symmetry(L):
    mid_x = np.mean([L["forehead_top"][0], L["chin"][0], L["nose_bridge"][0], L["nose_base"][0]])
    face_w = _d(L["cheek_l"], L["cheek_r"]) or 1
    pairs = [("eye_l_out", "eye_r_out"), ("mouth_l", "mouth_r"), ("cheek_l", "cheek_r"), ("jaw_l", "jaw_r")]
    diffs = [abs(abs(L[a][0] - mid_x) - abs(L[b][0] - mid_x)) / face_w for a, b in pairs]
    score = float(np.mean(diffs))
    return {"score": round(score, 3), "label": "high" if score < 0.04 else ("moderate" if score < 0.08 else "low")}


# ══════════════════════════════════════════════════════════════════════════════
# REGION CROPS for the VLM
# ══════════════════════════════════════════════════════════════════════════════

def _crop(rgb, xs, ys, pad_frac=0.12):
    h, w = rgb.shape[:2]
    x1, x2 = min(xs), max(xs); y1, y2 = min(ys), max(ys)
    pw = int((x2 - x1) * pad_frac) + 4; ph = int((y2 - y1) * pad_frac) + 4
    x1 = max(0, x1 - pw); y1 = max(0, y1 - ph)
    x2 = min(w, x2 + pw); y2 = min(h, y2 + ph)
    crop = rgb[y1:y2, x1:x2]
    return crop if crop.size else None


def _region_crops(rgb, L):
    out = {}
    forehead = _crop(rgb, [L["temple_l"][0], L["temple_r"][0]],
                     [L["forehead_top"][1], int((L["brow_l_peak"][1] + L["brow_r_peak"][1]) / 2)])
    eyes = _crop(rgb, [L["eye_l_out"][0], L["eye_r_out"][0]],
                 [min(L["brow_l_peak"][1], L["brow_r_peak"][1]), max(L["eye_l_bot"][1], L["eye_r_bot"][1])])
    nose = _crop(rgb, [L["ala_l"][0], L["ala_r"][0]], [L["nose_bridge"][1], L["nose_base"][1]])
    mouth = _crop(rgb, [L["mouth_l"][0], L["mouth_r"][0]], [L["lip_top"][1], L["chin"][1]])
    for name, c in [("forehead", forehead), ("eyes", eyes), ("nose", nose), ("mouth_chin", mouth)]:
        if c is not None:
            out[name] = c
    return out


def _draw_overlay(rgb, L, all_pts):
    out = cv2.cvtColor(rgb.copy(), cv2.COLOR_RGB2BGR)
    for (x, y) in all_pts:
        cv2.circle(out, (x, y), 1, (180, 160, 220), -1, cv2.LINE_AA)
    for key in ("forehead_top", "chin", "cheek_l", "cheek_r", "nose_tip",
                "eye_l_out", "eye_r_out", "mouth_l", "mouth_r"):
        cv2.circle(out, L[key], 4, (80, 180, 255), -1, cv2.LINE_AA)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def analyze_face(image_bytes):
    """Analyze a face photo. Returns a dict of reliable signals + VLM inputs.

    Keys: face_found, quality_issues, quality_metrics, pose_issues, pose_metrics,
          metrics (face_shape/zones/eyes/nose/lips_chin/symmetry),
          enhanced_face, region_crops, landmark_overlay, lm.
    Always returns the keys; missing data → empty/unknown rather than crashing.
    """
    img = PIL.ImageOps.exif_transpose(PIL.Image.open(io.BytesIO(image_bytes))).convert("RGB")
    raw = _gray_world_balance(_resize_to_width(np.array(img), CFG["target_width"]))
    quality_issues, quality_metrics = _assess_quality(raw)

    results = _get_face_mesh().process(raw)
    face_found = bool(results.multi_face_landmarks)

    if not face_found:
        return {
            "face_found": False, "quality_issues": quality_issues,
            "quality_metrics": quality_metrics, "pose_issues": [], "pose_metrics": {},
            "metrics": {}, "enhanced_face": enhance_for_vlm(raw),
            "region_crops": {}, "landmark_overlay": raw, "lm": None,
        }

    h, w = raw.shape[:2]
    pts = [(int(p.x * w), int(p.y * h)) for p in results.multi_face_landmarks[0].landmark]
    L = {name: pts[idx] for name, idx in LM.items()}

    pose_issues, pose_metrics = _pose_check(L)
    metrics = {
        "face_shape": _face_shape(L),
        "zones": _zones(L),
        "eyes": _eyes(L),
        "nose": _nose(L),
        "lips_chin": _lips_chin(L),
        "symmetry": _symmetry(L),
    }
    enhanced = enhance_for_vlm(raw)
    return {
        "face_found": True,
        "quality_issues": quality_issues,
        "quality_metrics": quality_metrics,
        "pose_issues": pose_issues,
        "pose_metrics": pose_metrics,
        "metrics": metrics,
        "enhanced_face": enhanced,
        "region_crops": _region_crops(enhanced, L),
        "landmark_overlay": _draw_overlay(enhanced, L, pts),
        "lm": L,
    }
