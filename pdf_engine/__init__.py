"""
pdf_engine/ — Premium kundli PDF rendering engine.

Pure backend. Zero Streamlit dependency. Returns PDF bytes (or HTML bytes
when WeasyPrint isn't installed — caller detects via b"%PDF" magic header).

All builder + chart-renderer logic lives in `pdf_engine/kundli_pdf.py`.
Jinja2 templates live in `pdf_engine/templates/`.
"""

__all__ = ["build_kundli_pdf", "THEMES", "render"]


def build_kundli_pdf(*args, **kwargs):
    """Lazy import — avoids hard dependency on WeasyPrint until first call."""
    from pdf_engine.kundli_pdf import build_kundli_pdf as _build
    return _build(*args, **kwargs)


def __getattr__(name):
    # Forward THEMES, render, etc. to the consolidated module on first access
    if name in ("THEMES", "DEFAULT_THEME", "render", "STYLES",
                "render_north", "render_south", "render_east"):
        from pdf_engine import kundli_pdf as _kp
        return getattr(_kp, name)
    raise AttributeError(f"module 'pdf_engine' has no attribute {name!r}")
