"""
math_engine/kundli/divisional.py
================================

The 16 classical divisional charts (Shodashavarga) used in Vedic astrology.

Each varga (D-N) divides every sign into N parts and assigns each part to
a destination sign per a varga-specific rule. The same planet thus produces
16 *different* chart placements, each illuminating a specific life domain.

References used:
    - BPHS (Brihat Parashara Hora Shastra), R. Santhanam translation, Ch. 6-7
    - "Vedic Astrology — A Guide to the Fundamentals of Jyotish",
      Sharma & Kapoor
    - Jagannatha Hora documentation (P.V.R. Narasimha Rao) — used as the
      tie-breaker for ambiguous lineages (esp. D60).

The 16 vargas, in classical order:
    D1  Rasi              — Body, physical self, all of life
    D2  Hora              — Wealth, monetary inheritance
    D3  Drekkana          — Siblings, courage, initiative
    D4  Chaturthamsha     — Property, fixed assets, vehicles, mother's home
    D7  Saptamsha         — Children, progeny
    D9  Navamsha          — Marriage, dharma, the soul (most important varga)
    D10 Dashamsha         — Career, profession, public standing
    D12 Dvadashamsha      — Parents, ancestors
    D16 Shodashamsha      — Vehicles, comforts, happiness from possessions
    D20 Vimshamsha        — Spiritual progress, devotion, sadhana
    D24 Chaturvimshamsha  — Education, learning, knowledge
    D27 Saptavimshamsha   — Strengths & weaknesses (Bhamsha / Nakshatramsha)
    D30 Trimshamsha       — Misfortunes, troubles, evils
    D40 Khavedamsha       — Maternal legacy, auspicious / inauspicious effects
    D45 Akshavedamsha     — Paternal legacy, character
    D60 Shashtiamsha      — Past-life karma (the deepest varga; PVRNR notes
                            it requires birth time accurate to ~12 seconds
                            to be reliable — flag in PDF when exact_time=False)

Each function returns a 0-indexed sign (0..11). Lagna and all 9 planets are
each passed through to produce a complete D-N chart.
"""

from __future__ import annotations

from dataclasses import dataclass

from math_engine.constants import SIGNS, MOVABLE_SIGNS, FIXED_SIGNS
from math_engine.astro_calc import sign_index_from_lon, sign_name


# ─────────────────────────────────────────────────────────────────────────────
# Per-varga sign-of-arrival rules
# ─────────────────────────────────────────────────────────────────────────────
#
# Convention used throughout this file:
#   - `s` is the natal sign 0-indexed (0=Aries, 1=Taurus, ..., 11=Pisces).
#   - "Odd sign" in classical terms = Aries(0), Gemini(2), Leo(4)...
#     i.e. s % 2 == 0 in code. ALWAYS verify which convention a formula uses.
#   - MOVABLE_SIGNS = {0, 3, 6, 9}    (Aries, Cancer, Libra, Capricorn)
#   - FIXED_SIGNS   = {1, 4, 7, 10}   (Taurus, Leo, Scorpio, Aquarius)
#   - DUAL_SIGNS    = {2, 5, 8, 11}   (Gemini, Virgo, Sagittarius, Pisces)
# ─────────────────────────────────────────────────────────────────────────────

DUAL_SIGNS = {2, 5, 8, 11}


def _slot(lon: float, n_parts: int) -> int:
    """Which of N equal parts of the sign this longitude falls into (0..N-1)."""
    deg_in_sign = lon % 30
    return min(int(deg_in_sign * n_parts / 30.0), n_parts - 1)


def d1_si(lon: float) -> int:
    """D1 Rasi — the natal chart itself."""
    return sign_index_from_lon(lon)


def d2_si(lon: float) -> int:
    """
    D2 Hora (wealth) — Sun's hora (Leo=4) or Moon's hora (Cancer=3).
    Odd signs: 0-15° → Sun's hora (Leo);  15-30° → Moon's hora (Cancer).
    Even signs: 0-15° → Moon's hora;       15-30° → Sun's hora.
    """
    s = sign_index_from_lon(lon)
    first_half = (lon % 30) < 15
    odd_sign = (s % 2 == 0)
    if odd_sign:
        return 4 if first_half else 3
    return 3 if first_half else 4


def d3_si(lon: float) -> int:
    """
    D3 Drekkana (siblings) — three parts of 10° each.
        Part 1 (0-10°)  → same sign.
        Part 2 (10-20°) → 5th sign from it.
        Part 3 (20-30°) → 9th sign from it.
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 3)
    return (s + slot * 4) % 12


def d4_si(lon: float) -> int:
    """
    D4 Chaturthamsha (property) — four parts of 7.5° each.
        Quarters land in the 1st, 4th, 7th, 10th from the sign.
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 4)
    return (s + slot * 3) % 12


def d7_si(lon: float) -> int:
    """
    D7 Saptamsha (children) — seven parts of 4°17'08" each.
        Odd signs:  start from same sign.
        Even signs: start from 7th sign from it.
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 7)
    start = s if (s % 2 == 0) else (s + 6) % 12
    return (start + slot) % 12


def d9_si(lon: float) -> int:
    """
    D9 Navamsha (marriage, dharma) — the single most important divisional chart.
    Nine parts of 3°20' each.
        Movable signs: start from same sign.
        Fixed signs:   start from 9th from it  (s+8).
        Dual signs:    start from 5th from it  (s+4).
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 9)
    if s in MOVABLE_SIGNS:
        start = s
    elif s in FIXED_SIGNS:
        start = (s + 8) % 12
    else:
        start = (s + 4) % 12
    return (start + slot) % 12


def d10_si(lon: float) -> int:
    """
    D10 Dashamsha (career) — ten parts of 3° each.
        Odd signs:  start from same sign.
        Even signs: start from 9th sign from it.
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 10)
    start = s if (s % 2 == 0) else (s + 8) % 12
    return (start + slot) % 12


def d12_si(lon: float) -> int:
    """
    D12 Dvadashamsha (parents) — twelve parts of 2°30' each.
        All signs: start from same sign.
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 12)
    return (s + slot) % 12


def d16_si(lon: float) -> int:
    """
    D16 Shodashamsha (vehicles, comforts) — sixteen parts of 1°52'30" each.
        Movable signs: start from Aries        (0).
        Fixed signs:   start from Leo          (4).
        Dual signs:    start from Sagittarius  (8).
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 16)
    if s in MOVABLE_SIGNS:
        start = 0
    elif s in FIXED_SIGNS:
        start = 4
    else:
        start = 8
    return (start + slot) % 12


def d20_si(lon: float) -> int:
    """
    D20 Vimshamsha (spiritual progress) — twenty parts of 1°30' each.
        Movable signs: start from Aries        (0).
        Fixed signs:   start from Sagittarius  (8).
        Dual signs:    start from Leo          (4).
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 20)
    if s in MOVABLE_SIGNS:
        start = 0
    elif s in FIXED_SIGNS:
        start = 8
    else:
        start = 4
    return (start + slot) % 12


def d24_si(lon: float) -> int:
    """
    D24 Chaturvimshamsha (education) — twenty-four parts of 1°15' each.
        Odd signs:  start from Leo    (4).
        Even signs: start from Cancer (3).
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 24)
    start = 4 if (s % 2 == 0) else 3
    return (start + slot) % 12


def d27_si(lon: float) -> int:
    """
    D27 Saptavimshamsha / Bhamsha (strengths & weaknesses) — 27 parts.
    Following the BPHS-as-implemented-by-JH convention, treats it like D9:
        Movable signs: start from same sign.
        Fixed signs:   start from 9th from it  (s+8).
        Dual signs:    start from 5th from it  (s+4).
    Some lineages start by element (Fire from Aries, Earth from Cancer, ...);
    Jagannatha Hora and most modern Indian softwares use the rule above.
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 27)
    if s in MOVABLE_SIGNS:
        start = s
    elif s in FIXED_SIGNS:
        start = (s + 8) % 12
    else:
        start = (s + 4) % 12
    return (start + slot) % 12


def d30_si(lon: float) -> int:
    """
    D30 Trimshamsha (misfortunes) — sign-of-arrival depends on which
    unequal sub-division you fall into, with a different mapping for odd
    vs even signs.
        Odd signs:  0-5°→Aries(0)  5-10°→Aquarius(10) 10-18°→Sag(8)
                    18-25°→Gemini(2)  25-30°→Libra(6)
        Even signs: 0-5°→Taurus(1) 5-12°→Virgo(5)    12-20°→Pisces(11)
                    20-25°→Capricorn(9)  25-30°→Scorpio(7)
    """
    s = sign_index_from_lon(lon)
    d = lon % 30
    if s % 2 == 0:                # classical odd sign
        if d < 5:  return 0
        if d < 10: return 10
        if d < 18: return 8
        if d < 25: return 2
        return 6
    else:                          # classical even sign
        if d < 5:  return 1
        if d < 12: return 5
        if d < 20: return 11
        if d < 25: return 9
        return 7


def d40_si(lon: float) -> int:
    """
    D40 Khavedamsha / Chatvarimshamsha (maternal legacy) — 40 parts of 0°45'.
        Odd signs:  start from Aries (0).
        Even signs: start from Libra (6).
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 40)
    start = 0 if (s % 2 == 0) else 6
    return (start + slot) % 12


def d45_si(lon: float) -> int:
    """
    D45 Akshavedamsha (paternal legacy / character) — 45 parts of 0°40'.
        Movable signs: start from Aries        (0).
        Fixed signs:   start from Leo          (4).
        Dual signs:    start from Sagittarius  (8).
    """
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 45)
    if s in MOVABLE_SIGNS:
        start = 0
    elif s in FIXED_SIGNS:
        start = 4
    else:
        start = 8
    return (start + slot) % 12


def d60_si(lon: float) -> int:
    """
    D60 Shashtiamsha (past karma) — the deepest and most sensitive varga.

    BPHS Ch. 7 / Jagannatha Hora convention: 60 parts of 0°30' each, count
    forward from the sign itself for all signs.

        D60_sign = (natal_sign + part_number) % 12

    where part_number = int((lon % 30) * 2), giving 0..59.

    Note: some older Indian softwares (and the original astro_calc.py in this
    repo) used a "count from Aries for odd / count backward from Pisces for
    even" variant. We standardise on the BPHS/JH version because (a) it is
    explicitly stated in BPHS, (b) it matches Jagannatha Hora (most rigorous
    open reference), and (c) it matches the Parashara's Light default.

    Sensitivity warning: D60 changes sign every ~2 minutes of birth time.
    PDFs should flag the D60 page as "low confidence" when exact_time is False
    until BTR has been applied.
    """
    s = sign_index_from_lon(lon)
    part = min(int((lon % 30) * 2), 59)
    return (s + part) % 12


# ─────────────────────────────────────────────────────────────────────────────
# The full Shodashavarga registry
# ─────────────────────────────────────────────────────────────────────────────

VARGA_REGISTRY: list[tuple[int, str, str, callable]] = [
    (1,  "Rasi",              "Body, physical self, all of life",            d1_si),
    (2,  "Hora",              "Wealth & monetary inheritance",                d2_si),
    (3,  "Drekkana",          "Siblings, courage, initiative",                d3_si),
    (4,  "Chaturthamsha",     "Property, vehicles, mother's home",            d4_si),
    (7,  "Saptamsha",         "Children, progeny",                            d7_si),
    (9,  "Navamsha",          "Marriage, dharma, the soul",                   d9_si),
    (10, "Dashamsha",         "Career, profession, public standing",          d10_si),
    (12, "Dvadashamsha",      "Parents, ancestors",                           d12_si),
    (16, "Shodashamsha",      "Vehicles, comforts, possessions",              d16_si),
    (20, "Vimshamsha",        "Spiritual progress, devotion",                 d20_si),
    (24, "Chaturvimshamsha",  "Education, learning, knowledge",               d24_si),
    (27, "Saptavimshamsha",   "Strengths & weaknesses (Bhamsha)",             d27_si),
    (30, "Trimshamsha",       "Misfortunes, troubles, evils",                 d30_si),
    (40, "Khavedamsha",       "Maternal legacy, auspicious effects",          d40_si),
    (45, "Akshavedamsha",     "Paternal legacy, character",                   d45_si),
    (60, "Shashtiamsha",      "Past-life karma (most sensitive varga)",       d60_si),
]


def compute_all(chart) -> dict[int, "DivisionalChart"]:
    """
    Build the full Shodashavarga from a populated KundliChart.

    Returns a dict keyed by varga number → DivisionalChart, e.g.
        result[9] is the D9 Navamsha.

    Each DivisionalChart contains the Lagna sign and all 9 planet signs
    *within that varga*. The PDF templates iterate over this registry to
    render each chart.
    """
    from math_engine.kundli.chart import DivisionalChart

    out: dict[int, DivisionalChart] = {}
    lagna_lon = chart.lagna.longitude
    for n, name, purpose, fn in VARGA_REGISTRY:
        planet_signs = {p: fn(pp.longitude) for p, pp in chart.planets.items()}
        out[n] = DivisionalChart(
            name=f"D{n} {name}",
            varga_number=n,
            purpose=purpose,
            lagna_sign_index=fn(lagna_lon),
            planet_signs=planet_signs,
        )
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: Vimshopaka Bala helpers
# ─────────────────────────────────────────────────────────────────────────────
#
# Vimshopaka is a weighted strength based on a planet's dignity across a set
# of vargas. There are three classical sets:
#
#   Sapta-varga (D1, D2, D3, D7, D9, D12, D30) — totals 20 points.
#   Dasa-varga  (above + D10, D16, D60)        — totals 20 points.
#   Shodasa-varga (all 16)                     — totals 20 points.
#
# The weight per varga differs in each set. This is consumed by shadbala.py.
# ─────────────────────────────────────────────────────────────────────────────

VIMSHOPAKA_SAPTA = {1: 5, 2: 2, 3: 3, 7: 2.5, 9: 4.5, 12: 2, 30: 1}
VIMSHOPAKA_DASA  = {1: 3, 2: 1.5, 3: 1.5, 7: 1.5, 9: 1.5, 10: 1.5,
                    12: 1.5, 16: 1.5, 30: 1.5, 60: 5}
VIMSHOPAKA_SHODASA = {1: 3.5, 2: 1, 3: 1, 4: 0.5, 7: 0.5, 9: 3, 10: 0.5,
                      12: 0.5, 16: 2, 20: 0.5, 24: 0.5, 27: 0.5, 30: 1,
                      40: 0.5, 45: 0.5, 60: 4}
