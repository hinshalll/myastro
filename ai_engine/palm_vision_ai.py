import json
import re
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
    Sends CLAHE-enhanced original palm crops to gemini-3.1-flash-lite-preview.
    JSON extracted via regex — immune to any conversational filler the LLM adds.
    """
    model    = get_ai_model_by_name("gemini-3.1-flash-lite-preview")
    target_h = 350
    parts    = []
    mount_order = []

    for mount_name, crop in orig_crops_raw.items():
        if crop is None or (isinstance(crop, np.ndarray) and crop.size == 0):
            continue
        crop_enh = enhance_crop_for_ai(crop) if isinstance(crop, np.ndarray) else np.array(crop)
        pil = PIL.Image.fromarray(crop_enh)
        ow, oh = pil.size
        nw = int(ow * target_h / max(oh, 1))
        arr = np.array(pil.resize((nw, target_h), PIL.Image.LANCZOS))
        cv2.putText(arr, mount_name, (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0,0,0), 3, cv2.LINE_AA)
        cv2.putText(arr, mount_name, (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255,255,255), 1, cv2.LINE_AA)
        parts.append(arr)
        mount_order.append(mount_name)

    if not parts:
        return []

    canvas_pil = PIL.Image.fromarray(np.hstack(parts))
    prompt = f"""You are an expert Vedic palmist and Samudrika Shastra specialist.
IMAGE 1: Palm mount crops labelled: {', '.join(mount_order)}.
IMAGE 2: Reference chart of auspicious/inauspicious Vedic palm symbols.
Compare each mount against Image 2. Only report if confidence >= 75. Output JSON only.
{{"findings":[{{"mount":"Jupiter","symbol":"Trident","confidence_score":88,"position":"centre","vedic_name":"Trishul"}}]}}
If nothing found: {{"findings":[]}}"""

    try:
        resp  = model.generate_content([canvas_pil, reference_pil, prompt])
        match = re.search(r'\{.*\}', resp.text, re.DOTALL)
        if match:
            return json.loads(match.group(0)).get("findings", [])
        return []
    except Exception:
        return []


def analyze_fingers_with_ai(full_hand_pil, finger_geo_data):
    """
    Sends the full CLAHE-enhanced hand image to gemini-3.1-flash-lite-preview.
    Reads qualitative finger features: tip shape, knuckle type, Mercury set,
    finger spacing, curve, and overall Samudrika Shastra Hasta character.
    JSON extracted via regex.
    """
    if full_hand_pil is None:
        return {}

    model = get_ai_model_by_name("gemini-3.1-flash-lite-preview")

    geo_ctx = ""
    if finger_geo_data:
        geo_ctx = (f"MediaPipe data (reference): hand type={finger_geo_data.get('hand_type','?')}, "
                   f"2D:4D={finger_geo_data.get('ratio_2d4d','?')}, "
                   f"dominant finger={finger_geo_data.get('dominant_finger','?')}")

    prompt = f"""You are an expert Vedic palmist specialising in Samudrika Shastra finger analysis.
{geo_ctx}

Examine this hand image. For each finger report tip shape and a Samudrika note.
Tip shapes: conic=pointed/intuitive, square=practical, rounded=balanced, spatulate=energetic/restless.
Also check if the little (Mercury) finger is set notably lower than the ring finger base — this is a key Samudrika marker.
Report joints (smooth=artistic or knotted=philosophical), finger spacing (wide=independent/close=cautious), curve direction.

Output valid JSON only. No markdown. No extra text.
{{
  "thumb":   {{"tip_shape":"conic",     "samudrika_note":"strong will, independent thinking"}},
  "index":   {{"tip_shape":"square",    "length_vs_middle":"shorter","samudrika_note":"practical leadership"}},
  "middle":  {{"tip_shape":"rounded",   "straight":true,  "samudrika_note":"balanced responsibility"}},
  "ring":    {{"tip_shape":"conic",     "length_vs_index":"equal",  "samudrika_note":"creative and aesthetic"}},
  "little":  {{"tip_shape":"spatulate", "low_set":false,  "samudrika_note":"expressive communicator"}},
  "joints":  "smooth",
  "finger_spacing":"moderate",
  "finger_curve":"slight inward",
  "overall_character":"Two sentences interpreting the finger profile in Samudrika Shastra."
}}"""

    try:
        resp  = model.generate_content([full_hand_pil, prompt])
        match = re.search(r'\{.*\}', resp.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {}
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def snipe_ancient_text(json_path, glossary_path, english_symbols):
    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            gloss = json.load(f)
        with open(json_path, "r", encoding="utf-8") as f:
            book  = json.load(f)
    except Exception:
        return "Ancient texts unavailable."

    clean_syms = [s for s in english_symbols if s and s not in ("None detected","None","")]
    if not clean_syms: return ""

    search_terms = []
    for sym in clean_syms:
        vedic = gloss.get(sym, sym)
        search_terms.append(vedic)
        if vedic != sym: search_terms.append(sym)

    text_blocks = []
    def _ex(node):
        if isinstance(node, dict):
            for v in node.values(): _ex(v)
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
    from math_engine.palm_vision import estimate_mount_elevations_relative as _fn
    return _fn(orig_crops_raw)