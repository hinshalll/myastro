"""
ai_engine/forecasts.py

Pure AI forecast functions — zero Streamlit imports.
Cache wrappers (@st.cache_data) live in ui_streamlit/pages/ files, not here.
FastAPI routes will call these functions directly without any cache layer.
"""

import json
import swisseph as swe
from datetime import datetime, date
from zoneinfo import ZoneInfo

from math_engine.constants import PLANETS, DASHA_ORDER
from math_engine.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed,
    sign_index_from_lon, sign_name, get_rahu_longitude,
)
from math_engine.dossier_builder import generate_astrology_dossier, get_gochara_overlay
from ai_engine.gemini_client import generate_content_with_fallback, FREE_MODELS
from ai_engine.knowledge import rag_context
from ai_engine.prompts import (
    GUARDRAILS, build_dashboard_data_prompt, build_daily_tarot_prompt,
)


# ── helpers ──────────────────────────────────────────────────────────────────

def safe_json(raw: str, fallback: dict) -> dict:
    """Parse a JSON string from the model, returning fallback on any error."""
    try:
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return fallback


def _get_local_today(tz_name: str) -> date:
    return datetime.now(ZoneInfo(tz_name)).date()


# ── Western forecast ──────────────────────────────────────────────────────────

def generate_western_forecast(sun_sign: str, today_str: str) -> str:
    """
    Generate a daily western (sun-sign) horoscope.
    today_str is passed in so the @st.cache_data TTL key works correctly.
    """
    now_jd = swe.julday(*[int(x) for x in today_str.split("-")], 12.0)

    transit_lines = [f"TODAY'S TROPICAL TRANSITS ({today_str}):"]
    for pname, pid in PLANETS.items():
        lon, _ = get_planet_longitude_and_speed(now_jd, pid)
        transit_lines.append(f"  {pname} at {lon:.2f}° ({sign_name(sign_index_from_lon(lon))})")
    r_lon = get_rahu_longitude(now_jd)
    transit_lines.append(f"  Rahu at {r_lon:.2f}° ({sign_name(sign_index_from_lon(r_lon))})")
    transit_data = "\n".join(transit_lines)

    prompt = f"""{GUARDRAILS}
<mission>
You are an elite Western Astrologer. Generate a highly accurate daily horoscope for {sun_sign}.
Use the exact tropical transit positions below. Focus on how today's planetary positions
specifically affect {sun_sign} based on its natural house rulerships.
</mission>

<KNOWLEDGE_ROUTING>
Use your knowledge of tropical astrology house meanings and planetary influences.
Format as a practical daily guide.
</KNOWLEDGE_ROUTING>

<transit_math>
{transit_data}
</transit_math>

<FORMAT>
Write extremely concise, 1 to 2 sentence summaries for each category:
**General:** (One sentence overall theme)
**Love & Relationships:** (One sentence romantic forecast)
**Career & Finance:** (One sentence professional forecast)
</FORMAT>"""

    try:
        return generate_content_with_fallback(prompt, knowledge_files=None)
    except Exception:
        return "**General:** The cosmic connection is resting.\n\n**Love & Relationships:** Try again later.\n\n**Career & Finance:** API limit reached."


# ── Vedic forecast ────────────────────────────────────────────────────────────

def generate_vedic_forecast(prof_json: str, timeframe: str, today_str: str) -> str:
    """
    Generate a Vedic (Moon-sign / Gochara) horoscope for Daily / Monthly / Yearly.
    today_str is passed in so the @st.cache_data TTL key works correctly.
    """
    prof = json.loads(prof_json)
    p_date = date.fromisoformat(prof["date"]) if isinstance(prof["date"], str) else prof["date"]
    p_time = datetime.strptime(prof["time"], "%H:%M").time() if isinstance(prof["time"], str) else prof["time"]
    tz = prof["tz"]

    jd_natal, _, _ = local_to_julian_day(p_date, p_time, tz)
    natal_moon_lon, _ = get_planet_longitude_and_speed(jd_natal, PLANETS["Moon"])
    natal_moon_sidx = sign_index_from_lon(natal_moon_lon)
    rashi = sign_name(natal_moon_sidx)

    # Build today's transit positions
    now_jd = swe.julday(*[int(x) for x in today_str.split("-")], 12.0)
    transit_lines = [f"GOCHARA (TRANSIT) FROM NATAL MOON ({today_str}):"]
    for pname, pid in PLANETS.items():
        t_lon, _ = get_planet_longitude_and_speed(now_jd, pid)
        t_sidx = sign_index_from_lon(t_lon)
        diff_houses = ((t_sidx - natal_moon_sidx) % 12) + 1
        transit_lines.append(
            f"  {pname} is transiting House {diff_houses} from Natal Moon (in {sign_name(t_sidx)})"
        )
    r_lon = get_rahu_longitude(now_jd)
    transit_lines.append(
        f"  Rahu is transiting House {((sign_index_from_lon(r_lon) - natal_moon_sidx) % 12) + 1} from Natal Moon"
    )
    transit_data = "\n".join(transit_lines)

    timeframe_rules = {
        "Daily":   "Focus heavily on the Moon's transit and fast-moving planets for immediate 24-hour events.",
        "Monthly": "Focus on the Sun, Mars, Venus, and Mercury transits to predict themes for the next 30 days.",
        "Yearly":  "Ignore the Moon. Focus EXCLUSIVELY on slow-moving transits of Jupiter, Saturn, and Rahu.",
    }

    # RAG: pull only the chunks relevant to this rashi + transit + timeframe.
    # Replaces the previous full-book injection (~254K tokens) with ~5K tokens.
    rag_query = f"gochara transit moon sign {rashi} {timeframe.lower()} forecast effects house"
    knowledge_ctx = rag_context(rag_query, ["bphs2.md"], k=10)

    prompt = f"""{GUARDRAILS}
<mission>
You are an elite Vedic Astrologer. Generate a highly accurate {timeframe} horoscope for a user
whose Moon Sign (Rashi) is {rashi}.
Read the mathematically exact Gochara (transit) data provided below.
{timeframe_rules[timeframe]}
</mission>

<KNOWLEDGE_CONTEXT>
{knowledge_ctx}
</KNOWLEDGE_CONTEXT>
<RULES>
Use only the Gochara/transit passages above for classical doctrine. Do not invent transit meanings outside them.
Anchor every claim to a specific transit line in transit_math.
</RULES>

<transit_math>
{transit_data}
</transit_math>

<FORMAT>
Write extremely concise, 1 to 2 sentence summaries for each category:
**General:** (One sentence overall theme)
**Love & Relationships:** (One sentence romantic forecast)
**Career & Finance:** (One sentence professional forecast)
</FORMAT>"""

    try:
        return generate_content_with_fallback(prompt, knowledge_files=None)
    except Exception:
        return "**General:** The cosmic connection is resting.\n\n**Love & Relationships:** Try again later.\n\n**Career & Finance:** API limit reached."


# ── Dashboard data ────────────────────────────────────────────────────────────

def fetch_dashboard_data(prof_json: str, today_str: str) -> dict:
    """
    Returns a dict with keys: GREETING, ENERGY, FOCUS, CAUTION, WINDOW, SUMMARY.
    today_str is passed in so the @st.cache_data TTL key works correctly.
    """
    prof = json.loads(prof_json)
    dos = generate_astrology_dossier(prof, False, compact=True)
    transits = get_gochara_overlay(prof)
    prompt = build_dashboard_data_prompt(dos, transits, prof["name"].split()[0])
    res = generate_content_with_fallback(
        prompt, knowledge_files=None,
        preferred_model="gemini-3.1-flash-lite-preview",
    )
    return safe_json(res, {
        "GREETING": f"Welcome back, {prof['name'].split()[0]}. The cosmic connection is catching its breath, but your tools are ready below.",
        "ENERGY":   "Mixed",
        "FOCUS":    "Routine",
        "CAUTION":  "Impulsivity",
        "WINDOW":   "Anytime",
        "SUMMARY":  "Balanced day. Stick to your routines.",
    })


# ── Daily tarot ───────────────────────────────────────────────────────────────

def fetch_daily_tarot(prof_json: str, today_str: str, daily_card: str, daily_state: str) -> dict:
    """
    Returns a dict with keys: MEANING, ACTION, MANTRA.
    today_str is passed in so the @st.cache_data TTL key works correctly.
    """
    base_prompt = build_daily_tarot_prompt(daily_card, daily_state)
    json_prompt = base_prompt + """
RESPOND ONLY IN VALID JSON FORMAT. NO MARKDOWN:
    {
        "MEANING": "What the card means today.",
        "ACTION":  "The best practical step to take.",
        "MANTRA":  "A short, powerful affirmation."
    }"""
    # RAG: only the chunks for this specific card + orientation, not the whole tguide.
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
    return safe_json(res, {
        "MEANING": "Trust the process unfolding today.",
        "ACTION":  "Observe before making any sudden moves.",
        "MANTRA":  "I am exactly where I need to be.",
    })
