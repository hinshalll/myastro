"""shared.pdf — Premium kundli PDF rendering + reusable PDF helpers.

Pure backend. Zero Streamlit dependency. Returns PDF bytes (or HTML bytes
when WeasyPrint isn't installed — caller detects via b"%PDF" magic header).

Module layout (was previously one 983-line `kundli_pdf.py`, now split):
    themes.py     — Premium themes (palettes) + DEFAULT_THEME for charts
    charts.py     — SVG renderers for North / South / East Indian styles
    builder.py    — Jinja2 + WeasyPrint orchestrator (build_kundli_pdf)
    theme_art.py  — Decorative SVG art (lotus, peacock, trishul, etc.)
    astro_pdf.py  — Generic markdown→PDF helper (used by every feature)
    palm_pdf.py   — Palm-reading-specific PDF builder
"""

from shared.pdf.themes import THEMES, DEFAULT_THEME
from shared.pdf.charts import (
    render, render_chart_for_chart,
    render_north, render_south, render_east,
    STYLES, SIGN_ABBR, SIGN_ABBR_3, PLANET_ABBR,
)
from shared.pdf.builder import build_kundli_pdf

__all__ = [
    "build_kundli_pdf",
    "THEMES", "DEFAULT_THEME",
    "render", "render_chart_for_chart",
    "render_north", "render_south", "render_east",
    "STYLES", "SIGN_ABBR", "SIGN_ABBR_3", "PLANET_ABBR",
]
