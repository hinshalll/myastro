"""
ui_streamlit/helpers.py

Small utility functions used across multiple page files.
No Streamlit imports here — pure Python only.
FastAPI can also import these freely.
"""

import json
from datetime import datetime, date
from zoneinfo import ZoneInfo

from shared.astro.constants import PLANETS
from shared.astro.astro_calc import (
    local_to_julian_day,
    get_planet_longitude_and_speed,
)


def get_local_today(tz_string: str = "Asia/Kolkata") -> date:
    """Return today's date in the given timezone."""
    try:
        return datetime.now(ZoneInfo(tz_string)).date()
    except Exception:
        return datetime.now(ZoneInfo("Asia/Kolkata")).date()


def get_moon_lon_from_profile(profile: dict) -> float:
    """Return the Moon longitude (float) for a stored profile dict."""
    d = date.fromisoformat(profile["date"]) if isinstance(profile["date"], str) else profile["date"]
    t = datetime.strptime(profile["time"], "%H:%M").time() if isinstance(profile["time"], str) else profile["time"]
    jd, _, __ = local_to_julian_day(d, t, profile["tz"])
    lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
    return lon


def profile_cache_key(prof: dict) -> str:
    return f"{prof['name']}|{prof['date']}|{prof['time']}|{prof.get('tz', 'Asia/Kolkata')}"


def safe_json(raw: str, fallback: dict) -> dict:
    """Parse a JSON string from an AI model, returning fallback on any error."""
    try:
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return fallback

# get_filename moved to features/tarot/constants.py as card_image_filename.
# Re-exported here for backward compatibility (dashboard/view.py imports from here).
from features.tarot.constants import card_image_filename as get_filename