"""shared.astro.retrospect — "The Proof / Why did that happen?" math.

Given a PAST date, explain in warm plain English which Vimshottari
Mahadasha/Antardasha were running then and which slow, era-defining transits
(Saturn, Jupiter, the Rahu/Ketu axis) were touching the birth Moon. The
trust-builder: it lets someone test the system against their own past.

FREE + cheap by design (cost rule): pure MATH + a pre-baked classical LOOKUP.
NO live AI call, NO new dependencies. All calc goes through the ephemeris
adapter (never swe/skyfield directly).

Everything here is standard Parashari doctrine, classically sourced:
  • Vimshottari dasha-lord natures — Brihat Parashara Hora Shastra. The 9 lords'
    significations are the universally-taught set (Sun=self/authority, Moon=mind/
    emotion, Mars=drive/courage, Rahu=worldly ambition/disruption, Jupiter=growth/
    wisdom/fortune, Saturn=discipline/limits/maturing, Mercury=intellect/commerce,
    Ketu=detachment/endings, Venus=love/comfort/relationships).
  • Sade Sati = Saturn transiting the 12th, 1st and 2nd house FROM the natal Moon
    (the 7.5-yr maturing passage); the 2.5-yr "small panoti" = Saturn in the 4th
    (Kantaka) or 8th (Ashtama) from the Moon. (BPHS / Phaladeepika tradition,
    cross-checked drikpanchang / astrosage / mpanchang.)
  • Jupiter's transit from the Moon is classically supportive in the 2, 5, 7, 9, 11
    houses, and quieter elsewhere (the Guru-Bala / Jupiter-gochara doctrine).

Birth-time tiers: the dasha needs the natal Moon, which needs a birth time for
full precision. An unknown birth time falls back to a NOON placeholder (the Moon
can drift ≤ ~6°, so dasha boundaries can shift by a few months) — we compute it
anyway and attach a plain `precision_note` so the reading is honest.

Framing rule (blueprint §2): warm, plain, beginner-friendly. No jargon in the
main lines; Sanskrit/technical terms live ONLY in `why` / `sanskrit`. Gentle
guidance about a felt texture of time — never a fated verdict.
"""

from datetime import date as _date, time as _time, datetime
from zoneinfo import ZoneInfo

from shared.astro import ephemeris
from shared.astro.constants import PLANETS
from shared.astro.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed, get_rahu_longitude,
    sign_index_from_lon, sign_name, nakshatra_info, calculate_tara_bala,
    build_vimshottari_timeline,
)


# ── The 9 Vimshottari lords → plain, warm theme + a keyword + the Sanskrit name.
#    Plain English in `theme`; the classical name stays in `sanskrit`.
_DASHA_LORD: dict[str, dict] = {
    "Sun":     {"word": "self & standing",   "sanskrit": "सूर्य",
                "theme": "stepping into your own authority — identity, recognition, and where you stand"},
    "Moon":    {"word": "heart & home",      "sanskrit": "चन्द्र",
                "theme": "feelings, home and care running close to the surface — a softer, more inward chapter"},
    "Mars":    {"word": "drive & action",    "sanskrit": "मंगल",
                "theme": "energy, courage and push — a chapter of doing, fighting for things, and sometimes friction"},
    "Rahu":    {"word": "hunger & change",   "sanskrit": "राहु",
                "theme": "big worldly wanting and sudden turns — ambition, the unfamiliar, and restlessness"},
    "Jupiter": {"word": "growth & meaning",  "sanskrit": "गुरु",
                "theme": "growth, learning and good fortune — a broadening, hopeful, meaning-seeking chapter"},
    "Saturn":  {"word": "work & maturing",   "sanskrit": "शनि",
                "theme": "discipline, limits and slow maturing — a heavier chapter that asks for patience and builds something lasting"},
    "Mercury": {"word": "mind & exchange",   "sanskrit": "बुध",
                "theme": "thinking, talking, learning and dealings — a busy, mental, communicative chapter"},
    "Ketu":    {"word": "letting go",        "sanskrit": "केतु",
                "theme": "detachment and endings — a chapter that quietly strips things back and turns you inward"},
    "Venus":   {"word": "love & comfort",    "sanskrit": "शुक्र",
                "theme": "relationships, pleasure and ease — a warmer chapter drawn to love, beauty and comfort"},
}


def _house_from(sign_idx: int, from_sign_idx: int) -> int:
    """1..12 house of `sign_idx` counted from `from_sign_idx` (whole-sign)."""
    return ((sign_idx - from_sign_idx) % 12) + 1


def _saturn_from_moon(saturn_sign: int, moon_sign: int) -> dict | None:
    """Classify Saturn's transit relative to the natal Moon. Returns a heads-up
    dict for the era-defining passages (Sade Sati / Dhaiya), else None."""
    h = _house_from(saturn_sign, moon_sign)
    if h in (12, 1, 2):
        phase = {12: "the opening", 1: "the peak", 2: "the closing"}[h]
        return {
            "what": "Saturn passing over your birth Moon",
            "meaning": f"a slow, weighty, maturing stretch — {phase} of Sade Sati, "
                       "the seven-and-a-half-year passage that tests and matures you",
            "key": "sade_sati", "house": h, "sanskrit": "साढ़े साती",
        }
    if h == 4:
        return {
            "what": "Saturn sitting in the fourth from your birth Moon",
            "meaning": "a two-and-a-half-year pull on home, peace of mind and inner comfort "
                       "(the 'small Saturn', Kantaka)",
            "key": "kantaka", "house": h, "sanskrit": "कंटक शनि",
        }
    if h == 8:
        return {
            "what": "Saturn in the eighth from your birth Moon",
            "meaning": "a two-and-a-half-year stretch of deep change and slowing down "
                       "(Ashtama Shani, the other 'small Saturn')",
            "key": "ashtama", "house": h, "sanskrit": "अष्टम शनि",
        }
    return None


def _jupiter_from_moon(jupiter_sign: int, moon_sign: int) -> dict | None:
    """Classify Jupiter's transit from the natal Moon. Returns a heads-up dict
    when it's in one of its classically supportive houses, else None."""
    h = _house_from(jupiter_sign, moon_sign)
    if h in (2, 5, 7, 9, 11):
        return {
            "what": "Jupiter in a supportive angle to your birth Moon",
            "meaning": "a broadening, hopeful current underneath — the year's most "
                       "growth-friendly transit (favourable Guru gochara)",
            "key": "jupiter_good", "house": h, "sanskrit": "गुरु बल",
        }
    return None


def _node_from_moon(rahu_sign: int, moon_sign: int) -> dict | None:
    """Rahu/Ketu axis over the natal Moon → an unsettled, fated-feeling stretch."""
    h_rahu = _house_from(rahu_sign, moon_sign)
    ketu_sign = (rahu_sign + 6) % 12
    h_ketu = _house_from(ketu_sign, moon_sign)
    if h_rahu == 1:
        return {"what": "Rahu over your birth Moon",
                "meaning": "a restless, hungry, slightly unsettled stretch where the mind "
                           "reaches for more than usual", "key": "rahu_moon", "sanskrit": "राहु"}
    if h_ketu == 1:
        return {"what": "Ketu over your birth Moon",
                "meaning": "a withdrawn, detached, inward stretch where things quietly fall away",
                "key": "ketu_moon", "sanskrit": "केतु"}
    return None


def _birth_moon_and_dt(profile: dict):
    """(natal Moon longitude, tz-aware birth datetime, birth-time-known?). Unknown
    birth time → noon placeholder (Moon-based dasha stays usable, lower precision)."""
    d = profile["date"]
    d = _date.fromisoformat(d) if isinstance(d, str) else d
    raw_t = profile.get("time")
    known = raw_t not in (None, "")
    if not known:
        t = _time(12, 0)
    elif isinstance(raw_t, str):
        parts = raw_t.split(":")
        t = _time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    else:
        t = raw_t
    jd, dt_local, _ = local_to_julian_day(d, t, profile["tz"])
    moon_lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
    return moon_lon, dt_local, known


def explain_past_date(profile: dict, on_date, event: str | None = None) -> dict:
    """Warm plain-English read of a PAST date: the dasha chapter that was running
    + the slow, era-defining transits over the birth Moon. Pure math + lookup, no
    AI. `profile` uses the /kundli/compute shape; `on_date` is a date or
    "YYYY-MM-DD". `event` (optional) is the user's own words for what happened,
    echoed back. Deterministic for the same profile + date.
    """
    tz = profile["tz"]
    if isinstance(on_date, str):
        on_date = _date.fromisoformat(on_date)

    moon_lon, dt_birth, time_known = _birth_moon_and_dt(profile)
    moon_sign = sign_index_from_lon(moon_lon)

    # The target moment: local noon on that past day, in the profile's tz (same
    # tz-aware frame as dt_birth, so build_vimshottari_timeline's comparisons hold).
    target = datetime.combine(on_date, _time(12, 0)).replace(tzinfo=ZoneInfo(tz))

    if target < dt_birth:
        return {
            "date": on_date.isoformat(),
            "error": "before_birth",
            "story": "That date is before your birth, so there's no chart to read for it yet.",
        }

    # 1. The dasha chapter running then (Mahadasha / Antardasha).
    di = build_vimshottari_timeline(dt_birth, moon_lon, target)
    md, ad = di["current_md"], di["current_ad"]
    md_info = _DASHA_LORD.get(md, {"word": md, "theme": md, "sanskrit": md})
    ad_info = _DASHA_LORD.get(ad, {"word": ad, "theme": ad, "sanskrit": ad})

    running = {
        "mahadasha": md,
        "antardasha": ad,
        "since": di["ad_start"].strftime("%b %Y"),
        "until": di["ad_end"].strftime("%b %Y"),
        "md_since": di["md_start"].strftime("%b %Y"),
        "md_until": di["md_end"].strftime("%b %Y"),
    }

    # 2. The slow, era-defining transits on that date (Saturn, Jupiter, the nodes).
    jd_then = ephemeris.julday(target.astimezone(ZoneInfo("UTC")).year,
                               target.astimezone(ZoneInfo("UTC")).month,
                               target.astimezone(ZoneInfo("UTC")).day, 12.0)
    sat_lon, _ = get_planet_longitude_and_speed(jd_then, PLANETS["Saturn"])
    jup_lon, _ = get_planet_longitude_and_speed(jd_then, PLANETS["Jupiter"])
    rahu_lon = get_rahu_longitude(jd_then)
    moon_then, _ = get_planet_longitude_and_speed(jd_then, PLANETS["Moon"])

    transits = []
    for hit in (
        _saturn_from_moon(sign_index_from_lon(sat_lon), moon_sign),
        _jupiter_from_moon(sign_index_from_lon(jup_lon), moon_sign),
        _node_from_moon(sign_index_from_lon(rahu_lon), moon_sign),
    ):
        if hit:
            transits.append({"what": hit["what"], "meaning": hit["meaning"]})

    # The day's own Moon texture (Tara Bala) — the fine grain on top of the era.
    nak, _lord, _pada = nakshatra_info(moon_then)
    tara = calculate_tara_bala(moon_lon, moon_then)
    tara_q = {"Go": "an easy", "Stop": "a challenging", "Caution": "a mixed"}.get(tara["status"], "a mixed")

    # 3. Stitch into a warm story. (Build the day plainly — %-d isn't portable.)
    when = f"{on_date.day} {on_date.strftime('%B %Y')}"

    if md == ad:
        chapter = f"you were in your {md_info['word']} chapter ({md} period) — {md_info['theme']}"
    else:
        chapter = (f"you were in your {md_info['word']} chapter ({md} period), in its "
                   f"{ad_info['word']} sub-stretch ({ad}) — {md_info['theme']}, "
                   f"coloured by {ad_info['theme']}")

    story_bits = [f"Around {when}, {chapter}."]
    if transits:
        t_clause = "; and ".join(t["meaning"] for t in transits)
        lead = transits[0]["what"]
        story_bits.append(f"At the same time, {lead} meant {t_clause}.")
    story_bits.append("That's the backdrop you were living against — take it as a gentle mirror "
                      "on the texture of that time, not a verdict on it.")
    story = " ".join(story_bits)

    headline = f"Back then you were in a {md}" + (f"–{ad}" if ad != md else "") + " chapter"
    if transits:
        headline += f", with {transits[0]['what']}"
    headline += "."

    why = (f"On {when}, the Vimshottari dasha running was {md} Mahadasha / {ad} Antardasha "
           f"({running['since']} → {running['until']}). The slow transits: "
           + (", ".join(f"{t['what']} ({t['meaning']})" for t in transits) if transits
              else "no major slow-transit passage over the birth Moon")
           + f". The day's Moon sat in {nak} — {tara_q} day-star (Tara Bala) from your birth Moon.")

    sanskrit = f"{md_info['sanskrit']}-{ad_info['sanskrit']} दशा"
    if transits:
        sanskrit += " · " + " · ".join(
            h["sanskrit"] for h in (
                _saturn_from_moon(sign_index_from_lon(sat_lon), moon_sign),
                _jupiter_from_moon(sign_index_from_lon(jup_lon), moon_sign),
                _node_from_moon(sign_index_from_lon(rahu_lon), moon_sign),
            ) if h
        )

    precision_note = None
    if not time_known:
        precision_note = ("Your birth time isn't set, so this uses a midday estimate — the "
                          "chapter dates can be off by a few months. Add your exact birth "
                          "time for a precise read.")

    return {
        "date": on_date.isoformat(),
        "headline": headline,
        "story": story,
        "running": running,
        "transits": transits,
        "event": event,
        "why": why,
        "sanskrit": sanskrit,
        "precision_note": precision_note,
        # Debug / transparency (cheap, safe).
        "moon_nakshatra_that_day": nak,
        "tara_quality": tara_q.strip().split()[-1],
    }
