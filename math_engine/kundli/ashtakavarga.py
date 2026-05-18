"""
math_engine/kundli/ashtakavarga.py
==================================

The complete Ashtakavarga predictive framework — the most quantitative tool
in classical Vedic astrology. Every house gets a "bindu" (benefic-point)
score from each of 8 reference points (7 grahas + Lagna), with the totals
used to gauge house strength, transit results, and longevity.

Pipeline (BPHS Ch. 76–78):

    1. Bhinnashtakavarga (BAV) — one 12-house grid per graha (0..8 per house).
       Already implemented in astro_calc.calculate_ashtakavarga.
    2. Sarvashtakavarga (SAV) — sum of all 7 BAVs by house (0..56).
    3. Trikona Shodhana — within each trine of signs {1,5,9}, {2,6,10},
       {3,7,11}, {4,8,12}, subtract the minimum bindu from all three (or
       zero them if any is zero, per BPHS).
    4. Ekadhipatya Shodhana — for each pair of signs ruled by the same
       planet (Mars: Ari/Sco, Venus: Tau/Lib, Mer: Gem/Vir, Jup: Sag/Pis,
       Sat: Cap/Aqu), reduce per the occupation rule.
    5. Shodhita Pinda — the post-reduction bindu, multiplied by graha-
       specific Shodhya constants → gives the strength used in transit
       reading and longevity calculation.

This module exposes the complete pipeline + convenient summaries for the PDF.
"""

from __future__ import annotations

from math_engine.astro_calc import (
    calculate_ashtakavarga as _bav_calc,
    sign_index_from_lon,
    get_planet_lon_helper,
)


# ─────────────────────────────────────────────────────────────────────────────
# Pre-known classical constants
# ─────────────────────────────────────────────────────────────────────────────

# Trikonas of the zodiac (0-indexed sign groups).
TRIKONA_GROUPS: list[list[int]] = [
    [0, 4, 8],    # Aries, Leo, Sagittarius (fire trine)
    [1, 5, 9],    # Taurus, Virgo, Capricorn (earth trine)
    [2, 6, 10],   # Gemini, Libra, Aquarius (air trine)
    [3, 7, 11],   # Cancer, Scorpio, Pisces (water trine)
]

# Each planet's two signs of rulership (used in Ekadhipatya).
EKADHIPATYA_PAIRS: dict[str, tuple[int, int]] = {
    "Mars":    (0, 7),    # Aries, Scorpio
    "Venus":   (1, 6),    # Taurus, Libra
    "Mercury": (2, 5),    # Gemini, Virgo
    "Jupiter": (8, 11),   # Sagittarius, Pisces
    "Saturn":  (9, 10),   # Capricorn, Aquarius
    # Sun (Leo) and Moon (Cancer) have only one sign — no reduction.
}

# Shodhya multipliers per planet (BPHS) — applied to the post-reduction
# bindu count to yield the predictive "Shodhya Pinda".
SHODHYA_PINDA_MULTIPLIER = {
    "Sun":     5,
    "Moon":    5,
    "Mars":    8,
    "Mercury": 5,
    "Jupiter": 10,
    "Venus":   7,
    "Saturn":  5,
}


# ─────────────────────────────────────────────────────────────────────────────
# Reductions
# ─────────────────────────────────────────────────────────────────────────────

def _trikona_shodhana(bav_by_sign: list[int]) -> list[int]:
    """
    Apply Trikona Shodhana to a 12-sign bindu list (in zodiac order:
    index 0 = Aries, …, 11 = Pisces).

    Rule (BPHS Ch.78):
        - In each trine, if any sign has zero bindus → all three become 0.
        - Otherwise subtract the smallest bindu from all three.
    """
    out = list(bav_by_sign)
    for trine in TRIKONA_GROUPS:
        vals = [out[s] for s in trine]
        if min(vals) == 0:
            for s in trine:
                out[s] = 0
        else:
            m = min(vals)
            for s in trine:
                out[s] -= m
    return out


def _ekadhipatya_shodhana(
    bav_by_sign: list[int],
    occupied_signs: set[int],
) -> list[int]:
    """
    Apply Ekadhipatya Shodhana given which zodiac signs are occupied by any
    of the 7 grahas (Rahu/Ketu excluded by convention).

    Rule:
        - Sign A occupied, sign B unoccupied → bindus of B = 0.
        - Both occupied → smaller bindu becomes 0 (or both zero if equal).
        - Neither occupied → smaller bindu becomes 0 (or both zero if equal).
        Net: the "weaker" of the pair is suppressed.
    """
    out = list(bav_by_sign)
    for _planet, (a, b) in EKADHIPATYA_PAIRS.items():
        va, vb = out[a], out[b]
        occ_a, occ_b = a in occupied_signs, b in occupied_signs
        if occ_a and not occ_b:
            out[b] = 0
        elif occ_b and not occ_a:
            out[a] = 0
        else:
            # both occupied or both unoccupied — suppress the smaller
            if va == vb:
                out[a] = 0
                out[b] = 0
            elif va < vb:
                out[a] = 0
            else:
                out[b] = 0
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def compute(chart) -> dict:
    """
    Compute the full Ashtakavarga workflow.

    Returns:
        {
          "bav_by_house": {planet: [12 ints]},   # 1..12 = H1..H12
          "bav_by_sign":  {planet: [12 ints]},   # 0..11 = Ari..Pis
          "sav_by_house":  [12 ints],            # H1..H12
          "sav_by_sign":   [12 ints],            # Ari..Pis
          "strongest_houses": [(house, bindus), ...],   # top 3
          "weakest_houses":   [(house, bindus), ...],   # bottom 3
          "shodhita_bav_by_sign": {planet: [12 ints]},  # after Trikona+Ekadhipatya
          "shodhya_pinda": {planet: int},               # × multiplier
          "shodhita_sav_by_sign": [12 ints],            # sum of shodhita BAVs
        }
    """
    # 1) Build planet_data + node lons in the form astro_calc expects.
    planet_data = {
        n: (p.longitude, p.speed)
        for n, p in chart.planets.items()
        if n not in ("Rahu", "Ketu")
    }
    r_lon = chart.planets["Rahu"].longitude
    k_lon = chart.planets["Ketu"].longitude
    ls = chart.lagna.sign_index

    # 2) BAV by HOUSE — existing helper returns this directly
    bav_house = _bav_calc(ls, planet_data, r_lon, k_lon)

    # 3) Rotate BAV-by-house into BAV-by-sign (template uses both)
    def by_house_to_by_sign(bindus_by_house):
        out = [0] * 12
        for h in range(1, 13):
            sign_idx = (ls + h - 1) % 12
            out[sign_idx] = bindus_by_house[h - 1]
        return out

    bav_sign = {p: by_house_to_by_sign(v) for p, v in bav_house.items()}

    # 4) Sarvashtakavarga
    sav_house = [0] * 12
    for v in bav_house.values():
        for i in range(12):
            sav_house[i] += v[i]
    sav_sign = by_house_to_by_sign(sav_house)

    ranked = sorted(((sav_house[i], i + 1) for i in range(12)), reverse=True)
    strongest = [(h, b) for b, h in ranked[:3]]
    weakest   = [(h, b) for b, h in ranked[-3:][::-1]]

    # 5) Reductions per planet — Trikona, then Ekadhipatya
    occupied = {chart.planets[p].sign_index for p in
                ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")}

    shodhita_bav_sign: dict[str, list[int]] = {}
    shodhya_pinda: dict[str, int] = {}
    shodhita_sav_sign = [0] * 12

    for planet, sign_vals in bav_sign.items():
        after_trikona = _trikona_shodhana(sign_vals)
        after_ekadhi  = _ekadhipatya_shodhana(after_trikona, occupied)
        shodhita_bav_sign[planet] = after_ekadhi
        for i in range(12):
            shodhita_sav_sign[i] += after_ekadhi[i]
        # Shodhya Pinda: bindus in the planet's natal sign × multiplier.
        # (BPHS: there are multiple formulations; this is the simplest one
        #  that the PDF can display alongside the longevity discussion.)
        natal_sign = chart.planets[planet].sign_index
        mult = SHODHYA_PINDA_MULTIPLIER.get(planet, 5)
        shodhya_pinda[planet] = after_ekadhi[natal_sign] * mult

    return {
        "bav_by_house":         bav_house,
        "bav_by_sign":          bav_sign,
        "sav_by_house":         sav_house,
        "sav_by_sign":          sav_sign,
        "strongest_houses":     strongest,
        "weakest_houses":       weakest,
        "shodhita_bav_by_sign": shodhita_bav_sign,
        "shodhita_sav_by_sign": shodhita_sav_sign,
        "shodhya_pinda":        shodhya_pinda,
    }
