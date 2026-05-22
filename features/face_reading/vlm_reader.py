"""features.face_reading.vlm_reader — single Gemini VLM call for face reading.

ONE call. Sends the full face + up to 4 small region crops (no reference image,
to keep the token budget — and cost — minimal: well under ₹1 on Flash Lite) plus
the measured geometry, the JSON knowledge block, and (optionally) the kundli
dossier. Returns Phase A (JSON observations) + Phase B (markdown reading).

Self-contained image/JSON helpers (kept local so the feature stays isolated and
doesn't import from another feature folder).
"""

import io
import re
import json
import PIL.Image
import numpy as np

from shared.ai.gemini_client import get_ai_model_by_name
from features.face_reading.prompts import build_face_reading_prompt

MODEL_NAME = "gemini-3.1-flash-lite-preview"
_CROP_ORDER = ["forehead", "eyes", "nose", "mouth_chin"]


def _arr_to_pil(arr):
    if isinstance(arr, PIL.Image.Image):
        return arr
    return PIL.Image.fromarray(arr.astype(np.uint8))


def _label_image(pil_img, label):
    import cv2
    arr = np.array(pil_img).copy()
    h, w = arr.shape[:2]
    bar_h = max(24, h // 18)
    cv2.rectangle(arr, (0, 0), (max(110, len(label) * 11 + 14), bar_h), (0, 0, 0), -1)
    cv2.putText(arr, label, (6, int(bar_h * 0.72)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return PIL.Image.fromarray(arr)


def _extract_json(text):
    if not text:
        return {}
    for pat in [r'```json\s*(\{.*?\})\s*```', r'```\s*(\{.*?\})\s*```']:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            for candidate in (m.group(1), re.sub(r',(\s*[}\]])', r'\1', m.group(1))):
                try:
                    return json.loads(candidate)
                except Exception:
                    pass
    start = text.find('{')
    if start < 0:
        return {}
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                for candidate in (text[start:i + 1], re.sub(r',(\s*[}\]])', r'\1', text[start:i + 1])):
                    try:
                        return json.loads(candidate)
                    except Exception:
                        pass
                break
    return {}


def _parse_response(text):
    if not text:
        return {"phase_a": {}, "phase_b": "", "raw": ""}
    phase_a = _extract_json(text)
    phase_b = ""
    if '```' in text:
        first = text.find('```')
        second = text.find('```', first + 3)
        if second >= 0:
            phase_b = text[second + 3:].strip()
    if not phase_b:
        depth = 0; end = -1
        for i, c in enumerate(text):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        phase_b = text[end:].strip() if end > 0 else text.strip()
    phase_b = re.sub(r'^(##\s*)?Phase\s*B[:\.\-—]*\s*\n?', '', phase_b, count=1, flags=re.IGNORECASE).strip()
    return {"phase_a": phase_a, "phase_b": phase_b, "raw": text}


def read_face(enhanced_face, region_crops: dict, metrics: dict, quality_metrics: dict,
              pose_metrics: dict, knowledge_context: str = "", dossier: str = "",
              use_kundli: bool = False) -> dict:
    """Single VLM call. Returns {phase_a, phase_b, raw, error}."""
    if not quality_metrics.get("is_usable", True):
        return {
            "phase_a": {"image_quality": "poor", "image_issues": ", ".join(quality_metrics.get("issues_list", []))},
            "phase_b": "This photo isn't usable for a confident reading. Please retake it front-facing, "
                       "in even light, with the whole face clearly visible and hair off the forehead.",
            "raw": "", "error": "",
        }

    main = _label_image(_arr_to_pil(enhanced_face), "FACE")
    crops = [_label_image(_arr_to_pil(region_crops[name]), name.upper().replace("_", " "))
             for name in _CROP_ORDER if name in region_crops]
    images = [main] + crops

    prompt = build_face_reading_prompt(
        metrics=metrics, quality_metrics=quality_metrics, pose_metrics=pose_metrics,
        n_crops=len(crops), knowledge_context=knowledge_context,
        dossier=dossier, use_kundli=use_kundli,
    )

    try:
        model = get_ai_model_by_name(MODEL_NAME)
        response = model.generate_content(images + [prompt])
        text = response.text or ""
    except Exception as e:
        return {"phase_a": {}, "phase_b": "", "raw": "",
                "error": f"VLM call failed: {type(e).__name__}: {e}"}

    parsed = _parse_response(text)
    parsed["error"] = ""
    return parsed
