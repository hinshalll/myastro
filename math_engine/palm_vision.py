"""
math_engine/palm_vision.py
============================
Slim, accuracy-first palm vision math engine.

WHAT THIS DOES (only deterministic, reliable signals):
  - MediaPipe 21-landmark detection
  - Orientation normalization (wrist at bottom, fingers up)
  - CLAHE enhancement on LAB L-channel
  - Hand type classification from geometry (Earth/Air/Fire/Water)
  - 2D:4D digit ratio (well-supported in research literature)
  - Skin vitality class (broad HSV buckets, no false precision)
  - Image quality gate (blur, exposure, resolution)
  - Mount region crops via landmark geometry (for VLM input only)
  - Clean landmark-overlay visualization for the UI

WHAT THIS DELIBERATELY DOES NOT DO:
  - Frangi vesselness filtering (was built for blood vessels, not palm creases)
  - Skeletonization, persistence voting, watershed line isolation
  - Major line tracing via component analysis (picks wrong components on real palms)
  - Mark detection (cross/star/triangle/island classification — was noise)
  - Minor line detection (was presence-thresholding skin texture)
  - Fingerprint pattern detection from a non-macro photo (impossible at this resolution)
  - Mount elevation scoring from brightness or sharpness (measures lighting, not depth)

The VLM (Gemini) does all of the above instead, by looking at the actual photograph.
This file produces only signals that are deterministic and accurate.
"""

# ── Protobuf compatibility patch for MediaPipe ─────────────────────────────────
from google.protobuf import symbol_database as _sym_db
if not hasattr(_sym_db.Default(), "GetPrototype"):
    from google.protobuf.message_factory import GetMessageClass
    _sym_db.SymbolDatabase.GetPrototype = lambda self, desc: GetMessageClass(desc)

import io
import cv2
import numpy as np
import PIL.Image
import mediapipe as mp

mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5,
)


# ── CONFIG ─────────────────────────────────────────────────────────────────────

CFG = {
    "target_width":      1024,    # Resize input to this width (good for VLM tokens)
    "clahe_clip":        2.5,
    "clahe_tile":        (8, 8),
    "blur_min":          80,      # Laplacian variance threshold
    "value_min":         35,
    "value_max":         235,
    "min_resolution":    600,     # Smallest dimension threshold
    "mount_crop_frac":   0.22,    # Mount crop size as fraction of palm height
}

HAND_TYPES = {
    "square_short": ("Earth Hand", "Prithvi Hasta", "Practical, grounded, reliable"),
    "square_long":  ("Air Hand",   "Vayu Hasta",    "Intellectual, communicative, restless"),
    "oblong_short": ("Fire Hand",  "Agni Hasta",    "Passionate, impulsive, creative"),
    "oblong_long":  ("Water Hand", "Jal Hasta",     "Intuitive, emotional, empathetic"),
}


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE PREPARATION
# ══════════════════════════════════════════════════════════════════════════════

def _resize_to_width(rgb, target_width):
    h, w = rgb.shape[:2]
    if w == target_width:
        return rgb
    scale = target_width / w
    return cv2.resize(rgb, (target_width, int(h * scale)), interpolation=cv2.INTER_AREA)


def _gray_world_balance(rgb):
    """Gray-world white balance. Corrects warm/cool casts."""
    f = rgb.astype(np.float32)
    means = f.reshape(-1, 3).mean(axis=0)
    gray = means.mean()
    scale = gray / np.maximum(means, 1e-6)
    return np.clip(f * scale, 0, 255).astype(np.uint8)


def _apply_clahe_lab(rgb):
    """CLAHE on L channel of LAB. Boosts line contrast without color shift."""
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=CFG["clahe_clip"], tileGridSize=CFG["clahe_tile"])
    l_eq = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l_eq, a, b]), cv2.COLOR_LAB2RGB)


def enhance_for_vlm(rgb):
    """
    Final enhancement before VLM input. CLAHE + mild unsharp mask.
    Boosts line contrast significantly without distorting color or geometry.
    """
    out = _apply_clahe_lab(rgb)
    blur = cv2.GaussianBlur(out, (0, 0), 1.2)
    out = cv2.addWeighted(out, 1.4, blur, -0.4, 0)
    return out




def _assess_quality(rgb):
    """Returns (issues_list, metrics_dict). Issues are actionable user-facing."""
    issues = []
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_v = float(cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[:, :, 2].mean())
    h, w = rgb.shape[:2]

    if blur_score < CFG["blur_min"]:
        issues.append("Image is blurry. Re-take with steady hands and good focus.")
    if mean_v < CFG["value_min"]:
        issues.append("Image is too dark. Use better lighting.")
    if mean_v > CFG["value_max"]:
        issues.append("Image is overexposed. Avoid direct flash on the palm.")
    if min(h, w) < CFG["min_resolution"]:
        issues.append("Image resolution is low. Use a higher-resolution photo.")

    return issues, {
        "blur_score":  round(blur_score, 1),
        "mean_v":      round(mean_v, 1),
        "resolution":  f"{w}x{h}",
        "is_usable":   len(issues) == 0,
    }


# Orientation normalization removed — rotating the image added awkward
# tilting artifacts and provided no benefit. The VLM reads lines correctly
# regardless of orientation, and users prefer to see their palm as shot.


# ══════════════════════════════════════════════════════════════════════════════
# HAND METRICS — deterministic geometry only
# ══════════════════════════════════════════════════════════════════════════════

def _compute_hand_metrics(lm_dict):
    """Hand type, 2D:4D ratio, dominant finger from MediaPipe landmarks."""
    if not lm_dict:
        return {}

    palm_w = float(np.linalg.norm(np.array(lm_dict[5]) - np.array(lm_dict[17])))
    palm_l = float(np.linalg.norm(np.array(lm_dict[9]) - np.array(lm_dict[0])))

    middle_len = float(np.linalg.norm(np.array(lm_dict[12]) - np.array(lm_dict[9])))
    index_len  = float(np.linalg.norm(np.array(lm_dict[8])  - np.array(lm_dict[5])))
    ring_len   = float(np.linalg.norm(np.array(lm_dict[16]) - np.array(lm_dict[13])))
    pinky_len  = float(np.linalg.norm(np.array(lm_dict[20]) - np.array(lm_dict[17])))
    thumb_len  = float(np.linalg.norm(np.array(lm_dict[4])  - np.array(lm_dict[2])))

    palm_aspect    = palm_l / max(palm_w, 1)
    finger_to_palm = middle_len / max(palm_l, 1)

    palm_class = "oblong" if palm_aspect > 1.10 else "square"
    finger_class = "long" if finger_to_palm > 0.85 else "short"
    key = f"{palm_class}_{finger_class}"
    type_name, vedic, gloss = HAND_TYPES.get(key, ("Mixed Hand", "Mishra Hasta", "Balanced qualities"))

    # 2D:4D ratio (index to ring) — well-supported in research
    ratio_2d4d = round(float(index_len / max(ring_len, 1)), 3)
    if ratio_2d4d < 0.95:
        ratio_reading = "Lower than typical (associated with higher prenatal androgen exposure)"
    elif ratio_2d4d > 1.00:
        ratio_reading = "Higher than typical (associated with lower prenatal androgen exposure)"
    else:
        ratio_reading = "Within typical range"

    # Dominant finger relative to palm length
    finger_ratios = {
        "Jupiter (index)":  index_len  / max(palm_l, 1),
        "Saturn (middle)":  middle_len / max(palm_l, 1),
        "Sun (ring)":       ring_len   / max(palm_l, 1),
        "Mercury (little)": pinky_len  / max(palm_l, 1),
    }
    dominant = max(finger_ratios.items(), key=lambda x: x[1])[0]

    return {
        "hand_type":         type_name,
        "hand_type_vedic":   vedic,
        "hand_type_gloss":   gloss,
        "palm_aspect":       round(palm_aspect, 3),
        "finger_to_palm":    round(finger_to_palm, 3),
        "ratio_2d4d":        ratio_2d4d,
        "ratio_reading":     ratio_reading,
        "dominant_finger":   dominant,
        "thumb_proportion":  round(thumb_len / max(palm_l, 1), 3),
    }


def _vitality_class(rgb, lm_dict):
    """
    Broad vitality bucket from HSV of palm interior.
    Four categories only — no fake precision.
    """
    if not lm_dict:
        return {"class": "unknown", "note": "Landmarks not detected"}

    h, w = rgb.shape[:2]
    pts = np.array([lm_dict[i] for i in [0, 1, 5, 9, 13, 17]], dtype=np.int32)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    region = mask > 0
    if not np.any(region):
        return {"class": "unknown", "note": ""}

    hue = float(np.mean(hsv[:, :, 0][region]))
    sat = float(np.mean(hsv[:, :, 1][region]))
    val = float(np.mean(hsv[:, :, 2][region]))

    if sat > 75 and val > 130 and 0 <= hue <= 22:
        cls, note = "Robust",   "Warm, well-perfused tone — strong vital energy"
    elif sat < 38 or val < 100:
        cls, note = "Subdued",  "Pale or muted tone — review rest and circulation"
    elif 5 <= hue <= 22 and 45 < sat < 95:
        cls, note = "Balanced", "Healthy, even tone"
    else:
        cls, note = "Cool",     "Cooler tone — variable energy reserves"

    return {
        "class": cls,
        "note":  note,
        "hue":   round(hue, 1),
        "sat":   round(sat, 1),
        "val":   round(val, 1),
    }


# ══════════════════════════════════════════════════════════════════════════════
# MOUNT REGION CROPS — for VLM input, not for scoring
# ══════════════════════════════════════════════════════════════════════════════

def _mount_centers(lm_dict):
    """Compute approximate (x, y) center of each planetary mount in image space."""
    if not lm_dict:
        return {}

    def shift_toward_palm_center(p, palm_center, frac):
        return (
            int(p[0] + (palm_center[0] - p[0]) * frac),
            int(p[1] + (palm_center[1] - p[1]) * frac),
        )

    palm_cx = int(np.mean([lm_dict[i][0] for i in [0, 5, 9, 13, 17]]))
    palm_cy = int(np.mean([lm_dict[i][1] for i in [0, 5, 9, 13, 17]]))
    palm_center = (palm_cx, palm_cy)

    # Finger-base mounts: shift slightly into the palm from the finger base
    jupiter = shift_toward_palm_center(lm_dict[5],  palm_center, 0.18)
    saturn  = shift_toward_palm_center(lm_dict[9],  palm_center, 0.18)
    sun     = shift_toward_palm_center(lm_dict[13], palm_center, 0.18)
    mercury = shift_toward_palm_center(lm_dict[17], palm_center, 0.18)

    # Venus: thumb base, lower part — between landmarks 1 and 2 shifted toward palm
    venus_raw = ((lm_dict[1][0] + lm_dict[2][0]) // 2,
                 (lm_dict[1][1] + lm_dict[2][1]) // 2)
    venus = shift_toward_palm_center(venus_raw, palm_center, 0.20)

    # Mars: middle of palm interior (combined Mars area)
    mars = palm_center

    # Luna: lower outer palm, opposite Venus
    # Use point between landmark 17 and wrist, shifted outward (away from thumb)
    luna_x = lm_dict[17][0]
    luna_y = int((lm_dict[17][1] + lm_dict[0][1]) * 0.55)
    # Push slightly outward (away from palm center)
    dx = luna_x - palm_cx
    luna_x = int(luna_x + dx * 0.12)
    luna = (luna_x, luna_y)

    return {
        "Jupiter": jupiter,
        "Saturn":  saturn,
        "Sun":     sun,
        "Mercury": mercury,
        "Venus":   venus,
        "Mars":    mars,
        "Luna":    luna,
    }


def _crop_mount(rgb, center, size_px, bg=(20, 14, 28)):
    h, w = rgb.shape[:2]
    half = size_px // 2
    x1 = max(0, center[0] - half)
    y1 = max(0, center[1] - half)
    x2 = min(w, center[0] + half)
    y2 = min(h, center[1] + half)
    crop = rgb[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    ch, cw = crop.shape[:2]
    if ch != size_px or cw != size_px:
        canvas = np.full((size_px, size_px, 3), bg, dtype=np.uint8)
        oy = (size_px - ch) // 2
        ox = (size_px - cw) // 2
        canvas[oy:oy + ch, ox:ox + cw] = crop
        return canvas
    return crop


def extract_mount_crops(rgb, lm_dict, palm_height_px):
    """
    Extract 7 mount crops from the enhanced palm.
    Sized as ~22% of palm height, clamped to [140, 320] px.
    Returns dict {mount_name: rgb_array}.
    """
    if not lm_dict:
        return {}
    centers = _mount_centers(lm_dict)
    size_px = int(palm_height_px * CFG["mount_crop_frac"])
    size_px = max(140, min(size_px, 320))
    crops = {}
    for name, c in centers.items():
        crop = _crop_mount(rgb, c, size_px)
        if crop is not None:
            crops[name] = crop
    return crops


# ══════════════════════════════════════════════════════════════════════════════
# LANDMARK OVERLAY — clean visualization for the UI
# ══════════════════════════════════════════════════════════════════════════════

def _draw_landmarks(rgb, lm_dict):
    """Draw clean 21-landmark skeleton on the palm. The only overlay we ship."""
    out = cv2.cvtColor(rgb.copy(), cv2.COLOR_RGB2BGR)
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),         # thumb
        (0, 5), (5, 6), (6, 7), (7, 8),         # index
        (0, 9), (9, 10), (10, 11), (11, 12),    # middle
        (0, 13), (13, 14), (14, 15), (15, 16),  # ring
        (0, 17), (17, 18), (18, 19), (19, 20),  # pinky
        (5, 9), (9, 13), (13, 17),              # palm bridge
    ]
    for a, b in connections:
        if a in lm_dict and b in lm_dict:
            cv2.line(out, lm_dict[a], lm_dict[b], (220, 200, 240), 1, cv2.LINE_AA)

    for i, (x, y) in lm_dict.items():
        if i in (4, 8, 12, 16, 20):  # tips
            cv2.circle(out, (x, y), 5, (80, 180, 255), -1, cv2.LINE_AA)
            cv2.circle(out, (x, y), 6, (255, 255, 255),  1, cv2.LINE_AA)
        elif i == 0:  # wrist
            cv2.circle(out, (x, y), 5, (220, 100, 220), -1, cv2.LINE_AA)
        else:
            cv2.circle(out, (x, y), 3, (220, 200, 240), -1, cv2.LINE_AA)

    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


# ══════════════════════════════════════════════════════════════════════════════
# HAND ISOLATION — landmark-guided GrabCut for premium display
# ══════════════════════════════════════════════════════════════════════════════

def isolate_hand_for_display(rgb, lm_dict, target_width=560):
    """
    Removes the background from a palm photo using landmark-guided GrabCut,
    returns a tightly-cropped RGBA image with the hand on a transparent
    background. Used by the UI for the premium animated palm display.

    Returns None on failure (caller falls back to the un-isolated image).

    How it works:
      1. Resize to target_width for speed (GrabCut is O(pixels)).
      2. Build initial mask from MediaPipe landmarks:
         - Corners marked as DEFINITE BACKGROUND
         - Expanded hand polygon (1.35x from centroid) marked PROBABLE FG
         - Inner palm polygon marked DEFINITE FG
      3. Run GrabCut for 4 iterations.
      4. Feather the resulting alpha mask with Gaussian blur.
      5. Tight crop to the hand bounding box + 8% padding.
    """
    h, w = rgb.shape[:2]
    if w == 0 or h == 0 or not lm_dict:
        return None

    # ── Resize for performance ───────────────────────────────────────────────
    scale = target_width / w
    target_h = int(h * scale)
    small = cv2.resize(rgb, (target_width, target_h), interpolation=cv2.INTER_AREA)
    small_lm = {k: (int(v[0] * scale), int(v[1] * scale)) for k, v in lm_dict.items()}

    sh, sw = small.shape[:2]

    # ── Build the GrabCut mask ───────────────────────────────────────────────
    mask = np.full((sh, sw), cv2.GC_PR_BGD, dtype=np.uint8)

    # Definite background — corners (8px borders)
    bw = max(4, min(sw, sh) // 60)
    mask[:bw, :]  = cv2.GC_BGD
    mask[-bw:, :] = cv2.GC_BGD
    mask[:, :bw]  = cv2.GC_BGD
    mask[:, -bw:] = cv2.GC_BGD

    # All 21 landmarks → convex hull → expanded 1.35x from centroid
    pts = np.array([small_lm[i] for i in range(21) if i in small_lm], dtype=np.int32)
    hull = cv2.convexHull(pts)

    M = cv2.moments(hull)
    cx = int(M['m10'] / M['m00']) if M['m00'] > 0 else sw // 2
    cy = int(M['m01'] / M['m00']) if M['m00'] > 0 else sh // 2

    expanded = np.array(
        [[int(cx + (p[0] - cx) * 1.35),
          int(cy + (p[1] - cy) * 1.30)] for p in hull[:, 0]],
        dtype=np.int32,
    )
    cv2.fillPoly(mask, [expanded], cv2.GC_PR_FGD)

    # Definite foreground — palm interior (landmarks 0, 5, 9, 13, 17 shrunk 0.7x)
    palm_pts = np.array(
        [small_lm[i] for i in [0, 5, 9, 13, 17] if i in small_lm],
        dtype=np.int32,
    )
    if len(palm_pts) >= 3:
        palm_hull = cv2.convexHull(palm_pts)
        shrunk = np.array(
            [[int(cx + (p[0] - cx) * 0.72),
              int(cy + (p[1] - cy) * 0.72)] for p in palm_hull[:, 0]],
            dtype=np.int32,
        )
        cv2.fillPoly(mask, [shrunk], cv2.GC_FGD)

    # Each fingertip — a small definite-foreground disc
    for i in (4, 8, 12, 16, 20):
        if i in small_lm:
            cv2.circle(mask, small_lm[i], 8, cv2.GC_FGD, -1)

    # ── Run GrabCut ──────────────────────────────────────────────────────────
    bgd_model = np.zeros((1, 65), dtype=np.float64)
    fgd_model = np.zeros((1, 65), dtype=np.float64)

    try:
        cv2.grabCut(
            small, mask, None, bgd_model, fgd_model, 4, cv2.GC_INIT_WITH_MASK
        )
    except Exception:
        return None

    # ── Build the alpha mask ─────────────────────────────────────────────────
    fg_mask = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)

    # Largest connected component only — drops isolated artifacts
    num, labels, stats, _ = cv2.connectedComponentsWithStats(fg_mask, connectivity=8)
    if num > 1:
        largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        fg_mask = np.where(labels == largest, 255, 0).astype(np.uint8)

    # Feather the edges — Gaussian blur for soft alpha falloff
    fg_mask = cv2.GaussianBlur(fg_mask, (15, 15), 4)

    # ── Build RGBA and tight-crop to hand ────────────────────────────────────
    rgba = np.dstack([small, fg_mask])

    # Tight crop using actual mask bounds (alpha > 8 threshold)
    ys, xs = np.where(fg_mask > 8)
    if len(xs) == 0:
        return None
    x1, x2 = int(xs.min()), int(xs.max())
    y1, y2 = int(ys.min()), int(ys.max())

    pad_x = int((x2 - x1) * 0.06)
    pad_y = int((y2 - y1) * 0.06)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(sw, x2 + pad_x)
    y2 = min(sh, y2 + pad_y)

    cropped = rgba[y1:y2, x1:x2]
    if cropped.size == 0:
        return None
    return cropped


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def analyze_palm(image_bytes):
    """
    Single entry point. Analyzes a palm photograph and returns a clean dict
    of reliable signals plus the inputs the VLM will need.

    Returns dict with keys:
      landmarks_found   : bool
      quality_issues    : list[str]   (user-facing actionable warnings)
      quality_metrics   : dict        (blur, exposure, resolution, is_usable)
      hand_metrics      : dict        (hand type, 2D:4D, dominant finger, etc.)
      vitality          : dict        (class, note, hsv values)
      enhanced_palm     : ndarray     (CLAHE-enhanced full palm — RGB)
      mount_crops       : dict        ({name: ndarray})
      landmark_overlay  : ndarray     (palm with landmark skeleton drawn — RGB)
      lm_dict           : dict        (raw landmarks, for downstream debugging)

    Always returns these keys; missing data yields empty dict / unknown values
    rather than crashing.
    """
    img = PIL.Image.open(io.BytesIO(image_bytes)).convert("RGB")
    raw = _resize_to_width(np.array(img), CFG["target_width"])
    raw = _gray_world_balance(raw)

    quality_issues, quality_metrics = _assess_quality(raw)

    # MediaPipe detection
    results = hands_detector.process(raw)
    landmarks_found = bool(results.multi_hand_landmarks)
    lm_dict = None

    if landmarks_found:
        h, w = raw.shape[:2]
        lm_raw = results.multi_hand_landmarks[0]
        lm_dict = {i: (int(p.x * w), int(p.y * h)) for i, p in enumerate(lm_raw.landmark)}
        # No rotation — palm shown as shot

    enhanced = enhance_for_vlm(raw)

    hand_metrics = _compute_hand_metrics(lm_dict) if landmarks_found else {}
    # Vitality uses RAW (pre-CLAHE) image so colour/tone is not shifted by enhancement
    vitality = _vitality_class(raw, lm_dict) if landmarks_found else {
        "class": "unknown",
        "note":  "Landmarks not detected",
    }

    mount_crops   = {}
    overlay       = enhanced.copy()
    hand_isolated = None
    if landmarks_found:
        palm_h_px     = abs(lm_dict[0][1] - lm_dict[9][1])
        mount_crops   = extract_mount_crops(enhanced, lm_dict, palm_h_px)
        overlay       = _draw_landmarks(enhanced, lm_dict)
        # Use raw (natural-colour) image for the display isolation — CLAHE can
        # make skin look unnatural. The VLM still gets the enhanced version.
        try:
            hand_isolated = isolate_hand_for_display(raw, lm_dict, target_width=560)
        except Exception:
            hand_isolated = None

    return {
        "landmarks_found":  landmarks_found,
        "quality_issues":   quality_issues,
        "quality_metrics":  quality_metrics,
        "hand_metrics":     hand_metrics,
        "vitality":         vitality,
        "enhanced_palm":    enhanced,
        "mount_crops":      mount_crops,
        "landmark_overlay": overlay,
        "hand_isolated":    hand_isolated,  # RGBA, hand on transparent bg, or None
        "lm_dict":          lm_dict,
    }