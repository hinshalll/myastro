"""
shared.ai/kundli_narrative.py
=============================

AI narrative layer for the premium kundli PDF.

Strict architectural rule: AI *never* computes astrology. The math engine
produces the structured facts; AI only verbalises them in user-friendly
tone. This keeps cost bounded and predictable, and eliminates hallucination
on chart data.

This module makes ONE batched Gemini call per kundli that produces:

    karmic_story         — a single-page narrative weaving D60 + Rahu/Ketu
                            + Atmakaraka into a past-life arc.
    decade_predictions   — age 0-9, 10-19, … 70-79 — eight ~150-word
                            paragraphs anchored to the active Vimshottari MD.
    yoga_paragraphs      — per detected yoga, a personalised 60-80-word
                            paragraph (max 12 yogas to stay in budget).
    transit_narrative    — 2-paragraph synthesis of the 12-month transit
                            forecast (Sade Sati phase, Jupiter sign change,
                            Rahu/Ketu axis, etc.).

Cost target: ≤ ~₹5 / kundli (Gemini Flash output @ ~150K tokens budget).

Failure mode: any exception returns an empty payload — the PDF still
renders, just without the narrative pages. Math facts are present in
their own dedicated sections regardless.
"""

from __future__ import annotations

import json
import re
from typing import Optional

from shared.ai.gemini_client import get_ai_model_by_name, FREE_MODELS
from shared.ai import config


# ─────────────────────────────────────────────────────────────────────────────
# Prompt construction
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_RULES = """
<CONSERVATIVE_VOICE>
Be conservative. When uncertain between two readings, prefer the safer one and
say you're uncertain. NEVER fabricate dates, degrees, planet positions,
nakshatras, or divisional placements — every such fact must come from the FACTS
block below.
</CONSERVATIVE_VOICE>

<ROLE>
You are a senior Vedic-astrology copywriter producing narrative prose for a
premium printed kundli. The native is reading this once and keeping it for
life. Tone: dignified, warm, specific, lightly poetic.
Never generic. Never preachy. Never "you might be a person who…".
</ROLE>

<HARD_RULES>
1. EVERY chart fact you cite must come from the FACTS block. Do not invent
   houses, signs, dashas, yogas, or doshas.
2. Do NOT compute anything. Do NOT change degrees, signs, dates, planet
   names, or dasha lords. Treat the FACTS block as immutable truth.
3. Speak directly to the native ("you") — never in third person.
4. Each output section must respect its word budget exactly.
5. Output VALID JSON only, no prose outside the JSON, no markdown fences.
</HARD_RULES>

<OUTPUT_SCHEMA>
{
  "karmic_story":       "<250-350 word narrative>",
  "decade_predictions": {
      "0-9":   "<140-180 word paragraph>",
      "10-19": "<140-180 word paragraph>",
      "20-29": "<140-180 word paragraph>",
      "30-39": "<140-180 word paragraph>",
      "40-49": "<140-180 word paragraph>",
      "50-59": "<140-180 word paragraph>",
      "60-69": "<140-180 word paragraph>",
      "70-79": "<140-180 word paragraph>"
  },
  "yoga_paragraphs": {
      "<Yoga Name>": "<60-80 word paragraph>",
      ...
  },
  "transit_narrative": "<200-260 word two-paragraph synthesis>"
}
</OUTPUT_SCHEMA>
"""


def _facts_for_ai(chart) -> dict:
    """Distil the chart down to the minimal facts needed for narrative."""
    planets = {
        p: {
            "sign": pp.sign,
            "house": pp.house,
            "nakshatra": pp.nakshatra,
            "pada": pp.pada,
            "dignity": pp.dignity,
            "retrograde": pp.is_retrograde,
            "combust": pp.is_combust,
        }
        for p, pp in chart.planets.items()
    }

    # Dasha timeline anchored to age decades
    dasha_by_decade = {}
    if chart.dashas.get("Vimshottari"):
        from zoneinfo import ZoneInfo
        from datetime import datetime, timedelta
        birth_dt = chart.datetime_local
        tz = ZoneInfo(chart.birth_data.tz)
        for d_start in range(0, 80, 10):
            target = birth_dt + timedelta(days=d_start * 365.25)
            md_lord = ad_lord = "—"
            for md in chart.dashas["Vimshottari"].periods:
                if md.start <= target <= md.end:
                    md_lord = md.lord
                    for ad in md.children:
                        if ad.start <= target <= ad.end:
                            ad_lord = ad.lord
                            break
                    break
            dasha_by_decade[f"{d_start}-{d_start+9}"] = {
                "md": md_lord, "ad_at_decade_start": ad_lord
            }

    yogas = [
        {"name": y.name, "category": y.category, "description": y.description}
        for y in chart.yogas[:12]
    ]

    doshas = [
        {"name": d.name, "severity": d.severity, "cause": d.cause}
        for d in chart.doshas if d.present
    ]

    transit = chart.transit_forecast or {}
    sade = transit.get("sade_sati", {}) if transit else {}
    transit_summary = {
        "saturn_now":  transit.get("current_transit", {}).get("Saturn", {}),
        "jupiter_now": transit.get("current_transit", {}).get("Jupiter", {}),
        "rahu_now":    transit.get("current_transit", {}).get("Rahu", {}),
        "sade_sati":   sade,
        "ashtama_shani":   transit.get("ashtama_shani", False),
        "kantaka_shani":   transit.get("kantaka_shani", False),
        "guru_chandra":    transit.get("guru_chandra_yoga", False),
    }

    return {
        "name":      chart.birth_data.name,
        "gender":    chart.birth_data.gender,
        "lagna":     {"sign": chart.lagna.sign, "nakshatra": chart.lagna.nakshatra,
                      "pada": chart.lagna.pada, "lord": chart.lagna.lord},
        "moon":      planets["Moon"],
        "sun":       planets["Sun"],
        "planets":   planets,
        "atmakaraka": chart.chara_karakas.atmakaraka,
        "amatyakaraka": chart.chara_karakas.amatyakaraka,
        "rahu":      planets["Rahu"],
        "ketu":      planets["Ketu"],
        "d60_lagna_sign": (chart.divisional_charts[60].lagna_sign_index
                           if 60 in chart.divisional_charts else None),
        "functional": {
            "yogakarakas": chart.functional.yogakarakas,
            "benefics":    chart.functional.benefics,
            "malefics":    chart.functional.malefics,
        },
        "yogas":     yogas,
        "doshas":    doshas,
        "dasha_by_decade": dasha_by_decade,
        "transit":   transit_summary,
    }


def _build_prompt(facts: dict, language: str = "en") -> str:
    lang_map = {
        "en": "English",
        "hi": "Hindi (Devanagari script)",
        "ta": "Tamil",
        "te": "Telugu",
        "mr": "Marathi",
        "bn": "Bengali",
        "gu": "Gujarati",
    }
    target_lang = lang_map.get(language, "English")
    yoga_names = ", ".join(y["name"] for y in facts["yogas"]) or "—"

    return f"""
Produce the four narrative sections defined in OUTPUT_SCHEMA, in **{target_lang}**.
Pull every concrete reference from the FACTS block.

For yoga_paragraphs include ONE entry for each of these yogas (and no others):
  {yoga_names}

FACTS:
{json.dumps(facts, indent=2, ensure_ascii=False, default=str)}

Now produce the JSON object — and nothing else.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Response parsing
# ─────────────────────────────────────────────────────────────────────────────

def _strip_to_json(text: str) -> str:
    """Pull out the first {...} JSON block from the response, tolerating fences."""
    s = text.strip()
    s = s.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    m = re.search(r"\{[\s\S]*\}", s)
    return m.group(0) if m else s


def _empty_payload() -> dict:
    return {
        "karmic_story": "",
        "decade_predictions": {},
        "yoga_paragraphs": {},
        "transit_narrative": "",
        "_meta": {"ok": False, "model": None, "reason": "skipped"},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def generate(chart, *, language: str = "en",
             model_name: Optional[str] = None) -> dict:
    """
    Run the batched narrative call. Returns the parsed JSON payload, or an
    empty payload on any failure (PDF still renders without it).

    Cost target: ≤ ~₹5 per kundli. Defaults to the smallest capable Gemini
    Flash variant. Override via `model_name` for testing.
    """
    facts = _facts_for_ai(chart)
    prompt = _build_prompt(facts, language=language)

    # Walk the 'json' ladder (Gemini → DeepSeek) with the circuit breaker.
    ladder = config.ladder_for("json")
    if model_name:
        ladder = [model_name] + [m for m in ladder if m != model_name]

    last_err = None
    for m_name in config.usable_models(ladder):
        try:
            model = get_ai_model_by_name(m_name, custom_system_rules=_SYSTEM_RULES)
            resp = model.generate_content(prompt)
            payload = json.loads(_strip_to_json((resp.text or "").strip()))
            config.note_success(m_name)
            payload["_meta"] = {"ok": True, "model": m_name, "reason": "ok"}
            return payload
        except Exception as e:
            last_err = e
            config.note_failure(m_name, str(e))   # cools only on quota errors
            continue

    out = _empty_payload()
    out["_meta"]["reason"] = f"{type(last_err).__name__}: {last_err}" if last_err else "no_model"
    return out
