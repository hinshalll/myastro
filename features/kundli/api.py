"""features.kundli.api — FastAPI router for the mobile app + website.

Three endpoints:
  POST /compute       Returns the raw KundliChart as JSON (cheap, no AI)
  POST /free-reading  Free in-app chart payload + optional 8-topic AI prose
  POST /premium-pdf   Premium themed PDF bytes (base64) + optional AI narrative
"""

import base64
from datetime import datetime, date

from features.kundli.schemas import (
    KundliRequest, FreeReadingRequest, PremiumPDFRequest, PremiumPDFResponse,
)

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:
    router = None


def _profile_to_birthdata(p: dict):
    from datetime import time as _time
    from shared.astro.kundli import BirthData

    # Birth-time tier: no time supplied → "unknown", fall back to a noon placeholder
    # so the chart still computes (Moon-based parts usable; time-sensitive parts flagged).
    time_known = bool(p.get("birth_time_known", True))
    raw_t = p.get("time")
    if raw_t in (None, ""):
        time_known = False
    if not time_known:
        t = _time(12, 0)
    elif isinstance(raw_t, str):
        parts = raw_t.split(":")
        t = _time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    else:
        t = raw_t

    return BirthData(
        name=p["name"],
        date=date.fromisoformat(p["date"]) if isinstance(p["date"], str) else p["date"],
        time=t,
        place=p.get("place", ""),
        lat=float(p["lat"]),
        lon=float(p["lon"]),
        tz=p["tz"],
        gender=p.get("gender", "M"),
        exact_time=bool(p.get("exact_time", False)),
        birth_time_known=time_known,
    )


if router is not None:

    @router.post("/compute")
    def compute(req: KundliRequest) -> dict:
        from features.kundli.service import compute_chart
        chart = compute_chart(_profile_to_birthdata(req.profile))
        # The chart dataclass is large; let the caller serialize as needed.
        # time_precision tells the mobile app what to trust: 'exact' / 'approximate'
        # / 'unknown' (see shared/astro/kundli.py BirthData.time_precision).
        bd = chart.birth_data
        return {
            "ok": True,
            "ascendant_sign": chart.lagna.sign,
            "time_precision": bd.time_precision,
            "houses_reliable": bd.houses_reliable,
            "divisionals_reliable": bd.divisionals_reliable,
        }

    @router.post("/free-reading")
    def free_reading(req: FreeReadingRequest) -> dict:
        from features.kundli.service import compute_chart, generate_kundli_content
        chart = compute_chart(_profile_to_birthdata(req.profile))
        out = {"ok": True, "lagna_sign": chart.lagna.sign}
        if req.include_ai:
            out["ai_prose"] = generate_kundli_content(chart, tier="free")
        return out

    @router.post("/premium-pdf", response_model=PremiumPDFResponse)
    def premium_pdf(req: PremiumPDFRequest) -> PremiumPDFResponse:
        from features.kundli.service import compute_chart, build_kundli_pdf, THEMES
        if req.theme_name not in THEMES:
            raise HTTPException(status_code=400,
                                detail=f"Unknown theme. Available: {list(THEMES)}")
        chart = compute_chart(_profile_to_birthdata(req.profile))
        pdf_bytes = build_kundli_pdf(
            chart,
            theme_name=req.theme_name,
            chart_style=req.chart_style,
            language=req.language,
            include_western_appendix=req.include_western_appendix,
            include_ai_narrative=req.include_ai_narrative,
        )
        return PremiumPDFResponse(
            pdf_base64=base64.b64encode(pdf_bytes).decode("ascii"),
            theme_name=req.theme_name,
            language=req.language,
        )
