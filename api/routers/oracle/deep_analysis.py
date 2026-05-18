"""
api/routers/oracle/deep_analysis.py — /api/v1/oracle/deep-analysis
=================================================================
Full Life Reading — 3 parallel AI agents (Parashari + Timing + KP)
synthesized into one reading.
"""

import concurrent.futures
from fastapi import APIRouter, HTTPException

from math_engine.dossier_builder import generate_astrology_dossier
from ai_engine.gemini_client import FREE_MODELS, agent_worker, generate_content_with_fallback
from ai_engine.prompts import (
    build_agent_parashari_prompt, build_agent_timing_prompt, build_agent_kp_prompt,
    build_master_synthesizer_prompt,
)
from ai_engine.knowledge import build_topic_query, rag_context
from api.schemas import DeepAnalysisRequest, ReadingResponse

router = APIRouter(prefix="/oracle", tags=["oracle"])

_EXPERT_RULES = (
    "<ROLE>Elite Vedic Astrologer</ROLE>"
    "<MATH_LOCK>Never alter, invent or estimate any number. "
    "Use only data present in the dossier.</MATH_LOCK>"
)


@router.post("/deep-analysis", response_model=ReadingResponse)
async def oracle_deep_analysis(req: DeepAnalysisRequest):
    """Full Life Reading. Returns ~600-1000 word markdown narrative."""
    try:
        dossier = generate_astrology_dossier(req.profile.dict(), include_d60=req.include_d60)

        # Concurrent RAG fetches
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            f_p = ex.submit(rag_context, build_topic_query(topic="parashari", dossier=dossier),
                            ("bphs1.md", "htrh1.md", "htrh2.md"), 10)
            f_t = ex.submit(rag_context, build_topic_query(topic="timing", dossier=dossier),
                            ("bphs2.md", "kp3.md"), 10)
            f_k = ex.submit(rag_context, build_topic_query(topic="kp", dossier=dossier),
                            ("bphs1.md", "kp3.md"), 8)
            ctx_p, ctx_t, ctx_k = f_p.result(), f_t.result(), f_k.result()

        # Concurrent AI agents
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            f_p = ex.submit(agent_worker,
                build_agent_parashari_prompt(dossier, knowledge_context=ctx_p),
                [], FREE_MODELS[0], _EXPERT_RULES)
            f_t = ex.submit(agent_worker,
                build_agent_timing_prompt(dossier, knowledge_context=ctx_t),
                [], FREE_MODELS[0], _EXPERT_RULES)
            f_k = ex.submit(agent_worker,
                build_agent_kp_prompt(dossier, knowledge_context=ctx_k),
                [], FREE_MODELS[1], _EXPERT_RULES)
            p_notes, t_notes, k_notes = f_p.result(), f_t.result(), f_k.result()

        final = build_master_synthesizer_prompt(dossier, p_notes, t_notes, k_notes)
        result = generate_content_with_fallback(final, knowledge_files=None)
        return ReadingResponse(
            feature="oracle_deep_analysis",
            markdown=result,
            metadata={"profile_name": req.profile.name},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
