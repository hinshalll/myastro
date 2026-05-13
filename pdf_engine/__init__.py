"""
pdf_engine/
===========

Premium kundli PDF rendering engine.

Pure backend — zero Streamlit dependency. Returns PDF bytes that the
Streamlit UI, the mobile app, or any HTTP server can consume identically.

Layout:
    builder.py            — orchestrator: takes (KundliChart, theme, options)
                            → returns PDF bytes.
    charts/               — SVG chart renderers (N / S / E Indian).
    templates/            — Jinja2 HTML templates.
        base.html
        sections/         — one partial per kundli section.
        themes/           — theme-specific overrides (Ganesha, Krishna, ...).
    interpretations/      — static text library (planet-in-sign, yoga
                            descriptions, etc.) — language-keyed.
    static/               — fonts (Noto Sans Devanagari + regionals),
                            theme decorative SVG/PNG, watermarks.

WeasyPrint is the recommended PDF backend (HTML+CSS → print-quality PDF).
For systems without WeasyPrint, a fallback `weasyprint_optional` flag can
be set and the builder will return the raw HTML string for browser printing.
"""

__all__ = ["build_kundli_pdf", "charts"]


def build_kundli_pdf(*args, **kwargs):
    """Lazy import to avoid hard dependency on WeasyPrint until needed."""
    from pdf_engine.builder import build_kundli_pdf as _build
    return _build(*args, **kwargs)
