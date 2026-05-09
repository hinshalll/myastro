import json
import requests
import io
import cv2
import numpy as np
import PIL.Image
from ai_engine.gemini_client import get_ai_model_by_name
import streamlit as st
from math_engine.palm_vision import enhance_crop_for_ai


@st.cache_data(show_spinner=False)
def fetch_reference_grid(filename):
    url = f"https://raw.githubusercontent.com/hinshalll/text2kprompt/main/palm_images/{filename}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return PIL.Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        return None


def scan_mount_for_symbols(orig_crops_raw, reference_pil):
    """
    Sends CLAHE-enhanced original palm crops to Gemini Vision — not the heatmap.
    Labels each crop with its mount name so Gemini has spatial context.
    Confidence threshold: 75%.
    """
    model      = get_ai_model_by_name("gemini-2.5-flash")
    target_h   = 350
    composites = []
    mount_order = []

    for mount_name, crop in orig_crops_raw.items():
        if crop is None or (isinstance(crop, np.ndarray) and crop.size == 0):
            continue
        # Apply stronger CLAHE so Gemini actually sees lines, not flat skin
        if isinstance(crop, np.ndarray):
            crop_enh = enhance_crop_for_ai(crop)
            crop_pil = PIL.Image.fromarray(crop_enh)
        else:
            crop_pil = crop

        ow, oh = crop_pil.size
        nw = int(ow * target_h / max(oh, 1))
        arr = np.array(crop_pil.resize((nw, target_h), PIL.Image.LANCZOS))

        # Burn label — black outline + white text so it's legible on any skin tone
        cv2.putText(arr, mount_name, (5, 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(arr, mount_name, (5, 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, (255, 255, 255), 1, cv2.LINE_AA)
        composites.append(arr)
        mount_order.append(mount_name)

    if not composites:
        return []

    canvas     = np.hstack(composites)
    canvas_pil = PIL.Image.fromarray(canvas)

    prompt = f"""You are an expert Vedic palmist and Samudrika Shastra specialist.

IMAGE 1: A composite of {len(mount_order)} palm mount crops. Each is labelled at the top: {', '.join(mount_order)}.
IMAGE 2: A reference chart of auspicious and inauspicious Vedic palm symbols.

YOUR TASK:
For each labelled mount in Image 1, carefully examine the skin markings, fine creases, and ridge patterns.
Compare them against the symbols in Image 2.

STRICT RULES:
- Only report a symbol if you see a clear geometric match — not just a random crease or skin texture.
- Do NOT report a symbol if confidence < 75.
- If no clear symbol is found on a mount, omit it entirely from findings.
- Report the mount name EXACTLY as labelled above.
- Report position within the mount: "centre", "upper", "lower", "left-edge", "right-edge".

OUTPUT: Valid JSON only. No markdown. No explanation outside the JSON.
{{
  "findings": [
    {{
      "mount": "Jupiter",
      "symbol": "Trident",
      "confidence_score": 88,
      "position": "centre",
      "vedic_name": "Trishul"
    }}
  ]
}}

If absolutely no symbols are found: {{"findings": []}}
"""
    try:
        resp  = model.generate_content([canvas_pil, reference_pil, prompt])
        clean = (resp.text.strip()
                 .removeprefix("```json").removeprefix("```")
                 .removesuffix("```").strip())
        return json.loads(clean).get("findings", [])
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def snipe_ancient_text(json_path, glossary_path, english_symbols):
    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            gloss = json.load(f)
        with open(json_path, "r", encoding="utf-8") as f:
            book  = json.load(f)
    except Exception:
        return "Ancient texts unavailable."

    clean_syms = [s for s in english_symbols
                  if s and s not in ("None detected", "None", "")]
    if not clean_syms:
        return ""

    search_terms = []
    for sym in clean_syms:
        vedic = gloss.get(sym, sym)
        search_terms.append(vedic)
        if vedic != sym:
            search_terms.append(sym)

    text_blocks = []
    def _extract(node):
        if isinstance(node, dict):
            for v in node.values(): _extract(v)
            if "content" in node and isinstance(node["content"], str):
                text_blocks.append(node["content"])
        elif isinstance(node, list):
            for i in node: _extract(i)
        elif isinstance(node, str) and len(node) > 20:
            text_blocks.append(node)
    _extract(book)
    full = " ".join(text_blocks)

    snippets = []; seen = set()
    for term in search_terms:
        idx = 0
        while len(snippets) < 6:
            pos = full.find(term, idx)
            if pos == -1: break
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


def estimate_mount_elevations_relative(orig_crops_raw):
    """Imported and called from palmistry.py — kept here for backward compat."""
    from math_engine.palm_vision import estimate_mount_elevations_relative as _fn
    return _fn(orig_crops_raw)
