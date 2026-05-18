"""
math_engine/kundli/yogas.py
===========================

Yoga detection wrapper.

The existing `astro_calc.detect_yogas` already implements ~20 of the most
practically important classical yogas:

    - Gajakesari, Adhi, Budha-Aditya, Chandra-Mangala
    - Pancha Mahapurusha (Ruchaka, Bhadra, Hamsa, Malavya, Shasha)
    - Raja Yoga, Dharma-Karma Adhipati Yoga, Parivartana, Viparita Raja
    - Lakshmi, Saraswati, Amala, Dhana
    - Sunapha / Anapha / Durudhura (Moon-flanking)
    - Veshi / Voshi / Ubhayachari (Sun-flanking)
    - Shubha Kartari (benefics flanking Lagna)
    - Kemadruma (negative, with cancellations)
    - Neecha Bhanga Raja Yoga

This module wraps that output, classifies each yoga by family, and converts
it into the Yoga dataclass the PDF reads. A future expansion pass can extend
toward the full 300+ classical yoga library (Saravali Nabhasa yogas,
unspecified Raja yogas, etc.) — those have diminishing predictive value
relative to the core set above and are best added incrementally.
"""

from __future__ import annotations

from math_engine.astro_calc import detect_yogas as _legacy_detect


# Classify yogas by family for the PDF section grouping.
_CATEGORY_TABLE = {
    "Gajakesari":             "Lunar — Jupiter pairing",
    "Adhi":                   "Lunar — benefics from Moon",
    "Sunapha":                "Lunar — planets from Moon",
    "Anapha":                 "Lunar — planets from Moon",
    "Durudhura":              "Lunar — planets from Moon",
    "Kemadruma":              "Lunar — affliction",
    "Veshi":                  "Solar — planets from Sun",
    "Voshi":                  "Solar — planets from Sun",
    "Ubhayachari":            "Solar — planets from Sun",
    "Budha-Aditya":           "Solar — Mercury conjunct Sun",
    "Chandra-Mangala":        "Mars — Moon-Mars",
    "Ruchaka":                "Pancha Mahapurusha — Mars",
    "Bhadra":                 "Pancha Mahapurusha — Mercury",
    "Hamsa":                  "Pancha Mahapurusha — Jupiter",
    "Malavya":                "Pancha Mahapurusha — Venus",
    "Shasha":                 "Pancha Mahapurusha — Saturn",
    "Raja":                   "Raja Yoga — power & authority",
    "Dharma-Karma":           "Raja Yoga — career & dharma",
    "Parivartana":            "Mutual sign exchange",
    "Viparita":               "Viparita Raja Yoga — rise after fall",
    "Neecha Bhanga":          "Debilitation cancellation",
    "Lakshmi":                "Wealth — prosperity yoga",
    "Saraswati":              "Knowledge — wisdom yoga",
    "Amala":                  "10th house — spotless reputation",
    "Dhana":                  "Wealth — wealth yoga",
    "Shubha Kartari":         "Lagna protection",
}


def _classify(yoga_name: str) -> str:
    for key, category in _CATEGORY_TABLE.items():
        if yoga_name.startswith(key) or key in yoga_name:
            return category
    return "Special yoga"


def _extract_planets(description: str) -> list[str]:
    """Pull planet names out of the yoga description (best-effort)."""
    out = []
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
              "Saturn", "Rahu", "Ketu"):
        if p in description and p not in out:
            out.append(p)
    return out


def detect(chart) -> list:
    """
    Detect all yogas present in the chart.

    Returns a list of Yoga dataclasses ready for PDF rendering.
    """
    from math_engine.kundli.chart import Yoga

    planet_data = {n: (p.longitude, p.speed)
                   for n, p in chart.planets.items() if n not in ("Rahu", "Ketu")}
    r_lon = chart.planets["Rahu"].longitude
    k_lon = chart.planets["Ketu"].longitude
    moon_sidx = chart.planets["Moon"].sign_index

    present, _absent = _legacy_detect(
        chart.lagna.sign_index, moon_sidx, planet_data, r_lon, k_lon,
    )

    out: list = []
    for name, description in present:
        out.append(Yoga(
            name=name,
            category=_classify(name),
            planets_involved=_extract_planets(description),
            description=description,
            activation_dasha=None,  # filled by AI narrative pass when relevant
        ))
    return out
