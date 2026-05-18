"""features.dashboard.service — AI orchestration for the dashboard tiles.

Two functions:
  fetch_data(prof_json, today_str)      → {GREETING, ENERGY, FOCUS, CAUTION, WINDOW, SUMMARY}
  fetch_daily_tarot(prof_json, today_str, daily_card, daily_state)
                                        → {MEANING, ACTION, MANTRA}

today_str is part of the cache key (cached 24h in ui_streamlit/cache.py).
"""

import json

from shared.astro.dossier_builder import generate_astrology_dossier, get_gochara_overlay
from shared.ai.gemini_client import generate_content_with_fallback
from shared.ai.knowledge import rag_context
from features.dashboard.prompts import build_data_prompt
from features.tarot.prompts import build_daily_card_prompt


def _safe_json(raw: str, fallback: dict) -> dict:
    try:
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return fallback


def fetch_data(prof_json: str, today_str: str) -> dict:
    """Returns a dict: GREETING, ENERGY, FOCUS, CAUTION, WINDOW, SUMMARY."""
    prof = json.loads(prof_json)
    dos = generate_astrology_dossier(prof, False, compact=True)
    transits = get_gochara_overlay(prof)
    prompt = build_data_prompt(dos, transits, prof["name"].split()[0])
    res = generate_content_with_fallback(
        prompt, knowledge_files=None,
        preferred_model="gemini-3.1-flash-lite-preview",
    )
    return _safe_json(res, {
        "GREETING": f"Welcome back, {prof['name'].split()[0]}. The cosmic connection is catching its breath, but your tools are ready below.",
        "ENERGY":   "Mixed",
        "FOCUS":    "Routine",
        "CAUTION":  "Impulsivity",
        "WINDOW":   "Anytime",
        "SUMMARY":  "Balanced day. Stick to your routines.",
    })


def fetch_daily_tarot(prof_json: str, today_str: str, daily_card: str, daily_state: str) -> dict:
    """Returns a dict: MEANING, ACTION, MANTRA."""
    base_prompt = build_daily_card_prompt(daily_card, daily_state)
    json_prompt = base_prompt + """
RESPOND ONLY IN VALID JSON FORMAT. NO MARKDOWN:
    {
        "MEANING": "What the card means today.",
        "ACTION":  "The best practical step to take.",
        "MANTRA":  "A short, powerful affirmation."
    }"""
    tarot_ctx = rag_context(
        f"{daily_card} {daily_state} daily guidance meaning",
        ["tguide.md"], k=6,
    )
    if tarot_ctx:
        json_prompt = (
            f"<KNOWLEDGE_CONTEXT>\n{tarot_ctx}\n</KNOWLEDGE_CONTEXT>\n"
            "<RULES>Use only the tarot passages above for card meaning. "
            "Do not invent meanings outside them.</RULES>\n\n"
            + json_prompt
        )
    res = generate_content_with_fallback(json_prompt, knowledge_files=None)
    return _safe_json(res, {
        "MEANING": "Trust the process unfolding today.",
        "ACTION":  "Observe before making any sudden moves.",
        "MANTRA":  "I am exactly where I need to be.",
    })
