import json
import re
import requests
import io
import cv2
import numpy as np
import PIL.Image
from functools import lru_cache

from ai_engine.gemini_client import get_ai_model_by_name
from math_engine.palm_vision import enhance_crop_for_ai


# ── helpers ───────────────────────────────────────────────────────────────────

def _pil_from_arr(arr):
    if isinstance(arr, PIL.Image.Image):
        return arr
    return PIL.Image.fromarray(arr.astype(np.uint8))


def _mount_interestingness(crop_arr):
    """
    Score a mount crop for 'how much is there to see'.
    High sharpness (Laplacian) + dense skeleton branches = most interesting.
    Used to pick which mounts to send to Gemini for symbol scanning.
    """
    if crop_arr is None or (isinstance(crop_arr, np.ndarray) and crop_arr.size == 0):
        return 0.0
    gray = cv2.cvtColor(crop_arr, cv2.COLOR_RGB2GRAY) if crop_arr.ndim == 3 else crop_arr
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    # Edge density as proxy for line density
    edges = cv2.Canny(gray, 30, 90)
    density = float(edges.sum()) / max(gray.size, 1)
    return sharpness * 0.6 + density * 500 * 0.4


# ══════════════════════════════════════════════════════════════════════
# REFERENCE GRID — lru_cache replaces st.cache_data (Streamlit-free)
# ══════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=4)
def fetch_reference_grid(filename):
    """
    Download the symbol reference chart from GitHub.
    Cached in-process; survives re-runs within the same Streamlit session.
    Migration note: swap @lru_cache for Redis when on FastAPI.
    """
    url = f"https://raw.githubusercontent.com/hinshalll/text2kprompt/main/palm_images/{filename}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return PIL.Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# MOUNT SYMBOL DETECTION
# ══════════════════════════════════════════════════════════════════════

def scan_mount_for_symbols(orig_crops_raw, reference_pil):
    """
    Scans the TOP-3 most visually interesting mounts for classical symbols.
    Sends each at full resolution rather than squashed into a 7-mount canvas.
    Two-pass strategy:
      Pass 1: "Is there anything symbol-like here? Yes / No."
      Pass 2 (only if yes): Identify and locate the specific symbol.
    Stays within 2 Gemini calls total for most palms (no symbols = 1 call).
    """
    model   = get_ai_model_by_name("gemini-2.0-flash")
    target_h = 360

    # Score and pick top-3
    scored = []
    for mount_name, crop in orig_crops_raw.items():
        if crop is None or (isinstance(crop, np.ndarray) and crop.size == 0):
            continue
        score = _mount_interestingness(crop)
        scored.append((score, mount_name, crop))
    scored.sort(key=lambda x: -x[0])
    top3 = scored[:3]

    if not top3:
        return []

    # Build resized, labelled crops for Pass 1
    pass1_parts  = []
    mount_order  = []
    crop_pils    = {}

    for _, mount_name, crop in top3:
        enh = enhance_crop_for_ai(crop) if isinstance(crop, np.ndarray) else np.array(crop)
        pil = _pil_from_arr(enh)
        ow, oh = pil.size
        nw = int(ow * target_h / max(oh, 1))
        arr = np.array(pil.resize((nw, target_h), PIL.Image.LANCZOS))
        # Label the crop
        cv2.putText(arr, mount_name, (5, 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, (0,0,0), 3, cv2.LINE_AA)
        cv2.putText(arr, mount_name, (5, 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, (255,255,255), 1, cv2.LINE_AA)
        pass1_parts.append(arr)
        mount_order.append(mount_name)
        crop_pils[mount_name] = PIL.Image.fromarray(arr)

    canvas_pil = PIL.Image.fromarray(np.hstack(pass1_parts))

    # ── Pass 1: quick screening ────────────────────────────────────────
    screen_prompt = (
        f"You are a Vedic palmist. The image shows palm mount crops labelled: "
        f"{', '.join(mount_order)}.\n"
        "For EACH labelled mount, answer only: does it contain any auspicious or "
        "inauspicious Vedic symbol (cross, star, triangle, square, island, fish, "
        "trident, grille, circle)? Answer strictly as JSON:\n"
        '{"screenings": [{"mount": "Jupiter", "has_symbol": true}, ...]}\n'
        "If uncertain, answer false. No other text."
    )

    try:
        resp1   = model.generate_content([canvas_pil, screen_prompt])
        match1  = re.search(r'\{.*\}', resp1.text, re.DOTALL)
        screen  = json.loads(match1.group(0)) if match1 else {}
        flagged = [
            s["mount"] for s in screen.get("screenings", [])
            if s.get("has_symbol")
        ]
    except Exception:
        flagged = []

    if not flagged:
        return []

    # ── Pass 2: identification on flagged mounts only ─────────────────
    id_parts = []
    id_order = []
    for mname in flagged:
        if mname in crop_pils:
            id_parts.append(np.array(crop_pils[mname]))
            id_order.append(mname)

    if not id_parts:
        return []

    id_canvas = PIL.Image.fromarray(np.hstack(id_parts))

    id_prompt = (
        f"You are an expert Vedic palmist (Samudrika Shastra).\n"
        f"IMAGE 1: Palm mount crops for {', '.join(id_order)}.\n"
        f"IMAGE 2: Reference chart of classical Vedic palm symbols.\n\n"
        "For each mount, identify the symbol, its position within the mount, "
        "your confidence (0-100), and its Vedic Sanskrit name.\n"
        "Only report if confidence >= 75.\n"
        "Output valid JSON only, no markdown:\n"
        '{"findings": [{"mount": "Jupiter", "symbol": "Trident", '
        '"confidence_score": 88, "position": "centre", "vedic_name": "Trishul"}]}\n'
        'If nothing qualifies: {"findings": []}'
    )

    try:
        resp2 = model.generate_content([id_canvas, reference_pil, id_prompt])
        match2 = re.search(r'\{.*\}', resp2.text, re.DOTALL)
        if match2:
            return json.loads(match2.group(0)).get("findings", [])
    except Exception:
        pass

    return []


# ══════════════════════════════════════════════════════════════════════
# FINGER + FINGERPRINT ANALYSIS  (single Gemini call)
# ══════════════════════════════════════════════════════════════════════

def analyze_fingers_with_ai(full_hand_pil, finger_geo_data, math_fingerprints=None):
    """
    Sends the full CLAHE-enhanced hand image to Gemini.
    Single call covers:
      - Tip shape per finger (conic / square / rounded / spatulate)
      - Samudrika note per finger
      - Fingerprint pattern per finger (arch / loop / whorl) — cross-checks
        the orientation-field result from detect_fingerprint_patterns()
      - Mercury low-set, joint type, spacing, curve, overall character
    Returns parsed JSON dict or {}.
    """
    if full_hand_pil is None:
        return {}

    model = get_ai_model_by_name("gemini-2.0-flash")

    geo_ctx = ""
    if finger_geo_data:
        geo_ctx = (
            f"MediaPipe geometry: hand_type={finger_geo_data.get('hand_type','?')}, "
            f"2D:4D={finger_geo_data.get('ratio_2d4d','?')}, "
            f"dominant={finger_geo_data.get('dominant_finger','?')}."
        )

    math_fp_ctx = ""
    if math_fingerprints:
        fp_str = ", ".join(f"{k}={v}" for k, v in math_fingerprints.items())
        math_fp_ctx = (
            f"\nMath-engine fingerprint estimates (orientation field): {fp_str}. "
            "Cross-check these against what you see and correct if clearly wrong."
        )

    prompt = f"""You are an expert Vedic palmist specialising in Samudrika Shastra finger and dermatoglyphic analysis.
{geo_ctx}{math_fp_ctx}

Examine this hand image carefully.

For EACH finger report:
  - tip_shape: conic (pointed/psychic) | square (practical) | rounded (balanced) | spatulate (energetic/restless)
  - fingerprint: arch | loop | whorl  (look at the ridge pattern on the fingertip)
  - samudrika_note: one short sentence

Also check:
  - Is the little (Mercury) finger set notably LOWER than the ring finger base? (low_set: true/false)
  - Joint type across all fingers: smooth (artistic) | knotted (philosophical)
  - Finger spacing: wide (independent) | moderate | close (cautious)
  - Finger curve: slight inward | straight | slight outward | pronounced inward
  - overall_character: 2 sentences synthesising the finger profile in Samudrika Shastra

Output valid JSON ONLY. No markdown, no preamble, no trailing text.
{{
  "thumb":   {{"tip_shape":"conic",     "fingerprint":"whorl", "samudrika_note":"strong will"}},
  "index":   {{"tip_shape":"square",    "fingerprint":"loop",  "length_vs_middle":"shorter", "samudrika_note":"practical leader"}},
  "middle":  {{"tip_shape":"rounded",   "fingerprint":"loop",  "straight":true,  "samudrika_note":"balanced"}},
  "ring":    {{"tip_shape":"conic",     "fingerprint":"loop",  "length_vs_index":"equal",  "samudrika_note":"creative"}},
  "little":  {{"tip_shape":"spatulate", "fingerprint":"arch",  "low_set":false,  "samudrika_note":"expressive"}},
  "joints":  "smooth",
  "finger_spacing": "moderate",
  "finger_curve":   "slight inward",
  "overall_character": "Two sentence synthesis here."
}}"""

    try:
        resp  = model.generate_content([full_hand_pil, prompt])
        match = re.search(r'\{.*\}', resp.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass

    return {}


# ══════════════════════════════════════════════════════════════════════
# IMAGE STITCHING FOR REPORT LLM
# ══════════════════════════════════════════════════════════════════════

def stitch_palm_for_llm(original_rgb_arr, xray_bgr_arr, target_height=600):
    """
    Produce a side-by-side PIL image: [CLAHE original | Annotated X-ray].
    Sent to the final report LLM instead of just the heatmap.
    The LLM reads actual palm features from the original AND understands
    where the math engine found lines from the annotated xray.
    """
    if original_rgb_arr is None or xray_bgr_arr is None:
        if original_rgb_arr is not None:
            return _pil_from_arr(original_rgb_arr)
        return None

    def _resize_h(arr, h):
        oh, ow = arr.shape[:2]
        nw = int(ow * h / max(oh, 1))
        return cv2.resize(arr, (nw, h), interpolation=cv2.INTER_AREA)

    orig_r  = _resize_h(original_rgb_arr, target_height)
    xray_r  = _resize_h(
        cv2.cvtColor(xray_bgr_arr, cv2.COLOR_BGR2RGB), target_height
    )

    # Label divider
    divider = np.full((target_height, 6, 3), [80, 80, 80], dtype=np.uint8)

    canvas = np.hstack([orig_r, divider, xray_r])

    # Add header labels
    cv2.putText(canvas, "Enhanced Palm", (6, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(canvas, "Enhanced Palm", (6, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1, cv2.LINE_AA)

    xray_x_offset = orig_r.shape[1] + 6
    cv2.putText(canvas, "Ridge Map (labelled)", (xray_x_offset + 5, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(canvas, "Ridge Map (labelled)", (xray_x_offset + 5, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220,220,100), 1, cv2.LINE_AA)

    return PIL.Image.fromarray(canvas)


# ══════════════════════════════════════════════════════════════════════
# ANCIENT TEXT SNIPER — lru_cache (Streamlit-free)
# ══════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=32)
def snipe_ancient_text(json_path, glossary_path, english_symbols_tuple):
    """
    Keyword-search ancient text JSON for passages related to detected symbols.
    english_symbols_tuple must be a tuple (hashable) for lru_cache.
    """
    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            gloss = json.load(f)
        with open(json_path, "r", encoding="utf-8") as f:
            book  = json.load(f)
    except Exception:
        return "Ancient texts unavailable."

    clean_syms = [
        s for s in english_symbols_tuple
        if s and s not in ("None detected", "None", "")
    ]
    if not clean_syms:
        return ""

    search_terms = []
    for sym in clean_syms:
        vedic = gloss.get(sym, sym)
        search_terms.append(vedic)
        if vedic != sym:
            search_terms.append(sym)

    text_blocks = []
    def _ex(node):
        if isinstance(node, dict):
            for v in node.values():
                _ex(v)
            if "content" in node and isinstance(node["content"], str):
                text_blocks.append(node["content"])
        elif isinstance(node, list):
            for i in node: _ex(i)
        elif isinstance(node, str) and len(node) > 20:
            text_blocks.append(node)
    _ex(book)
    full = " ".join(text_blocks)

    snippets = []; seen = set()
    for term in search_terms:
        idx = 0
        while len(snippets) < 6:
            pos = full.find(term, idx)
            if pos == -1:
                break
            wk = pos // 500
            if wk not in seen:
                seen.add(wk)
                start = max(0, full.rfind(".", 0, pos-1)+1)
                end   = full.find(".", pos+len(term)+600)
                end   = end if end != -1 else min(len(full), pos+900)
                snip  = full[start:end].strip()
                if len(snip) > 50:
                    snippets.append(f"--- ANCIENT TEXT: '{term}' ---\n{snip}\n")
            idx = pos + len(term)

    return "\n".join(snippets) if snippets else ""


# ══════════════════════════════════════════════════════════════════════
# RE-EXPORT for palmistry.py compat
# ══════════════════════════════════════════════════════════════════════

def estimate_mount_elevations_relative(orig_crops_raw):
    from math_engine.palm_vision import estimate_mount_elevations_relative as _fn
    return _fn(orig_crops_raw)