"""
api/routers/consultation.py — /api/v1/consultation/*
=====================================================
Ask-the-Astrologer chat. Stateless from the API's perspective — the
client sends the full conversation history each turn (mobile-friendly,
no server-side session state).

Wires together:
  • math_engine.dossier_builder.generate_astrology_dossier
  • Event Timing Atlas (in the dossier)
  • ai_engine.prompts.build_consultation_prompt + intent classifier
  • Gemini with conversational temperature
"""

from fastapi import APIRouter, HTTPException

from math_engine.dossier_builder import generate_astrology_dossier, get_gochara_overlay
from ai_engine.gemini_client import FREE_MODELS, get_ai_model_by_name
from ai_engine.prompts import build_consultation_prompt, classify_consultation_intent
from ai_engine.knowledge import rag_context
from api.schemas import ConsultationRequest, ReadingResponse

router = APIRouter(prefix="/consultation", tags=["consultation"])


# Same book selection used by the Streamlit consultation view
_INTENT_RAG_BOOKS = {
    "TIMING":        ("bphs1.md", "bphs2.md", "kp3.md", "kp4.md", "htrh2.md"),
    "MARRIAGE":      ("kp4.md",  "bphs2.md", "htrh1.md", "htrh2.md"),
    "CAREER_WEALTH": ("bphs1.md", "bphs2.md", "kp3.md", "htrh1.md"),
    "HEALTH":        ("bphs2.md", "htrh2.md", "kp6.md"),
    "CHILDREN":      ("bphs1.md", "htrh1.md", "kp4.md"),
    "SPIRITUAL":     ("bphs2.md", "htrh2.md"),
    "EDUCATION":     ("bphs1.md", "htrh1.md"),
    "FOREIGN":       ("bphs2.md", "htrh2.md", "kp3.md"),
    "GOCHARA":       ("htrh1.md", "htrh2.md", "bphs2.md"),
    "GENERAL":       ("htrh1.md", "htrh2.md"),
}


@router.post("/ask", response_model=ReadingResponse)
async def consultation_ask(req: ConsultationRequest):
    """One turn of the consultation chat.

    The client sends the user's profile, the new question, and the
    recent conversation history. Backend returns the assistant's reply.
    Client appends both turns to its own state and sends the updated
    history on the next call.
    """
    try:
        prof_dict = req.profile.dict()
        dos       = generate_astrology_dossier(prof_dict)
        transits  = get_gochara_overlay(prof_dict)
        intent    = classify_consultation_intent(req.question)
        sys_prompt = build_consultation_prompt(intent)

        # RAG retrieval based on intent
        books = _INTENT_RAG_BOOKS.get(intent, _INTENT_RAG_BOOKS["GENERAL"])
        try:
            consult_ctx = rag_context(req.question, books, k=8)
        except Exception:
            consult_ctx = ""

        # History formatting
        is_first_turn = not req.history
        hist_text = ""
        if req.history:
            last_few = req.history[-4:]
            hist_text = "\n\nRECENT CONVERSATION:\n" + "\n".join(
                f"{'User' if m.role=='user' else 'Astrologer'}: {m.content}"
                for m in last_few
            )

        turn_hint = (
            "TURN_TYPE: FIRST_REPLY — you MAY use a brief warm opener "
            "naming the user once, then go to the answer."
            if is_first_turn else
            "TURN_TYPE: FOLLOW_UP — the user has already been greeted. "
            "Do NOT open with 'Hello [name]…'. Start with the answer directly."
        )

        full_prompt = (
            f"{turn_hint}\n\n"
            f"DETECTED_INTENT: {intent}\n\n"
            f"BIRTH CHART DOSSIER FOR {prof_dict['name']}:\n{dos}\n\n"
            f"TODAY'S LIVE TRANSITS:\n{transits}"
            f"{hist_text}\n\n"
            f"USER QUESTION: {req.question}"
        )
        content = [consult_ctx, full_prompt] if consult_ctx else [full_prompt]

        # Try models in order with simple fallback
        last_err = None
        for m_id in FREE_MODELS:
            try:
                model = get_ai_model_by_name(m_id, custom_system_rules=sys_prompt)
                reply = model.generate_content(content).text
                return ReadingResponse(
                    feature="consultation",
                    markdown=reply,
                    metadata={"intent": intent, "is_first_turn": is_first_turn},
                )
            except Exception as e:
                last_err = e
                continue
        raise HTTPException(status_code=503, detail=f"All AI models unavailable: {last_err}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
