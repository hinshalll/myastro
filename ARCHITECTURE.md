# ARCHITECTURE.md — Read This First (For AI Assistants)

> **If you are an AI assistant (Claude Code, Antigravity, Codex, Gemini, etc.)
> editing this codebase, read this file completely before making any change.**
> Everything you need to navigate, edit, or extend this app is here.

---

## 1. What this app is

**AIS (Astro Suite)** is a Vedic-astrology + AI divination app.

- **Backend stack**: Python (math via Swiss Ephemeris, AI via Google Gemini,
  vector search via Qdrant Cloud, PDF via WeasyPrint).
- **Frontend (current)**: Streamlit prototype at `ui_streamlit/`.
- **Frontend (planned)**: Next.js web app + Flutter mobile app — both
  calling the same FastAPI backend.
- **Owner is a non-coder** who edits via AI assistants. Keep things SIMPLE.
  No clever metaprogramming. No premature abstraction. Each file = one
  feature, named obviously.

---

## 2. Top-level directory layout

```
AIS/
├── api/                         ← NEW: FastAPI backend (mobile-app-shaped)
│   ├── main.py                  ← FastAPI app + CORS + router mount
│   ├── deps.py                  ← startup init (Swiss Eph + Gemini)
│   ├── schemas.py               ← Pydantic request/response models
│   └── routers/
│       ├── profiles.py          ← /api/v1/profiles/*
│       ├── kundli.py            ← /api/v1/kundli/{free,premium}
│       ├── palm.py              ← /api/v1/palm/analyze
│       ├── tarot.py             ← /api/v1/tarot/draw
│       ├── numerology.py        ← /api/v1/numerology/profile
│       ├── horoscopes.py        ← /api/v1/horoscopes/vedic
│       ├── consultation.py      ← /api/v1/consultation/ask
│       └── oracle/
│           ├── deep_analysis.py ← /api/v1/oracle/deep-analysis
│           ├── matchmaking.py   ← /api/v1/oracle/matchmaking
│           ├── marriage.py      ← /api/v1/oracle/marriage
│           ├── gochara.py       ← /api/v1/oracle/gochara
│           ├── compare.py       ← /api/v1/oracle/compare
│           └── prashna.py       ← /api/v1/oracle/prashna
│
├── math_engine/                 ← PURE compute layer (no Streamlit deps)
│   ├── constants.py             ← PLANETS, SIGNS, DASHA_YEARS, etc.
│   ├── astro_calc.py            ← Swiss Ephemeris wrappers, yogas, KP, etc.
│   ├── dossier_builder.py       ← Builds the "chart dossier" sent to AI
│   ├── scoring.py               ← Comparison/compat/numerology math
│   ├── kundli.py                ← Kundli chart engine (single-file, ~2500 lines)
│   ├── kundli_text.py           ← Static interpretation library
│   └── palm_vision.py           ← Palm-photo quality + MediaPipe landmarks
│
├── ai_engine/                   ← PURE AI layer (no Streamlit deps)
│   ├── gemini_client.py         ← Gemini init + model fallback chain
│   ├── knowledge.py             ← RAG retrieval (Qdrant)
│   ├── prompts.py               ← All system prompts (1 file, big-but-flat)
│   ├── forecasts.py             ← Horoscope generation
│   ├── kundli_narrative.py      ← Karmic story + decade predictions
│   ├── kundli_content.py        ← Multi-call personalised kundli prose
│   ├── palm_vision_ai.py        ← Gemini Vision for palm images
│   ├── palm_knowledge_lookup.py ← Palmistry knowledge retrieval
│   └── palmistry_qdrant.py      ← Qdrant vector search for palmistry
│
├── pdf_engine/                  ← PDF generation (WeasyPrint)
│   ├── kundli_pdf.py            ← Consolidated PDF builder + chart renderers
│   ├── theme_art.py             ← Per-theme SVG glyphs + borders
│   ├── generate_theme_assets.py ← CLI script for theme image gen
│   ├── static/themes/<theme>/   ← AI-generated deity images per theme
│   └── templates/               ← Jinja2 templates (base.html + sections/)
│
├── ui_streamlit/                ← Streamlit UI (prototype — being replaced by Next.js)
│   ├── app.py                   ← Entry point (`streamlit run`)
│   ├── state.py                 ← Session state setup + profile helpers
│   ├── components.py            ← Reusable UI components
│   ├── cache.py                 ← @st.cache_data wrappers
│   ├── helpers.py               ← Small generic helpers
│   └── views/                   ← One file per top-level screen
│       ├── dashboard.py
│       ├── kundli.py
│       ├── consultation.py
│       ├── palmistry.py
│       ├── tarot.py
│       ├── numerology.py
│       ├── horoscopes.py
│       ├── vault.py             ← Saved profiles management
│       ├── astro_pdf.py / palm_pdf.py  ← PDF helpers
│       └── oracle/              ← Oracle is a PACKAGE — one file per feature
│           ├── __init__.py       ← `show_oracle()` dropdown router
│           ├── _shared.py        ← Shared imports + helpers
│           ├── deep_analysis.py  ← Full Life Reading
│           ├── matchmaking.py    ← Compatibility Match
│           ├── marriage.py       ← Destiny Marriage Matrix
│           ├── gochara.py        ← Live Transit
│           ├── compare.py        ← Compare Profiles
│           └── prashna.py        ← Horary
│
├── scripts/                     ← Standalone scripts (smoke tests, diagnostics)
│   ├── smoke_test_oracle_math.py
│   ├── smoke_test_rag.py
│   └── inspect_qdrant_payload.py
│
├── kundli/_smoke_test_kundli.py ← End-to-end kundli compute smoke test
├── ephe/                        ← Swiss Ephemeris .se1 data files (do not edit)
├── qdrant_utils.py              ← Qdrant client + vector store factory
├── requirements.txt             ← Python deps (used by both Streamlit + FastAPI)
├── packages.txt                 ← Linux system deps for WeasyPrint
├── APP_OVERVIEW.md              ← (legacy) Detailed feature/structure reference
├── DEPLOY.md                    ← Step-by-step Render deploy guide for the owner
└── ARCHITECTURE.md              ← THIS FILE
```

---

## 3. The two app entry points

### Streamlit (current, used for daily testing)

```bash
streamlit run ui_streamlit/app.py
```

Reads `GEMINI_API_KEY` from `.streamlit/secrets.toml`.
Initialises Swiss Ephemeris and Gemini, then routes via `app.py`'s `_ROUTES`
dict to one `show_*()` function per nav page.

### FastAPI (new — what mobile + web app will call)

```bash
uvicorn api.main:app --reload --port 8000
```

Reads `GEMINI_API_KEY` from env. Initialises everything in `api/deps.py`.
Auto-generates `/docs` Swagger UI for testing every endpoint.

**Both entry points share the same `math_engine`, `ai_engine`, `pdf_engine`
underneath.** All real logic lives in those — the UI / API layers are thin
wrappers.

---

## 4. Backend Purity Rule (CRITICAL — do not violate)

`math_engine/`, `ai_engine/`, `pdf_engine/` have **ZERO** imports of
`streamlit`, `st.session_state`, etc. They are pure backend modules.

This is enforced by convention and by the fact that the FastAPI backend
imports them. If you add a `import streamlit` to any of these layers,
the FastAPI deploy will crash.

**If you need UI state in an engine function, refactor the function to
take that state as a parameter instead.**

---

## 5. How to add a new feature

### Step 1 — Decide where the LOGIC lives

Math (calculations on the chart) → `math_engine/astro_calc.py` or similar.
AI (prompts + Gemini calls) → `ai_engine/prompts.py` for the prompt,
caller in the appropriate router/view.
PDF rendering → `pdf_engine/`.

### Step 2 — Add the FastAPI endpoint

1. Create a new router file in `api/routers/` (or add to an existing one
   if it fits).
2. Define a Pydantic request/response model in `api/schemas.py`.
3. Wire the route in `api/main.py` via `app.include_router(...)`.

### Step 3 — (Optional) Add the Streamlit view

If the feature is in the current prototype:
1. Create a new file in `ui_streamlit/views/`.
2. Add to the `_ROUTES` dict in `ui_streamlit/app.py`.

For the mobile-first future, you can skip the Streamlit view entirely
and test directly via FastAPI's `/docs`.

### Step 4 — Test
- Local: `uvicorn api.main:app --reload` → open `/docs` → hit the endpoint.
- Smoke test: extend `scripts/smoke_test_oracle_math.py` if it's
  comparison/oracle related.

---

## 6. The Oracle Split (post-refactor structure)

The Oracle was previously one 422-line file. Now it's a package: each of
the 6 oracle features lives in its own ≤100-line file:

| Feature | Streamlit view | FastAPI router |
|---|---|---|
| Full Life Reading | `ui_streamlit/views/oracle/deep_analysis.py` | `api/routers/oracle/deep_analysis.py` |
| Compatibility Match | `ui_streamlit/views/oracle/matchmaking.py` | `api/routers/oracle/matchmaking.py` |
| Destiny Marriage Matrix | `ui_streamlit/views/oracle/marriage.py` | `api/routers/oracle/marriage.py` |
| Live Transit (Gochara) | `ui_streamlit/views/oracle/gochara.py` | `api/routers/oracle/gochara.py` |
| Compare Profiles | `ui_streamlit/views/oracle/compare.py` | `api/routers/oracle/compare.py` |
| Prashna (Horary) | `ui_streamlit/views/oracle/prashna.py` | `api/routers/oracle/prashna.py` |

When the mobile app is built, each feature becomes its own screen + tab.
When the website is built, each becomes its own URL path. The current
Streamlit dropdown is just a transition convenience.

---

## 7. Critical conventions / patterns

### BirthProfile is the universal data structure
Every endpoint that needs chart context accepts a `BirthProfile` (see
`api/schemas.py`). Mobile app stores its current user's `BirthProfile`
and sends it with every API request.

### Chart "dossier" is the AI context
`math_engine/dossier_builder.py:generate_astrology_dossier(profile_dict)`
returns a multi-thousand-character text block with all the chart's
salient facts: planet positions, KP cusps, divisional charts,
Vimshottari dasha timeline, Event Timing Atlas, yogas, doshas, etc.

When an AI feature needs chart context, it ALWAYS uses this dossier.
Never invent or recompute chart facts in a prompt.

### RAG-grounded narratives
The AI uses Qdrant to retrieve classical-text passages. Per-feature book
selection is in `ai_engine/knowledge.py:build_topic_query()` and the
per-router book tuples (see `api/routers/consultation.py:_INTENT_RAG_BOOKS`
for an example).

### Math first, narrative second
Python computes the answer (e.g., "destiny percentage = 67"). The AI
only narrates around that number. AI is NEVER allowed to recompute or
override the math.

This is enforced via `<MATH_LOCK>` blocks in the system prompts.

### Cost budget per feature
- Free kundli ≤ ₹1 per generation
- Premium kundli ≤ ₹5 per generation
- Oracle / consultation: light Gemini Flash, RAG-grounded

Don't add expensive AI calls without checking cost impact.

---

## 8. Engine layers in one paragraph each

**`math_engine/astro_calc.py`** — the lowest layer. Wraps Swiss Ephemeris
to compute lagna, planet positions, KP cusps, nakshatra info, panchanga,
divisional charts (D2 through D60), Shadbala, SAV, yogas, doshas, neecha
bhanga, manglik with cancellation, Argala, etc. Pure functions, no AI,
no state.

**`math_engine/kundli.py`** — single-file (~2500 lines) higher-level
chart computation. `BirthData` and `KundliChart` are the public types.
`compute_chart(BirthData)` returns a `KundliChart` with everything
filled in. Used by the kundli PDF generator + free kundli view.

**`math_engine/dossier_builder.py`** — builds the chart dossier (the
text block fed to AI prompts). Also contains `calculate_matchmaking_synastry`
and `get_gochara_overlay`. Critical for any AI feature.

**`math_engine/scoring.py`** — comparison/compat/numerology math.
`calculate_and_rank_profiles` is the big one (cohort comparison with
band labels, percentiles, discrimination index, tie groups, generational
deduplication, driver evidence per rank).

**`math_engine/palm_vision.py`** — palm photo analysis: quality gate
(EXIF rotation, blur detection with soft warning, downscale-only resize),
MediaPipe 21-landmark detection, hand-type classification, mount crops.

**`ai_engine/prompts.py`** — ALL system prompts in one file. Big, but
flat and grep-able. Find the function for the feature (e.g.,
`build_matchmaking_prompt`) and edit its prompt string.

**`ai_engine/gemini_client.py`** — `init_gemini(api_key)` at startup,
then `get_ai_model_by_name(model)` / `agent_worker(...)` /
`generate_content_with_fallback(...)` for actual calls. Has a fallback
chain across models (Flash-Lite → Flash → Gemma).

**`ai_engine/knowledge.py`** — RAG. `rag_context(query, books, k)`
returns the top-k retrieved chunks for the prompt.

**`pdf_engine/kundli_pdf.py`** — the only PDF builder. `THEMES` dict
declares the 6 visual themes. `build_kundli_pdf(chart, theme_name=...)`
is the entry point.

---

## 9. The trust layer (Compare Profiles + Consultation)

These features have explicit "honesty scaffolding" — read them before
editing similar features:

- **Compare Profiles** — `math_engine/scoring.py:calculate_and_rank_profiles`
  outputs Chart Headlines + Rankings Table with `(score, band, percentile)`
  + Discrimination per Criterion + Tie Groups + per-rank Drivers split
  into "Distinguishing" vs "Cohort-shared". The AI prompt
  (`ai_engine/prompts.py:build_comparison_prompt`) enforces this honest
  framing in the narrative.

- **Consultation Room** — `ai_engine/prompts.py:CONSULTATION_SYSTEM_PROMPT`
  has hard rules: PRIME_DIRECTIVE (answer first, warmth second),
  NEVER_REFUSE_TIMING (Atlas always has windows), KP_VS_PARASHARI (KP
  denial ≠ event impossibility), FORBIDDEN_CLAIMS (no fatalistic
  stereotypes), STYLE_RULES (no greeting loop on follow-ups).

When adding new AI features, mirror these patterns:
- Compute the answer in Python first
- Surface explicit trust calibration (bands, percentiles, "low
  discrimination" warnings)
- Forbid common AI failure modes explicitly in the system prompt
- Give the AI structured evidence to cite, not raw chart text

---

## 10. Where settings/configuration live

- Gemini API key: `.streamlit/secrets.toml` (Streamlit) OR `GEMINI_API_KEY`
  env var (FastAPI / Render).
- Qdrant URL + key: hardcoded in `qdrant_utils.py` (TODO: move to env).
- Theme assets: `pdf_engine/static/themes/<theme>/cover.png`.
- Profile data (in current Streamlit): browser localStorage via
  `streamlit_local_storage`. When mobile ships, switches to Supabase.

---

## 11. What's NOT here (planned but not implemented)

- Database — currently `st.session_state` + browser localStorage. Will
  move to Supabase (Postgres + Auth + file storage).
- Mobile app — Flutter, planned for next month. Will call the FastAPI
  backend.
- Web app frontend — Next.js, planned. Will call the same FastAPI backend.
- User authentication — TBD with Supabase Auth.
- Caching layer — currently `@st.cache_data` for Streamlit; FastAPI side
  is uncached, will add Redis when needed.

---

## 12. Smoke tests (run before any major change)

```bash
# Math engine + scoring tests
python scripts/smoke_test_oracle_math.py     # expect 90+/90+ pass

# RAG retrieval tests
python scripts/smoke_test_rag.py             # expect 12/12 OK

# Kundli engine end-to-end (Sachin Tendulkar reference)
python kundli/_smoke_test_kundli.py          # prints chart, no assertion

# FastAPI import sanity
python -c "from api.main import app; print('OK', len(app.routes))"
```

---

## 13. Rules of thumb for editing this codebase

1. **One file = one feature.** Don't bundle.
2. **Files should be <300 lines** when possible. If a file grows past 500,
   it's a candidate for splitting.
3. **No clever metaprogramming.** Plain function calls, plain dicts.
4. **Compute first, narrate second.** Python returns numbers; AI writes
   prose around them.
5. **Trust the user — they are non-coder but smart.** Explain in plain
   English, not jargon. Surface clear options when uncertain.
6. **Backend purity rule** (see §4) — `math_engine`/`ai_engine`/`pdf_engine`
   must NEVER import `streamlit`.
7. **Both Streamlit and FastAPI share the same engines.** Don't duplicate
   logic between `ui_streamlit/views/X.py` and `api/routers/X.py` — both
   should call the same engine function.
8. **When adding a feature**: prefer adding a FastAPI router (mobile-app
   shape) over a Streamlit view. Mobile is the future; Streamlit is for
   convenience testing.

---

## 14. Last reviewed

This document was generated as part of the Oracle-split + FastAPI scaffold
refactor (May 2026). The structure described here matches the codebase
state immediately after that refactor. If you find drift, update this
document as you fix it.
