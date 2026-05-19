"""shared.pdf.builder — kundli PDF orchestrator (Jinja2 + WeasyPrint).

Public API:
    build_kundli_pdf(chart, *, theme_name, chart_style, language, ...) -> bytes

Returns PDF bytes when WeasyPrint is usable; HTML bytes otherwise (caller
detects by checking the magic header b"%PDF").
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader, select_autoescape

from shared.pdf.themes import THEMES, DEFAULT_THEME
from shared.pdf.charts import render as render_chart_svg, _svg_theme_from
from shared.pdf.theme_art import (
    cover_art, cover_image_data_url,
    section_icon_data_url, ornament_divider_svg,
    page_watermark_data_url,
    section_divider, corner_ornament,
    page_border_data_url, cover_page_border_data_url,
)


# ══════════════════════════════════════════════════════════════════════════
# PDF BUILDER — Jinja2 + WeasyPrint orchestrator
# ══════════════════════════════════════════════════════════════════════════

_PKG_ROOT = Path(__file__).parent
TEMPLATES_DIR = _PKG_ROOT / "templates"
STATIC_DIR    = _PKG_ROOT / "static"
THEMES_DIR    = TEMPLATES_DIR / "themes"


def _weasyprint_usable() -> bool:
    try:
        import weasyprint  # noqa: F401
        return True
    except Exception:
        return False


_jinja_env: Optional[Environment] = None


def _filter_dms(value: float) -> str:
    if value is None:
        return ""
    deg = int(value); m = int((value - deg) * 60)
    return f"{deg:02d}°{m:02d}'"


def _env() -> Environment:
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        _jinja_env.filters["dms"] = _filter_dms
        _jinja_env.filters["yn"]  = lambda b: "Yes" if b else "No"
    return _jinja_env


# _svg_theme_from moved to shared/pdf/charts.py

def _to_devanagari(name: str) -> str:
    try:
        from indic_transliteration.sanscript import transliterate, IAST, DEVANAGARI
        return transliterate(name, IAST, DEVANAGARI)
    except Exception:
        return name


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
    """Build the kundli PDF. Returns PDF bytes (or HTML bytes when WeasyPrint
    isn't available — caller detects via the b"%PDF" magic header)."""
    if theme_name not in THEMES:
        raise ValueError(f"Unknown theme: {theme_name}. Available: {list(THEMES)}")
    theme = THEMES[theme_name]
    svg_theme = _svg_theme_from(theme)

    retrograde = {p for p, pp in chart.planets.items() if pp.is_retrograde}
    combust    = {p for p, pp in chart.planets.items() if pp.is_combust}
    d1_planet_degrees = {p: pp.longitude % 30 for p, pp in chart.planets.items()}

    chart_svgs: dict[int, str] = {}
    for varga_n, varga in chart.divisional_charts.items():
        # D1 = full labels (sign abbrs + house numbers + degrees)
        # Other vargas = minimal (planets only) — varga thumbnails are too small
        # to fit sign abbrs/house nums readably; AstroTalk-style clean look.
        is_d1 = (varga_n == 1)
        chart_svgs[varga_n] = render(
            style=chart_style,
            lagna_sign_idx=varga.lagna_sign_index,
            planet_signs=varga.planet_signs,
            theme=svg_theme,
            size=320,
            title="",
            retrograde=retrograde,
            combust=combust,
            planet_degrees=(d1_planet_degrees if is_d1 else None),
            show_house_numbers=is_d1,
            show_sign_abbr=is_d1,
            minimal=not is_d1,
        )

    sections = sections or [
        # ── Front matter ─────────────────────────────────────────────
        "cover", "birth_details", "panchanga", "nakshatra_profile",
        # ── Core chart ────────────────────────────────────────────────
        "planetary_positions", "rasi_chart", "divisional_charts",
        # ── AI-personalised life predictions (the AstroSage-style prose)
        "life_predictions" if include_ai_narrative else None,
        # ── Predictive layer ──────────────────────────────────────────
        "dasha_vimshottari", "yogas", "doshas",
        "karmic_story" if include_ai_narrative else None,
        "decade_predictions" if include_ai_narrative else None,
        # ── Deep per-element analysis (premium expansion) ────────────
        "per_house_analysis",   # 12 pages — one per bhava
        "per_planet_analysis",  # 9 pages — one per graha
        "life_domains",         # 8 pages — Career, Wealth, Health, etc.
        # ── Quantitative + remedial ──────────────────────────────────
        "shadbala", "ashtakavarga", "remedies", "lal_kitab",
        # ── Timing & forecast ────────────────────────────────────────
        "transit_forecast", "varshaphala",
        "year_predictions",     # 5 years × Vimshottari
        "auspicious_dates",     # 12-month calendar
        # ── Specialty systems ────────────────────────────────────────
        "jaimini", "kp_extras", "sudarshan", "child_naming",
        # ── Appendices ───────────────────────────────────────────────
        "western_appendix" if include_western_appendix else None,
    ]
    sections = [s for s in sections if s]

    narrative = None
    ai_content = None
    if include_ai_narrative:
        # Old karmic-story narrative (premium only — kept for back-compat)
        try:
            from features.kundli.narrative import generate as _narrate
            narrative = _narrate(chart, language=language)
        except Exception:
            narrative = None
        # NEW: per-topic life-predictions prose (AstroSage-style)
        # tier = 'free' (8 topics, ~150 words each, ~₹0.1)
        #      = 'premium' (20 topics, ~220 words each, ~₹0.4)
        try:
            from features.kundli.content import generate_kundli_content
            # Premium tier when the user opted into a deep PDF; free tier otherwise
            tier = "premium" if include_western_appendix else "free"
            ai_content = generate_kundli_content(
                chart, tier=tier, language=language,
            )
        except Exception:
            ai_content = None

    if "varshaphala" in sections and not getattr(chart, "_varshaphala_cache", None):
        try:
            from shared.astro.kundli import compute_varshaphala
            chart._varshaphala_cache = compute_varshaphala(chart)
        except Exception:
            chart._varshaphala_cache = None

    ctx = {
        "chart":           chart,
        "theme":           theme,
        "theme_name":      theme_name,
        "language":        language,
        "chart_style":     chart_style,
        "chart_svgs":      chart_svgs,
        "rasi_svg":        chart_svgs.get(1, ""),
        "navamsha_svg":    chart_svgs.get(9, ""),
        "sections":        sections,
        "devanagari_name": _to_devanagari(chart.birth_data.name),
        "generated_at":    datetime.now(ZoneInfo(chart.birth_data.tz)),
        "varshaphala":     getattr(chart, "_varshaphala_cache", None),
        "narrative":       narrative,
        "ai_content":      ai_content,
        # ── Theme imagery: deity-themed inline elements ─────────────────
        "cover_art_svg":              cover_art(theme),
        "cover_art_image_url":        cover_image_data_url(theme),
        "section_icon_data_url":      section_icon_data_url(theme),
        "ornament_divider_svg":       ornament_divider_svg(theme),
        "ornament_divider_data_url": (
            "data:image/svg+xml;base64,"
            + __import__("base64").b64encode(
                ornament_divider_svg(theme).encode("utf-8")
            ).decode("ascii")
        ),
        "page_watermark_data_url":    page_watermark_data_url(theme),
        # Back-compat (no longer drawn — empty data URLs)
        "page_border_data_url":       page_border_data_url(theme),
        "cover_page_border_data_url": cover_page_border_data_url(theme),
        "section_divider_svg":        ornament_divider_svg(theme),
        "corner_ornament_svg":        corner_ornament(theme),
    }

    env = _env()
    template = env.get_template("base.html")
    html_str = template.render(**ctx)

    if _weasyprint_usable():
        try:
            import weasyprint
            pdf_bytes = weasyprint.HTML(
                string=html_str, base_url=str(_PKG_ROOT),
            ).write_pdf()
            return pdf_bytes
        except Exception as e:
            html_str = (f"<!-- WeasyPrint failed: {type(e).__name__}: {e}. "
                        f"Returning HTML for manual browser-print. -->\n"
                        + html_str)

    return html_str.encode("utf-8")
