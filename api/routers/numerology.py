"""
api/routers/numerology.py — /api/v1/numerology/*
==================================================
Numerology profile (Chaldean / Pythagorean / Vedic systems).
"""

from datetime import date as _date
from fastapi import APIRouter, HTTPException

from math_engine.astro_calc import get_personal_year, get_personal_month, get_personal_day
from api.schemas import NumerologyRequest, ReadingResponse

router = APIRouter(prefix="/numerology", tags=["numerology"])


@router.post("/profile", response_model=ReadingResponse)
async def numerology_profile(req: NumerologyRequest):
    """Compute the user's numerology profile and return narrative + breakdown.

    The actual narrative is produced by the AI; the numbers themselves
    come from deterministic math in math_engine.astro_calc.
    """
    try:
        from ai_engine.prompts import GUARDRAILS
        from ai_engine.gemini_client import generate_content_with_fallback

        dob = _date.fromisoformat(req.dob)
        py = get_personal_year(dob)
        pm = get_personal_month(dob)
        pd = get_personal_day(dob)

        prompt = (
            f"{GUARDRAILS}\n\n"
            f"Numerology system: {req.system}\n"
            f"Full name: {req.full_name}\n"
            f"DOB: {req.dob}\n"
            f"Personal Year: {py}\n"
            f"Personal Month: {pm}\n"
            f"Personal Day: {pd}\n\n"
            "Write a 3-paragraph numerology reading covering:\n"
            "1. Core number / life-path meaning\n"
            "2. This year's theme + month/day pulse\n"
            "3. One concrete suggestion grounded in the numbers."
        )
        markdown = generate_content_with_fallback(prompt, knowledge_files=None)
        return ReadingResponse(
            feature="numerology",
            markdown=markdown,
            metadata={
                "system": req.system,
                "personal_year":  py,
                "personal_month": pm,
                "personal_day":   pd,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
