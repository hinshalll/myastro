"""
api/routers/kundli.py — /api/v1/kundli/*
==========================================
Kundli (birth-chart) endpoints. Two tiers:
  • free     — compact in-app summary (JSON)
  • premium  — themed PDF binary (paid in mobile app, free during prototyping)

The real work is in math_engine.kundli (chart computation) and
pdf_engine.kundli_pdf (theming + PDF render) — this router is a thin
HTTP wrapper.
"""

from datetime import datetime, date as _date, time as _time
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from api.schemas import BirthProfile, KundliPremiumRequest, KundliFreeResponse

router = APIRouter(prefix="/kundli", tags=["kundli"])


def _profile_to_birthdata(profile: BirthProfile):
    """Convert API BirthProfile → math_engine.kundli BirthData."""
    from math_engine.kundli import BirthData
    return BirthData(
        name=profile.name,
        date=_date.fromisoformat(profile.date),
        time=datetime.strptime(profile.time, "%H:%M").time(),
        place=profile.place,
        lat=profile.lat, lon=profile.lon, tz=profile.tz,
        gender=profile.gender or "O",
        exact_time=profile.exact_time,
    )


@router.post("/free", response_model=KundliFreeResponse)
async def kundli_free(profile: BirthProfile):
    """Compute the in-app kundli summary (Avakahada, planetary positions,
    houses, MD/AD, yogas, doshas, Shadbala, SAV, remedies)."""
    try:
        from math_engine.kundli import compute_chart
        bd = _profile_to_birthdata(profile)
        chart = compute_chart(bd)
        # Return a serialisable summary. The chart object has nested
        # dataclasses; we shallow-convert to dict for JSON.
        return KundliFreeResponse(chart_summary={
            "lagna":              chart.lagna.__dict__ if hasattr(chart.lagna, "__dict__") else str(chart.lagna),
            "ayanamsha_value":    chart.ayanamsha_value,
            "ayanamsha_used":     chart.ayanamsha_used,
            "datetime_local":     chart.datetime_local.isoformat() if hasattr(chart, "datetime_local") else None,
            "panchanga":          chart.panchanga.__dict__ if hasattr(chart.panchanga, "__dict__") else None,
            "planets":            {n: p.__dict__ for n, p in chart.planets.items()},
            "yogas":              chart.yogas if hasattr(chart, "yogas") else [],
            "current_dasha":      chart.current_dasha.__dict__ if hasattr(chart, "current_dasha") and chart.current_dasha else None,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kundli computation failed: {e}")


@router.post("/premium",
             responses={200: {"content": {"application/pdf": {}}, "description": "Themed kundli PDF"}})
async def kundli_premium(req: KundliPremiumRequest):
    """Generate a premium themed kundli PDF. Returns the PDF binary
    directly so the mobile app can save / share / display it."""
    try:
        from math_engine.kundli import compute_chart
        from pdf_engine.kundli_pdf import build_kundli_pdf
        bd = _profile_to_birthdata(req.profile)
        chart = compute_chart(bd)
        pdf_bytes = build_kundli_pdf(
            chart,
            theme_name=req.theme,
            chart_style=req.chart_style,
            language=req.language,
            include_western=req.include_western,
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="kundli_{req.profile.name}.pdf"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")
