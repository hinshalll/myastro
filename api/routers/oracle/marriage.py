"""
api/routers/oracle/marriage.py — /api/v1/oracle/marriage
==========================================================
Destiny Marriage Matrix — Jaimini + D9 + dasha-overlap cross-chart
confirmation between two profiles.
"""

from datetime import date as _date, datetime as _dt
from fastapi import APIRouter, HTTPException

from math_engine.astro_calc import local_to_julian_day
from math_engine.dossier_builder import generate_astrology_dossier
from math_engine.scoring import calculate_destiny_confirmation
from ai_engine.gemini_client import generate_content_with_fallback
from ai_engine.prompts import build_destiny_confirmation_prompt
from ai_engine.knowledge import build_topic_query, rag_context
from api.schemas import MarriageMatrixRequest, ReadingResponse

router = APIRouter(prefix="/oracle", tags=["oracle"])


@router.post("/marriage", response_model=ReadingResponse)
async def oracle_marriage(req: MarriageMatrixRequest):
    """Cross-chart destiny + marriage matrix between two profiles."""
    try:
        p_boy_d  = req.boy.dict()
        p_girl_d = req.girl.dict()
        jda, _, _ = local_to_julian_day(
            _date.fromisoformat(p_boy_d["date"]),
            _dt.strptime(p_boy_d["time"], "%H:%M").time(), p_boy_d["tz"])
        jdb, _, _ = local_to_julian_day(
            _date.fromisoformat(p_girl_d["date"]),
            _dt.strptime(p_girl_d["time"], "%H:%M").time(), p_girl_d["tz"])

        dos_a = generate_astrology_dossier(p_boy_d)
        dos_b = generate_astrology_dossier(p_girl_d)
        dest_data = calculate_destiny_confirmation(p_boy_d, p_girl_d, jda, jdb, dos_a, dos_b)

        match_ctx = rag_context(
            build_topic_query(topic="match",
                              extras={"score": str(dest_data.get("Percentage", ""))}),
            ("htrh2.md", "kp4.md"), k=10)
        final = build_destiny_confirmation_prompt(
            p_boy_d, p_girl_d, dos_a, dos_b, dest_data, knowledge_context=match_ctx)
        result = generate_content_with_fallback(final, knowledge_files=None)
        return ReadingResponse(
            feature="oracle_marriage",
            markdown=result,
            metadata={
                "destiny_percentage": dest_data.get("Percentage"),
                "details": dest_data,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
