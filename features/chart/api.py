"""features.chart.api — FastAPI router for the plain-English chart interpretation.

Mounted at /chart in fastapi_main.py. Stateless + pure data (no AI).

    POST /chart/interpret   the curated "front room" read (hero cards)
"""
from __future__ import annotations

from features.chart import service
from features.chart.schemas import InterpretRequest

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.post("/interpret")
    def interpret(req: InterpretRequest) -> dict:
        """The curated, plain-English "front room" read of the chart.

        FREE: pure data + composition from verified classical atoms, NO AI. Returns
        warm, jargon-free hero cards — { headline, core:[{title, body, sanskrit,
        why}], current_chapter, precision_note }. The `body` of every card is plain
        English any first-time user understands; the Sanskrit / technical detail
        lives only in `sanskrit` / `why`. Same { profile } shape as /kundli/compute
        (needs lat/lon; an exact birth time unlocks the rising sign + houses, an
        unknown time reads from Sun + Moon + a precision note). Gentle guidance,
        never fate. Deterministic per profile (cache-friendly).
        """
        try:
            return service.interpret(req.profile)
        except ValueError as e:
            if str(e) == "birthplace_required":
                raise HTTPException(status_code=422,
                    detail="A birthplace (lat/lon) is needed to read the chart.")
            raise

    @router.post("/houses")
    def houses(req: InterpretRequest) -> dict:
        """The 12 houses, each as a warm, plain-English card (the deeper dive).

        FREE: pure data + composition, NO AI. Each card = { title, body, sanskrit,
        why }: the house's part of life, the sign on it, and any planets sitting
        there — all in plain language. Houses are built from the rising sign, so
        this needs an **exact birth time** (else returns ok:false +
        birth_time_required). Same { profile } shape as /kundli/compute (lat/lon).
        """
        try:
            return service.houses(req.profile)
        except ValueError as e:
            if str(e) == "birthplace_required":
                raise HTTPException(status_code=422,
                    detail="A birthplace (lat/lon) is needed to read the chart.")
            raise

    @router.post("/planets")
    def planets(req: InterpretRequest) -> dict:
        """Each of the 9 planets in its sign (+ house) as a warm card.

        FREE: pure data + composition, NO AI. Each card = { title, body, sanskrit,
        why }: what that part of you is like (planet), how it shows up (sign), and
        where it plays out (house). Sign reads work at every birth-time tier; the
        house clause needs an exact birth time (a precision note says so otherwise).
        Same { profile } shape as /kundli/compute (lat/lon).
        """
        try:
            return service.planets(req.profile)
        except ValueError as e:
            if str(e) == "birthplace_required":
                raise HTTPException(status_code=422,
                    detail="A birthplace (lat/lon) is needed to read the chart.")
            raise
