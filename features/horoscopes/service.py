"""features.horoscopes.service — pure-Python forecast generators.

Replaces the old shared.ai/forecasts.py:generate_western_forecast / generate_vedic_forecast
functions. They've been moved here so horoscope-related code lives in one place.

No Streamlit. The 24-hour caching wrapper lives in ui_streamlit/cache.py for now;
the FastAPI side caches via Redis/dict (not implemented yet).
"""

import json
from datetime import datetime, date
from zoneinfo import ZoneInfo

from shared.astro import ephemeris
from shared.astro.constants import PLANETS
from shared.astro.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed,
    sign_index_from_lon, sign_name, get_rahu_longitude,
)
from shared.ai.gemini_client import generate_content_with_fallback
from shared.ai.knowledge import rag_context

from features.horoscopes.prompts import build_western_prompt, build_vedic_prompt


_FALLBACK = (
    "**General:** The cosmic connection is resting.\n\n"
    "**Love & Relationships:** Try again later.\n\n"
    "**Career & Finance:** API limit reached."
)


# ── Western forecast (sun sign) ──────────────────────────────────────────────

def generate_western_forecast(sun_sign: str, today_str: str) -> str:
    """Daily Western (tropical) horoscope. `today_str` is part of the cache key."""
    now_jd = ephemeris.julday(*[int(x) for x in today_str.split("-")], 12.0)

    lines = [f"TODAY'S TROPICAL TRANSITS ({today_str}):"]
    for pname, pid in PLANETS.items():
        lon, _ = get_planet_longitude_and_speed(now_jd, pid)
        lines.append(f"  {pname} at {lon:.2f}° ({sign_name(sign_index_from_lon(lon))})")
    r_lon = get_rahu_longitude(now_jd)
    lines.append(f"  Rahu at {r_lon:.2f}° ({sign_name(sign_index_from_lon(r_lon))})")

    prompt = build_western_prompt(sun_sign, today_str, "\n".join(lines))
    try:
        return generate_content_with_fallback(prompt, knowledge_files=None)
    except Exception:
        return _FALLBACK


# ── Vedic forecast (moon sign, 3 timeframes) ─────────────────────────────────

def generate_vedic_forecast(prof_json: str, timeframe: str, today_str: str) -> str:
    """
    Vedic moon-sign horoscope. timeframe: "Daily" / "Monthly" / "Yearly".
    `today_str` is part of the cache key.
    """
    prof = json.loads(prof_json)
    p_date = date.fromisoformat(prof["date"]) if isinstance(prof["date"], str) else prof["date"]
    p_time = datetime.strptime(prof["time"], "%H:%M").time() if isinstance(prof["time"], str) else prof["time"]
    tz = prof["tz"]

    jd_natal, _, _ = local_to_julian_day(p_date, p_time, tz)
    natal_moon_lon, _ = get_planet_longitude_and_speed(jd_natal, PLANETS["Moon"])
    natal_moon_sidx = sign_index_from_lon(natal_moon_lon)
    rashi = sign_name(natal_moon_sidx)

    now_jd = ephemeris.julday(*[int(x) for x in today_str.split("-")], 12.0)
    lines = [f"GOCHARA (TRANSIT) FROM NATAL MOON ({today_str}):"]
    for pname, pid in PLANETS.items():
        t_lon, _ = get_planet_longitude_and_speed(now_jd, pid)
        t_sidx = sign_index_from_lon(t_lon)
        house = ((t_sidx - natal_moon_sidx) % 12) + 1
        lines.append(
            f"  {pname} is transiting House {house} from Natal Moon (in {sign_name(t_sidx)})"
        )
    r_lon = get_rahu_longitude(now_jd)
    lines.append(
        f"  Rahu is transiting House "
        f"{((sign_index_from_lon(r_lon) - natal_moon_sidx) % 12) + 1} from Natal Moon"
    )
    transit_data = "\n".join(lines)

    # RAG: only the chunks relevant to this rashi + transit + timeframe.
    rag_query = f"gochara transit moon sign {rashi} {timeframe.lower()} forecast effects house"
    knowledge_ctx = rag_context(rag_query, ["bphs2.md"], k=10)

    prompt = build_vedic_prompt(rashi, timeframe, transit_data, knowledge_ctx)
    try:
        return generate_content_with_fallback(prompt, knowledge_files=None)
    except Exception:
        return _FALLBACK
