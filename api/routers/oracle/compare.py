"""
api/routers/oracle/compare.py — /api/v1/oracle/compare
=========================================================
Compare 2-10 profiles across user-selected criteria. The Python ranker
returns score bands, cohort percentiles, discrimination index, tie
groups, generational placements, and per-rank driver evidence.
"""

from fastapi import APIRouter, HTTPException

from math_engine.dossier_builder import generate_astrology_dossier
from ai_engine.gemini_client import generate_content_with_fallback
from ai_engine.prompts import build_comparison_prompt
from ai_engine.knowledge import build_comparison_knowledge
from api.schemas import CompareRequest, ReadingResponse

router = APIRouter(prefix="/oracle", tags=["oracle"])


@router.post("/compare", response_model=ReadingResponse)
async def oracle_compare(req: CompareRequest):
    """Compare multiple profiles across the selected criteria."""
    try:
        # Use compact dossiers when comparing many profiles (saves tokens).
        compact = len(req.profiles) > 3
        # Build 3-tuples (name, dossier, profile_dict) so the ranker uses
        # the direct math path (bypassing dossier-text regex).
        pairs = [
            (p.name, generate_astrology_dossier(p.dict(), compact=compact), p.dict())
            for p in req.profiles
        ]
        compare_ctx = build_comparison_knowledge(req.criteria)
        final = build_comparison_prompt(pairs, req.criteria, knowledge_context=compare_ctx)
        result = generate_content_with_fallback(final, knowledge_files=None)
        return ReadingResponse(
            feature="oracle_compare",
            markdown=result,
            metadata={
                "n_profiles":   len(req.profiles),
                "criteria":     req.criteria,
                "profile_names":[p.name for p in req.profiles],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
