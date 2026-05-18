"""features.consultation.api — FastAPI router."""

from features.consultation.prompts import classify_intent, build_prompt
from features.consultation.service import INTENT_RAG_BOOKS
from features.consultation.schemas import ConsultationRequest, ConsultationResponse

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    @router.post("/ask", response_model=ConsultationResponse)
    def ask(req: ConsultationRequest) -> ConsultationResponse:
        from shared.astro.dossier_builder import generate_astrology_dossier, get_gochara_overlay
        from shared.ai.gemini_client import FREE_MODELS, get_ai_model_by_name
        from shared.ai.knowledge import rag_context

        dossier = generate_astrology_dossier(req.profile)
        transits = get_gochara_overlay(req.profile)
        intent = classify_intent(req.question)
        system_prompt = build_prompt(intent)

        rag_books = INTENT_RAG_BOOKS.get(intent, INTENT_RAG_BOOKS["GENERAL"])
        try:
            ctx = rag_context(req.question, list(rag_books), k=8)
        except Exception:
            ctx = ""

        history_block = ""
        if req.history:
            tail = req.history[-4:]
            history_block = "\n\nRECENT CONVERSATION:\n" + "\n".join(
                f"{'User' if m.role == 'user' else 'Astrologer'}: {m.text}" for m in tail
            )

        turn_hint = (
            "TURN_TYPE: FIRST_REPLY — you MAY use a brief warm opener naming the user once, then go to the answer."
            if not req.history else
            "TURN_TYPE: FOLLOW_UP — the user has already been greeted in this session. Do NOT open with 'Hello [name]...'. Start with the answer directly."
        )

        full_prompt = (
            f"{turn_hint}\n\n"
            f"DETECTED_INTENT: {intent}\n\n"
            f"BIRTH CHART DOSSIER FOR {req.profile.get('name', 'the native')}:\n{dossier}\n\n"
            f"TODAY'S LIVE TRANSITS:\n{transits}"
            f"{history_block}\n\n"
            f"USER QUESTION: {req.question}"
        )
        content_parts = [ctx, full_prompt] if ctx else [full_prompt]

        # Try the model ladder
        last_error = None
        for m_id in FREE_MODELS:
            try:
                model = get_ai_model_by_name(m_id, custom_system_rules=system_prompt)
                text = model.generate_content(content_parts).text or ""
                return ConsultationResponse(intent=intent, reading=text)
            except Exception as e:
                last_error = e
        return ConsultationResponse(
            intent=intent,
            reading=f"All models are briefly at capacity ({last_error}). Please try again in a moment.",
        )
