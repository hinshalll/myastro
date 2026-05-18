"""
api/routers/tarot.py — /api/v1/tarot/*
========================================
Tarot draws + AI interpretation. The Python side picks the cards
randomly (deterministic given a session seed if you want); the AI
narrates the spread with optional kundli context.
"""

import random
from fastapi import APIRouter, HTTPException

from math_engine.constants import TAROT_BASE
from ai_engine.gemini_client import generate_content_with_fallback
from api.schemas import TarotDrawRequest, ReadingResponse

router = APIRouter(prefix="/tarot", tags=["tarot"])


_SPREAD_SIZE = {"one_card": 1, "three_card": 3, "celtic_cross": 10}


@router.post("/draw", response_model=ReadingResponse)
async def tarot_draw(req: TarotDrawRequest):
    """Draw cards for the requested spread and return an AI-narrated reading.

    The spread is rendered as text in the response; the client can show
    nice card visuals from its own deck assets.
    """
    n = _SPREAD_SIZE.get(req.spread, 3)
    deck = list(TAROT_BASE.keys())
    drawn = random.sample(deck, n)
    states = [random.choice(["upright", "reversed"]) for _ in drawn]

    prompt = (
        "You are a senior tarot reader. The user asks: "
        f"\"{req.question or '(no specific question)'}\".\n"
        f"Spread: {req.spread}\n"
        "Drawn cards (in order):\n"
        + "\n".join(f"  {i+1}. {c} ({s})" for i, (c, s) in enumerate(zip(drawn, states)))
        + "\n\nGive a 2-3 paragraph reading. Cite each card's traditional meaning, then weave them together."
    )
    try:
        markdown = generate_content_with_fallback(prompt, knowledge_files=None)
        return ReadingResponse(
            feature="tarot",
            markdown=markdown,
            metadata={"cards": drawn, "states": states, "spread": req.spread},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
