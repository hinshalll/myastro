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
    "dasha_timeline",
    "build_kundli_pdf", "THEMES", "render_chart_svg",
    "generate_kundli_content", "ai_is_available", "generate_narrative",
]


def dasha_timeline(chart) -> dict:
    """Display-ready Vimshottari Mahadasha timeline for the mobile 'Life Chapters' screen.

    Pure math (no AI / PDF). Reuses the existing engine:
      - build_lifetime_dasha_sequence: full MD list birth → ~120 yrs
      - build_vimshottari_timeline:    the MD/AD running "now"

    Dasha is Moon-based, so it works at every birth-time tier. Exact transition
    DATES only firm up with an exact birth time → dates_exact flag.
    """
    from datetime import datetime
    from shared.astro.astro_calc import (
        build_lifetime_dasha_sequence, build_vimshottari_timeline,
    )

    dt_birth = chart.datetime_local
    moon_lon = chart.planets["Moon"].longitude
    seq = build_lifetime_dasha_sequence(dt_birth, moon_lon)
    # Match birth datetime's tz-awareness so the engine's "now < period_end"
    # comparison doesn't mix naive/aware datetimes.
    now_dt = datetime.now(dt_birth.tzinfo)
    now = build_vimshottari_timeline(dt_birth, moon_lon, now_dt)
    current_md = now.get("current_md")

    mahadashas = [{
        "planet": md["lord"],
        "start_date": md["start"].date().isoformat(),
        "end_date": md["end"].date().isoformat(),
        "start_age": round(md["start_age"], 1),
        "end_age": round(md["end_age"], 1),
        "is_balance": md["is_balance"],
        "is_current": md["lord"] == current_md,
    } for md in seq]

    bd = chart.birth_data
    return {
        "ok": True,
        "birth_nakshatra": now.get("birth_nakshatra"),
        "start_lord": now.get("start_lord"),
        "mahadashas": mahadashas,
        "current_md": current_md,
        "current_ad": now.get("current_ad"),
        "time_precision": bd.time_precision,
        "dates_exact": bd.time_precision == "exact",
    }


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
