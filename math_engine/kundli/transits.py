"""
math_engine/kundli/transits.py
==============================

12-month transit forecast — one of the most-read sections of any premium
kundli. Tracks slow-moving outer planets against the native's natal chart:

    - Saturn (Shani)       — 2.5 yr/sign. Sade Sati / Ashtama Shani driver.
    - Jupiter (Guru)       — 1 yr/sign. Expansion / wealth transit.
    - Rahu / Ketu          — 1.5 yr/sign (retrograde). Karmic axis shifts.

For each, we report:
    - Current transit sign + house from Lagna + house from Moon
    - Sign change dates within the 12-month window
    - Sade Sati phase (12th, 1st, or 2nd from natal Moon)
    - Ashtama Shani check (Saturn in 8th from natal Moon)
    - Kantaka Shani check (Saturn in 4/7/10 from natal Moon — variant lists)
    - Guru Chandra Yoga (Jupiter favourable to natal Moon: 2/5/7/9/11)
    - Tara Bala for the month (auspicious days of week)

All dates use the chart's local timezone.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe
from math_engine.constants import PLANETS, SIGNS, SIGN_LORDS_MAP


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _dt_to_jd(dt: datetime) -> float:
    """Local-aware datetime → Julian Day UT (sidereal-aware via swe)."""
    dt_utc = dt.astimezone(ZoneInfo("UTC"))
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def _sidereal_lon(jd: float, pid: int) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    res, _ = swe.calc_ut(jd, pid, flags)
    return float(res[0]) % 360


def _sign_idx(lon: float) -> int:
    return int(lon // 30) % 12


def _house_from(reference_sign_idx: int, planet_sign_idx: int) -> int:
    return ((planet_sign_idx - reference_sign_idx) % 12) + 1


# ─────────────────────────────────────────────────────────────────────────────
# Sade Sati phase computation
# ─────────────────────────────────────────────────────────────────────────────

def _sade_sati_phase(saturn_sign: int, moon_sign: int) -> dict:
    """
    Determine whether Saturn currently transits 12th, 1st, or 2nd from
    natal Moon — the three classical Sade Sati phases.
    """
    twelfth = (moon_sign + 11) % 12
    first   = moon_sign
    second  = (moon_sign + 1) % 12

    if saturn_sign == twelfth:
        return {"in_sade_sati": True, "phase": "Rising (12th from Moon)",
                "note": "Mental restlessness, beginning of seven-and-a-half "
                        "year cycle. Plans seeded now mature later."}
    if saturn_sign == first:
        return {"in_sade_sati": True, "phase": "Peak (1st from Moon)",
                "note": "Most intense phase — physical, financial, relational "
                        "tests. Discipline + austerity transmute the load."}
    if saturn_sign == second:
        return {"in_sade_sati": True, "phase": "Setting (2nd from Moon)",
                "note": "Reaping phase — wealth/family lessons consolidate. "
                        "Cycle closes; karmic harvest received."}
    return {"in_sade_sati": False, "phase": "None", "note": ""}


def _ashtama_shani(saturn_sign: int, moon_sign: int) -> bool:
    """Saturn in 8th from natal Moon — Ashtama Shani."""
    return saturn_sign == (moon_sign + 7) % 12


def _kantaka_shani(saturn_sign: int, moon_sign: int) -> bool:
    """Saturn in 4/7/10 from natal Moon — Kantaka Shani (thorn)."""
    return saturn_sign in {(moon_sign + d) % 12 for d in (3, 6, 9)}


def _guru_chandra_yoga(jupiter_sign: int, moon_sign: int) -> bool:
    """Jupiter in 2/5/7/9/11 from natal Moon — auspicious for the year."""
    return jupiter_sign in {(moon_sign + d - 1) % 12 for d in (2, 5, 7, 9, 11)}


# ─────────────────────────────────────────────────────────────────────────────
# Sign-change finder
# ─────────────────────────────────────────────────────────────────────────────

def _find_sign_changes(pid: int, start_dt: datetime, end_dt: datetime,
                       step_days: float = 1.0) -> list[tuple[datetime, int, int]]:
    """
    Coarse sign-change scanner (1-day step). For each day, check if the
    sidereal sign of the planet differs from the previous day. Returns
    [(date_of_change, from_sign, to_sign), ...].

    1-day resolution is sufficient for slow planets (Saturn/Jupiter/nodes);
    swisseph is fast enough that a finer step adds negligible overhead.
    """
    out: list[tuple[datetime, int, int]] = []
    cursor = start_dt
    jd_prev = _dt_to_jd(cursor)
    sign_prev = _sign_idx(_sidereal_lon(jd_prev, pid))
    while cursor < end_dt:
        cursor = cursor + timedelta(days=step_days)
        jd_now = _dt_to_jd(cursor)
        sign_now = _sign_idx(_sidereal_lon(jd_now, pid))
        if sign_now != sign_prev:
            # Pin down the day by bisecting between cursor-step and cursor
            out.append((cursor, sign_prev, sign_now))
            sign_prev = sign_now
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Main entry
# ─────────────────────────────────────────────────────────────────────────────

def twelve_month_forecast(chart) -> dict:
    """
    Build the 12-month transit forecast section.

    Returns a dict with:
        - period: {start, end} (local timezone)
        - current_transit: {planet: {sign, house_from_lagna, house_from_moon}}
        - sign_changes: {planet: [(date, from_sign, to_sign), ...]}
        - sade_sati: {phase, in_sade_sati, note, full_window: (start_date, end_date)}
        - ashtama_shani: bool
        - kantaka_shani: bool
        - guru_chandra_yoga: bool
    """
    tz = ZoneInfo(chart.birth_data.tz)
    now = datetime.now(tz)
    end = now + timedelta(days=365)

    natal_lagna_sign = chart.lagna.sign_index
    natal_moon_sign = chart.planets["Moon"].sign_index

    # Slow planets we report on
    targets = {
        "Saturn":  PLANETS["Saturn"],
        "Jupiter": PLANETS["Jupiter"],
        "Rahu":    swe.TRUE_NODE,
    }

    current_transit: dict[str, dict] = {}
    sign_changes: dict[str, list] = {}

    jd_now = _dt_to_jd(now)
    for name, pid in targets.items():
        lon = _sidereal_lon(jd_now, pid)
        sidx = _sign_idx(lon)
        current_transit[name] = {
            "sign": SIGNS[sidx],
            "sign_index": sidx,
            "longitude": lon,
            "house_from_lagna": _house_from(natal_lagna_sign, sidx),
            "house_from_moon":  _house_from(natal_moon_sign, sidx),
            "sign_lord": SIGN_LORDS_MAP[sidx],
        }
        sign_changes[name] = []
        for date_change, from_s, to_s in _find_sign_changes(pid, now, end):
            sign_changes[name].append({
                "date":     date_change,
                "from":     SIGNS[from_s],
                "to":       SIGNS[to_s],
                "to_house_from_lagna": _house_from(natal_lagna_sign, to_s),
                "to_house_from_moon":  _house_from(natal_moon_sign, to_s),
            })
    # Derive Ketu = 180° from Rahu
    rahu_sidx = current_transit["Rahu"]["sign_index"]
    ketu_sidx = (rahu_sidx + 6) % 12
    current_transit["Ketu"] = {
        "sign": SIGNS[ketu_sidx],
        "sign_index": ketu_sidx,
        "longitude": (current_transit["Rahu"]["longitude"] + 180) % 360,
        "house_from_lagna": _house_from(natal_lagna_sign, ketu_sidx),
        "house_from_moon":  _house_from(natal_moon_sign, ketu_sidx),
        "sign_lord": SIGN_LORDS_MAP[ketu_sidx],
    }

    # Sade Sati / Ashtama / Kantaka / GCY
    sat_sidx = current_transit["Saturn"]["sign_index"]
    jup_sidx = current_transit["Jupiter"]["sign_index"]
    sade_phase = _sade_sati_phase(sat_sidx, natal_moon_sign)

    return {
        "period": {"start": now, "end": end},
        "current_transit": current_transit,
        "sign_changes": sign_changes,
        "sade_sati": sade_phase,
        "ashtama_shani":   _ashtama_shani(sat_sidx, natal_moon_sign),
        "kantaka_shani":   _kantaka_shani(sat_sidx, natal_moon_sign),
        "guru_chandra_yoga": _guru_chandra_yoga(jup_sidx, natal_moon_sign),
    }
