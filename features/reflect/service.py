"""features.reflect.service — the big-picture reflective readings.

  • purpose       — Your Purpose: a warm soul/career blueprint from the Atmakaraka
    (soul planet), the 10th house + its lord (career/karma), the D10 Dashamsha
    (career chart) and the dharma trikona (1/5/9). Cached-friendly: deterministic
    per profile.
  • year_in_review — Cosmic Wrapped: a shareable yearly recap from the Varshaphala
    (Tajik annual chart — Muntha + solar return), the dasha chapter that ran across
    the year, and the year's slow, era-defining transits.

All chart math goes through shared.astro.kundli (compute_chart / compute_varshaphala,
which themselves go through the ephemeris adapter); the slow-transit reads reuse
shared.astro.retrospect. This layer extracts chart fields and applies the static,
classically-sourced meaning tables in meanings.py. No live AI (cost rule).
"""
from __future__ import annotations

from datetime import date as _date, time as _time, datetime
from zoneinfo import ZoneInfo

from features.reflect import meanings as M


def _build_chart(profile: dict):
    """A profile (kundli/compute shape) → a full KundliChart. Needs lat/lon for
    houses/Lagna/D10; an unknown birth time falls back to noon (the time-sensitive
    parts — houses, Muntha — get a precision note). Returns (chart, time_known)."""
    from shared.astro.kundli import BirthData, compute_chart

    if profile.get("lat") in (None, "") or profile.get("lon") in (None, ""):
        raise ValueError("birthplace_required")

    raw_t = profile.get("time")
    time_known = raw_t not in (None, "") and bool(profile.get("birth_time_known", True))
    if not time_known:
        t = _time(12, 0)
    elif isinstance(raw_t, str):
        parts = raw_t.split(":")
        t = _time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    else:
        t = raw_t

    d = profile["date"]
    bd = BirthData(
        name=profile.get("name", "You"),
        date=_date.fromisoformat(d) if isinstance(d, str) else d,
        time=t, place=profile.get("place", ""),
        lat=float(profile["lat"]), lon=float(profile["lon"]),
        tz=profile["tz"], gender=profile.get("gender", "M"),
        exact_time=bool(profile.get("exact_time", False)),
        birth_time_known=time_known,
    )
    return compute_chart(bd), time_known


# ─────────────────────────────────────────────────────────────────────────────
# Your Purpose — soul / career blueprint
# ─────────────────────────────────────────────────────────────────────────────

def purpose(profile: dict) -> dict:
    chart, time_known = _build_chart(profile)

    # 1. Soul planet (Atmakaraka) — the soul's strongest desire + the karma to resolve.
    ak = chart.chara_karakas.atmakaraka
    ak_pos = chart.planets[ak]
    ak_info = M.ATMAKARAKA.get(ak, {"theme": ak, "verb": ak, "sanskrit": ak})
    soul = {
        "planet": ak,
        "theme": ak_info["theme"],
        "sign": ak_pos.sign,
        "house": ak_pos.house,
        "house_theme": M.HOUSE_THROUGH.get(ak_pos.house, ""),
        "sanskrit": ak_info["sanskrit"],
    }

    # 2. The calling — the 10th house (karma/career) + where its lord sits.
    h10 = chart.houses[10]
    lord10 = h10.sign_lord
    lord10_house = chart.planets[lord10].house if lord10 in chart.planets else None
    calling = {
        "tenth_sign": h10.sign,
        "tenth_lord": lord10,
        "tenth_occupants": h10.occupants,
        "lord_in_house": lord10_house,
        "line": (
            f"Your work in the world tends to be carried {M.SIGN_STYLE.get(h10.sign, '').lstrip()} "
            f"({h10.sign} on your 10th), and it's built through "
            f"{M.HOUSE_THROUGH.get(lord10_house, 'your everyday life') if lord10_house else 'your everyday life'} "
            f"— that's where your career-energy naturally flows."
        ),
    }

    # 3. The career chart (D10 Dashamsha) — the flavour you lead with at work.
    from shared.astro.constants import SIGNS
    d10 = chart.divisional_charts.get(10)
    career_chart = None
    if d10:
        d10_sign = SIGNS[d10.lagna_sign_index]
        career_chart = {
            "d10_lagna": d10_sign,
            "line": (f"In the deeper picture of career (the Dashamsha chart), you tend to "
                     f"meet your work {M.SIGN_STYLE.get(d10_sign, '').lstrip()}."),
        }

    # 4. Dharma trikona (1/5/9) — where your sense of meaning lives.
    trikona = {h: chart.houses[h].occupants for h in (1, 5, 9)}
    filled = [h for h in (1, 5, 9) if trikona[h]]
    if filled:
        areas = " and ".join(M.HOUSE_THROUGH[h].split(",")[0] for h in filled)
        dharma_line = (f"Your sense of meaning gathers around {areas} — that's your dharma "
                       "triangle (the 1st, 5th and 9th), the part of life that feels purposeful.")
    else:
        dharma_line = ("Your sense of meaning isn't tied to one fixed area — it's something you "
                       "grow into across the 1st, 5th and 9th houses, your dharma triangle.")
    dharma = {"line": dharma_line, "occupants": trikona}

    headline = (f"You're here to {ak_info['verb']}, and to express it through "
                f"{M.HOUSE_THROUGH.get(ak_pos.house, 'your life')}.")
    summary = (f"At your core, the soul wants {ak_info['theme'].split('—')[0].strip()}. "
               f"{calling['line']} {dharma_line} Take this as a compass, not a cage — "
               "a sense of which way your life naturally wants to grow.")

    why = (f"Soul planet (Atmakaraka): {ak} in {ak_pos.sign}, house {ak_pos.house}. "
           f"Career: 10th house {h10.sign}, its lord {lord10} in house {lord10_house}. "
           + (f"Dashamsha (D10) Lagna in {SIGNS[d10.lagna_sign_index]}. " if d10 else "")
           + f"Dharma trikona (1/5/9) occupants: "
           + ", ".join(f"H{h}: {', '.join(trikona[h]) or '—'}" for h in (1, 5, 9)) + ".")

    sanskrit = f"{ak_info['sanskrit']} · दशम भाव · धर्म त्रिकोण"

    precision_note = None
    if not time_known:
        precision_note = ("Your birth time isn't set, so the house-based parts (your soul "
                          "planet's house, the 10th and its lord) use a midday estimate and "
                          "may shift. Add your exact birth time for a precise blueprint.")

    return {
        "ok": True,
        "soul": soul,
        "calling": calling,
        "career_chart": career_chart,
        "dharma": dharma,
        "headline": headline,
        "summary": summary,
        "why": why,
        "sanskrit": sanskrit,
        "precision_note": precision_note,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Year in Review — "Cosmic Wrapped"
# ─────────────────────────────────────────────────────────────────────────────

def year_in_review(profile: dict, year: int | None = None) -> dict:
    from shared.astro.kundli import compute_varshaphala
    from shared.astro.astro_calc import build_vimshottari_timeline
    from shared.astro.retrospect import (
        _saturn_from_moon, _jupiter_from_moon, _node_from_moon,
    )
    from shared.astro.constants import PLANETS
    from shared.astro.astro_calc import get_planet_longitude_and_speed, get_rahu_longitude, sign_index_from_lon
    from shared.astro import ephemeris

    chart, time_known = _build_chart(profile)
    tz = profile["tz"]
    if year is None:
        year = datetime.now(ZoneInfo(tz)).year

    # 1. Varshaphala (Tajik annual chart) — the Muntha is the year's spotlight.
    vp = compute_varshaphala(chart, year)
    muntha_house = vp["muntha"]["house_from_lagna"]
    muntha = {
        "sign": vp["muntha"]["sign"],
        "house": muntha_house,
        "line": M.MUNTHA_LINE.get(muntha_house, "this year asked for steady, ordinary living"),
    }

    # 2. The dasha chapter across the year (read at mid-year), + note any AD shift.
    dt_birth = chart.datetime_local
    moon_lon = chart.planets["Moon"].longitude
    mid = datetime(year, 7, 1, 12, 0, tzinfo=ZoneInfo(tz))
    di = build_vimshottari_timeline(dt_birth, moon_lon, mid)
    start = build_vimshottari_timeline(dt_birth, moon_lon, datetime(year, 1, 1, 12, 0, tzinfo=ZoneInfo(tz)))
    end = build_vimshottari_timeline(dt_birth, moon_lon, datetime(year, 12, 31, 12, 0, tzinfo=ZoneInfo(tz)))
    md, ad = di["current_md"], di["current_ad"]
    shift = None
    if start["current_ad"] != end["current_ad"]:
        shift = f"part-way through, your sub-period shifted from {start['current_ad']} to {end['current_ad']}"
    chapter = {
        "mahadasha": md, "antardasha": ad,
        "line": (f"You spent {year} inside your {md} chapter"
                 + (f", in its {ad} sub-stretch" if ad != md else "")
                 + (f" — {shift}" if shift else "") + "."),
    }

    # 3. The year's slow, era-defining transits over the natal Moon (mid-year).
    moon_sign = chart.planets["Moon"].sign_index
    target_utc = mid.astimezone(ZoneInfo("UTC"))
    jd = ephemeris.julday(target_utc.year, target_utc.month, target_utc.day, 12.0)
    sat_sign = sign_index_from_lon(get_planet_longitude_and_speed(jd, PLANETS["Saturn"])[0])
    jup_sign = sign_index_from_lon(get_planet_longitude_and_speed(jd, PLANETS["Jupiter"])[0])
    rahu_sign = sign_index_from_lon(get_rahu_longitude(jd))

    gifts, lessons = [], []
    j = _jupiter_from_moon(jup_sign, moon_sign)
    if j:
        gifts.append({"what": j["what"], "meaning": j["meaning"]})
    s = _saturn_from_moon(sat_sign, moon_sign)
    if s:
        lessons.append({"what": s["what"], "meaning": s["meaning"]})
    n = _node_from_moon(rahu_sign, moon_sign)
    if n:
        lessons.append({"what": n["what"], "meaning": n["meaning"]})

    # 4. Headline + a punchy shareable line (the "Wrapped" card).
    headline = f"Your {year}: a {md} year" + (f" with a {ad} undercurrent" if ad != md else "") + "."
    share_bits = [f"My {year} was a {md} chapter"]
    if gifts:
        share_bits.append("with a little grace from Jupiter")
    elif lessons:
        share_bits.append("and Saturn taught me a few things")
    share_text = " ".join(share_bits) + f" — and the year shone its light on {M.HOUSE_THROUGH.get(muntha_house, 'my life').split(',')[0]}."

    summary_bits = [chapter["line"], muntha["line"].capitalize() + "."]
    if gifts:
        summary_bits.append(f"Underneath, {gifts[0]['meaning']}.")
    if lessons:
        summary_bits.append(f"And {lessons[0]['meaning']}.")
    summary_bits.append("A year is a chapter, not a verdict — take from it what helps and leave the rest.")
    summary = " ".join(summary_bits)

    why = (f"Varshaphala {year}: Muntha in {muntha['sign']} (house {muntha_house} from your Lagna). "
           f"Dasha at mid-year: {md} Mahadasha / {ad} Antardasha. Slow transits: "
           + (", ".join(t["what"] for t in gifts + lessons) if (gifts or lessons)
              else "no major slow-transit passage over the birth Moon") + ".")

    precision_note = None
    if not time_known:
        precision_note = ("Your birth time isn't set, so the year's Muntha (which is counted from "
                          "your Lagna) uses a midday estimate and may shift by a house. Add your "
                          "exact birth time for a precise recap.")

    return {
        "ok": True,
        "year": year,
        "chapter": chapter,
        "muntha": muntha,
        "gifts": gifts,
        "lessons": lessons,
        "headline": headline,
        "share_text": share_text,
        "summary": summary,
        "why": why,
        "sanskrit": "वर्षफल · मुन्था · महादशा",
        "precision_note": precision_note,
    }
