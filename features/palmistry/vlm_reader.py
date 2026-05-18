"""
ai_engine/palm_vision_ai.py
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

from ai_engine.gemini_client import get_ai_model_by_name
from features.palmistry.prompts import build_palm_reading_prompt


# ── MODEL CONFIG ──────────────────────────────────────────────────────────────

# Adjust this string to match the exact model identifier in your gemini_client.
# Gemini model names follow patterns like 'gemini-3-flash-lite-preview'
# or 'gemini-3.1-flash-lite-preview-MM-DD'. Check your gemini_client wrapper.
MODEL_NAME = "gemini-3.1-flash-lite-preview"


# ── REFERENCE IMAGE (one only — keeps token budget tight for Flash Lite) ──────
# book_image_18 is the most informative single reference: dual hand showing
# all planet names + Sattva/Rajas/Tamas guna zone distribution.

_REF_URL = (
    "https://hmspryhmyhegraqccnsh.supabase.co/storage/v1/object/public/"
    "palmistry-images/book_image_18.jpg"
)


@lru_cache(maxsize=2)
def _fetch_reference_image():
    """Cached reference image fetch. Returns PIL or None on failure."""
    try:
        r = requests.get(_REF_URL, timeout=10)
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
    Main entry point. Performs the single VLM call and returns a parsed result.

    Args:
        enhanced_palm:     CLAHE-enhanced full palm RGB ndarray
        mount_crops:       dict {mount_name: rgb_ndarray}
        hand_metrics:      from analyze_palm()
        vitality:          from analyze_palm()
        quality_metrics:   from analyze_palm()
        dossier:           kundli astrology dossier text
        knowledge_context: structured Vedic knowledge text
        qdrant_context:    classical text passages

    Returns:
        {
            "phase_a":   dict — structured observations
            "phase_b":   str  — markdown reading
            "raw":       str  — full VLM response
            "error":     str  — error message if call failed (empty otherwise)
        }
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

    ref = _fetch_reference_image()
    images = [main_palm] + mount_imgs + ([ref] if ref is not None else [])

    # Build prompt
    prompt = build_palm_reading_prompt(
        hand_metrics=hand_metrics,
        vitality=vitality,
        quality_metrics=quality_metrics,
        n_mount_crops=len(mount_imgs),
        dossier=dossier,
        knowledge_context=knowledge_context,
        qdrant_context=qdrant_context,
    )

    # Single VLM call
    try:
        model = get_ai_model_by_name(MODEL_NAME)
        response = model.generate_content(images + [prompt])
        text = response.text or ""
    except Exception as e:
        return {
            "phase_a": {},
            "phase_b": "",
            "raw":     "",
            "error":   f"VLM call failed: {type(e).__name__}: {e}",
        }

    parsed = _parse_response(text)
    parsed["error"] = ""
    return parsed
