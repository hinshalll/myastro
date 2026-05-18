"""
api/routers/oracle/gochara.py — /api/v1/oracle/gochara
========================================================
Live transit (Gochara) analysis — overlay today's planets on the
selected natal chart, AI narrates the influences.
"""

from fastapi import APIRouter, HTTPException

from math_engine.dossier_builder import generate_astrology_dossier, get_gochara_overlay
from ai_engine.gemini_client import generate_content_with_fallback
from ai_engine.prompts import build_transit_prompt
from ai_engine.knowledge import build_topic_query, rag_context
from api.schemas import GocharaRequest, ReadingResponse

router = APIRouter(prefix="/oracle", tags=["oracle"])


@router.post("/gochara", response_model=ReadingResponse)
async def oracle_gochara(req: GocharaRequest):
    """Live transit reading. Picks up today's planet positions automatically."""
    try:
        prof_d  = req.profile.dict()
        dos     = generate_astrology_dossier(prof_d)
        overlay = get_gochara_overlay(prof_d)
        ctx = rag_context(
            build_topic_query(topic="gochara", dossier=dos),
            ("bphs2.md", "htrh2.md"), k=10,
        )
        final = build_transit_prompt(dos, overlay, knowledge_context=ctx)
        result = generate_content_with_fallback(final, knowledge_files=None)
        return ReadingResponse(
            feature="oracle_gochara",
            markdown=result,
            metadata={"profile_name": prof_d.get("name", "")},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
