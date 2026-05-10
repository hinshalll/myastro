# Protobuf >= 4.21 removed GetPrototype — patch it back for MediaPipe compatibility
from google.protobuf import symbol_database as _sym_db
if not hasattr(_sym_db.Default(), "GetPrototype"):
    from google.protobuf.message_factory import GetMessageClass
    _sym_db.SymbolDatabase.GetPrototype = lambda self, desc: GetMessageClass(desc)

import io
import cv2
import numpy as np
import PIL.Image
from skimage.filters import frangi
from skimage.morphology import skeletonize, remove_small_objects
from skimage.measure import label as sk_label, regionprops
from scipy.ndimage import convolve

import mediapipe as mp
mp_hands = mp.solutions.hands

hands_detector = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5,
)

# ── FEATURE FLAG ───────────────────────────────────────────────────────────────
USE_DEPTH_MODEL = False   # Flip to True only on FastAPI server with enough RAM

_depth_model_cache = {}   # module-level cache; no Streamlit import needed


def _load_depth_model():
    if "model" not in _depth_model_cache:
        try:
            from transformers import pipeline as hf_pipeline
            _depth_model_cache["model"] = hf_pipeline(
                "depth-estimation",
                model="depth-anything/Depth-Anything-V2-Small-hf",
                device=-1,
            )
        except Exception:
            _depth_model_cache["model"] = None
    return _depth_model_cache["model"]


# ── GLOBAL CONFIG ──────────────────────────────────────────────────────────────
CFG = {
    "resize_width":           900,
    "clahe_clip":             3.0,
    "clahe_tile":             (8, 8),
    "clahe_crop_clip":        5.0,
    "clahe_crop_tile":        (4, 4),
    "frangi_sigmas":          range(1, 9),
    "persist_thresholds":     [15, 25, 35, 45, 55, 65, 75, 85],
    "persist_min_count":      3,      # Otsu floor
    "watershed_dilate":       12,
    "watershed_terrain_t":    15,
    "min_component_px":       200,
    "skel_min_size":          30,
    "quality_blur_min":       80,     # Laplacian variance
    "quality_v_min":          35,
    "quality_v_max":          235,
    "line_min_horiz_frac":    0.38,   # min length as fraction of palm width
    "line_min_vert_frac":     0.22,   # min length as fraction of palm height
    "line_min_life_frac":     0.28,
    "mark_min_area":          8,
    "mark_max_area":          650,
}

LINE_LABELS = {
    "heart_line": "Heart Line",
    "head_line":  "Head Line",
    "life_line":  "Life Line",
    "fate_line":  "Fate Line",
    "sun_line":   "Sun / Apollo Line",
}

HAND_TYPES = {
    "square_short": ("Earth Hand", "Prithvi Hasta — Practical, grounded, reliable"),
    "square_long":  ("Air Hand",   "Vayu Hasta — Intellectual, communicative, restless"),
    "oblong_short": ("Fire Hand",  "Agni Hasta — Passionate, impulsive, creative"),
    "oblong_long":  ("Water Hand", "Jal Hasta — Intuitive, emotional, empathetic"),
}


# ══════════════════════════════════════════════════════════════════════
# SECTION 1 — IMAGE PREPARATION
# ══════════════════════════════════════════════════════════════════════

def gray_world_balance(rgb):
    """
    Gray-world white balance. Corrects for tungsten, overcast, and sunset casts.
    Skin-tone agnostic — operates on per-channel means, not thresholds.
    """
    f = rgb.astype(np.float32)
    means = f.reshape(-1, 3).mean(axis=0)          # R, G, B means
    gray  = means.mean()
    scale = gray / np.maximum(means, 1e-6)
    return np.clip(f * scale, 0, 255).astype(np.uint8)


def enhance_and_resize(image_array, target_width=None):
    if target_width is None:
        target_width = CFG["resize_width"]
    h, w   = image_array.shape[:2]
    resized = cv2.resize(
        image_array,
        (target_width, int(target_width * h / max(w, 1))),
        interpolation=cv2.INTER_AREA,
    )
    kernel = np.array([[0, -0.5, 0], [-0.5, 3, -0.5], [0, -0.5, 0]])
    return cv2.filter2D(resized, -1, kernel)


def pad_to_square(crop_rgb, size=300, bg=(12, 8, 20)):
    if crop_rgb is None or (isinstance(crop_rgb, np.ndarray) and crop_rgb.size == 0):
        return np.full((size, size, 3), bg, dtype=np.uint8)
    h, w   = crop_rgb.shape[:2]
    scale  = min(size / max(h, 1), size / max(w, 1))
    nw, nh = int(w * scale), int(h * scale)
    res    = cv2.resize(crop_rgb, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.full((size, size, 3), bg, dtype=np.uint8)
    yo, xo = (size - nh) // 2, (size - nw) // 2
    canvas[yo:yo + nh, xo:xo + nw] = res
    return canvas


def get_safe_box(x, y, w, h, img_w, img_h, pad=0.35):
    pw, ph = int(w * pad), int(h * pad)
    return (
        max(0, x - pw), max(0, y - ph),
        min(img_w, x + w + pw), min(img_h, y + h + ph),
    )


def remove_background(frame_rgb):
    """GrabCut background removal with threshold fallback."""
    try:
        mask = np.zeros(frame_rgb.shape[:2], np.uint8)
        bgd  = np.zeros((1, 65), np.float64)
        fgd  = np.zeros((1, 65), np.float64)
        h, w = frame_rgb.shape[:2]
        mg   = max(5, int(min(h, w) * 0.03))
        cv2.grabCut(
            cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR),
            mask, (mg, mg, w - mg * 2, h - mg * 2),
            bgd, fgd, 5, cv2.GC_INIT_WITH_RECT,
        )
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
        ctrs, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if ctrs:
            c = max(ctrs, key=cv2.contourArea)
            x, y, bw, bh = cv2.boundingRect(c)
            p = 20
            x, y = max(0, x - p), max(0, y - p)
            return frame_rgb[y:y + min(h - y, bh + p * 2),
                             x:x + min(w - x, bw + p * 2)]
    except Exception:
        pass
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    _, th = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    ctrs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if ctrs:
        c = max(ctrs, key=cv2.contourArea)
        x, y, bw, bh = cv2.boundingRect(c)
        p = 20
        x, y = max(0, x - p), max(0, y - p)
        return frame_rgb[y:y + min(frame_rgb.shape[0] - y, bh + p * 2),
                         x:x + min(frame_rgb.shape[1] - x, bw + p * 2)]
    return frame_rgb


# ══════════════════════════════════════════════════════════════════════
# SECTION 2 — QUALITY GATE
# ══════════════════════════════════════════════════════════════════════

def assess_image_quality(frame_rgb):
    """
    Returns (quality_dict, issues_list).
    issues_list is empty if image is acceptable.
    Called BEFORE MediaPipe so bad images are rejected cheaply.
    """
    gray   = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    blur   = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    hsv    = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)
    mean_v = float(cv2.mean(hsv)[2])
    mean_s = float(cv2.mean(hsv)[1])
    h, w   = frame_rgb.shape[:2]
    issues = []

    if blur < CFG["quality_blur_min"]:
        issues.append(
            f"Image is too blurry (sharpness {blur:.0f}, need >{CFG['quality_blur_min']}). "
            "Hold your phone steady and tap to focus before capturing."
        )
    if mean_v > CFG["quality_v_max"]:
        issues.append(
            "Image is overexposed. Move away from direct light or switch off flash."
        )
    if mean_v < CFG["quality_v_min"]:
        issues.append(
            "Image is too dark. Use natural daylight or switch on a room light."
        )
    if w < 400 or h < 400:
        issues.append(
            "Image resolution is too low. Upload at least 1080p."
        )

    return {
        "blur_score":  round(blur, 1),
        "mean_v":      round(mean_v, 1),
        "mean_s":      round(mean_s, 1),
        "resolution":  f"{w}x{h}",
        "acceptable":  len(issues) == 0,
    }, issues


# ══════════════════════════════════════════════════════════════════════
# SECTION 3 — PREPROCESSING
# ══════════════════════════════════════════════════════════════════════

def apply_clahe_lab(frame_rgb):
    """
    CLAHE in LAB colour space on the Lightness channel only.
    Works on all skin tones. Returns (enhanced_rgb, enhanced_gray 0-255).
    """
    lab   = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l_enh = cv2.createCLAHE(
        clipLimit=CFG["clahe_clip"],
        tileGridSize=CFG["clahe_tile"],
    ).apply(l)
    enh_rgb  = cv2.cvtColor(cv2.merge([l_enh, a, b]), cv2.COLOR_LAB2RGB)
    enh_gray = cv2.normalize(
        cv2.cvtColor(enh_rgb, cv2.COLOR_RGB2GRAY),
        None, 0, 255, cv2.NORM_MINMAX,
    )
    return enh_rgb, enh_gray


def enhance_crop_for_ai(crop_rgb):
    """Stronger CLAHE for crops sent to Gemini Vision."""
    if crop_rgb is None or (isinstance(crop_rgb, np.ndarray) and crop_rgb.size == 0):
        return crop_rgb
    lab   = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l_enh = cv2.createCLAHE(
        clipLimit=CFG["clahe_crop_clip"],
        tileGridSize=CFG["clahe_crop_tile"],
    ).apply(l)
    return cv2.cvtColor(cv2.merge([l_enh, a, b]), cv2.COLOR_LAB2RGB)


def get_skin_mask(frame_rgb):
    """
    HSV skin detection across all ethnicities.
    Returns a dilated binary mask — kills background noise in Frangi output.
    """
    hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)
    m1  = cv2.inRange(hsv, np.array([0,   15,  50], np.uint8),
                           np.array([25,  255, 255], np.uint8))
    m2  = cv2.inRange(hsv, np.array([160, 15,  50], np.uint8),
                           np.array([180, 255, 255], np.uint8))
    mask = cv2.bitwise_or(m1, m2)
    kn   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    return cv2.dilate(mask, kn, iterations=3)


# ══════════════════════════════════════════════════════════════════════
# SECTION 4 — ORIENTATION NORMALISATION
# ══════════════════════════════════════════════════════════════════════

def normalize_palm_orientation(frame_rgb, lm):
    """Rotate so middle-finger base (lm 9) points straight up from wrist (lm 0)."""
    w_pt  = np.array(lm[0], float)
    m_pt  = np.array(lm[9], float)
    d     = m_pt - w_pt
    angle = np.degrees(np.arctan2(d[0], -d[1]))
    h, w  = frame_rgb.shape[:2]
    M     = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(
        frame_rgb, M, (w, h),
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated, M


def rotate_landmarks(lm, M, iw, ih):
    out = {}
    for idx, (x, y) in lm.items():
        r = cv2.transform(np.array([[[float(x), float(y)]]], np.float32), M)
        out[idx] = (
            int(np.clip(r[0][0][0], 0, iw - 1)),
            int(np.clip(r[0][0][1], 0, ih - 1)),
        )
    return out


# ══════════════════════════════════════════════════════════════════════
# SECTION 5 — FRANGI + PERSISTENCE
# ══════════════════════════════════════════════════════════════════════

def run_dual_frangi(enhanced_gray):
    """
    Dual-direction Frangi: dark ridges (common) + bright ridges (overexposed).
    Mild Gaussian denoise first so sensor noise is not amplified.
    """
    blurred = cv2.GaussianBlur(enhanced_gray, (3, 3), 0)
    g       = blurred.astype(np.float64) / 255.0
    r_dark  = frangi(g, sigmas=CFG["frangi_sigmas"], black_ridges=True)
    r_brt   = frangi(g, sigmas=CFG["frangi_sigmas"], black_ridges=False)
    return cv2.normalize(
        np.maximum(r_dark, r_brt),
        None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U,
    )


def build_persistence_map_adaptive(frangi_norm):
    """
    8-threshold voting: each pixel scored 0-8.
    ADAPTIVE cutoff via Otsu on the non-zero persistence histogram.
    Replaces hardcoded >= 4 which failed on low-contrast images.
    """
    thresholds  = CFG["persist_thresholds"]
    persistence = np.zeros_like(frangi_norm, dtype=np.uint8)
    for t in thresholds:
        persistence += (frangi_norm > t).astype(np.uint8)

    # Adaptive Otsu cutoff on persistence distribution
    flat = persistence[persistence > 0].astype(np.uint8)
    if len(flat) > 50:
        from skimage.filters import threshold_otsu
        try:
            otsu_t = int(threshold_otsu(flat))
        except Exception:
            otsu_t = 4
    else:
        otsu_t = 4
    adaptive_t = max(CFG["persist_min_count"], otsu_t)

    total  = np.sum(persistence >= 1)
    strong = np.sum(persistence >= adaptive_t)
    return persistence, float(strong / max(total, 1)), adaptive_t


# Keep old name for any legacy calls
def build_persistence_map(frangi_norm):
    persistence, ratio, _ = build_persistence_map_adaptive(frangi_norm)
    return persistence, ratio


# ══════════════════════════════════════════════════════════════════════
# SECTION 6 — LINE ISOLATION & TOPOLOGY
# ══════════════════════════════════════════════════════════════════════

def isolate_lines_watershed(frangi_norm, persistence, skin_mask=None, adaptive_t=4):
    fn = (cv2.bitwise_and(frangi_norm, frangi_norm, mask=skin_mask)
          if skin_mask is not None else frangi_norm)
    ps = (cv2.bitwise_and(persistence, persistence, mask=skin_mask)
          if skin_mask is not None else persistence)

    seeds   = (ps >= adaptive_t).astype(np.uint8)
    terrain = (fn > CFG["watershed_terrain_t"]).astype(np.uint8)

    if seeds.sum() == 0:
        return (fn > 35).astype(np.uint8) * 255

    kn    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    grown = seeds.copy()
    for _ in range(CFG["watershed_dilate"]):
        grown = cv2.bitwise_and(cv2.dilate(grown, kn, iterations=1), terrain)

    min_area = max(200, int(frangi_norm.shape[0] * 0.05))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(grown)
    clean = np.zeros_like(grown, dtype=np.uint8)
    for lid in range(1, n):
        if stats[lid, cv2.CC_STAT_AREA] >= min_area:
            clean[labels == lid] = 255
    return clean


def extract_topology(clean_mask, img_h, img_w):
    binary = (clean_mask > 0).astype(np.uint8)
    kn     = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN,  kn)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kn)

    skel = skeletonize(binary.astype(bool))
    skel = remove_small_objects(skel, min_size=CFG["skel_min_size"])
    skel = skel.astype(np.uint8)

    k3   = np.ones((3, 3), dtype=int)
    nbrs = convolve(skel.astype(int), k3) - skel.astype(int)

    endpoints    = int(np.sum((skel == 1) & (nbrs == 1)))
    branchpoints = int(np.sum((skel == 1) & (nbrs >= 3)))

    # Two-zone Simian validation: must span heart AND head zone
    heart_y1 = int(img_h * 0.20)
    heart_y2 = int(img_h * 0.38)
    head_y2  = int(img_h * 0.55)
    simian   = False
    zone_sk  = skel[heart_y1:head_y2, :]
    if zone_sk.sum() > 0:
        labeled = sk_label(zone_sk)
        for region in regionprops(labeled):
            bbox  = region.bbox
            b_w   = bbox[3] - bbox[1]
            b_top = bbox[0] + heart_y1
            b_bot = bbox[2] + heart_y1
            if b_w > img_w * 0.50 and b_top < heart_y2 and b_bot > heart_y2:
                simian = True
                break

    return {
        "line_endpoints":  endpoints,
        "line_forks":      branchpoints,
        "simian_line":     simian,
        "line_complexity": int(branchpoints / max(endpoints, 1) * 100),
    }


# ══════════════════════════════════════════════════════════════════════
# SECTION 7 — PER-LINE TRACING (core accuracy upgrade)
# ══════════════════════════════════════════════════════════════════════

def _zone_mask(shape, y1, y2, x1, x2):
    """Create a rectangular binary zone mask."""
    mask = np.zeros(shape[:2], dtype=np.uint8)
    mask[max(0, y1):min(shape[0], y2),
         max(0, x1):min(shape[1], x2)] = 255
    return mask


def _position_label(px, py, lm, ih, iw):
    """Describe a pixel position in palm anatomy terms."""
    wy  = lm[0][1]; my = lm[5][1]
    ph  = max(wy - my, 1)
    lx  = min(lm[17][0], lm[5][0])
    rx  = max(lm[17][0], lm[5][0])
    pw  = max(rx - lx, 1)
    rel_y = (py - my) / ph
    rel_x = (px - lx) / pw

    if rel_y < 0.08:   y_lab = "near finger bases"
    elif rel_y < 0.40: y_lab = "upper palm"
    elif rel_y < 0.70: y_lab = "mid palm"
    else:              y_lab = "lower palm / wrist"

    if rel_x < 0.05:   x_lab = "radial (thumb) edge"
    elif rel_x < 0.30: x_lab = "under Jupiter"
    elif rel_x < 0.55: x_lab = "under Saturn"
    elif rel_x < 0.78: x_lab = "under Apollo"
    else:              x_lab = "ulnar (pinky) edge"

    return f"{y_lab}, {x_lab}"


def _extract_component_features(coords, frangi_norm, lm, ih, iw, pw, ph, line_type):
    """
    Compute rich palmistry features for a single traced line component.
    coords: Nx2 array of (row, col) skeleton pixels in image space.
    """
    rows, cols = coords[:, 0], coords[:, 1]
    length_px  = len(coords)

    # Depth proxy: mean Frangi response along the traced skeleton
    intensities = frangi_norm[
        np.clip(rows, 0, frangi_norm.shape[0]-1),
        np.clip(cols, 0, frangi_norm.shape[1]-1),
    ].astype(float)
    mean_depth  = float(intensities.mean())

    # Length as % of reference dimension
    ref_dim    = pw if line_type == "horizontal" else ph
    length_pct = min(100, int(length_px / max(ref_dim, 1) * 100))

    # Orientation via PCA on component coordinates
    centered = coords.astype(float) - coords.mean(axis=0)
    try:
        if len(centered) >= 3:
            _, _, vt = np.linalg.svd(centered, full_matrices=False)
            pa  = vt[0]
            angle_from_horiz = float(np.degrees(np.arctan2(abs(pa[0]), abs(pa[1]))))
        else:
            angle_from_horiz = 45.0
    except Exception:
        angle_from_horiz = 45.0

    # Curvature: measure directional change across thirds of the component
    curvature = "straight"
    curve_direction = "level"
    if length_px >= 12:
        try:
            third = length_px // 3
            s1 = coords[:third].mean(axis=0).astype(float)
            s2 = coords[third:2*third].mean(axis=0).astype(float)
            s3 = coords[2*third:].mean(axis=0).astype(float)
            v1 = s2 - s1
            v2 = s3 - s2
            cross = float(v1[0]*v2[1] - v1[1]*v2[0])
            dot   = float(np.dot(v1, v2))
            curl  = np.arctan2(abs(cross), max(abs(dot), 1e-6))

            if curl < 0.22:    curvature = "straight"
            elif curl < 0.52:  curvature = "gentle curve"
            else:              curvature = "pronounced curve"

            if   cross < -0.8:  curve_direction = "upward (toward fingers)"
            elif cross >  0.8:  curve_direction = "downward (toward wrist)"
            else:               curve_direction = "level"
        except Exception:
            pass

    # Build sparse component mask in image space for topology
    comp_mask = np.zeros((ih, iw), dtype=np.uint8)
    r_clip = np.clip(rows, 0, ih-1)
    c_clip = np.clip(cols, 0, iw-1)
    comp_mask[r_clip, c_clip] = 1

    k3   = np.ones((3, 3), dtype=int)
    nbrs = convolve(comp_mask.astype(int), k3) - comp_mask.astype(int)

    branch_pts = int(np.sum((comp_mask == 1) & (nbrs >= 3)))
    end_pts    = int(np.sum((comp_mask == 1) & (nbrs == 1)))

    # Branch directions: compare branch point row to component centroid row
    centroid_r = rows.mean()
    bp_rows    = np.argwhere((comp_mask == 1) & (nbrs >= 3))[:, 0]
    branches_up   = int((bp_rows < centroid_r).sum())  # toward fingers (smaller row)
    branches_down = int((bp_rows >= centroid_r).sum()) # toward wrist

    # Start and end zones from endpoints
    ep_locs = np.argwhere((comp_mask == 1) & (nbrs == 1))  # (row, col) pairs
    start_zone = end_zone = "not detected"
    if len(ep_locs) >= 2:
        if line_type == "horizontal":
            ep_sorted = ep_locs[ep_locs[:, 1].argsort()]  # sort by col
        else:
            ep_sorted = ep_locs[ep_locs[:, 0].argsort()]  # sort by row
        r0, c0 = ep_sorted[0]
        r1, c1 = ep_sorted[-1]
        start_zone = _position_label(int(c0), int(r0), lm, ih, iw)
        end_zone   = _position_label(int(c1), int(r1), lm, ih, iw)
    elif len(ep_locs) == 1:
        r0, c0 = ep_locs[0]
        start_zone = _position_label(int(c0), int(r0), lm, ih, iw)

    score = min(100, int(mean_depth / 255 * 100))

    return {
        "present":          True,
        "score":            score,
        "depth_label":      score_to_label(score),
        "mean_depth":       round(mean_depth),
        "length_pct":       length_pct,
        "length_px":        length_px,
        "curvature":        curvature,
        "curve_direction":  curve_direction,
        "angle_from_horiz": round(angle_from_horiz, 1),
        "branches_up":      branches_up,
        "branches_down":    branches_down,
        "branch_total":     branch_pts,
        "endpoints":        end_pts,
        "start_zone":       start_zone,
        "end_zone":         end_zone,
    }


def _absent_line():
    return {
        "present":          False,
        "score":            0,
        "depth_label":      "Absent / Not Detected",
        "mean_depth":       0,
        "length_pct":       0,
        "curvature":        "n/a",
        "curve_direction":  "n/a",
        "branches_up":      0,
        "branches_down":    0,
        "branch_total":     0,
        "start_zone":       "n/a",
        "end_zone":         "n/a",
    }


def trace_major_lines(clean_mask, frangi_norm, lm, ih, iw):
    """
    Trace the 5 major palm lines as skeleton components.
    Returns:
        traced       : dict of {line_name: feature_dict}
        palm_skel    : full skeletonized binary image (uint8)
        line_masks   : dict of {line_name: binary mask | None}
    """
    if not lm:
        return _fallback_traced_lines(frangi_norm, ih, iw)

    wy  = lm[0][1];  my  = lm[5][1]
    ph  = max(wy - my, 1)
    lx  = min(lm[17][0], lm[5][0])
    rx  = max(lm[17][0], lm[5][0])
    pw  = max(rx - lx, 1)
    tx  = lm[2][0]    # thumb base x
    fx  = lm[9][0]    # middle finger base x
    sx  = lm[13][0]   # ring finger base x

    # Skeletonize
    binary = remove_small_objects(
        (clean_mask > 0), min_size=CFG["skel_min_size"]
    )
    skel = skeletonize(binary).astype(np.uint8)

    min_horiz_px = int(pw * CFG["line_min_horiz_frac"])
    min_vert_px  = int(ph * CFG["line_min_vert_frac"])
    min_life_px  = int(ph * CFG["line_min_life_frac"])

    traced     = {}
    line_masks = {}
    claimed    = np.zeros((ih, iw), dtype=np.uint8)   # tracks "owned" skel pixels

    # ── HEART & HEAD LINES ────────────────────────────────────────────
    # Search full-width upper palm; pick top-2 horizontal components
    hh_zone = _zone_mask(
        skel.shape,
        my, my + int(ph * 0.58),
        max(0, lx - int(pw * 0.10)), min(iw, rx + int(pw * 0.10)),
    )
    hh_skel = skel * (hh_zone > 0).astype(np.uint8)

    labeled  = sk_label(hh_skel)
    regions  = regionprops(labeled)

    horizontal_cands = []
    for r in regions:
        bbox   = r.bbox
        w_span = bbox[3] - bbox[1]
        h_span = max(bbox[2] - bbox[0], 1)
        if r.area >= min_horiz_px and (w_span / h_span) >= 1.6:
            horizontal_cands.append(r)

    # Sort by centroid row (ascending = highest in image = heart line first)
    horizontal_cands.sort(key=lambda r: r.centroid[0])

    for line_name, reg in zip(["heart_line", "head_line"], horizontal_cands[:2]):
        coords = reg.coords  # (row, col)
        feats  = _extract_component_features(
            coords, frangi_norm, lm, ih, iw, pw, ph, "horizontal"
        )
        lmask = (labeled == reg.label).astype(np.uint8)
        traced[line_name]     = feats
        line_masks[line_name] = lmask
        claimed = cv2.bitwise_or(claimed, lmask)

    for name in ["heart_line", "head_line"]:
        if name not in traced:
            traced[name]     = _absent_line()
            line_masks[name] = None

    # ── LIFE LINE ─────────────────────────────────────────────────────
    ll_x1 = max(0,  tx - int(iw * 0.24))
    ll_x2 = min(iw, tx + int(iw * 0.12))
    ll_y1 = max(0,  my + int(ph * 0.05))
    ll_y2 = wy

    ll_zone = _zone_mask(skel.shape, ll_y1, ll_y2, ll_x1, ll_x2)
    ll_skel = skel * (ll_zone > 0).astype(np.uint8)
    ll_skel[claimed > 0] = 0

    ll_labeled = sk_label(ll_skel)
    ll_regs    = sorted(
        [r for r in regionprops(ll_labeled) if r.area >= min_life_px],
        key=lambda r: -r.area,
    )
    if ll_regs:
        reg   = ll_regs[0]
        feats = _extract_component_features(
            reg.coords, frangi_norm, lm, ih, iw, pw, ph, "curved"
        )
        lmask = (ll_labeled == reg.label).astype(np.uint8)
        traced["life_line"]     = feats
        line_masks["life_line"] = lmask
        claimed = cv2.bitwise_or(claimed, lmask)
    else:
        traced["life_line"]     = _absent_line()
        line_masks["life_line"] = None

    # ── FATE LINE ─────────────────────────────────────────────────────
    fa_x1 = max(0,  fx - int(iw * 0.13))
    fa_x2 = min(iw, fx + int(iw * 0.13))
    fa_y1 = max(0,  my + int(ph * 0.18))
    fa_y2 = wy

    fa_zone = _zone_mask(skel.shape, fa_y1, fa_y2, fa_x1, fa_x2)
    fa_skel = skel * (fa_zone > 0).astype(np.uint8)
    fa_skel[claimed > 0] = 0

    fa_labeled = sk_label(fa_skel)
    fa_regs    = sorted(
        [r for r in regionprops(fa_labeled) if r.area >= min_vert_px],
        key=lambda r: -r.area,
    )
    fate_feat = fate_mask = None
    for r in fa_regs:
        bbox   = r.bbox
        h_span = bbox[2] - bbox[0]
        w_span = max(bbox[3] - bbox[1], 1)
        if h_span / w_span >= 0.9:   # reasonably vertical
            fate_feat = _extract_component_features(
                r.coords, frangi_norm, lm, ih, iw, pw, ph, "vertical"
            )
            fate_mask = (fa_labeled == r.label).astype(np.uint8)
            break

    traced["fate_line"]     = fate_feat if fate_feat else _absent_line()
    line_masks["fate_line"] = fate_mask
    if fate_mask is not None:
        claimed = cv2.bitwise_or(claimed, fate_mask)

    # ── SUN LINE ──────────────────────────────────────────────────────
    su_x1 = max(0,  sx - int(iw * 0.12))
    su_x2 = min(iw, sx + int(iw * 0.12))
    su_y1 = max(0,  my + int(ph * 0.25))
    su_y2 = max(0,  wy - int(ph * 0.06))

    su_zone = _zone_mask(skel.shape, su_y1, su_y2, su_x1, su_x2)
    su_skel = skel * (su_zone > 0).astype(np.uint8)
    su_skel[claimed > 0] = 0

    su_labeled = sk_label(su_skel)
    su_regs    = sorted(
        [r for r in regionprops(su_labeled) if r.area >= int(min_vert_px * 0.55)],
        key=lambda r: -r.area,
    )
    sun_feat = sun_mask = None
    if su_regs:
        r        = su_regs[0]
        sun_feat = _extract_component_features(
            r.coords, frangi_norm, lm, ih, iw, pw, ph, "vertical"
        )
        sun_mask = (su_labeled == r.label).astype(np.uint8)

    traced["sun_line"]     = sun_feat if sun_feat else _absent_line()
    line_masks["sun_line"] = sun_mask

    return traced, skel, line_masks


def _fallback_traced_lines(frangi_norm, ih, iw):
    """Zone-density fallback when no landmarks detected."""
    zone_scores = _fallback_zone_scores(frangi_norm, ih, iw)
    traced, masks = {}, {}
    for name, score in zone_scores.items():
        if score > 8:
            traced[name] = {
                "present": True, "score": score,
                "depth_label": score_to_label(score),
                "mean_depth": int(score * 2.55),
                "length_pct": score, "length_px": 0,
                "curvature": "unknown (no landmarks)",
                "curve_direction": "unknown",
                "branches_up": 0, "branches_down": 0, "branch_total": 0,
                "endpoints": 0,
                "start_zone": "unknown", "end_zone": "unknown",
            }
        else:
            traced[name] = _absent_line()
        masks[name] = None
    return traced, np.zeros((ih, iw), dtype=np.uint8), masks


def extract_zone_scores(frangi_norm, lm, img_h, img_w):
    """Legacy wrapper — returns simple {line: score} dict from zone density."""
    def sc(zone):
        if zone.size == 0: return 0
        thr = max(12, int(np.percentile(zone, 40)))
        px  = zone[zone > thr]
        if len(px) == 0: return 0
        return min(100, int((len(px) / zone.size * 0.6
                             + float(np.mean(px)) / 255 * 0.4) * 100))
    if not lm:
        return _fallback_zone_scores(frangi_norm, img_h, img_w)
    wy  = lm[0][1]; my = lm[5][1]
    ph  = max(wy - my, 1)
    lx  = min(lm[17][0], lm[5][0]); rx = max(lm[17][0], lm[5][0])
    tx  = lm[2][0]; fx = lm[9][0];  sx = lm[13][0]
    hy2 = my + int(ph * 0.22); hd2 = hy2 + int(ph * 0.22)
    lx1 = max(0, tx - int(img_w*0.13)); lx2 = min(img_w, tx + int(img_w*0.10))
    fx1 = max(0, fx - int(img_w*0.07)); fx2 = min(img_w, fx + int(img_w*0.07))
    sx1 = max(0, sx - int(img_w*0.06)); sx2 = min(img_w, sx + int(img_w*0.06))
    return {
        "heart_line": sc(frangi_norm[my:hy2, lx:rx]),
        "head_line":  sc(frangi_norm[hy2:hd2, lx:rx]),
        "life_line":  sc(frangi_norm[hd2:wy,  lx1:lx2]),
        "fate_line":  sc(frangi_norm[hd2:wy,  fx1:fx2]),
        "sun_line":   sc(frangi_norm[hd2:wy,  sx1:sx2]),
    }


def _fallback_zone_scores(frangi_norm, img_h, img_w):
    def sc(zone):
        if zone.size == 0: return 0
        thr = max(12, int(np.percentile(zone, 40)))
        px  = zone[zone > thr]
        if len(px) == 0: return 0
        return min(100, int((len(px) / zone.size * 0.6
                             + float(np.mean(px)) / 255 * 0.4) * 100))
    t = img_h // 3
    return {
        "heart_line": sc(frangi_norm[0:int(t*.7), img_w//4:img_w*3//4]),
        "head_line":  sc(frangi_norm[int(t*.7):t,  img_w//4:img_w*3//4]),
        "life_line":  sc(frangi_norm[t:t*2,         0:img_w//3]),
        "fate_line":  sc(frangi_norm[t:t*2, img_w//3:img_w*2//3]),
        "sun_line":   sc(frangi_norm[t:t*2, img_w*2//3:img_w]),
    }


def score_to_label(s):
    if s >= 65: return "Deep & Prominent"
    if s >= 45: return "Clear & Defined"
    if s >= 25: return "Moderate"
    if s >= 10: return "Faint"
    return "Absent / Not Detected"


# ══════════════════════════════════════════════════════════════════════
# SECTION 8 — MARK & MINOR LINE DETECTION
# ══════════════════════════════════════════════════════════════════════

def detect_marks_classical(palm_skel, line_masks, lm, ih, iw):
    """
    Detect classical marks in the residual skeleton after removing major lines.
    Looks for: cross, star, triangle, square, island (closed loop on a line).
    Returns list of dicts: [{type, position, x, y}]
    """
    if palm_skel is None or palm_skel.sum() == 0:
        return []

    residual = palm_skel.copy().astype(np.uint8)
    kn7 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    for lmask in line_masks.values():
        if lmask is not None and lmask.shape == residual.shape:
            residual[cv2.dilate(lmask, kn7) > 0] = 0

    n, labels, stats, centroids = cv2.connectedComponentsWithStats(residual)
    k3   = np.ones((3, 3), dtype=int)
    marks = []

    for lid in range(1, n):
        area = stats[lid, cv2.CC_STAT_AREA]
        if area < CFG["mark_min_area"] or area > CFG["mark_max_area"]:
            continue

        cx_m, cy_m = int(centroids[lid][0]), int(centroids[lid][1])
        comp = (labels == lid).astype(np.uint8)

        nbrs       = convolve(comp.astype(int), k3) - comp.astype(int)
        branch_pts = int(np.sum((comp == 1) & (nbrs >= 3)))
        end_pts    = int(np.sum((comp == 1) & (nbrs == 1)))

        contours, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        mark_type = None

        # Closed / near-closed loops
        if end_pts <= 2 and area >= 14 and contours:
            hull_a = cv2.contourArea(cv2.convexHull(contours[0]))
            if hull_a > 0 and (area / hull_a) > 0.45:
                eps   = max(1.5, 0.04 * cv2.arcLength(contours[0], True))
                approx = cv2.approxPolyDP(contours[0], eps, True)
                nv     = len(approx)
                if nv == 3:
                    mark_type = "triangle"
                elif nv == 4:
                    mark_type = "square"
                else:
                    mark_type = "island"
        elif branch_pts >= 4:
            mark_type = "star"
        elif branch_pts == 2 and end_pts >= 3:
            mark_type = "cross"

        if mark_type and lm:
            marks.append({
                "type":     mark_type,
                "position": _position_label(cx_m, cy_m, lm, ih, iw),
                "x": cx_m, "y": cy_m,
            })

    return marks


def detect_minor_lines(palm_skel, line_masks, lm, ih, iw):
    """
    Detect classical minor lines from skeleton residual.
    Returns dict of {minor_line_name: True | count}.
    False positives are possible at ~15-20%; treat as indicative.
    """
    if palm_skel is None or not lm:
        return {}

    residual = palm_skel.copy().astype(np.uint8)
    kn5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    for lmask in line_masks.values():
        if lmask is not None and lmask.shape == residual.shape:
            residual[cv2.dilate(lmask, kn5) > 0] = 0

    wy  = lm[0][1]; my = lm[5][1]
    ph  = max(wy - my, 1)
    lx  = min(lm[17][0], lm[5][0]); rx = max(lm[17][0], lm[5][0])
    tx  = lm[2][0]
    jx, jy   = lm[5]    # Jupiter finger base
    sx9, sy9 = lm[9]    # Saturn finger base
    mx17_x, mx17_y = lm[17]   # Mercury finger base

    found = {}

    def _zone_count(y1, y2, x1, x2, min_pixels=15):
        z = _zone_mask(residual.shape, y1, y2, x1, x2)
        return int(residual[z > 0].sum())

    # Girdle of Venus: arc between heart line and finger bases, central palm
    if _zone_count(my, my + int(ph*0.18), lm[5][0], lm[17][0]) > 20:
        found["girdle_of_venus"] = True

    # Ring of Solomon: arc/ring below Jupiter finger
    if _zone_count(jy - int(ph*0.07), jy + int(ph*0.04), jx-45, jx+45) > 10:
        found["ring_of_solomon"] = True

    # Ring of Saturn: arc below middle finger
    if _zone_count(sy9 - int(ph*0.07), sy9 + int(ph*0.04), sx9-45, sx9+45) > 10:
        found["ring_of_saturn"] = True

    # Marriage lines: short horizontal segments on Mercury mount
    heart_y_approx = my + int(ph * 0.10)
    mar_zone = _zone_mask(
        residual.shape,
        heart_y_approx, my + int(ph*0.08),
        mx17_x, min(iw, mx17_x + 85),
    )
    mar_skel = residual * (mar_zone > 0).astype(np.uint8)
    n_m, _, ms, _ = cv2.connectedComponentsWithStats(mar_skel)
    mar_count = sum(
        1 for lid in range(1, n_m)
        if ms[lid, cv2.CC_STAT_AREA] > 8
        and ms[lid, cv2.CC_STAT_WIDTH] > ms[lid, cv2.CC_STAT_HEIGHT]
    )
    if mar_count > 0:
        found["marriage_lines"] = mar_count

    # Bracelets (rascettes): horizontal lines at wrist
    brac_zone = _zone_mask(
        residual.shape,
        wy - int(ph*0.09), wy + int(ph*0.04),
        lx, rx,
    )
    brac_skel = residual * (brac_zone > 0).astype(np.uint8)
    n_b, _, bs, _ = cv2.connectedComponentsWithStats(brac_skel)
    brac_count = sum(1 for lid in range(1, n_b) if bs[lid, cv2.CC_STAT_AREA] > 15)
    if brac_count > 0:
        found["bracelets"] = brac_count

    # Intuition crescent: curved line on ulnar side, mid-to-lower palm
    if _zone_count(
        my + int(ph*0.35), wy - int(ph*0.10),
        mx17_x - 25, min(iw, mx17_x + 65)
    ) > 25:
        found["intuition_crescent"] = True

    # Mystic cross: cross shape between head and heart lines, central palm
    cx_zone_y1 = my + int(ph * 0.22)
    cx_zone_y2 = my + int(ph * 0.52)
    cx_center   = (lx + rx) // 2
    mys_zone    = _zone_mask(
        residual.shape, cx_zone_y1, cx_zone_y2,
        cx_center - 55, cx_center + 55,
    )
    mys_skel = residual * (mys_zone > 0).astype(np.uint8)
    k3_m     = np.ones((3,3), dtype=int)
    mys_nbrs = convolve(mys_skel.astype(int), k3_m) - mys_skel.astype(int)
    if (int(np.sum((mys_skel == 1) & (mys_nbrs >= 3))) >= 1
            and mys_skel.sum() > 8):
        found["mystic_cross"] = True

    return found


# ══════════════════════════════════════════════════════════════════════
# SECTION 9 — FINGERPRINT PATTERN DETECTION
# ══════════════════════════════════════════════════════════════════════

def detect_fingerprint_patterns(frame_rgb, lm_dict):
    """
    Classify each fingertip as arch / loop / whorl using gradient orientation field.
    Uses the double-angle method (skin-tone invariant, no intensity thresholds).

    Vedic mapping:
      arch   = stable, practical, earth nature (Dhanusha)
      loop   = adaptable, balanced (most common, ~65% of population)
      whorl  = intense, unique, leadership (Chakra / Chandra marking)
    """
    TIPS  = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}
    BASES = {"thumb": 3, "index": 7, "middle": 11, "ring":  15, "pinky": 19}

    if not lm_dict:
        return {}

    results = {}
    ih, iw  = frame_rgb.shape[:2]
    gray    = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)

    for fname, tip_idx in TIPS.items():
        if tip_idx not in lm_dict:
            results[fname] = "unknown"
            continue

        tx, ty  = lm_dict[tip_idx]
        bx, by  = lm_dict.get(BASES.get(fname, tip_idx), (tx, ty + 20))
        seg_len = max(22, int(np.sqrt((tx-bx)**2 + (ty-by)**2) * 0.75))

        x1 = max(0,  tx - seg_len // 2)
        x2 = min(iw, tx + seg_len // 2)
        y1 = max(0,  ty - seg_len)
        y2 = min(ih, ty + seg_len // 2)

        crop = gray[y1:y2, x1:x2]
        if crop.size < 100:
            results[fname] = "unknown"
            continue

        crop = cv2.resize(crop, (64, 64))

        # Gradient computation
        gx = cv2.Sobel(crop.astype(np.float32), cv2.CV_32F, 1, 0, ksize=5)
        gy = cv2.Sobel(crop.astype(np.float32), cv2.CV_32F, 0, 1, ksize=5)

        # Double-angle trick eliminates 0 vs 180 degree ambiguity
        gx2 = gx**2 - gy**2
        gxy = 2.0 * gx * gy

        # Block-wise orientation (8x8 blocks → 8x8 grid)
        block = 8
        n_b   = 64 // block
        orients = []
        for i in range(n_b):
            for j in range(n_b):
                bx_ = gx2[i*block:(i+1)*block, j*block:(j+1)*block]
                by_ = gxy[i*block:(i+1)*block, j*block:(j+1)*block]
                o   = 0.5 * np.arctan2(float(by_.sum()), float(bx_.sum()))
                orients.append(o)

        orients    = np.array(orients)
        orient_std = float(np.std(orients))

        # Spatial gradient of orientation (curl proxy)
        og   = orients.reshape(n_b, n_b)
        curl = float(
            np.abs(np.diff(og, axis=0)).mean() +
            np.abs(np.diff(og, axis=1)).mean()
        )

        if orient_std < 0.35:
            pat = "arch"
        elif curl > 0.72:
            pat = "whorl"
        else:
            pat = "loop"

        results[fname] = pat

    return results


# ══════════════════════════════════════════════════════════════════════
# SECTION 10 — GEOMETRY & VITALITY
# ══════════════════════════════════════════════════════════════════════

def compute_finger_ratios(lm):
    def fl(t, p):
        return float(np.linalg.norm(np.array(lm[t]) - np.array(lm[p])))

    il   = fl(8,  5)
    rl   = fl(16, 13)
    ml   = fl(12, 9)
    pl   = fl(20, 17)
    r244 = il / max(rl, 1)
    pw   = abs(lm[17][0] - lm[5][0])
    ph   = fl(9, 0)
    pr   = float(pw / max(ph, 1))
    fr   = float(ml / max(ph, 1))

    shape  = "square" if pr >= 0.85 else "oblong"
    length = "short"  if fr < 0.75  else "long"
    western, vedic = HAND_TYPES.get(
        f"{shape}_{length}",
        ("Mixed Hand", "Mishra Hasta — Complex, adaptable nature"),
    )

    if r244 < 0.95:
        rr = "Longer ring finger — strong Mars/Sun energy, assertive leadership drive"
    elif r244 > 1.05:
        rr = "Longer index finger — strong Jupiter energy, ambition, desire for authority"
    else:
        rr = "Balanced index-ring ratio — harmonised masculine/feminine energies"

    ratios = {"Index": il, "Ring": rl, "Middle": ml, "Pinky": pl}
    dom    = max(ratios, key=ratios.get)

    return {
        "ratio_2d4d":      round(r244, 3),
        "ratio_reading":   rr,
        "hand_type":       western,
        "hand_type_vedic": vedic,
        "dominant_finger": dom,
        "palm_ratio":      round(pr, 3),
    }


def get_vitality_relative(frame_rgb, lm, iw, ih):
    """
    Relative Venus mount HSV vs whole-palm mean.
    Skin-tone invariant: a dark-skinned healthy person no longer reads as 'Cool Vata'.
    Returns (detailed_label, short_ui_label).
    """
    vx, vy = lm[2]
    box    = max(40, int(iw * 0.07))
    venus_crop = frame_rgb[
        max(0, vy):min(ih, vy + box * 2),
        max(0, vx - box):min(iw, vx + box),
    ]
    # Whole palm region (roughly)
    lx  = min(lm[17][0], lm[5][0]); rx = max(lm[17][0], lm[5][0])
    wy  = lm[0][1]; my = lm[5][1]
    palm_crop = frame_rgb[
        max(0, my):min(ih, wy),
        max(0, lx):min(iw, rx),
    ]

    if venus_crop.size == 0 or palm_crop.size == 0:
        return "Balanced Kapha (Steady vitality)", "Balanced & Steady Energy"

    def _mean_s_v(crop):
        hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
        return float(cv2.mean(hsv)[1]), float(cv2.mean(hsv)[2])

    v_s, v_v = _mean_s_v(venus_crop)
    p_s, p_v = _mean_s_v(palm_crop)
    ds = v_s - p_s   # positive = Venus more saturated than rest of palm
    dv = v_v - p_v   # positive = Venus brighter

    if ds > 12 or (ds > 5 and dv > 10):
        return (
            "Active Pitta (High vitality — elevated Venus mount warmth)",
            "Warm, Passionate & High Energy",
        )
    if ds < -8 or v_s < 20:
        return (
            "Cool Vata (Variable vitality — lower Venus energy)",
            "Cool, Sensitive & Variable Energy",
        )
    return "Balanced Kapha (Steady vitality)", "Balanced & Steady Energy"


# Keep old name for backward compat
def get_vitality_hsv(frame_rgb, lm, iw, ih):
    return get_vitality_relative(frame_rgb, lm, iw, ih)


# ══════════════════════════════════════════════════════════════════════
# SECTION 11 — MOUNT ELEVATION
# ══════════════════════════════════════════════════════════════════════

def _normalize_elevations(raw):
    if not raw:
        return {}
    mn, mx = min(raw.values()), max(raw.values())
    sp     = max(mx - mn, 1e-6)
    out    = {}
    for m, s in raw.items():
        r  = int((s - mn) / sp * 100)
        lb = ("Highly Developed"     if r >= 70 else
              "Moderately Developed" if r >= 45 else
              "Slightly Developed"   if r >= 25 else
              "Flat / Underdeveloped")
        out[m] = {"elevation": lb, "score": r}
    return out


def estimate_mount_elevations_relative(orig_crops_raw):
    """Brightness + sharpness heuristic with relative normalization."""
    raw = {}
    for m, c in orig_crops_raw.items():
        if c is None or c.size == 0:
            continue
        hsv        = cv2.cvtColor(c, cv2.COLOR_RGB2HSV)
        v          = float(cv2.mean(hsv)[2])
        gray       = cv2.cvtColor(c, cv2.COLOR_RGB2GRAY)
        lap        = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = min(100, v / 2.55)
        sharpness  = min(100, float(np.log1p(lap)) * 12)
        raw[m]     = brightness * 0.5 + sharpness * 0.5
    return _normalize_elevations(raw)


def get_mount_elevations_depth(frame_rgb, lm):
    if not USE_DEPTH_MODEL or not lm:
        return None
    estimator = _load_depth_model()
    if not estimator:
        return None
    try:
        dep    = np.array(
            estimator(PIL.Image.fromarray(frame_rgb))["depth"], np.float32
        )
        mn, mx = dep.min(), dep.max()
        if mx - mn < 1e-6:
            return None
        dep    = (dep - mn) / (mx - mn) * 100
        ih, iw = frame_rgb.shape[:2]
        box    = int(np.sqrt(
            (lm[5][0]-lm[9][0])**2 + (lm[5][1]-lm[9][1])**2
        )) * 2
        anchors = {
            "Jupiter":    lm[5],
            "Saturn":     lm[9],
            "Sun":        lm[13],
            "Mercury":    lm[17],
            "Venus":      lm[2],
            "Mars_Upper": (lm[17][0], int((lm[17][1] + lm[0][1]) / 2)),
            "Luna":       (lm[17][0], int(lm[17][1]*.4 + lm[0][1]*.6)),
        }
        raw = {}
        for m, (ax, ay) in anchors.items():
            bs = int(box * 1.4) if m in ("Venus", "Mars_Upper", "Luna") else box
            r  = dep[max(0, ay-bs//2):min(ih, ay+bs//2),
                     max(0, ax-bs//2):min(iw, ax+bs//2)]
            if r.size > 0:
                raw[m] = float(np.mean(r))
        return _normalize_elevations(raw)
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# SECTION 12 — ANNOTATION & CONSISTENCY
# ══════════════════════════════════════════════════════════════════════

def annotate_xray_with_labels(xray_bgr, traced_lines, lm):
    """
    Draw traced line labels on the diagnostic xray with coloured outlines.
    Helps both human inspection and provides context to Gemini if stitched.
    """
    if not lm:
        return xray_bgr

    out = xray_bgr.copy()
    wy  = lm[0][1]; my = lm[5][1]
    ph  = max(wy - my, 1)
    lx  = min(lm[17][0], lm[5][0]); rx = max(lm[17][0], lm[5][0])
    cx  = (lx + rx) // 2
    tx  = lm[2][0]; fx = lm[9][0]; sx = lm[13][0]

    COLORS = {
        "heart_line": (80,  120, 255),
        "head_line":  (120, 220, 255),
        "life_line":  (80,  255, 140),
        "fate_line":  (50,  220, 255),
        "sun_line":   (50,  165, 255),
    }

    # Approximate label positions (shifted left so text fits)
    POSITIONS = {
        "heart_line": (lx + 4,  my + int(ph * 0.10)),
        "head_line":  (lx + 4,  my + int(ph * 0.36)),
        "life_line":  (max(4, tx - 75), my + int(ph * 0.52)),
        "fate_line":  (max(4, fx - 35), my + int(ph * 0.62)),
        "sun_line":   (max(4, sx - 25), my + int(ph * 0.67)),
    }

    for line_name, feat in (traced_lines or {}).items():
        if feat is None or not feat.get("present"):
            continue
        label = LINE_LABELS.get(line_name, line_name).split("/")[0].strip()
        score = feat.get("score", 0)
        text  = f"{label} ({score})"
        color = COLORS.get(line_name, (200, 200, 200))
        px, py = POSITIONS.get(line_name, (cx, my + int(ph*0.5)))
        px = max(4, min(out.shape[1] - 110, px))
        py = max(14, min(out.shape[0] - 4,  py))
        cv2.putText(out, text, (px, py), cv2.FONT_HERSHEY_SIMPLEX,
                    0.40, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(out, text, (px, py), cv2.FONT_HERSHEY_SIMPLEX,
                    0.40, color,    1, cv2.LINE_AA)

    return out


def pre_llm_consistency_check(palm_data):
    """
    Catch obvious math contradictions before they reach the LLM.
    Returns list of warning strings (empty = all good).
    """
    warnings = []
    topo    = palm_data.get("topology", {})
    traced  = palm_data.get("traced_lines", {})
    zone    = palm_data.get("zone_scores", {})
    pr      = palm_data.get("persistence_ratio", 0)

    # Simian paradox: simian AND both heart/head present is contradictory
    if topo.get("simian_line"):
        heart = (traced.get("heart_line") or {}).get("present", False)
        head  = (traced.get("head_line")  or {}).get("present", False)
        if heart and head:
            hl = (traced.get("heart_line") or {}).get("length_pct", 0)
            hdl = (traced.get("head_line") or {}).get("length_pct", 0)
            if hl > 40 and hdl > 40:
                warnings.append(
                    "Simian flag + both full heart/head lines detected. "
                    "Likely a strong head line crossing — treat simian with lower confidence."
                )

    # All lines absent but palm has content
    all_absent = all(
        not (traced.get(k) or {}).get("present", False)
        for k in ["heart_line", "head_line", "life_line"]
    )
    if all_absent and pr > 0.20:
        warnings.append(
            "Major lines undetected but palm has ridge content (persistence "
            f"{int(pr*100)}%). Try a clearer photo with better lighting."
        )

    # Very high fork count is usually noise
    forks = topo.get("line_forks", 0)
    if forks > 80:
        warnings.append(
            f"High fork count ({forks}) may include skin texture noise. "
            "Branch interpretations should be moderated."
        )

    return warnings


# ══════════════════════════════════════════════════════════════════════
# SECTION 13 — MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════

def analyze_palm_hybrid(image_bytes):
    """
    Master pipeline. Returns:
      palm_data       — full feature dict
      diagnostic_xray — BGR numpy array (heatmap for UI)
      best_frame      — RGB numpy array (original enhanced frame)
      lm_dict         — landmark pixel coords dict or None
    """
    img        = PIL.Image.open(io.BytesIO(image_bytes)).convert("RGB")
    raw_frame  = enhance_and_resize(np.array(img))

    # White-balance correction BEFORE background removal
    raw_frame  = gray_world_balance(raw_frame)
    best_frame = remove_background(raw_frame)
    ih, iw     = best_frame.shape[:2]
    data       = {"landmarks_found": False}

    # Quality gate
    quality, quality_issues = assess_image_quality(best_frame)
    data["quality"]        = quality
    data["quality_issues"] = quality_issues

    # MediaPipe landmark detection
    results = hands_detector.process(best_frame)
    lm_dict = None

    if results.multi_hand_landmarks:
        lm_raw  = results.multi_hand_landmarks[0]
        lm_dict = {
            i: (int(p.x * iw), int(p.y * ih))
            for i, p in enumerate(lm_raw.landmark)
        }
        data["landmarks_found"] = True
        best_frame, M = normalize_palm_orientation(best_frame, lm_dict)
        ih, iw        = best_frame.shape[:2]
        lm_dict       = rotate_landmarks(lm_dict, M, iw, ih)
        vitality_hsv, ui_vitality = get_vitality_relative(best_frame, lm_dict, iw, ih)
        finger_data   = compute_finger_ratios(lm_dict)
        fingerprints  = detect_fingerprint_patterns(best_frame, lm_dict)
    else:
        vitality_hsv = "Unknown (no landmarks detected)"
        ui_vitality  = "Upload a clearer image for vitality reading"
        finger_data  = {}
        fingerprints = {}

    # CLAHE
    enhanced_rgb, enhanced_gray = apply_clahe_lab(best_frame)

    # Skin mask
    skin_mask = get_skin_mask(best_frame)

    # Frangi
    frangi_norm = run_dual_frangi(enhanced_gray)
    frangi_norm = cv2.bitwise_and(frangi_norm, frangi_norm, mask=skin_mask)

    # Adaptive persistence
    persistence, persistence_ratio, adaptive_t = build_persistence_map_adaptive(frangi_norm)

    # Watershed-lite
    clean_mask = isolate_lines_watershed(
        frangi_norm, persistence, skin_mask, adaptive_t
    )

    # Topology
    topology = extract_topology(clean_mask, ih, iw)

    # Per-line tracing (core accuracy upgrade)
    if lm_dict:
        traced_lines, palm_skel, line_masks = trace_major_lines(
            clean_mask, frangi_norm, lm_dict, ih, iw
        )
    else:
        traced_lines, palm_skel, line_masks = _fallback_traced_lines(
            frangi_norm, ih, iw
        )

    # Zone scores (backward compat scalar dict)
    zone_scores = {k: (v["score"] if v else 0) for k, v in traced_lines.items()}

    # Marks and minor lines
    marks        = detect_marks_classical(palm_skel, line_masks, lm_dict, ih, iw)
    minor_lines  = detect_minor_lines(palm_skel, line_masks, lm_dict, ih, iw)

    # Global score
    px = frangi_norm[frangi_norm > 35]
    gs = int((np.mean(px) / 255) * 100) if len(px) > 0 else 0

    # Depth elevation
    depth_elev = get_mount_elevations_depth(best_frame, lm_dict)

    data.update({
        "vitality_hsv":       vitality_hsv,
        "ui_vitality":        ui_vitality,
        "line_clarity_score": gs,
        "ui_line":            ("Deep & Prominent" if gs > 35 else
                               "Clear & Defined"  if gs > 20 else "Delicate & Fine"),
        "zone_scores":        zone_scores,
        "traced_lines":       traced_lines,
        "topology":           topology,
        "persistence_ratio":  persistence_ratio,
        "finger_data":        finger_data,
        "fingerprints":       fingerprints,
        "marks":              marks,
        "minor_lines":        minor_lines,
        "depth_elevations":   depth_elev,
        "used_depth_model":   depth_elev is not None,
        "enhanced_rgb":       enhanced_rgb,
        "palm_skel":          palm_skel,
        "line_masks":         line_masks,
    })

    # Pre-LLM sanity check
    data["consistency_warnings"] = pre_llm_consistency_check(data)

    # Build diagnostic X-ray
    hm   = cv2.applyColorMap(frangi_norm, cv2.COLORMAP_BONE)
    pv   = cv2.normalize(persistence, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    pc   = cv2.applyColorMap(pv, cv2.COLORMAP_JET)
    xr   = cv2.addWeighted(hm, 0.55, pc, 0.45, 0)
    cy   = np.zeros_like(xr)
    cy[clean_mask > 0] = (255, 200, 0)
    xray = cv2.addWeighted(xr, 0.80, cy, 0.20, 0)
    if lm_dict:
        _draw_lm(xray, lm_dict)

    # Annotate X-ray with detected line labels
    xray = annotate_xray_with_labels(xray, traced_lines, lm_dict)

    return data, xray, best_frame, lm_dict


def _draw_lm(bgr, lm):
    conns = [
        (0,1),(1,2),(2,3),(3,4),
        (0,5),(5,6),(6,7),(7,8),
        (5,9),(9,10),(10,11),(11,12),
        (9,13),(13,14),(14,15),(15,16),
        (13,17),(17,18),(18,19),(19,20),
        (0,17),(5,9),(9,13),(13,17),
    ]
    for a, b in conns:
        if a in lm and b in lm:
            cv2.line(bgr, lm[a], lm[b], (80, 180, 80), 1, cv2.LINE_AA)
    for (x, y) in lm.values():
        cv2.circle(bgr, (x, y), 2, (120, 220, 120), -1)


# ══════════════════════════════════════════════════════════════════════
# SECTION 14 — MOUNT SLICER
# ══════════════════════════════════════════════════════════════════════

def slice_xray_mounts(best_frame_rgb, diagnostic_xray, lm_dict, enhanced_rgb=None):
    ih, iw = best_frame_rgb.shape[:2]
    src    = enhanced_rgb if enhanced_rgb is not None else best_frame_rgb
    xc, oc, ocr = {}, {}, {}

    if not lm_dict:
        th, tw = ih // 3, iw // 3
        fallback = {
            "Jupiter": (0,      th,      0,      tw),
            "Venus":   (th * 2, ih,      0,      tw),
            "Luna":    (th * 2, ih,      tw * 2, iw),
        }
        for nm, (y1, y2, x1, x2) in fallback.items():
            _xc = diagnostic_xray[y1:y2, x1:x2]
            _oc = src[y1:y2, x1:x2]
            xr  = cv2.cvtColor(_xc, cv2.COLOR_BGR2RGB) if _xc.ndim == 3 else _xc
            xc[nm]  = pad_to_square(xr)
            oc[nm]  = pad_to_square(_oc)
            ocr[nm] = _oc
        return xc, oc, ocr

    box  = int(np.sqrt(
        (lm_dict[5][0] - lm_dict[9][0])**2 +
        (lm_dict[5][1] - lm_dict[9][1])**2
    )) * 2
    vbox = int(box * 1.4)

    defs = {
        "Jupiter":    (lm_dict[5],  box),
        "Saturn":     (lm_dict[9],  box),
        "Sun":        (lm_dict[13], box),
        "Mercury":    (lm_dict[17], box),
        "Venus":      (lm_dict[2],  vbox),
        "Mars_Upper": ((lm_dict[17][0],
                        int((lm_dict[17][1] + lm_dict[0][1]) / 2)), vbox),
        "Luna":       ((lm_dict[17][0],
                        int(lm_dict[17][1]*.4 + lm_dict[0][1]*.6)), vbox),
    }

    for nm, ((ax, ay), bs) in defs.items():
        if nm in ("Jupiter", "Saturn", "Sun", "Mercury"):
            ay -= int(bs * .1)
        x1, y1, x2, y2 = get_safe_box(
            ax - bs // 2, ay - bs // 2, bs, bs, iw, ih, 0.30
        )
        _xc = diagnostic_xray[y1:y2, x1:x2]
        _oc = src[y1:y2, x1:x2]
        if _xc.size == 0:
            continue
        xr  = cv2.cvtColor(_xc, cv2.COLOR_BGR2RGB)
        lbl = xr.copy()
        cv2.putText(lbl, nm, (5, 18), cv2.FONT_HERSHEY_SIMPLEX,
                    .45, (255, 255, 255), 1, cv2.LINE_AA)
        xc[nm]  = pad_to_square(lbl)
        oc[nm]  = pad_to_square(_oc)
        ocr[nm] = _oc

    return xc, oc, ocr