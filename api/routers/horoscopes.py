"""
api/routers/horoscopes.py — /api/v1/horoscopes/*
==================================================
Daily / weekly / monthly / yearly horoscopes — Vedic with dasha/transit
context, AI-narrated.
"""

from datetime import date as _date
from fastapi import APIRouter, HTTPException

from ai_engine.forecasts import generate_vedic_forecast
from api.schemas import HoroscopeRequest, ReadingResponse

router = APIRouter(prefix="/horoscopes", tags=["horoscopes"])


@router.post("/vedic", response_model=ReadingResponse)
async def horoscope_vedic(req: HoroscopeRequest):
    """Generate a kundli-aware horoscope for the requested timeframe.

    The forecast is grounded in:
      • current Vimshottari Mahadasha/Antardasha lords
      • live Saturn + Jupiter transits relative to natal positions
      • per-house themes from the user's chart
    """
    try:
        today = _date.today().isoformat()
        markdown = generate_vedic_forecast(
            profile=req.profile.dict(),
            timeframe=req.timeframe,
            today_str=today,
        )
        return ReadingResponse(
            feature=f"horoscope_vedic_{req.timeframe}",
            markdown=markdown,
            metadata={"timeframe": req.timeframe, "date": today},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
