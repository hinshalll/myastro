"""shared.astro.panchang — display-ready daily Panchang for the Today → Plan tab.

Composes already-validated engine pieces into one per-day card:
  • the sunrise tithi / nakshatra / yoga / karana (get_panchanga),
  • the PERSONAL day-colour good/mixed/low (forecast.day_quality — the SAME
    source the Today reading uses, so the calendar can never contradict the
    reading),
  • festival/observance markers + Grahan days,
  • the day's strongest window (Abhijit Muhurta).
Plus a multi-day range for the 3-day strip and the month grid. Pure math +
lookup, NO AI.

Accuracy (confirmed against multiple standard almanac sources — Drik Panchang
et al.):
  • Day-naming follows the classical UDAYA TITHI rule: the tithi prevailing at
    LOCAL SUNRISE rules the whole calendar day (so two longitudes can differ on
    the same English date). We therefore read the panchanga at local sunrise,
    matching shared.astro.muhurta's din-shuddhi.
  • Markers are definitional: Ekadashi = 11th tithi of either paksha; Purnima =
    15th tithi of Shukla paksha (full moon); Amavasya = 15th tithi of Krishna
    paksha (new moon).
"""

from datetime import date as _date, timedelta

from shared.astro.constants import PLANETS
from shared.astro.astro_calc import (
    sun_rise_set, local_to_julian_day, get_planet_longitude_and_speed,
    get_panchanga, nakshatra_info, next_eclipse,
)
from shared.astro.forecast import day_quality
from shared.astro.festivals import festival_for

_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _hm(dt):
    return dt.strftime("%H:%M")


def _tithi_markers(tithi: str) -> list[dict]:
    """Definitional festival/observance markers from the sunrise tithi string
    (get_panchanga emits e.g. "11 Shukla (Waxing)" / "15 Krishna (Waning)")."""
    try:
        num = int(tithi.split()[0])
    except (ValueError, IndexError):
        return []
    shukla = "Shukla" in tithi
    marks = []
    if num == 15 and shukla:
        marks.append({"key": "purnima", "label": "Full moon (Purnima)"})
    elif num == 15 and not shukla:
        marks.append({"key": "amavasya", "label": "New moon (Amavasya)"})
    if num == 11:
        marks.append({"key": "ekadashi", "label": "Ekadashi (fasting day)"})
    return marks


def panchang_for_day(profile: dict, d, lat: float, lon: float, tz: str,
                     full: bool = True) -> dict:
    """One day's Panchang card. `full` adds the day's strongest window +
    sunrise/sunset (used for the 3-day strip; the month grid runs light)."""
    if isinstance(d, str):
        d = _date.fromisoformat(d)

    sunrise, sunset, _next = sun_rise_set(d, lat, lon, tz)
    jd, dtl, _ = local_to_julian_day(d, sunrise.time(), tz)   # tithi AT local sunrise (Udaya Tithi)
    sun_lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Sun"])
    moon_lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
    pan = get_panchanga(sun_lon, moon_lon, dtl)
    nak, _lord, _pada = nakshatra_info(moon_lon)

    dq = day_quality(profile, d)   # personal colour — SAME source as the reading

    out = {
        "date": d.isoformat(),
        "weekday": _WEEKDAYS[d.weekday()],
        "band": dq["band"],          # good / mixed / low (personal)
        "label": dq["label"],        # "a good day for you" / "a mixed day" / "a low-key day"
        "vibe_word": dq["vibe_word"],
        "tithi": pan["tithi"],
        "nakshatra": nak,
        "yoga": pan["yoga"],
        "karana": pan["karana"],
        "markers": _tithi_markers(pan["tithi"]),
    }
    if dq.get("chandrashtama"):
        out["markers"].append({"key": "chandrashtama", "label": "Your Chandrashtama (a low day)"})
    fest = festival_for(d)
    if fest:
        out["markers"].insert(0, {"key": "festival", "label": fest["name"]})
    if full:
        # Abhijit Muhurta — the day's strongest ~48-min stretch, centred on local
        # noon (same formula as daily_timing_windows' "good" window).
        day_len = sunset - sunrise
        midday = sunrise + day_len / 2
        half = day_len / 30
        out["best_window"] = {"start": _hm(midday - half), "end": _hm(midday + half)}
        out["sunrise"] = _hm(sunrise)
        out["sunset"] = _hm(sunset)
    return out


def _eclipse_dates_in_range(start: _date, end: _date, tz: str,
                            lat: float, lon: float) -> dict[str, str]:
    """Every eclipse date within [start, end] → its type. Usually 0-2; eclipses
    arrive in pairs ~2 weeks apart, so we walk next_eclipse forward a few times."""
    found: dict[str, str] = {}
    cursor = start
    for _ in range(6):                       # safety cap
        horizon = (end - cursor).days
        if horizon < 0:
            break
        ev = next_eclipse(cursor, tz, lat, lon, horizon_days=horizon + 1)
        if not ev.get("present") or not ev.get("date"):
            break
        ed = _date.fromisoformat(ev["date"])
        if ed > end:
            break
        found[ed.isoformat()] = ev["type"]   # "Surya Grahan" / "Chandra Grahan"
        cursor = ed + timedelta(days=1)
    return found


def panchang_range(profile: dict, start, days: int, lat: float, lon: float, tz: str,
                   full: bool = True) -> dict:
    """`days` consecutive Panchang cards from `start` (the 3-day strip or the
    month grid), with Grahan days marked across the whole span."""
    if isinstance(start, str):
        start = _date.fromisoformat(start)
    days = max(1, min(days, 40))             # cap at a month-ish
    end = start + timedelta(days=days - 1)
    eclipses = _eclipse_dates_in_range(start, end, tz, lat, lon)

    out = []
    for i in range(days):
        d = start + timedelta(days=i)
        day = panchang_for_day(profile, d, lat, lon, tz, full=full)
        kind = eclipses.get(d.isoformat())
        if kind:
            label = "Solar eclipse (Grahan)" if "Surya" in kind else "Lunar eclipse (Grahan)"
            day["markers"].append({"key": "grahan", "label": label})
            day["grahan"] = True
        out.append(day)
    return {"start_date": start.isoformat(), "days": out}
