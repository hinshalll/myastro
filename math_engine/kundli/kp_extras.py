"""
math_engine/kundli/kp_extras.py
===============================

Krishnamurti Paddhati (KP) supplementary tables for the kundli PDF.

The KP section answers, for each of the 12 cusps:
    - Sign-lord, star-lord (nakshatra lord), sub-lord (KP sub-lord)
    - The significators (planets that signify each house through KP's
      "4-level rule": planet's NL, planet itself, occupants of NL's
      houses, occupants of planet's houses)

KP is highly predictive for timing. The PDF presents the cuspal table +
a per-planet significators grid + a "Ruling Planets" table for the moment
the kundli is generated.

Reuses the existing `astro_calc.get_kp_sub_lord` and `get_kp_4step` helpers.
"""

from __future__ import annotations

from math_engine.constants import SIGN_LORDS_MAP, NAKSHATRA_LORDS
from math_engine.astro_calc import (
    get_kp_sub_lord,
    get_kp_4step,
    nakshatra_info,
)


def _cusp_lords(cusp_lon: float) -> dict:
    """Return KP sign-lord, star-lord, sub-lord for a cusp longitude."""
    sign_idx = int(cusp_lon // 30) % 12
    nak, nak_lord, _pada = nakshatra_info(cusp_lon)
    sub = get_kp_sub_lord(cusp_lon)
    return {
        "sign":       sign_idx,
        "sign_lord":  SIGN_LORDS_MAP[sign_idx],
        "nakshatra":  nak,
        "star_lord":  nak_lord,
        "sub_lord":   sub,
    }


def build(chart) -> dict:
    """
    Build the KP supplements dict.

    Returns:
        {
          "cusps": [{cusp_num, longitude, sign_lord, star_lord, sub_lord}, ...],
          "significators": {planet: "L1(...), L2(...), L3(...), L4(...)"},
          "ruling_planets": {...}   # placeholder — needs current-time inputs
        }
    """
    planet_data = {n: (p.longitude, p.speed) for n, p in chart.planets.items()
                   if n not in ("Rahu", "Ketu")}
    r_lon = chart.planets["Rahu"].longitude
    k_lon = chart.planets["Ketu"].longitude
    ls = chart.lagna.sign_index

    # Cuspal table — 12 Placidus cusps
    cusps = []
    for i, cusp_lon in enumerate(chart.placidus_cusps[:12], start=1):
        lords = _cusp_lords(cusp_lon)
        cusps.append({
            "cusp":       i,
            "longitude":  cusp_lon,
            **lords,
        })

    # Significators per planet (4-step KP rule)
    significators = {}
    for pname in list(chart.planets.keys()):
        sigs = get_kp_4step(pname, ls, planet_data, r_lon, k_lon)
        significators[pname] = sigs

    return {
        "cusps":           cusps,
        "significators":   significators,
        "ruling_planets":  None,   # populated at query-time, not chart-time
    }
