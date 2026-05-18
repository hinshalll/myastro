"""
math_engine/kundli/sudarshan.py
===============================

Sudarshan Chakra — a composite "three-eye" view of the chart that reads
every planet's placement from three different reference points simultaneously:

    1. From Lagna  (the physical body, environment, this-life identity)
    2. From Moon   (the mind, emotion, mother, daily life)
    3. From Sun    (the soul, father, vitality, public role)

When a planet is well-placed from ALL THREE references, its significations
manifest powerfully. When only from one or two, the effect is partial. The
classical predictive heuristic: read every life topic three ways and average.

This module produces a single dict with each planet's "tri-view" house, plus
per-house occupant lists from each lens — directly consumable by the PDF
template that draws the three concentric chart wheels.
"""

from __future__ import annotations


def _whole_sign_house(ref_sign: int, planet_sign: int) -> int:
    """Whole-sign house number (1..12) of `planet_sign` viewed from `ref_sign`."""
    return ((planet_sign - ref_sign) % 12) + 1


def build(chart) -> dict:
    """
    Build the Sudarshan Chakra data structure.

    Returns:
        {
          "references": {"lagna": <sign_idx>, "moon": <sign_idx>, "sun": <sign_idx>},
          "planet_views": {
              "Sun": {"from_lagna": 8, "from_moon": 5, "from_sun": 1},
              ...
          },
          "house_occupants": {
              "from_lagna": {1: [...], 2: [...], ...},
              "from_moon":  {1: [...], ...},
              "from_sun":   {1: [...], ...},
          },
          "triple_strong": [planet, ...],  # well-placed from all three
          "triple_weak":   [planet, ...],  # afflicted from all three (dusthanas)
        }
    """
    refs = {
        "lagna": chart.lagna.sign_index,
        "moon":  chart.planets["Moon"].sign_index,
        "sun":   chart.planets["Sun"].sign_index,
    }

    planet_views: dict[str, dict[str, int]] = {}
    house_occupants: dict[str, dict[int, list[str]]] = {
        f"from_{key}": {h: [] for h in range(1, 13)} for key in refs
    }

    for pname, pp in chart.planets.items():
        view = {
            "from_lagna": _whole_sign_house(refs["lagna"], pp.sign_index),
            "from_moon":  _whole_sign_house(refs["moon"],  pp.sign_index),
            "from_sun":   _whole_sign_house(refs["sun"],   pp.sign_index),
        }
        planet_views[pname] = view
        house_occupants["from_lagna"][view["from_lagna"]].append(pname)
        house_occupants["from_moon"][view["from_moon"]].append(pname)
        house_occupants["from_sun"][view["from_sun"]].append(pname)

    GOOD = {1, 4, 5, 7, 9, 10, 11}     # kendras + trikonas + 11th (gain)
    BAD  = {6, 8, 12}                  # dusthanas

    triple_strong: list[str] = []
    triple_weak:   list[str] = []
    for pname, v in planet_views.items():
        if v["from_lagna"] in GOOD and v["from_moon"] in GOOD and v["from_sun"] in GOOD:
            triple_strong.append(pname)
        if v["from_lagna"] in BAD and v["from_moon"] in BAD and v["from_sun"] in BAD:
            triple_weak.append(pname)

    return {
        "references": refs,
        "planet_views": planet_views,
        "house_occupants": house_occupants,
        "triple_strong": triple_strong,
        "triple_weak":   triple_weak,
    }
