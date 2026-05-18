"""
math_engine/kundli/western.py
=============================

Western (tropical) chart appendix.

Vedic astrology uses sidereal positions (planets fixed against the stars);
Western astrology uses tropical positions (planets fixed against the
equinoxes). The numerical difference is the ayanamsha — currently ~24°.

For users who follow both systems, this module computes the tropical
positions and the standard Western aspects (conjunction, opposition,
trine, square, sextile) with classical orbs.

Aspect system: Ptolemaic majors only, +/- 8° for luminaries, +/- 6° for
others. Adds a tropical Sun-sign + element + modality + Western nakshatra
substitute (tropical sign + decanate).
"""

from __future__ import annotations

import swisseph as swe
from math_engine.constants import PLANETS
from math_engine.astro_calc import format_dms


TROPICAL_SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

ELEMENTS = {
    "Aries":"Fire","Leo":"Fire","Sagittarius":"Fire",
    "Taurus":"Earth","Virgo":"Earth","Capricorn":"Earth",
    "Gemini":"Air","Libra":"Air","Aquarius":"Air",
    "Cancer":"Water","Scorpio":"Water","Pisces":"Water",
}
MODALITIES = {
    "Aries":"Cardinal","Cancer":"Cardinal","Libra":"Cardinal","Capricorn":"Cardinal",
    "Taurus":"Fixed","Leo":"Fixed","Scorpio":"Fixed","Aquarius":"Fixed",
    "Gemini":"Mutable","Virgo":"Mutable","Sagittarius":"Mutable","Pisces":"Mutable",
}
RULERS = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
    "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars/Pluto",
    "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn/Uranus","Pisces":"Jupiter/Neptune",
}


def _tropical_long(jd: float, pid: int) -> tuple[float, float]:
    """Return tropical (lon, speed) — same swisseph call without sidereal flag."""
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    res, _ = swe.calc_ut(jd, pid, flags)
    return float(res[0]) % 360, float(res[3])


def _tropical_lagna(jd: float, lat: float, lon: float) -> float:
    """Tropical ascendant via Placidus."""
    flags = swe.FLG_SWIEPH
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", flags)
    return float(ascmc[0]) % 360


def _aspect_between(a: float, b: float, orb_luminary: float = 8.0,
                    orb_other: float = 6.0, is_luminary: bool = False) -> tuple[str, float] | None:
    """
    Detect a Ptolemaic major aspect between two longitudes.
    Returns (aspect_name, separation_deg) or None.
    """
    sep = abs((a - b + 180.0) % 360.0 - 180.0)
    orb = orb_luminary if is_luminary else orb_other
    targets = [
        ("Conjunction",  0.0),
        ("Sextile",     60.0),
        ("Square",      90.0),
        ("Trine",      120.0),
        ("Opposition", 180.0),
    ]
    for name, deg in targets:
        if abs(sep - deg) <= orb:
            return name, sep
    return None


def build(chart) -> dict:
    """
    Compute the tropical (Western) appendix for the chart owner.

    Returns a self-contained dict ready for the Western appendix page:
        - sun_sign, moon_sign, rising_sign
        - element/modality/ruler of each
        - planet positions (tropical lon + sign + house)
        - aspect grid (only majors)
    """
    jd = chart.julian_day_ut
    bd = chart.birth_data

    # Tropical planet positions
    tropical_positions: dict[str, dict] = {}
    longs: dict[str, float] = {}
    for pname, pid in PLANETS.items():
        lon, spd = _tropical_long(jd, pid)
        sign_idx = int(lon // 30) % 12
        sign = TROPICAL_SIGNS[sign_idx]
        tropical_positions[pname] = {
            "longitude":   lon,
            "longitude_dms": format_dms(lon % 30),
            "sign":        sign,
            "sign_index":  sign_idx,
            "element":     ELEMENTS[sign],
            "modality":    MODALITIES[sign],
            "speed":       spd,
            "is_retrograde": spd < 0 and pname not in ("Sun", "Moon"),
        }
        longs[pname] = lon

    # Tropical Rahu / Ketu
    res, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH)
    rahu_lon = float(res[0]) % 360
    ketu_lon = (rahu_lon + 180.0) % 360
    for pname, plon in (("Rahu", rahu_lon), ("Ketu", ketu_lon)):
        sign_idx = int(plon // 30) % 12
        sign = TROPICAL_SIGNS[sign_idx]
        tropical_positions[pname] = {
            "longitude":   plon,
            "longitude_dms": format_dms(plon % 30),
            "sign":        sign,
            "sign_index":  sign_idx,
            "element":     ELEMENTS[sign],
            "modality":    MODALITIES[sign],
            "speed":       0.0,
            "is_retrograde": False,
        }
        longs[pname] = plon

    # Tropical Ascendant
    asc = _tropical_lagna(jd, bd.lat, bd.lon)
    asc_sign_idx = int(asc // 30) % 12
    asc_sign = TROPICAL_SIGNS[asc_sign_idx]

    # Tropical houses (whole-sign for simplicity; tropical Placidus is shown
    # alongside in the PDF if needed)
    for pname, plon in longs.items():
        sign_idx = int(plon // 30) % 12
        tropical_positions[pname]["house"] = ((sign_idx - asc_sign_idx) % 12) + 1

    # Aspect grid
    aspects: list[dict] = []
    names = list(longs.keys())
    for i, p1 in enumerate(names):
        for p2 in names[i+1:]:
            is_lum = p1 in ("Sun","Moon") or p2 in ("Sun","Moon")
            r = _aspect_between(longs[p1], longs[p2], is_luminary=is_lum)
            if r:
                aspects.append({
                    "p1": p1, "p2": p2, "aspect": r[0], "separation": r[1],
                })

    sun_sign  = tropical_positions["Sun"]["sign"]
    moon_sign = tropical_positions["Moon"]["sign"]

    return {
        "sun_sign":      sun_sign,
        "sun_element":   ELEMENTS[sun_sign],
        "sun_modality":  MODALITIES[sun_sign],
        "moon_sign":     moon_sign,
        "moon_element":  ELEMENTS[moon_sign],
        "rising_sign":   asc_sign,
        "rising_element": ELEMENTS[asc_sign],
        "rising_modality": MODALITIES[asc_sign],
        "rising_ruler":  RULERS[asc_sign],
        "ascendant_longitude": asc,
        "ascendant_dms": format_dms(asc % 30),
        "planets":       tropical_positions,
        "aspects":       aspects,
    }
