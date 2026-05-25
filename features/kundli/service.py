"""features.kundli.service — thin convenience layer.

The heavy chart-compute lives in shared.astro/kundli.py (>2500 lines). When
shared/ rename happens in Phase 3, this just keeps re-exporting from
shared.astro.kundli — view + api never care which name resolves it.

Lazy heavy imports
------------------
Computing a chart is pure math (Swiss Ephemeris only). The PDF builder
(jinja2 / weasyprint) and the AI content/narrative helpers are imported
**lazily** via module ``__getattr__`` so that `/kundli/compute` — and any lean
deploy that only serves the chart — never has to install PDF or AI libraries.
The heavy modules load on first access of their symbol (e.g. when
`/kundli/premium-pdf` or a `?include_ai=true` reading is requested).
"""

# Lean, always-available chart math (needs only pyswisseph)
from shared.astro.kundli import (
    BirthData, compute_chart, yoga_audit, sade_sati_timeline,
)

__all__ = [
    "BirthData", "compute_chart", "yoga_audit", "sade_sati_timeline",
    "build_kundli_pdf", "THEMES", "render_chart_svg",
    "generate_kundli_content", "ai_is_available", "generate_narrative",
]


def __getattr__(name: str):
    """Lazily resolve the heavy (PDF / AI) symbols on first access."""
    if name in ("build_kundli_pdf", "THEMES"):
        from shared.pdf import build_kundli_pdf, THEMES
        return {"build_kundli_pdf": build_kundli_pdf, "THEMES": THEMES}[name]
    if name == "render_chart_svg":
        from shared.pdf.charts import render as render_chart_svg
        return render_chart_svg
    if name in ("generate_kundli_content", "ai_is_available"):
        from features.kundli.content import generate_kundli_content, is_available
        return {"generate_kundli_content": generate_kundli_content, "ai_is_available": is_available}[name]
    if name == "generate_narrative":
        from features.kundli.narrative import generate
        return generate
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
