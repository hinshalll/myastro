"""shared.astro.forecast — daily "Cosmic Weather" hero for the mobile Today tab.

FREE + cheap by design (cost rule): pure MATH + a pre-baked meaning LOOKUP.
NO live AI call. Moon-only, so it works at every birth-time tier — an unknown
birth time just uses a noon placeholder for the natal Moon (≤ ~6° drift; the
nakshatra may shift by one at worst, the forecast still computes fully).

State the day is mapped from (all Moon-based, no Lagna / birth time needed):
  • transiting Moon's nakshatra + sign today (computed at LOCAL NOON on the
    given date → deterministic, so identical profile+date is cacheable),
  • the transiting Moon's house counted from the natal Moon (Chandra Lagna), 1..12,
  • Tara Bala quality (favourable / neutral / challenging) via calculate_tara_bala.

Framing rule (blueprint §2): actionable + reflective, never hard fate claims.
Plain English everywhere; Sanskrit only inside `why` / `sanskrit`.
"""

from datetime import date as _date, time as _time, datetime
from zoneinfo import ZoneInfo

from shared.astro.constants import PLANETS
from shared.astro.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed,
    nakshatra_info, sign_index_from_lon, sign_name, calculate_tara_bala,
)

# Devanagari names for the transiting Moon's nakshatra (index 0..26), used only
# inside the `sanskrit` string. Plain-English meaning lives in the lookup below.
_NAK_DEVANAGARI = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु",
    "पुष्य", "आश्लेषा", "मघा", "पूर्वफाल्गुनी", "उत्तरफाल्गुनी", "हस्त", "चित्रा",
    "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूल", "पूर्वाषाढा", "उत्तराषाढा",
    "श्रवण", "धनिष्ठा", "शतभिषा", "पूर्वभाद्रपदा", "उत्तरभाद्रपदा", "रेवती",
]

# ── Pre-baked meaning table: 12 entries keyed by the Moon's house FROM the natal
#    Moon (Chandra house). Tara Bala quality then nudges the score + framing.
#    Easy to expand later (e.g. add a nakshatra layer). Each entry is plain data.
_CHANDRA_HOUSE: dict[int, dict] = {
    1:  {"vibe": "Tender",    "theme": "inward and sensitive", "base": 0.55,
         "mood": "Feelings sit close to the surface, so you may notice your moods more than usual.",
         "opportunity": "A good day for honest self-check-ins and gentle self-care.",
         "caution": "Try not to take passing comments too personally.",
         "action": "Move at your own pace and protect a little quiet time."},
    2:  {"vibe": "Grounded",  "theme": "practical and value-focused", "base": 0.52,
         "mood": "Attention drifts toward home, money and the people closest to you.",
         "opportunity": "Sorting finances or family matters can feel satisfying now.",
         "caution": "Watch a tendency to cling to comfort or overspend on treats.",
         "action": "Tidy one small practical thing you've been putting off."},
    3:  {"vibe": "Bold",      "theme": "energetic and expressive", "base": 0.70,
         "mood": "Courage and curiosity run high — you feel like reaching out and doing.",
         "opportunity": "Great for conversations, short trips and starting things.",
         "caution": "Channel the restlessness so it doesn't scatter your focus.",
         "action": "Make that call or send that message you've been sitting on."},
    4:  {"vibe": "Nesting",   "theme": "homeward and reflective", "base": 0.44,
         "mood": "You may want to retreat to familiar comforts and slow right down.",
         "opportunity": "Lovely for nesting, rest and time with family.",
         "caution": "Low energy or a wistful mood can creep in — that's normal today.",
         "action": "Give yourself permission to do less and recharge at home."},
    5:  {"vibe": "Playful",   "theme": "creative and warm-hearted", "base": 0.60,
         "mood": "The heart feels lighter and more expressive than usual.",
         "opportunity": "Good for creativity, romance, play and time with children.",
         "caution": "Enthusiasm can outrun follow-through, so don't over-promise.",
         "action": "Make space for one thing that's purely fun."},
    6:  {"vibe": "Driven",    "theme": "productive and resilient", "base": 0.62,
         "mood": "You feel capable of tackling chores and clearing obstacles.",
         "opportunity": "Strong for work, health routines and sorting out problems.",
         "caution": "Don't let a critical eye turn into stress or friction with others.",
         "action": "Knock out one task that's been nagging at you."},
    7:  {"vibe": "Magnetic",  "theme": "relational and social", "base": 0.72,
         "mood": "You're drawn toward others and conversation flows more easily.",
         "opportunity": "Excellent for partnerships, meetings and calm, open talk.",
         "caution": "Avoid leaning on others' approval to feel settled.",
         "action": "Have the warm conversation you've been meaning to have."},
    8:  {"vibe": "Deep",      "theme": "intense and introspective", "base": 0.34,
         "mood": "Things may feel heavier or more under-the-surface than usual.",
         "opportunity": "Useful for rest, research and quietly processing emotions.",
         "caution": "Steer clear of big risks, confrontations and impulsive moves.",
         "action": "Be kind to yourself and postpone anything high-stakes."},
    9:  {"vibe": "Restless",  "theme": "seeking and a little scattered", "base": 0.42,
         "mood": "The mind wanders toward bigger questions and far-off places.",
         "opportunity": "Good for learning, planning travel and broadening your view.",
         "caution": "Patience may be short, and small details can slip.",
         "action": "Read or plan something that expands your horizon."},
    10: {"vibe": "Sharp",     "theme": "ambitious and outward", "base": 0.74,
         "mood": "You feel switched-on and ready to be seen and to get things done.",
         "opportunity": "Strong for work, visible effort and steps toward your goals.",
         "caution": "Don't let drive tip into impatience with people who move slower.",
         "action": "Take one concrete step on something that matters for your future."},
    11: {"vibe": "Buoyant",   "theme": "hopeful and connected", "base": 0.82,
         "mood": "Optimism is high and you feel more sociable and supported.",
         "opportunity": "Excellent for networking, friends and small wins coming in.",
         "caution": "Enjoy it without over-committing to too many people at once.",
         "action": "Reconnect with someone who lifts your energy."},
    12: {"vibe": "Reflective", "theme": "quiet and restorative", "base": 0.38,
         "mood": "Energy turns inward — you may feel dreamy, tired or withdrawn.",
         "opportunity": "Ideal for rest, reflection, winding down and letting go.",
         "caution": "Not the day to force decisions or chase a packed schedule.",
         "action": "Wind down early and let yourself rest without guilt."},
}

# Tara Bala status (from calculate_tara_bala) → plain quality + score nudge + framing.
_TARA_QUALITY = {"Go": "favourable", "Stop": "challenging", "Caution": "neutral"}
_TARA_DELTA = {"favourable": 0.15, "neutral": 0.0, "challenging": -0.18}
_TARA_CLAUSE = {
    "favourable": "the day gently supports forward motion.",
    "neutral": "it's an even day — pace yourself and keep things steady.",
    "challenging": "it's a day to slow down and tend to things rather than push.",
}

_ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
            7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th"}


def _natal_moon_lon(profile: dict) -> float:
    """Natal Moon longitude. Unknown birth time → noon placeholder (Moon-based
    parts stay usable; this matches the kundli _profile_to_birthdata fallback)."""
    d = profile["date"]
    d = _date.fromisoformat(d) if isinstance(d, str) else d
    raw_t = profile.get("time")
    if raw_t in (None, ""):
        t = _time(12, 0)
    elif isinstance(raw_t, str):
        parts = raw_t.split(":")
        t = _time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    else:
        t = raw_t
    jd, _, _ = local_to_julian_day(d, t, profile["tz"])
    lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
    return lon


def _transit_moon_lon(on_date: _date, tz: str) -> float:
    """Transiting Moon at LOCAL NOON on the date → deterministic & cacheable."""
    jd, _, _ = local_to_julian_day(on_date, _time(12, 0), tz)
    lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
    return lon


def daily_moon_forecast(profile: dict, on_date=None) -> dict:
    """Display-ready daily "Cosmic Weather" forecast. Pure math + lookup, no AI.

    `on_date`: None → today (in the profile's tz); else a date or "YYYY-MM-DD".
    Same { profile } contract as /kundli/compute; works at every birth-time tier.
    """
    tz = profile["tz"]
    if on_date is None:
        on_date = datetime.now(ZoneInfo(tz)).date()
    elif isinstance(on_date, str):
        on_date = _date.fromisoformat(on_date)

    natal = _natal_moon_lon(profile)
    transit = _transit_moon_lon(on_date, tz)

    nak, _nak_lord, _pada = nakshatra_info(transit)
    t_sidx = sign_index_from_lon(transit)
    n_sidx = sign_index_from_lon(natal)
    house = ((t_sidx - n_sidx) % 12) + 1

    ns = 360.0 / 27
    nak_idx = int((transit % 360) // ns)
    natal_nak_idx = int((natal % 360) // ns)
    tara_value = ((nak_idx - natal_nak_idx) % 9) + 1

    tara = calculate_tara_bala(natal, transit)
    quality = _TARA_QUALITY.get(tara["status"], "neutral")

    m = _CHANDRA_HOUSE[house]
    score = round(min(0.98, max(0.05, m["base"] + _TARA_DELTA[quality])), 2)

    sign = sign_name(t_sidx)
    why = (f"Today the Moon moves through {nak} ({sign}), the {_ORDINAL[house]} house "
           f"from your birth Moon — a time that classically feels {m['theme']} for the mind. "
           f"Tara Bala is {tara['tara']} ({quality}), so {_TARA_CLAUSE[quality]}")
    sanskrit = f"चन्द्रः {_NAK_DEVANAGARI[nak_idx]}-नक्षत्रे"

    return {
        "date": on_date.isoformat(),
        "vibe_word": m["vibe"],
        "vibe_score": score,
        "mood": m["mood"],
        "opportunity": m["opportunity"],
        "caution": m["caution"],
        "action": m["action"],
        "why": why,
        "sanskrit": sanskrit,
        # Everything the lookup keys on → identical states share this key (cacheable).
        "astro_state_key": f"ch{house}-tara{tara_value}-nak{nak_idx}",
        # Transparency / debug fields (cheap, Moon-based, safe at any tier)
        "moon_nakshatra": nak,
        "moon_sign": sign,
        "chandra_house": house,
        "tara": tara["tara"],
        "tara_quality": quality,
    }
