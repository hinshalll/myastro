"""
pdf_engine/builder.py
=====================

Orchestrator: takes (KundliChart, theme, options) → returns PDF bytes.

Pipeline:
    1. Load Jinja2 environment rooted at pdf_engine/templates.
    2. Compute SVG charts (N/S/E Indian) for D1 + the 15 other vargas.
    3. Render `base.html` with the chart + theme as context.
    4. Pipe HTML through WeasyPrint → return PDF bytes.
    5. If WeasyPrint isn't usable (Windows-dev without GTK3 runtime),
       return the rendered HTML bytes instead — caller can save as
       `.html` and browser-print until GTK3 is installed.

Returns:
    bytes — the PDF content. The Streamlit/mobile UI just hands these
    bytes to a download/share action; no temp files needed.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from pdf_engine.charts import render as render_chart_svg


# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

_PKG_ROOT = Path(__file__).parent
TEMPLATES_DIR = _PKG_ROOT / "templates"
STATIC_DIR    = _PKG_ROOT / "static"
THEMES_DIR    = TEMPLATES_DIR / "themes"


# ─────────────────────────────────────────────────────────────────────────────
# WeasyPrint availability
# ─────────────────────────────────────────────────────────────────────────────

def _weasyprint_usable() -> bool:
    """Probe whether WeasyPrint can actually render (catches missing GTK3)."""
    try:
        import weasyprint  # noqa: F401
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Jinja2 environment
# ─────────────────────────────────────────────────────────────────────────────

_jinja_env: Optional[Environment] = None


def _env() -> Environment:
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Useful filters
        _jinja_env.filters["dms"] = _filter_dms
        _jinja_env.filters["yn"]  = lambda b: "Yes" if b else "No"
    return _jinja_env


def _filter_dms(value: float) -> str:
    """Format a degree value as Dxx°MM' DMS."""
    if value is None:
        return ""
    deg = int(value); m = int((value - deg) * 60)
    return f"{deg:02d}°{m:02d}'"


# ─────────────────────────────────────────────────────────────────────────────
# Theme loading
# ─────────────────────────────────────────────────────────────────────────────

# Built-in themes (palette + decorative settings). New themes drop in here.
THEMES: dict[str, dict] = {
    "classic_vedic": {
        "name":              "Classic Vedic",
        "primary":           "#7B3F00",      # saffron-brown
        "accent":            "#C41E3A",      # cardinal red
        "ink":               "#2B1810",
        "paper":             "#FBF6E9",      # parchment
        "muted":             "#8A6E4E",
        "heading_font":      "Cinzel, 'Cormorant Garamond', serif",
        "body_font":         "'Cormorant Garamond', Georgia, serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Janma Kundli",
        "ornament":          "lotus",
        "page_numeral_color":"#7B3F00",
    },
    "ganesha": {
        "name":              "Ganesha",
        "primary":           "#B8860B",      # dark goldenrod
        "accent":            "#8B0000",      # dark red
        "ink":               "#3B2F2F",
        "paper":             "#FFF8DC",      # cornsilk
        "muted":             "#9B7E40",
        "heading_font":      "Cinzel, 'Cormorant Garamond', serif",
        "body_font":         "'Cormorant Garamond', Georgia, serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Shri Ganesha Janma Kundli",
        "ornament":          "ganesha",
        "page_numeral_color":"#B8860B",
    },
    "krishna": {
        "name":              "Krishna",
        "primary":           "#1F4E79",      # deep blue
        "accent":            "#D4AF37",      # gold
        "ink":               "#1A2B3D",
        "paper":             "#FBF8F1",
        "muted":             "#5C7A99",
        "heading_font":      "Cinzel, 'Cormorant Garamond', serif",
        "body_font":         "'Cormorant Garamond', Georgia, serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Shri Krishna Janma Kundli",
        "ornament":          "peacock_feather",
        "page_numeral_color":"#1F4E79",
    },
    "shiva": {
        "name":              "Shiva",
        "primary":           "#4B0082",      # indigo
        "accent":            "#C0C0C0",      # silver
        "ink":               "#1C1C1C",
        "paper":             "#F5F5F5",
        "muted":             "#7A7A82",
        "heading_font":      "Cinzel, 'Cormorant Garamond', serif",
        "body_font":         "'Cormorant Garamond', Georgia, serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Shri Mahadev Janma Kundli",
        "ornament":          "trishul",
        "page_numeral_color":"#4B0082",
    },
    "durga": {
        "name":              "Durga",
        "primary":           "#8B0000",      # dark red
        "accent":            "#FF8C00",      # dark orange
        "ink":               "#2D0A0A",
        "paper":             "#FFF8F0",
        "muted":             "#8B5A2B",
        "heading_font":      "Cinzel, 'Cormorant Garamond', serif",
        "body_font":         "'Cormorant Garamond', Georgia, serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Shri Durga Janma Kundli",
        "ornament":          "trishul_lion",
        "page_numeral_color":"#8B0000",
    },
    "lakshmi": {
        "name":              "Lakshmi",
        "primary":           "#D4AF37",      # gold
        "accent":            "#FF1493",      # deep pink
        "ink":               "#3B2F1F",
        "paper":             "#FFFAF0",
        "muted":             "#B8860B",
        "heading_font":      "Cinzel, 'Cormorant Garamond', serif",
        "body_font":         "'Cormorant Garamond', Georgia, serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Shri Mahalakshmi Janma Kundli",
        "ornament":          "lotus_gold",
        "page_numeral_color":"#D4AF37",
    },
    "saraswati": {
        "name":              "Saraswati",
        "primary":           "#FFFFFF",
        "accent":            "#B0C4DE",
        "ink":               "#2B3D4F",
        "paper":             "#F8FCFF",
        "muted":             "#6A8BAA",
        "heading_font":      "Cinzel, 'Cormorant Garamond', serif",
        "body_font":         "'Cormorant Garamond', Georgia, serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Shri Saraswati Janma Kundli",
        "ornament":          "veena_lotus",
        "page_numeral_color":"#6A8BAA",
    },
    "royal_gold": {
        "name":              "Royal Gold",
        "primary":           "#B8860B",
        "accent":            "#8B0000",
        "ink":               "#2B1810",
        "paper":             "#FAF4DC",
        "muted":             "#A0844B",
        "heading_font":      "Cinzel, 'Cormorant Garamond', serif",
        "body_font":         "'Cormorant Garamond', Georgia, serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Janma Kundli — Premium Edition",
        "ornament":          "royal_seal",
        "page_numeral_color":"#B8860B",
    },
}


# Map the theme palette → the SVG chart theme dict used by pdf_engine/charts.
def _svg_theme_from(theme: dict) -> dict:
    return {
        "frame_color":  theme["primary"],
        "frame_width":  2,
        "bg_color":     theme["paper"],
        "house_text":   theme["muted"],
        "sign_text":    theme["muted"],
        "planet_text":  theme["ink"],
        "title_color":  theme["primary"],
        "lagna_marker_color": theme["accent"],
        "retro_color":  theme["accent"],
        "planet_font_size": 14,
        "house_font_size":  10,
        "title_font_size":  14,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers — Devanagari transliteration for cover page
# ─────────────────────────────────────────────────────────────────────────────

def _to_devanagari(name: str) -> str:
    """
    Render the native's name in Devanagari script. Uses indic-transliteration
    if installed; falls back to the original Latin name otherwise.
    """
    try:
        from indic_transliteration.sanscript import transliterate, IAST, DEVANAGARI
        return transliterate(name, IAST, DEVANAGARI)
    except Exception:
        return name


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def build_kundli_pdf(
    chart,
    *,
    theme_name: str = "classic_vedic",
    chart_style: str = "north_indian",
    language: str = "en",
    sections: Optional[list[str]] = None,
    include_western_appendix: bool = True,
    include_ai_narrative: bool = True,
) -> bytes:
    """
    Build the kundli PDF for `chart`. Returns PDF bytes (or HTML bytes if
    WeasyPrint isn't available — caller can detect by checking the magic
    header: PDFs start with b"%PDF").

    Parameters
    ----------
    chart : KundliChart
        Fully-computed chart (from math_engine.kundli.compute_chart).
    theme_name : str
        One of THEMES keys.
    chart_style : str
        "north_indian" | "south_indian" | "east_indian"
    language : str
        Language code: en | hi | ta | te | mr | bn | gu
    sections : list[str] | None
        Optional ordered list of section template names to include.
        None = full premium set.
    include_western_appendix : bool
        Whether to render the Western chart appendix.
    """
    if theme_name not in THEMES:
        raise ValueError(f"Unknown theme: {theme_name}. "
                         f"Available: {list(THEMES)}")
    theme = THEMES[theme_name]
    svg_theme = _svg_theme_from(theme)

    # Build SVG renders for D1 + all other vargas at once — templates index in.
    retrograde = {p for p, pp in chart.planets.items() if pp.is_retrograde}
    combust    = {p for p, pp in chart.planets.items() if pp.is_combust}

    chart_svgs: dict[int, str] = {}
    for varga_n, varga in chart.divisional_charts.items():
        chart_svgs[varga_n] = render_chart_svg(
            style=chart_style,
            lagna_sign_idx=varga.lagna_sign_index,
            planet_signs=varga.planet_signs,
            theme=svg_theme,
            size=320,
            title="",  # title is set by the HTML template
            retrograde=retrograde,
            combust=combust,
        )

    # Section list — sensible default ordering
    sections = sections or [
        "cover",
        "birth_details",
        "panchanga",
        "nakshatra_profile",
        "planetary_positions",
        "rasi_chart",
        "divisional_charts",
        "dasha_vimshottari",
        "yogas",
        "doshas",
        "karmic_story" if include_ai_narrative else None,
        "decade_predictions" if include_ai_narrative else None,
        "shadbala",
        "ashtakavarga",
        "remedies",
        "transit_forecast",
        "varshaphala",
        "jaimini",
        "kp_extras",
        "sudarshan",
        "child_naming",
        "western_appendix" if include_western_appendix else None,
    ]
    sections = [s for s in sections if s]

    # AI narrative (single batched Gemini call; ≤ ~₹5/kundli budget)
    narrative = None
    if include_ai_narrative:
        try:
            from ai_engine.kundli_narrative import generate as _narrate
            narrative = _narrate(chart, language=language)
        except Exception:
            narrative = None

    # Optionally compute Varshaphala (since not auto-attached)
    if "varshaphala" in sections and not getattr(chart, "_varshaphala_cache", None):
        try:
            from math_engine.kundli import varshaphala as _vp
            chart._varshaphala_cache = _vp.compute(chart)
        except Exception:
            chart._varshaphala_cache = None

    ctx = {
        "chart":          chart,
        "theme":          theme,
        "theme_name":     theme_name,
        "language":       language,
        "chart_style":    chart_style,
        "chart_svgs":     chart_svgs,
        "rasi_svg":       chart_svgs.get(1, ""),
        "navamsha_svg":   chart_svgs.get(9, ""),
        "sections":       sections,
        "devanagari_name": _to_devanagari(chart.birth_data.name),
        # Timezone-aware so dasha/transit comparisons work in templates
        "generated_at":   datetime.now(ZoneInfo(chart.birth_data.tz)),
        "varshaphala":    getattr(chart, "_varshaphala_cache", None),
        "narrative":      narrative,
    }

    env = _env()
    template = env.get_template("base.html")
    html_str = template.render(**ctx)

    # Try WeasyPrint
    if _weasyprint_usable():
        try:
            import weasyprint
            pdf_bytes = weasyprint.HTML(
                string=html_str,
                base_url=str(_PKG_ROOT),
            ).write_pdf()
            return pdf_bytes
        except Exception as e:
            # Fall through to HTML if WeasyPrint stumbles
            html_str = (f"<!-- WeasyPrint failed: {type(e).__name__}: {e}. "
                        f"Returning HTML for manual browser-print. -->\n"
                        + html_str)

    # HTML fallback
    return html_str.encode("utf-8")
