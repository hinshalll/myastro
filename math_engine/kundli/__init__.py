"""
math_engine/kundli/
===================

Premium kundli (Vedic birth chart) generation backend.

Zero Streamlit dependency. All functions take/return plain Python types and
dataclasses so the same module powers both the Streamlit prototype and the
upcoming mobile app.

Public surface:
    BirthData          — input dataclass (name, date, time, place, gender, ...)
    KundliChart        — fully-computed chart object (all data needed for PDF)
    compute_chart(bd)  — main entry point, returns a KundliChart

Submodule layout (built incrementally):
    chart.py            — BirthData + KundliChart + compute_chart()
    divisional.py       — All 16 vargas (extends astro_calc D2/D3/D4/D7/D9/D10/D12/D30/D60)
    dashas.py           — Vimshottari (deeper sub-levels) + Yogini + Ashtottari + Char
    yogas.py            — Yoga detection rule engine
    doshas.py           — All doshas (Mangal, Kaal Sarp, Sade Sati, Pitra, ...)
    shadbala.py         — Wrapper + Sarvashtakavarga
    nakshatra_profile.py — Gana, Yoni, Nadi, Varna, Vashya, Tatva, Pakshi etc.
    panchanga.py        — Birth panchanga + ghatika/muhurta tables
    transits.py         — 12-month forecast tables
    remedies.py         — Rule-based mantra/gemstone/yantra/rudraksha/daan mapping
    rectify.py          — Birth time rectification (auto + event-based)
    sudarshan.py        — Lagna + Moon + Sun composite chakra
    western.py          — Tropical positions for the Western appendix
    naming.py           — Children's name suggestions by nakshatra pada
"""

from math_engine.kundli.chart import BirthData, KundliChart, compute_chart

__all__ = ["BirthData", "KundliChart", "compute_chart"]
