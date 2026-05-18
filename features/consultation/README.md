# Consultation Room — "Ask the Astrologer"

Open-chat conversational reading. Uses the user's default profile.

## Pipeline (per user message)

1. Build full chart dossier via `math_engine.dossier_builder.generate_astrology_dossier` (includes EVENT TIMING ATLAS).
2. Classify intent (`classify_intent`) — one of TIMING, MARRIAGE, CAREER_WEALTH, HEALTH, CHILDREN, SPIRITUAL, EDUCATION, FOREIGN, GOCHARA, GENERAL.
3. Build system prompt = `SYSTEM_PROMPT` + per-intent framework overlay.
4. RAG retrieval from per-intent book set (`INTENT_RAG_BOOKS`).
5. Append last 4 conversation turns + turn-style hint (first vs follow-up).
6. Stream from Gemini Flash Lite with conversational temperature 0.5.

## What's in this folder

| File | What it holds |
|---|---|
| `prompts.py` | `SYSTEM_PROMPT`, `INTENT_FRAMEWORKS`, `classify_intent`, `build_prompt` |
| `service.py` | RAG-book routing map |
| `schemas.py` | Pydantic models |
| `view.py`    | Streamlit chat page |
| `api.py`     | FastAPI router |

## Knowledge / RAG

10 intents × different book sets. See `INTENT_RAG_BOOKS` in `service.py`. Each query pulls k=8 chunks.

## AI cost

~1 streaming Gemini Flash Lite call per user message. Conversational temperature 0.5.

## Editing tips

- Add a new intent → edit `INTENT_FRAMEWORKS` (prompts.py) + `INTENT_RAG_BOOKS` (service.py) + `classify_intent` keywords.
- Tune system tone → edit `SYSTEM_PROMPT` in prompts.py.
