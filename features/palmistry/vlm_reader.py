"""
shared.ai/palm_vision_ai.py
============================
Single-call VLM palm reader.

Replaces the previous 4-call orchestration (symbol scan x2, finger analysis,
final report) with one focused call to Gemini 3 Flash Lite Preview that
gets the full palm + 7 mount crops + math signals + dossier + Qdrant
context, and produces a two-phase response (JSON observations + markdown
reading).

Why a single call:
  - Faster (one network round trip instead of four)
  - Cheaper (no duplicated context across calls)
  - More coherent (one model owns the visual judgment end-to-end)
  - More honest (the model can say 'not_assessable' instead of being forced
    to fill structured fields the previous pipeline assumed)

Why mount crops as additional images (not just the full palm):
  - Smaller models like Flash Lite get more pixels per mount this way
  - Mark detection accuracy improves substantially with focused crops
  - The cost is ~7 extra small image tokens, well within budget
"""

import io
import re
import json
import requests
import PIL.Image
import numpy as np
from functools import lru_cache

from shared.ai.gemini_client import get_ai_model_by_name
from features.palmistry.prompts import build_palm_reading_prompt, build_phase_a_prompt, build_phase_b_prompt


# ── MODEL CONFIG ──────────────────────────────────────────────────────────────

# Adjust this string to match the exact model identifier in your gemini_client.
# Gemini model names follow patterns like 'gemini-3-flash-lite-preview'
# or 'gemini-3.1-flash-lite-preview-MM-DD'. Check your gemini_client wrapper.
MODEL_NAME = "gemini-3.1-flash-lite-preview"


# ── REFERENCE IMAGES (Dual diagram comparative calibration) ────────────────────
# _MOUNTS_REF_URL: Dual hand planet mounts + Sattva/Rajas/Tamas gunas
_MOUNTS_REF_URL = (
    "https://hmspryhmyhegraqccnsh.supabase.co/storage/v1/object/public/palmistry-images/palmistry/book_image_18.jpg"
)

# _LINES_REF_URL: Grid of 25 boxes (A to Y) of line structures/defects (islands, breaks, chains)
_LINES_REF_URL = (
    "https://hmspryhmyhegraqccnsh.supabase.co/storage/v1/object/public/palmistry-images/palmistry/reference_grid_3.jpg"
)


@lru_cache(maxsize=2)
def _fetch_mounts_ref():
    """Cached fetch of the mounts and gunas reference image. Returns PIL or None."""
    try:
        r = requests.get(_MOUNTS_REF_URL, timeout=10)
        r.raise_for_status()
        return PIL.Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        return None


@lru_cache(maxsize=2)
def _fetch_lines_ref():
    """Cached fetch of the line structures grid reference image. Returns PIL or None."""
    try:
        r = requests.get(_LINES_REF_URL, timeout=10)
        r.raise_for_status()
        return PIL.Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        return None


# ── HELPERS ────────────────────────────────────────────────────────────────────

def _arr_to_pil(arr):
    """Convert numpy RGB array to PIL Image, passthrough if already PIL."""
    if isinstance(arr, PIL.Image.Image):
        return arr
    return PIL.Image.fromarray(arr.astype(np.uint8))


def _label_image(pil_img, label):
    """
    Stamp a small text label at the top of an image. The VLM uses the label
    to disambiguate which mount crop is which when looking at a multi-image input.
    """
    import cv2
    arr = np.array(pil_img).copy()
    h, w = arr.shape[:2]
    bar_h = max(26, h // 18)
    cv2.rectangle(arr, (0, 0), (max(120, len(label) * 11 + 14), bar_h), (0, 0, 0), -1)
    cv2.putText(
        arr, label, (6, int(bar_h * 0.72)),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA,
    )
    return PIL.Image.fromarray(arr)


# ── JSON EXTRACTION ────────────────────────────────────────────────────────────

def _extract_json(text):
    """
    Robustly extract a JSON object from text. Handles:
      - ```json fenced blocks
      - ``` fenced blocks (no language tag)
      - Bare {...} blocks
      - Trailing commas (light cleanup)
    Returns parsed dict or {} on failure.
    """
    if not text:
        return {}

    # Try fenced JSON first
    for fence_pattern in [
        r'```json\s*(\{.*?\})\s*```',
        r'```\s*(\{.*?\})\s*```',
    ]:
        m = re.search(fence_pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                # Light cleanup: remove trailing commas
                cleaned = re.sub(r',(\s*[}\]])', r'\1', m.group(1))
                try:
                    return json.loads(cleaned)
                except Exception:
                    pass

    # Fallback: find largest balanced {...} block
    start = text.find('{')
    if start < 0:
        return {}
    depth = 0
    end = -1
    for i in range(start, len(text)):
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            cleaned = re.sub(r',(\s*[}\]])', r'\1', candidate)
            try:
                return json.loads(cleaned)
            except Exception:
                return {}

    return {}


def _parse_response(text):
    """
    Split the VLM output into Phase A (JSON observations) and Phase B (markdown reading).
    Returns dict with phase_a, phase_b, raw.
    """
    if not text:
        return {"phase_a": {}, "phase_b": "", "raw": ""}

    phase_a = _extract_json(text)

    # Find where Phase B starts: after the closing ``` of the JSON block,
    # OR after the closing } of a bare JSON block.
    phase_b = ""

    # Try fenced JSON end
    fence_end = re.search(r'```\s*\n', text[text.find('```') + 3:] if '```' in text else '')
    if '```' in text:
        # Find second ``` (closing the JSON fence)
        first_fence = text.find('```')
        if first_fence >= 0:
            second_fence = text.find('```', first_fence + 3)
            if second_fence >= 0:
                phase_b = text[second_fence + 3:].strip()

    # If no fences, try after first closing brace
    if not phase_b:
        depth = 0
        in_json = False
        end = -1
        for i, c in enumerate(text):
            if c == '{':
                depth += 1
                in_json = True
            elif c == '}':
                depth -= 1
                if in_json and depth == 0:
                    end = i + 1
                    break
        if end > 0:
            phase_b = text[end:].strip()
        else:
            phase_b = text.strip()

    # Strip leading "Phase B" / "## Phase B" if the model included it
    phase_b = re.sub(
        r'^(##\s*)?Phase\s*B[:\.\-—]*\s*\n?',
        '', phase_b, count=1, flags=re.IGNORECASE
    ).strip()

    return {"phase_a": phase_a, "phase_b": phase_b, "raw": text}


# ── PUBLIC API ─────────────────────────────────────────────────────────────────

# Mount order for consistent input to the VLM
_MOUNT_ORDER = ["Jupiter", "Saturn", "Sun", "Mercury", "Venus", "Mars", "Luna"]


def _build_rich_palm_data(phase_a: dict, hand_metrics: dict, vitality: dict) -> tuple[dict, dict]:
    """
    Build rich_palm and mount elevations dicts compatible with 
    get_palm_context and query_palmistry from Phase A JSON results.
    """
    rich_palm = {}
    
    # 1. Traced lines
    traced_lines = {}
    phase_a_lines = phase_a.get("lines", {})
    
    # Heart line
    heart = phase_a_lines.get("heart", {})
    heart_vis = heart.get("visibility", "not_visible")
    traced_lines["heart_line"] = {
        "present": heart_vis in ["clear", "faint", "fragmented"],
        "depth_label": heart_vis,
        "curvature": heart.get("path", "not_assessable") + f" ending {heart.get('endpoint', '')}",
        "length_pct": 75 if heart_vis == "clear" else (40 if heart_vis in ["faint", "fragmented"] else 0)
    }
    
    # Head line
    head = phase_a_lines.get("head", {})
    head_vis = head.get("visibility", "not_visible")
    traced_lines["head_line"] = {
        "present": head_vis in ["clear", "faint", "fragmented"],
        "depth_label": head_vis,
        "curvature": f"slope {head.get('slope', '')}, joined to life: {head.get('joined_to_life', '')}",
        "length_pct": 80 if head_vis == "clear" else (45 if head_vis in ["faint", "fragmented"] else 0)
    }
    
    # Life line
    life = phase_a_lines.get("life", {})
    life_vis = life.get("visibility", "not_visible")
    traced_lines["life_line"] = {
        "present": life_vis in ["clear", "faint", "fragmented"],
        "depth_label": life_vis,
        "curvature": f"curve {life.get('curve', '')}",
        "length_pct": 90 if life_vis == "clear" else (50 if life_vis in ["faint", "fragmented"] else 0)
    }
    
    # Fate line
    fate = phase_a_lines.get("fate", {})
    fate_vis = fate.get("visibility", "not_visible")
    traced_lines["fate_line"] = {
        "present": fate_vis in ["clear", "faint", "fragmented"],
        "depth_label": fate_vis,
        "curvature": f"starts at {fate.get('starts_at', '')}",
        "length_pct": 60 if fate_vis == "clear" else (20 if fate_vis in ["faint", "fragmented"] else 0)
    }
    
    # Sun line
    sun = phase_a_lines.get("sun", {})
    sun_vis = sun.get("visibility", "not_visible")
    traced_lines["sun_line"] = {
        "present": sun_vis in ["clear", "faint", "fragmented"],
        "depth_label": sun_vis,
        "length_pct": 50 if sun_vis == "clear" else (15 if sun_vis in ["faint", "fragmented"] else 0)
    }
    
    rich_palm["traced_lines"] = traced_lines

    # 2. Mounts & Elevations
    elevations = {}
    phase_a_mounts = phase_a.get("mounts", {})
    for mount, details in phase_a_mounts.items():
        fullness = details.get("fullness", "moderate")
        score = 60 if fullness == "prominent" else (40 if fullness == "moderate" else 20)
        elevations[mount] = {"score": score}

    # 3. Marks
    marks = []
    for mount, details in phase_a_mounts.items():
        m_txt = details.get("marks", "no notable marks")
        if m_txt and m_txt != "no notable marks" and m_txt != "not_assessable":
            marks.append({"type": m_txt, "position": f"{mount} mount"})
            
    phase_a_special = phase_a.get("special_marks", {})
    for sm, status in phase_a_special.items():
        if status == "visible":
            marks.append({"type": sm.replace("_", " "), "position": "palm"})
            
    rich_palm["marks"] = marks

    # 4. Minor lines
    minor_lines = {}
    marr = phase_a_lines.get("marriage_lines", {})
    if marr.get("count_visible") not in ["0", "not_assessable"]:
        minor_lines["marriage_lines"] = marr.get("description", "visible")
    rich_palm["minor_lines"] = minor_lines

    # 5. Topology
    simian = phase_a_lines.get("simian", {})
    rich_palm["topology"] = {
        "simian_line": simian.get("present", False)
    }

    # 6. Finger data & Hand Metrics
    rich_palm["finger_data"] = {
        "hand_type": hand_metrics.get("hand_type", "") or phase_a.get("fingers", {}).get("tip_shape_dominant", "")
    }
    
    # Pass along vitality
    rich_palm["vitality"] = vitality
    rich_palm["ui_vitality"] = vitality.get("class", "")
    rich_palm["vitality_hsv"] = vitality.get("note", "")

    return rich_palm, elevations


def read_palm(
    enhanced_palm,
    mount_crops: dict,
    hand_metrics: dict,
    vitality: dict,
    quality_metrics: dict,
    dossier: str = "",
    knowledge_context: str = "",
    qdrant_context: str = "",
) -> dict:
    """
    Main entry point. Performs a two-pass VLM orchestration.
    1. Pass 1: Cheap visual-only VLM call to get Phase A JSON.
    2. Local context lookup (RAG + static Vedic) using the verified Phase A observations.
    3. Pass 3: Detailed VLM call combining image inputs with all computed contexts for a grounded reading.
    """
    # Refuse to call VLM if image is unusable — saves an API call
    if not quality_metrics.get("is_usable", True):
        return {
            "phase_a": {"image_quality": "poor", "image_issues": ", ".join(quality_metrics.get("issues_list", []))},
            "phase_b": "This photo isn't usable for a confident reading. Please re-take the photo with better lighting, focus, and the palm filling most of the frame.",
            "raw": "",
            "error": "",
        }

    # Build labelled image inputs
    main_palm = _label_image(_arr_to_pil(enhanced_palm), "FULL PALM")

    mount_imgs = []
    for name in _MOUNT_ORDER:
        if name in mount_crops:
            mount_imgs.append(_label_image(_arr_to_pil(mount_crops[name]), f"MT {name}"))

    ref_mounts = _fetch_mounts_ref()
    ref_lines = _fetch_lines_ref()

    images = [main_palm] + mount_imgs
    if ref_mounts is not None:
        images.append(ref_mounts)
    if ref_lines is not None:
        images.append(ref_lines)

    # ── Pass 1: Visual Observation Detection ──
    prompt_a = build_phase_a_prompt(
        hand_metrics=hand_metrics,
        vitality=vitality,
        quality_metrics=quality_metrics,
        n_mount_crops=len(mount_imgs),
    )

    try:
        model = get_ai_model_by_name(MODEL_NAME)
        response_a = model.generate_content(images + [prompt_a])
        text_a = response_a.text or ""
    except Exception as e:
        return {
            "phase_a": {},
            "phase_b": "",
            "raw":     "",
            "error":   f"VLM Pass A call failed: {type(e).__name__}: {e}",
        }

    phase_a = _extract_json(text_a)
    if not phase_a:
        # Fallback in case VLM failed to output valid JSON or parse failed
        phase_a = {
            "image_quality": "acceptable",
            "image_issues": "",
            "lines": {},
            "mounts": {},
            "special_marks": {},
            "fingers": {},
            "thumb": {}
        }

    # ── VLM Visual Self-Correction ──
    vlm_fingers = phase_a.get("fingers", {})
    if isinstance(vlm_fingers, dict):
        vlm_ratio = vlm_fingers.get("index_vs_ring_length")
        if vlm_ratio == "ring_longer":
            hand_metrics["dominant_finger"] = "Sun (ring)"
            hand_metrics["ratio_2d4d"] = 0.96
            hand_metrics["ratio_reading"] = "Lower than typical (indicating a longer Ring finger, associated with active Surya energy, creativity, and drive)"
        elif vlm_ratio == "index_longer":
            hand_metrics["dominant_finger"] = "Jupiter (index)"
            hand_metrics["ratio_2d4d"] = 1.04
            hand_metrics["ratio_reading"] = "Higher than typical (indicating a longer Index finger, associated with active Jupiter energy, leadership, and wisdom)"
        elif vlm_ratio == "equal":
            if hand_metrics.get("dominant_finger") not in ("Jupiter (index)", "Sun (ring)"):
                hand_metrics["dominant_finger"] = "Sun (ring)"
            hand_metrics["ratio_2d4d"] = 1.0
            hand_metrics["ratio_reading"] = "Within typical range (balanced Index and Ring finger heights)"

    vlm_vit = phase_a.get("vitality_visual_class")
    if vlm_vit and vlm_vit != "not_assessable":
        vitality["class"] = vlm_vit
        if vlm_vit == "Robust":
            vitality["note"] = "Warm, well-perfused tone — strong vital energy"
        elif vlm_vit == "Subdued":
            vitality["note"] = "Pale or muted tone — review rest and circulation"
        elif vlm_vit == "Balanced":
            vitality["note"] = "Healthy, even tone"
        elif vlm_vit == "Cool":
            vitality["note"] = "Cooler tone — variable energy reserves"

    # ── Pass 2: Local & Free Context Gathering ──
    # Construct compatible palm data structures for local lookups
    rich_palm, elevations = _build_rich_palm_data(phase_a, hand_metrics, vitality)

    # Dynamic imports to avoid circular dependencies
    try:
        from features.palmistry.knowledge_lookup import get_palm_context
    except ImportError:
        get_palm_context = None

    try:
        from features.palmistry.qdrant_search import query_palmistry
    except ImportError:
        query_palmistry = None

    # Retrieve context, letting dynamic Two-Pass flow override blind RAG contexts if they are empty
    knowledge_ctx = knowledge_context
    if not knowledge_ctx and get_palm_context:
        try:
            kctx = get_palm_context(rich_palm, elevations, dossier=dossier)
            knowledge_ctx = kctx.get("formatted_block", "")
        except Exception as e:
            print(f"[vlm_reader] knowledge lookup failed: {e}")

    qdrant_ctx = qdrant_context
    if not qdrant_ctx and query_palmistry:
        try:
            qdrant_ctx = query_palmistry(rich_palm, elevations, k=6)
        except Exception as e:
            print(f"[vlm_reader] qdrant search failed: {e}")

    # ── Pass 3: Coherent Reading Generation ──
    phase_a_str = json.dumps(phase_a, indent=2)
    prompt_b = build_phase_b_prompt(
        hand_metrics=hand_metrics,
        vitality=vitality,
        quality_metrics=quality_metrics,
        phase_a_json_str=phase_a_str,
        dossier=dossier,
        knowledge_context=knowledge_ctx,
        qdrant_context=qdrant_ctx,
    )

    try:
        response_b = model.generate_content(images + [prompt_b])
        text_b = response_b.text or ""
    except Exception as e:
        return {
            "phase_a": phase_a,
            "phase_b": "",
            "raw":     text_a,
            "error":   f"VLM Pass B call failed: {type(e).__name__}: {e}",
        }

    parsed = _parse_response(text_b)
    # Ensure phase_a returned to caller is the rich Phase A we detected
    parsed["phase_a"] = phase_a
    parsed["hand_metrics"] = hand_metrics
    parsed["vitality"] = vitality
    parsed["error"] = ""
    return parsed
