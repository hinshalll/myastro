"""
math_engine/kundli/varshaphala.py
=================================

Varshaphala (Tajik annual chart) — the year-ahead birthday chart.

Each year, the moment the Sun returns to its exact natal longitude defines
a "Solar Return" chart, used for year-specific predictions. The Tajik
system adds:

    - Muntha — a "year-pointer" sign that progresses one sign per year
                from the natal Lagna.
    - Sahams — calculated points (~50 in classical Tajik) for specific
                topics (Punya, Vidya, Karya, Bhratri, Putra, etc.). v1
                ships the 8 most-used Sahams; rest can be added later.
    - Year Lord (Varshesha) — strongest of the five Tajik year-rulers.

For v1 we compute the solar return time, Muntha sign, and 8 core Sahams.
A full Varshaphala chart (32-page Tajik analysis) is a future expansion.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

from math_engine.constants import SIGNS, SIGN_LORDS_MAP


# ─────────────────────────────────────────────────────────────────────────────
# Solar Return time finder (bisection)
# ─────────────────────────────────────────────────────────────────────────────

def _find_solar_return(chart, year: int) -> datetime:
    """
    Find the moment (UT) the Sun returns to its natal sidereal longitude
    during the given solar year (around the native's birthday).

    Bisection method — fast (sub-second precision in <20 iterations).
    """
    target = chart.planets["Sun"].longitude

    # Search window: ±5 days around the birthday in the given year.
    bd = chart.birth_data
    bd_dt = datetime(year, bd.date.month, bd.date.day,
                     bd.time.hour, bd.time.minute, tzinfo=ZoneInfo(bd.tz))
    lo = bd_dt - timedelta(days=5)
    hi = bd_dt + timedelta(days=5)

    def sun_lon_at(dt):
        utc = dt.astimezone(ZoneInfo("UTC"))
        jd = swe.julday(utc.year, utc.month, utc.day,
                        utc.hour + utc.minute / 60 + utc.second / 3600)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        res, _ = swe.calc_ut(jd, swe.SUN, flags)
        return float(res[0]) % 360

    def diff(dt):
        d = (sun_lon_at(dt) - target + 180) % 360 - 180
        return d

    # Bisection
    for _ in range(40):
        mid = lo + (hi - lo) / 2
        d_lo = diff(lo)
        d_mid = diff(mid)
        if abs(d_mid) < 1e-5:
            return mid
        if d_lo * d_mid < 0:
            hi = mid
        else:
            lo = mid
    return mid


# ─────────────────────────────────────────────────────────────────────────────
# Sahams — 8 most-used (per Saravali / Tajik Neelakanthi)
# ─────────────────────────────────────────────────────────────────────────────
#
# A "Saham" is a calculated sensitive point: Saham_X = sign of (planet_A -
# planet_B + Lagna) % 360. Classical Tajik defines ~50 Sahams; the most
# commonly read are:
#
#   Punya     — happiness, virtue       = Moon - Sun + Asc
#   Vidya     — learning, education     = Sun - Moon + Asc  (or 9th-lord–Moon+Asc)
#   Karya     — work / accomplishments  = Saturn - Sun + Asc  (for day birth;
#                                          reverse for night)
#   Yashas    — fame                    = Jupiter - Sun + Asc
#   Mitra     — friends                 = Jupiter - Moon + Asc
#   Bhratri   — siblings                = Mars - Saturn + Asc
#   Pitri     — father                  = Saturn - Sun + Asc
#   Matri     — mother                  = Moon - Venus + Asc
# ─────────────────────────────────────────────────────────────────────────────

def _saham(a_lon: float, b_lon: float, asc_lon: float) -> float:
    """Generic Saham formula: (A - B + Asc) mod 360."""
    return (a_lon - b_lon + asc_lon) % 360


def _compute_sahams(chart) -> dict:
    p = chart.planets
    asc = chart.lagna.longitude
    sahams_raw = {
        "Punya":   _saham(p["Moon"].longitude, p["Sun"].longitude, asc),
        "Vidya":   _saham(p["Sun"].longitude,  p["Moon"].longitude, asc),
        "Karya":   _saham(p["Saturn"].longitude, p["Sun"].longitude, asc),
        "Yashas":  _saham(p["Jupiter"].longitude, p["Sun"].longitude, asc),
        "Mitra":   _saham(p["Jupiter"].longitude, p["Moon"].longitude, asc),
        "Bhratri": _saham(p["Mars"].longitude, p["Saturn"].longitude, asc),
        "Pitri":   _saham(p["Saturn"].longitude, p["Sun"].longitude, asc),
        "Matri":   _saham(p["Moon"].longitude, p["Venus"].longitude, asc),
    }
    out = {}
    for name, lon in sahams_raw.items():
        sidx = int(lon // 30) % 12
        out[name] = {
            "longitude": lon,
            "sign":      SIGNS[sidx],
            "sign_lord": SIGN_LORDS_MAP[sidx],
            "house_from_lagna": ((sidx - chart.lagna.sign_index) % 12) + 1,
        }
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Muntha — year-pointer sign
# ─────────────────────────────────────────────────────────────────────────────

def _muntha(chart, year: int) -> dict:
    """
    Muntha progresses one sign per year from natal Lagna. Year-of-life =
    (current_year - birth_year). Muntha_sign = (lagna_sign + years_lived) % 12.
    """
    years_lived = year - chart.birth_data.date.year
    muntha_sidx = (chart.lagna.sign_index + years_lived) % 12
    return {
        "year":       year,
        "age":        years_lived,
        "sign":       SIGNS[muntha_sidx],
        "sign_lord":  SIGN_LORDS_MAP[muntha_sidx],
        "house_from_lagna": ((muntha_sidx - chart.lagna.sign_index) % 12) + 1,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def compute(chart, year: int | None = None) -> dict:
    """
    Build the Varshaphala dict for the given (default: current) year.

    Returns:
        {
          "year":            int,
          "solar_return_utc": datetime,
          "solar_return_local": datetime,
          "muntha":           {...},
          "sahams":           {name: {sign, longitude, ...}}
        }
    """
    tz = ZoneInfo(chart.birth_data.tz)
    if year is None:
        year = datetime.now(tz).year

    sr_utc = _find_solar_return(chart, year)
    sr_local = sr_utc.astimezone(tz)

    return {
        "year":               year,
        "solar_return_utc":   sr_utc,
        "solar_return_local": sr_local,
        "muntha":             _muntha(chart, year),
        "sahams":             _compute_sahams(chart),
    }
