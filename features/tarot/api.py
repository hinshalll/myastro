"""features.tarot.api — FastAPI router for the mobile app + website.

Mirrors what view.py does, but returns JSON instead of streaming to Streamlit.
The Streamlit app does NOT use this. It exists so the mobile app + website
hit the same business logic without going through Streamlit.

To wire up later, add this in fastapi_main.py:
    from features.tarot.api import router as tarot_router
    app.include_router(tarot_router, prefix="/tarot", tags=["tarot"])
"""

from features.tarot.constants import CELTIC_CROSS_POSITIONS
from features.tarot.service import (
    draw_three, draw_one, draw_celtic_cross, get_birth_card,
    create_draw_session, reveal_session, TarotDrawError,
)
from features.tarot.prompts import (
    build_three_card_prompt, build_yes_no_prompt,
    build_celtic_cross_prompt, build_birth_card_prompt,
    three_card_roles,
)
from features.tarot.schemas import (
    ThreeCardRequest, ThreeCardResponse,
    YesNoRequest, YesNoResponse,
    CelticCrossRequest, CelticCrossResponse,
    BirthCardRequest, BirthCardResponse,
    DrawSessionRequest, DrawSessionResponse,
    RevealRequest, RevealResponse,
)


try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:
    # FastAPI not installed in Streamlit-only environments — skip route registration.
    router = None
    HTTPException = None


def _position_labels(spread: str, mode: str, n: int) -> list[str]:
    """Human-readable label for each picked card, matching the spread."""
    if spread == "three":
        return three_card_roles(mode)
    if spread == "celtic":
        return CELTIC_CROSS_POSITIONS[:n]
    return ["The Answer"]  # yes_no


def _generate(prompt: str) -> str:
    """Synchronous Gemini call. Imported lazily to keep this file FastAPI-light."""
    from shared.ai.gemini_client import generate_content_with_fallback
    return generate_content_with_fallback(prompt, knowledge_files=None)


def _rag(query: str, k: int) -> str:
    from shared.ai.knowledge import rag_context
    try:
        return rag_context(query, ["tguide.md"], k=k)
    except Exception:
        return ""


# ── Routes ───────────────────────────────────────────────────────────────────

if router is not None:

    @router.post("/three-card", response_model=ThreeCardResponse)
    def three_card(req: ThreeCardRequest) -> ThreeCardResponse:
        cards, states = draw_three(include_reversed=req.include_reversed)
        ctx = _rag(f"{req.question} {' '.join(cards)} {' '.join(states)} tarot meaning", k=8)
        reading = _generate(build_three_card_prompt(req.question, cards, states,
                                                    mode=req.mode, knowledge_context=ctx))
        return ThreeCardResponse(cards=cards, states=states, reading=reading)

    @router.post("/yes-no", response_model=YesNoResponse)
    def yes_no(req: YesNoRequest) -> YesNoResponse:
        card, state = draw_one(include_reversed=req.include_reversed)
        ctx = _rag(f"{req.question} {card} {state} tarot meaning upright reversed", k=6)
        reading = _generate(build_yes_no_prompt(req.question, card, state, knowledge_context=ctx))
        return YesNoResponse(card=card, state=state, reading=reading)

    @router.post("/celtic-cross", response_model=CelticCrossResponse)
    def celtic_cross(req: CelticCrossRequest) -> CelticCrossResponse:
        cards, states = draw_celtic_cross(include_reversed=req.include_reversed)
        q = req.question or "General life overview"
        ctx = _rag(f"{q} {' '.join(cards)} celtic cross tarot spread", k=10)
        reading = _generate(build_celtic_cross_prompt(q, cards, states, knowledge_context=ctx))
        return CelticCrossResponse(cards=cards, states=states, reading=reading)

    @router.post("/birth-card", response_model=BirthCardResponse)
    def birth_card(req: BirthCardRequest) -> BirthCardResponse:
        card = get_birth_card(req.dob)
        ctx = _rag(f"{card} birth card tarot soul archetype lifelong meaning", k=6)
        reading = _generate(build_birth_card_prompt(card, req.dob, knowledge_context=ctx))
        return BirthCardResponse(card=card, reading=reading)

    # ── Interactive picker: shuffle a hidden deck, then reveal the user's picks ─
    # The recommended path for the future React Native / Expo app.

    @router.post("/draw-session", response_model=DrawSessionResponse)
    def draw_session(req: DrawSessionRequest) -> DrawSessionResponse:
        try:
            return DrawSessionResponse(**create_draw_session(req.spread, req.include_reversed))
        except TarotDrawError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/reveal", response_model=RevealResponse)
    def reveal(req: RevealRequest) -> RevealResponse:
        try:
            drawn = reveal_session(req.token, req.picks)
        except TarotDrawError as e:
            raise HTTPException(status_code=400, detail=str(e))

        spread = drawn["spread"]
        cards, states = drawn["cards"], drawn["states"]
        labels = _position_labels(spread, req.mode, len(cards))

        if spread == "three":
            ctx = _rag(f"{req.question} {' '.join(cards)} {' '.join(states)} tarot meaning", k=8)
            reading = _generate(build_three_card_prompt(
                req.question, cards, states, mode=req.mode, knowledge_context=ctx))
        elif spread == "celtic":
            q = req.question or "General life overview"
            ctx = _rag(f"{q} {' '.join(cards)} celtic cross tarot spread", k=10)
            reading = _generate(build_celtic_cross_prompt(q, cards, states, knowledge_context=ctx))
        else:  # yes_no
            ctx = _rag(f"{req.question} {cards[0]} {states[0]} tarot meaning upright reversed", k=6)
            reading = _generate(build_yes_no_prompt(req.question, cards[0], states[0], knowledge_context=ctx))

        return RevealResponse(
            spread=spread, cards=cards, states=states, positions=labels,
            image_urls=drawn["image_urls"], reading=reading,
        )
