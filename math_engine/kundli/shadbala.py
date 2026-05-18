"""
math_engine/kundli/shadbala.py
==============================

Shadbala (six-fold strength) + Bhava Bala + Vimshopaka Bala — the
quantitative planetary-strength layer of the kundli.

Wraps the existing `calculate_shadbala`, `get_bhava_bala`, and `calc_drishti`
helpers from astro_calc.py and presents the results in a structured form
the PDF templates can render directly.

Shadbala output is in Rupas (1 Rupa = 60 Virupas). The classical minimum-
required Rupas (Ishta Bala) thresholds, per BPHS:

    Sun:     6.5  Rupas
    Moon:    6.0
    Mars:    5.0
    Mercury: 7.0
    Jupiter: 6.5
    Venus:   5.5
    Saturn:  5.0

A planet meeting/exceeding its threshold is "strong"; below = "weak".

Vimshopaka Bala is a separate 20-point weighted index over the divisional
charts (Sapta-Varga, Dasa-Varga, or Shodasa-Varga selection). Used here in
the Shodasa-Varga (16-chart) form for the most complete strength reading.
"""

from __future__ import annotations

from math_engine.constants import SIGN_LORDS_MAP
from math_engine.astro_calc import (
    calculate_shadbala as _legacy_shadbala,
)
from math_engine.kundli.divisional import (
    VARGA_REGISTRY, VIMSHOPAKA_SHODASA,
)


# Per-planet minimum-required Shadbala (Rupas) per BPHS / Saravali.
SHADBALA_MIN_RUPAS = {
    "Sun":     6.5,
    "Moon":    6.0,
    "Mars":    5.0,
    "Mercury": 7.0,
    "Jupiter": 6.5,
    "Venus":   5.5,
    "Saturn":  5.0,
}


# ─────────────────────────────────────────────────────────────────────────────
# Minimal "facts" stub for the legacy shadbala helper.
# The legacy function reads only `planet_strength(facts, planet)` from facts,
# which itself reads `tags` (dignity strings) and a few other markers. We
# construct just enough to make it work cleanly from a KundliChart.
# ─────────────────────────────────────────────────────────────────────────────

def _build_legacy_facts(chart) -> dict:
    facts = {
        "planets": {},
        "lagna_sign": chart.lagna.sign,
        "lagna_lord": chart.lagna.lord,
        "neecha_bhanga": set(),
        "manglik": "",
        "karakas": {},
    }
    for pname, pp in chart.planets.items():
        tags = set()
        if pp.dignity == "Exalted":      tags.add("Exalted")
        if pp.dignity == "Debilitated":  tags.add("Debilitated")
        if pp.dignity == "Own Sign":     tags.add("Own Sign")
        if pp.dignity == "Mooltrikona":  tags.add("Mooltrikona")
        if pp.is_retrograde:             tags.add("Retrograde")
        if pp.is_combust:                tags.add(f"Combust({pp.combust_orb:.0f}°)")
        facts["planets"][pname] = {
            "house":    pp.house,
            "sign":     pp.sign,
            "tags":     tags,
            "nak_lord": pp.nakshatra_lord,
            "avastha":  pp.avastha,
            "kp_sigs":  set(),
            "war":      "",
        }
    return facts


# ─────────────────────────────────────────────────────────────────────────────
# Vimshopaka Bala — 16-fold dignity-weighted strength (Shodasa-Varga form)
# ─────────────────────────────────────────────────────────────────────────────

def _dignity_factor(planet_sign: int, planet: str) -> float:
    """
    A simple 0..1 factor for how 'dignified' a planet is in a given sign.

    Returns:
        1.0  if exalted, own sign, or mooltrikona
        0.5  if in a sign of its friend (classical Naisargika friendship —
             not implemented in full; uses a coarse approximation)
        0.0  if debilitated
        0.5  otherwise (neutral)
    """
    DIG = {
        "Sun":     (4,  6),
        "Moon":    (1,  7),
        "Mars":    (9,  3),
        "Mercury": (5, 11),
        "Jupiter": (3,  9),
        "Venus":   (11, 5),
        "Saturn":  (6,  0),
    }
    OWN = {
        "Sun":     {4},
        "Moon":    {3},
        "Mars":    {0, 7},
        "Mercury": {2, 5},
        "Jupiter": {8, 11},
        "Venus":   {1, 6},
        "Saturn":  {9, 10},
    }
    if planet not in DIG:
        return 0.5
    exalt, debil = DIG[planet]
    if planet_sign == exalt:
        return 1.0
    if planet_sign == debil:
        return 0.0
    if planet_sign in OWN.get(planet, set()):
        return 1.0
    return 0.5


def _vimshopaka_for_planet(chart, planet: str) -> float:
    """Sum (varga_dignity_factor × varga_weight) over the 16 vargas → 0..20."""
    if planet in ("Rahu", "Ketu"):
        return 10.0  # nominal; nodes lack standard dignity
    total = 0.0
    for n, _name, _purpose, fn in VARGA_REGISTRY:
        weight = VIMSHOPAKA_SHODASA.get(n, 0)
        if weight == 0:
            continue
        planet_long = chart.planets[planet].longitude
        varga_sign = fn(planet_long)
        total += weight * _dignity_factor(varga_sign, planet)
    return round(total, 2)


# ─────────────────────────────────────────────────────────────────────────────
# Bhava Bala — simplified composite per house
# ─────────────────────────────────────────────────────────────────────────────
# Classical Bhava Bala has many sub-components (Adhipati, Digbala, Drig).
# We compute a clean composite using:
#     - SAV (Sarvashtakavarga) bindus for the house  (0..56)         × 1.5 wt
#     - Bhava-lord's own Shadbala Rupas (clamped 0..10)               × 4.0 wt
#     - Benefic vs malefic occupation/aspect net                      ± 5
# Output is in Rupas-equivalent units (roughly 0..15).
# ─────────────────────────────────────────────────────────────────────────────

_NAT_BEN = {"Jupiter", "Venus", "Mercury", "Moon"}
_NAT_MAL = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def _compute_bhava_bala(chart, shadbala_totals, sav_by_house) -> dict:
    """Bhava Bala for all 12 houses. Returns {house: rupas}."""
    out = {}
    for h in range(1, 13):
        sign_idx = (chart.lagna.sign_index + h - 1) % 12
        lord = SIGN_LORDS_MAP[sign_idx]
        lord_rupas = float(shadbala_totals.get(lord, 5.0))

        sav = sav_by_house[h - 1] if sav_by_house and h - 1 < len(sav_by_house) else 28
        sav_component = (sav / 56.0) * 1.5 * 5.0  # max ~7.5

        lord_component = min(lord_rupas, 10.0) * 0.4  # max ~4

        # Aspect-occupation modifier
        modifier = 0.0
        for pname, pp in chart.planets.items():
            if pp.house == h:
                modifier += 0.5 if pname in _NAT_BEN else -0.5 if pname in _NAT_MAL else 0
        out[h] = round(sav_component + lord_component + modifier, 2)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def compute(chart) -> tuple[dict, dict]:
    """
    Compute Shadbala + Bhava Bala + Vimshopaka Bala for the chart.

    Returns:
        (shadbala_dict, bhava_bala_dict)
    where shadbala_dict has shape:
        {
          "totals":     {planet: rupas},
          "minimums":   {planet: required_rupas},
          "strong":     [planets meeting minimum],
          "weak":       [planets below minimum],
          "vimshopaka": {planet: 0..20},      # Shodasa-Varga form
          "strongest":  (planet, rupas),
          "weakest":    (planet, rupas),
        }
    """
    facts = _build_legacy_facts(chart)

    totals = {}
    for pname, pp in chart.planets.items():
        if pname in ("Rahu", "Ketu"):
            totals[pname] = 5.0
            continue
        try:
            rupas = _legacy_shadbala(
                pname, pp.longitude, pp.speed,
                chart.lagna.longitude, chart.lagna.sign_index,
                facts,
                {n: (p.longitude, p.speed) for n, p in chart.planets.items()
                 if n not in ("Rahu", "Ketu")},
                chart.julian_day_ut,
            )
        except Exception:
            rupas = 5.0
        totals[pname] = round(float(rupas), 2)

    # Nodes have no classical Shadbala threshold — exclude them from the
    # strong/weak audit (they always appear in the "neutral" tier).
    classical = {p for p in totals if p not in ("Rahu", "Ketu")}
    strong = [p for p in classical if totals[p] >= SHADBALA_MIN_RUPAS[p]]
    weak   = [p for p in classical if totals[p] <  SHADBALA_MIN_RUPAS[p]]

    ranked = sorted(((p, r) for p, r in totals.items() if p in classical),
                    key=lambda kv: kv[1], reverse=True)
    strongest = ranked[0]
    weakest   = ranked[-1]

    vimshopaka = {p: _vimshopaka_for_planet(chart, p) for p in chart.planets}

    shadbala_out = {
        "totals":     totals,
        "minimums":   dict(SHADBALA_MIN_RUPAS),
        "strong":     strong,
        "weak":       weak,
        "vimshopaka": vimshopaka,
        "strongest":  strongest,
        "weakest":    weakest,
    }

    # Bhava Bala — uses the SAV we just produced
    sav_by_house = (chart.ashtakavarga or {}).get("sav_by_house", [])
    bhava_bala = _compute_bhava_bala(chart, totals, sav_by_house)
    return shadbala_out, bhava_bala
