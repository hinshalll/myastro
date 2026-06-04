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
