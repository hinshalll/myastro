"""features.kundli.service — thin convenience layer.

The heavy chart-compute lives in shared.astro/kundli.py (>2500 lines). When
shared/ rename happens in Phase 3, this just keeps re-exporting from
shared.astro.kundli — view + api never care which name resolves it.
"""

from shared.astro.kundli import (
    BirthData, compute_chart, yoga_audit, sade_sati_timeline,
)
from shared.pdf import build_kundli_pdf, THEMES
from shared.pdf.charts import render as render_chart_svg

from features.kundli.content import generate_kundli_content, is_available as ai_is_available
from features.kundli.narrative import generate as generate_narrative


__all__ = [
    "BirthData", "compute_chart", "yoga_audit", "sade_sati_timeline",
    "build_kundli_pdf", "THEMES", "render_chart_svg",
    "generate_kundli_content", "ai_is_available", "generate_narrative",
]
