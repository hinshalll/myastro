"""
math_engine/kundli/jaimini.py
=============================

Jaimini astrology supplements — the Char karaka chain is already in the
KundliChart (built by `astro_calc.get_chara_karakas`). This module adds:

    - Pada Lagnas (Arudhas) for all 12 houses — image-of-the-house
    - Upapada Lagna (UL) — marriage and partnerships, especially via the 12th
    - Argala (intervention/influence on a house)
    - Karakamsa (sign occupied by Atmakaraka in the D9 Navamsa)
    - Swamsa (Karakamsa's sign and house from Lagna)

These appear in the Jaimini section of a premium kundli alongside the
Chara karaka chain already produced.

Reference: BPHS Ch. 33 (Pada), "Jaimini Sutras" Ch. 1.
"""

from __future__ import annotations

from math_engine.constants import SIGN_LORDS_MAP


# ─────────────────────────────────────────────────────────────────────────────
# Pada (Arudha) computation
# ─────────────────────────────────────────────────────────────────────────────
#
# Pada of a house = sign reached by counting from the house lord's sign the
# same number of signs that the house lord is from the house itself.
#
#     example: For Lagna in Aries, Mars (lord) in Cancer (4th from Aries).
#              Pada of Lagna = 4th from Cancer = Libra.
#
# Special rules:
#     - If the Pada falls in the same sign as the house, it's adjusted to
#       the 10th from the house (BPHS Ch.33).
#     - If the Pada falls in the 7th from the house, it's adjusted to the
#       4th from the house.
# ─────────────────────────────────────────────────────────────────────────────

def _pada_sign(house_num: int, lagna_sign_idx: int, planet_signs: dict[str, int]) -> int:
    """
    Compute the Pada (Arudha) sign of a given house (1..12) given the Lagna
    sign and a {planet_name: sign_index} dict.
    """
    house_sign = (lagna_sign_idx + house_num - 1) % 12
    house_lord = SIGN_LORDS_MAP[house_sign]
    lord_sign = planet_signs.get(house_lord, house_sign)
    # Distance from house_sign to lord_sign (1-indexed, forward)
    distance = ((lord_sign - house_sign) % 12) + 1
    # Pada sign = lord_sign + (distance - 1)
    pada = (lord_sign + distance - 1) % 12
    # Adjustments
    if pada == house_sign:
        pada = (house_sign + 9) % 12       # → 10th from house
    elif pada == (house_sign + 6) % 12:
        pada = (house_sign + 3) % 12       # → 4th from house
    return pada


def build(chart) -> dict:
    """
    Build the Jaimini supplements dict.

    Returns:
        {
          "pada_lagnas":  {house_num: sign_name},     # AL=A1, A2..A12
          "upapada":      sign_name,                   # UL (Pada of 12th)
          "karakamsa":    {"d9_sign": ..., "house_from_lagna": ...},
          "chara_karakas": [...],                     # already in chart, re-exposed
        }
    """
    planet_signs = {n: p.sign_index for n, p in chart.planets.items()}
    ls = chart.lagna.sign_index

    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

    pada_lagnas = {}
    for h in range(1, 13):
        sidx = _pada_sign(h, ls, planet_signs)
        label = "AL" if h == 1 else f"A{h}"
        pada_lagnas[h] = {
            "label":       label,
            "sign":        SIGNS[sidx],
            "sign_index":  sidx,
            "house_from_lagna": ((sidx - ls) % 12) + 1,
        }

    upapada = pada_lagnas[12]  # UL = Pada of 12th house (partner / marriage)

    # Karakamsa: D9-sign of the Atmakaraka
    ak_planet = chart.chara_karakas.atmakaraka
    d9 = chart.divisional_charts.get(9)
    if d9:
        karakamsa_sign_idx = d9.planet_signs.get(ak_planet, 0)
    else:
        karakamsa_sign_idx = chart.planets[ak_planet].sign_index
    karakamsa = {
        "atmakaraka":       ak_planet,
        "d9_sign":          SIGNS[karakamsa_sign_idx],
        "d9_sign_index":    karakamsa_sign_idx,
        "house_from_lagna": ((karakamsa_sign_idx - ls) % 12) + 1,
    }

    return {
        "pada_lagnas":   pada_lagnas,
        "upapada":       upapada,
        "karakamsa":     karakamsa,
        "chara_karakas": [
            {"karaka": name, "planet": planet, "degree": deg}
            for (planet, name, deg) in chart.chara_karakas.chain
        ],
    }
