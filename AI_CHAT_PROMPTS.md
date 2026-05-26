# AI Chat Prompts — copy from here (always current)

These are the prompts to paste when you open a **new chat** to work on Myastro.
This file is the **single source of truth** — copy from here, not an old saved snapshot,
so the rules (incl. `CONTENT_STYLE.md`) are always up to date.

- **Start** every new chat by pasting the **OPENING prompt**, then write your request where
  it says `[WRITE WHAT YOU WANT HERE]`.
- **End** the chat by pasting the **CLOSING prompt** (keeps docs + deploy config in sync).

---

## ▶️ OPENING prompt

```
I'm working on Myastro — a Vedic astrology + AI divination app at C:\Users\hinsh\Desktop\myastro. I'm a non-coder ("vibe coder"), so explain in plain English, don't dump huge code blocks unless I ask, verify changes with a quick smoke test before saying "done," and commit after each logical chunk.

## Read these first, in order:
1. README.md          — project layout + how to run
2. FEATURE_SPEC.md    — master spec: every feature, architecture, bug history
3. MOBILE_APP_BLUEPRINT.md — the mobile app plan + product direction
4. CONTENT_STYLE.md   — accuracy + warm, jargon-free voice rules (read before writing ANY user-facing text or meaning table)
5. features/<feature>/README.md — read the one relevant to my request

## How the code is organised
- features/ — 10 self-contained feature folders (tarot, horoscopes, numerology, consultation, dashboard, kundli, palmistry, face_reading, oracle, vault). Each has: view.py (Streamlit page), api.py (FastAPI route), service.py (pure logic), prompts.py (Gemini prompts), schemas.py (Pydantic), README.md.
- shared/ — backend reused across features: shared/astro/ (Swiss Ephemeris, dasha, scoring, forecast), shared/ai/ (Gemini client, RAG, reranker), shared/pdf/ (themes, charts, builder, helpers).
- qdrant_utils.py — Qdrant client + vector store. Dense embeddings via FastEmbed (ONNX).
- ui_streamlit/ — OLD Streamlit prototype UI (reference only, NOT the product frontend).
- mobile/ — the real frontend: React Native + Expo app (pinned to Expo SDK 54). Calls the FastAPI backend over HTTP.
- fastapi_main.py — FastAPI entry; mounts every features/<feat>/api.py router. THIS is the backend the mobile app calls.
- Dockerfile + .dockerignore + render.yaml — deploy config (see Deploy below).

## Rules to follow
- To edit one feature, edit only its folder + maybe shared/. Don't reach into other features.
- shared/* must NEVER import streamlit (purity rule).
- Any user-facing astrology text or interpretation/meaning table MUST follow CONTENT_STYLE.md: verify meanings against multiple authoritative sources online (don't improvise; don't confuse a natal-house meaning with a transit result), keep primary text jargon-free (Sanskrit only behind the "why?" reveal), warm + actionable never fate, and pre-bake as static data (NO live AI on free surfaces — AI only for paid/heavy features).
- Secrets (GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY, RERANK_DISABLE, RERANKER_MODEL): read from env vars first, then .streamlit/secrets.toml. Never hardcode.
- Gemini SDK is google-genai (new), NOT google.generativeai (deprecated).
- RAG = Qdrant hybrid (dense BGE + BM25 sparse) + optional cross-encoder reranker. ALL embeddings run on FastEmbed (ONNX) — dense via the FastEmbedDense class in qdrant_utils.py. NO PyTorch / sentence-transformers. If you change the dense model, the books must be re-ingested.
- Adding a feature = copy any features/<feat>/ folder and rename its 6 files.
- The backend must run with only requirements.txt deps; AI/PDF/vision imports are lazy or guarded so a missing lib never crashes the math endpoints.

## Deploy
- The FastAPI backend is hosted on Render's free tier as a DOCKER web service (the Dockerfile installs the system libraries weasyprint + mediapipe need). Render auto-deploys on every push to main.
- Do NOT edit the Dockerfile for normal code changes — code is copied in on each build automatically. Only touch the Dockerfile if you add a dependency that needs a new SYSTEM (apt) package; in that case update BOTH requirements.txt and the Dockerfile's apt list.
- The old Streamlit prototype still auto-deploys to Streamlit Cloud on push (reference only).

## STANDING RULE — keep docs + deploy config in sync
Whenever you add, change, remove, or upgrade ANYTHING, also update the matching files so they always reflect the live app:
  - README.md (if structure/run/deploy changed)
  - FEATURE_SPEC.md (always — the master record)
  - features/<feature>/README.md (if that feature changed)
  - requirements.txt (if you added/removed a Python dependency)
  - Dockerfile + .dockerignore (if a new dependency needs a system/apt package, or the run/start command changed)
  - render.yaml (if env vars, start command, or service config changed)
Treat these updates as part of the task, not optional.

## Stack
Python 3.11, FastAPI (backend for mobile/web), React Native + Expo (mobile frontend, SDK 54), Streamlit (OLD prototype UI), Gemini Flash Lite via google-genai, Qdrant Cloud (RAG, FastEmbed ONNX embeddings), Swiss Ephemeris, MediaPipe + OpenCV (palm/face vision), WeasyPrint (PDFs). Backend deploys on Render (Docker, free tier), auto-deploy on git push to main.

## My request
[WRITE WHAT YOU WANT HERE]
```

---

## ⏹️ CLOSING prompt

```
Before we finish: review everything you changed this session and update the documentation AND deploy config so they match the current state of the app. Specifically:
  - FEATURE_SPEC.md — update the affected sections + bug/change history
  - README.md — only if structure, setup, or deploy steps changed
  - features/<feature>/README.md — for any feature you touched
  - requirements.txt — if you added or removed a Python dependency
  - Dockerfile + .dockerignore — if a new dependency needs a system (apt) package, or the run/start command changed
  - render.yaml — if environment variables, the start command, or service settings changed
Then run a quick smoke test and commit.
```
