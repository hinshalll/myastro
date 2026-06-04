"""features.reflect.api — FastAPI router for the big-picture reflective readings.

Mounted at /reflect in fastapi_main.py. Both stateless + pure math (no AI).

    POST /reflect/purpose   Your Purpose — soul/career blueprint
    POST /reflect/year      Year in Review — "Cosmic Wrapped"
"""
from __future__ import annotations

from features.reflect import service
from features.reflect.schemas import PurposeRequest, YearRequest

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.post("/purpose")
    def purpose(req: PurposeRequest) -> dict:
        """Your Purpose — a warm soul/career blueprint.

        FREE: pure math + a static, classically-sourced lookup, NO AI. Built from
        the Atmakaraka (soul planet), the 10th house + its lord (career/karma), the
        D10 Dashamsha (career chart) and the dharma trikona (1/5/9). Same { profile }
        shape as /kundli/compute (needs lat/lon; birth time → precise, unknown time →
        a midday estimate + a precision note). Deterministic per profile, so the app
        can cache it once. Returns { soul, calling, career_chart, dharma, headline,
        summary, why, sanskrit, precision_note }.
        """
        try:
            return service.purpose(req.profile)
        except ValueError as e:
            if str(e) == "birthplace_required":
                raise HTTPException(status_code=422,
                    detail="A birthplace (lat/lon) is needed for the purpose blueprint.")
            raise

    @router.post("/year")
    def year(req: YearRequest) -> dict:
        """Year in Review — "Cosmic Wrapped", a shareable yearly recap.

        FREE: pure math + a static lookup, NO AI. Built from the Varshaphala (Tajik
        annual chart — the Muntha spotlight + solar return), the Vimshottari dasha
        chapter that ran across the year, and the year's slow, era-defining transits
        (Jupiter's gift, Saturn's lesson). Same { profile } shape as /kundli/compute
        (needs lat/lon); optional "year" (defaults to the current year). Returns
        { chapter, muntha, gifts, lessons, headline, share_text, summary, why,
        sanskrit, precision_note }.
        """
        try:
            return service.year_in_review(req.profile, req.year)
        except ValueError as e:
            if str(e) == "birthplace_required":
                raise HTTPException(status_code=422,
                    detail="A birthplace (lat/lon) is needed for the year-in-review.")
            raise
