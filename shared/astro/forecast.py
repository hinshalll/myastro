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

from datetime import date as _date, time as _time, datetime, timedelta
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
#
#    AUSPICIOUSNESS follows the classical Chandra Gochara rule (Phaladeepika /
#    Brihat Jataka): the Moon's transit is FAVOURABLE in the 1, 3, 6, 7, 10, 11
#    houses from the natal Moon, and CHALLENGING in the 2, 4, 5, 8, 9, 12.
#    (Cross-checked against multiple classical sources — see commit message.)
#    `base` scores reflect that: favourable ≈ 0.60–0.84, challenging ≈ 0.32–0.46,
#    with the 11th strongest and the 8th hardest. Each house keeps its own DOMAIN
#    flavour (self, money, courage, home, …) in plain, warm English.
_CHANDRA_HOUSE: dict[int, dict] = {
    1:  {"vibe": "Settled",   "theme": "steady and self-contained", "base": 0.62,
         "mood": "You feel a little more at home in yourself today — steadier, and comfortable in your own skin.",
         "opportunity": "A good day to take care of yourself and move at an easy, unhurried pace.",
         "caution": "It's easy to get wrapped up in your own world — stay in touch with people too.",
         "action": "Do one small, kind thing just for you."},
    2:  {"vibe": "Guarded",   "theme": "focused on money, home and words", "base": 0.42,
         "mood": "Thoughts circle around money, home and close family, and feelings can run a little tight.",
         "opportunity": "Careful, steady handling of finances or family matters works better than anything bold.",
         "caution": "Words can land harder than you mean, and spending can feel reactive — go gently on both.",
         "action": "Pause before reacting; calmly sort one small money or home detail."},
    3:  {"vibe": "Bold",      "theme": "courageous and outgoing", "base": 0.72,
         "mood": "Courage and energy run high — you feel like reaching out and getting things moving.",
         "opportunity": "Great for conversations, reaching out, short trips and starting things.",
         "caution": "So much momentum can scatter — point it at just one or two things.",
         "action": "Make that call or send that message you've been sitting on."},
    4:  {"vibe": "Tender",    "theme": "homeward and soft-hearted", "base": 0.44,
         "mood": "The heart tugs toward home and comfort, and you may feel more sensitive than usual.",
         "opportunity": "Lovely for rest, nesting and quiet time with family.",
         "caution": "A wistful or low mood can drift in — that's the day, not you; let it pass.",
         "action": "Give yourself permission to slow down and be at home."},
    5:  {"vibe": "Restless",  "theme": "stimulation-seeking and a touch unsettled", "base": 0.40,
         "mood": "The mind craves a little play, romance or attention, but can feel restless underneath.",
         "opportunity": "Fine for light creativity and enjoying yourself — as long as you keep it low-stakes.",
         "caution": "Not the steadiest day — skip big gambles and don't chase recognition.",
         "action": "Pour the buzzy energy into something playful but harmless."},
    6:  {"vibe": "Capable",   "theme": "productive and good at clearing problems", "base": 0.66,
         "mood": "You feel ready to face problems head-on and clear what's been in your way.",
         "opportunity": "Strong for work, health routines, and getting the upper hand on a nagging issue.",
         "caution": "Don't let a sharp, problem-hunting mood turn into friction with people.",
         "action": "Knock out the task or obstacle that's been nagging at you."},
    7:  {"vibe": "Warm",      "theme": "relational and easy with others", "base": 0.74,
         "mood": "You're drawn toward others, and conversation and connection flow more easily.",
         "opportunity": "Excellent for partnerships, meeting people and warm, open talk.",
         "caution": "Lovely as company is, don't lean on others' approval to feel okay.",
         "action": "Have the warm conversation you've been meaning to have."},
    8:  {"vibe": "Deep",      "theme": "deep, inward and a little heavy", "base": 0.32,
         "mood": "Things can feel heavier and more under-the-surface — emotions run deep today.",
         "opportunity": "Useful for rest, quiet research and gently processing what's beneath.",
         "caution": "Steer clear of big risks, confrontations and impulsive moves — worry can mislead.",
         "action": "Be gentle with yourself and postpone anything high-stakes."},
    9:  {"vibe": "Wandering", "theme": "searching and a little scattered", "base": 0.44,
         "mood": "The mind drifts to bigger questions and far-off places, and the here-and-now can feel dull.",
         "opportunity": "Good for reading, planning ahead and zooming out on your life.",
         "caution": "Patience is short and small details slip — and you may bristle at people in charge.",
         "action": "Feed the wandering mind with something that widens your view."},
    10: {"vibe": "Driven",    "theme": "ambitious and switched-on", "base": 0.76,
         "mood": "You feel switched-on and ready to be seen and to get real things done.",
         "opportunity": "Strong for work, visible effort and steps toward your goals.",
         "caution": "Don't let the drive tip into impatience with people who move slower.",
         "action": "Take one concrete step on something that matters for your future."},
    11: {"vibe": "Buoyant",   "theme": "hopeful, social and in flow", "base": 0.84,
         "mood": "Optimism is high and you feel more sociable, supported and in flow.",
         "opportunity": "One of the best days for friends, networking and small wins landing.",
         "caution": "Enjoy it without over-committing to everyone at once.",
         "action": "Reconnect with someone who lifts your energy."},
    12: {"vibe": "Quiet",     "theme": "quiet, inward and restorative", "base": 0.36,
         "mood": "Energy turns inward — you may feel dreamy, tired or a little withdrawn.",
         "opportunity": "Ideal for rest, winding down, reflection and quietly letting go.",
         "caution": "Not a day to force decisions or pack the schedule; watch your energy and spending.",
         "action": "Wind down early and let yourself rest without guilt."},
}

# Tara Bala status (from calculate_tara_bala) → plain quality + score nudge + framing.
_TARA_QUALITY = {"Go": "favourable", "Stop": "challenging", "Caution": "neutral"}
_TARA_DELTA = {"favourable": 0.15, "neutral": 0.0, "challenging": -0.18}
_TARA_CLAUSE = {
    "favourable": "The day's natural rhythm is with you, so progress comes a little more easily.",
    "neutral": "There's no strong pull either way, so set your own steady pace.",
    "challenging": "It leans more toward tending and resting than pushing hard.",
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
    why = (f"Right now the Moon is passing through {sign} (its star, {nak}). Counted from the "
           f"sign your Moon was in when you were born, that's the {_ORDINAL[house]} step around "
           f"the circle — a stretch that traditionally feels {m['theme']}. {_TARA_CLAUSE[quality]}")
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


def _band(score: float) -> str:
    """Coarse good / neutral / difficult band for the 7-day rail's colour."""
    if score >= 0.60:
        return "good"
    if score < 0.45:
        return "difficult"
    return "neutral"


def weekly_moon_forecast(profile: dict, start_date=None, days: int = 7) -> dict:
    """`days` consecutive daily forecasts from start_date for the Today tab's
    "next N days" rail. Each entry is the full daily_moon_forecast plus a coarse
    `band` (good/neutral/difficult) for the rail colour and an `is_today` flag.

    Pure math + lookup, no AI. Same { profile } contract as daily_moon_forecast;
    works at every birth-time tier. `start_date`: None → today (profile's tz).
    """
    tz = profile["tz"]
    today = datetime.now(ZoneInfo(tz)).date()
    if start_date is None:
        start_date = today
    elif isinstance(start_date, str):
        start_date = _date.fromisoformat(start_date)

    out = []
    for i in range(max(1, days)):
        d = start_date + timedelta(days=i)
        f = daily_moon_forecast(profile, d)
        f["band"] = _band(f["vibe_score"])
        f["is_today"] = (d == today)
        out.append(f)
    return {"start_date": start_date.isoformat(), "days": out}
