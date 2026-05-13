"""
pdf_engine/charts/
==================

SVG chart renderers for the three classical Indian styles:

    - North Indian (Diamond)  — Lagna at top center; signs rotate.
    - South Indian (Square)   — Signs fixed; planets move.
    - East Indian  (Bengali)  — Variation of South with corner diamonds.

All three accept a uniform input shape:

    render(*, lagna_sign_idx: int, planet_signs: dict[str, int],
            theme: dict, size: int = 400, title: str = "") -> str

`planet_signs` is {planet_name: 0..11 sign_index} for that varga. Use:

    chart.divisional_charts[1].planet_signs   # D1 Rasi
    chart.divisional_charts[9].planet_signs   # D9 Navamsha
    ... etc.

The returned string is a self-contained SVG that can be embedded directly
into HTML (no external file refs). WeasyPrint renders SVG natively.
"""

from pdf_engine.charts.north_indian import render as render_north
from pdf_engine.charts.south_indian import render as render_south
from pdf_engine.charts.east_indian  import render as render_east


STYLES = {
    "north_indian": render_north,
    "south_indian": render_south,
    "east_indian":  render_east,
}


def render(style: str, **kwargs) -> str:
    """Convenience dispatcher: render('north_indian', lagna_sign_idx=…, …)."""
    if style not in STYLES:
        raise ValueError(f"Unknown chart style: {style}. "
                         f"Choose from: {list(STYLES)}")
    return STYLES[style](**kwargs)


# Default themed palette (overridable per template/theme)
DEFAULT_THEME = {
    "frame_color":  "#7B3F00",
    "frame_width":  2,
    "bg_color":     "#FBF6E9",
    "house_text":   "#5C3317",
    "sign_text":    "#5C3317",
    "planet_text":  "#2B1810",
    "planet_font_size": 14,
    "house_font_size":  10,
    "title_color":  "#7B3F00",
    "title_font_size":  14,
    "lagna_marker_color": "#C41E3A",
    "retro_color": "#C41E3A",
}
