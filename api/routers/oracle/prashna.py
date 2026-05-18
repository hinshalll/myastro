"""
api/routers/oracle/prashna.py — /api/v1/oracle/prashna
========================================================
Prashna (Horary) — chart cast at the moment of asking, from the asker's
current location. Returns the KP verdict + AI narrative.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, HTTPException

from math_engine.dossier_builder import generate_astrology_dossier
from ai_engine.gemini_client import generate_content_with_fallback
from ai_engine.prompts import build_prashna_prompt
from ai_engine.knowledge import rag_context
from api.schemas import PrashnaRequest, ReadingResponse

router = APIRouter(prefix="/oracle", tags=["oracle"])


@router.post("/prashna", response_model=ReadingResponse)
async def oracle_prashna(req: PrashnaRequest):
    """Cast a horary chart at 'now' from asker's location and answer."""
    try:
        now = datetime.now(ZoneInfo(req.asker_tz))
        prof = {
            "name": "Prashna",
            "date": now.date().isoformat(),
            "time": now.strftime("%H:%M"),
            "place": req.asker_place,
            "lat": req.asker_lat, "lon": req.asker_lon, "tz": req.asker_tz,
        }
        dos = generate_astrology_dossier(prof)
        ctx = rag_context(req.question, ("kp6.md",), k=8)
        final = build_prashna_prompt(req.question, dos, knowledge_context=ctx)
        result = generate_content_with_fallback(final, knowledge_files=None)
        return ReadingResponse(
            feature="oracle_prashna",
            markdown=result,
            metadata={"question": req.question, "cast_time": now.isoformat()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
