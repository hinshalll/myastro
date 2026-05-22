"""
features.face_reading.knowledge_lookup
=======================================
Runtime lookup. Maps the deterministic measurements from face_vision.analyze_face()
onto meanings in data/face_knowledge.json, and formats a grounded block for the
VLM prompt.

No API calls. No Qdrant. Pure dict lookups in milliseconds — this is what keeps
the face reader lightweight AND grounded (the model interprets only what the
knowledge base says, instead of inventing meanings).

get_face_context(metrics, use_kundli=False, dossier="") -> dict
"""

import json
from functools import lru_cache
from pathlib import Path

KNOWLEDGE_PATH = Path(__file__).resolve().parent / "data" / "face_knowledge.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    if not KNOWLEDGE_PATH.exists():
        return {}
    try:
        with open(KNOWLEDGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _variant(kb, feature, key):
    """Safe meaning lookup for features.<feature>.variants.<key>."""
    if not key or key in ("average", "neutral", "medium"):
        return None
    v = (((kb.get("features", {}).get(feature, {})).get("variants", {})).get(key, {}))
    return v.get("meaning")


def _forehead_key(face_shape):
    fc = face_shape.get("forehead_to_cheek", 0.85)
    if fc >= 0.95:
        return "broad_high"
    if fc < 0.8:
        return "narrow_low"
    return None


def get_face_context(metrics: dict, use_kundli: bool = False, dossier: str = "") -> dict:
    """Return {formatted_block, available, sections} for this face reading.

    `metrics` is face_vision.analyze_face()['metrics']. `use_kundli`/`dossier`
    add the optional birth-chart cross-reference layer (only when the user
    linked their own chart).
    """
    kb = _load()
    result = {"formatted_block": "", "available": bool(kb), "sections": {}}
    if not kb or not metrics:
        result["formatted_block"] = "Structured face knowledge unavailable."
        return result

    lines = []
    sec = result["sections"]

    # ── Face shape → element ─────────────────────────────────────────────────
    fs = metrics.get("face_shape", {})
    shape = fs.get("primary")
    shape_data = kb.get("face_shapes", {}).get(shape, {})
    if shape_data:
        elem = kb.get("elements", {}).get(shape_data.get("element", ""), {})
        block = (f"FACE SHAPE — {shape} ({shape_data.get('sanskrit','')}), element "
                 f"{shape_data.get('element','')} ({elem.get('sanskrit','')}; conf={fs.get('confidence')}).\n"
                 f"  Traits: {shape_data.get('traits','')}\n"
                 f"  Shadow: {shape_data.get('shadow','')}\n"
                 f"  Element keywords: {', '.join(elem.get('keywords', []))}")
        lines.append(block)
        sec["face_shape"] = block

    # ── Dominant three-zone ──────────────────────────────────────────────────
    zones = metrics.get("zones", {})
    dom = zones.get("dominant")
    z = kb.get("three_zones", {}).get(dom, {})
    if z:
        block = (f"DOMINANT ZONE — {dom} ({z.get('sanskrit','')}).\n"
                 f"  Governs: {z.get('governs','')}\n"
                 f"  Meaning: {z.get('dominant_meaning','')}")
        lines.append(block)
        sec["zone"] = block

    # ── Per-feature meanings ─────────────────────────────────────────────────
    feats = []
    e = metrics.get("eyes", {})
    for k in (e.get("size"), e.get("spacing"), e.get("tilt")):
        m = _variant(kb, "eyes", k)
        if m: feats.append(f"  Eyes [{k}]: {m}")
    n = metrics.get("nose", {})
    for k in (n.get("length"), n.get("width")):
        m = _variant(kb, "nose", k)
        if m: feats.append(f"  Nose [{k}]: {m}")
    lc = metrics.get("lips_chin", {})
    for k in (lc.get("lip_fullness"), lc.get("mouth_width")):
        m = _variant(kb, "lips", k)
        if m: feats.append(f"  Lips [{k}]: {m}")
    jk = lc.get("jaw")
    jm = _variant(kb, "chin_jaw", jk)
    if jm: feats.append(f"  Chin/Jaw [{jk}]: {jm}")
    fk = _forehead_key(fs)
    fm = _variant(kb, "forehead", fk)
    if fm: feats.append(f"  Forehead [{fk}]: {fm}")
    if feats:
        block = "FEATURE READINGS (from measured geometry):\n" + "\n".join(feats)
        lines.append(block)
        sec["features"] = block

    # ── Optional kundli cross-reference layer ────────────────────────────────
    if use_kundli:
        kl = kb.get("kundli_layer", {})
        nak = "; ".join(f"{x['part']}={x['nakshatra']}({x['lord']})" for x in kl.get("face_nakshatras", []))
        asc = kl.get("ascendant_lord_appearance", {})
        asc_txt = "\n".join(f"  {p}: {d}" for p, d in asc.items())
        block = ("KUNDLI CROSS-REFERENCE (the user linked their birth chart — connect face to chart):\n"
                 f"  Face→Nakshatra map: {nak}\n"
                 "  Ascendant-lord appearance signatures:\n" + asc_txt +
                 ("\n  Birth-chart dossier follows in the prompt — match the measured features "
                  "to the chart's ascendant, ascendant lord, and 1st-house planets." if dossier else ""))
        lines.append(block)
        sec["kundli"] = block

    result["formatted_block"] = "\n\n".join(lines) if lines else "No matching knowledge for detected features."
    return result
