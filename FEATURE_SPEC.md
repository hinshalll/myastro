# Myastro — Feature Specification & Architectural Plan

**Purpose:** Single source of truth for every feature in the app, written so any AI (or human) can pick up one feature and edit it without touching the rest.

**Last audited:** 2026-05-18 (full read-through of all 14,191 lines of backend + all 9 Streamlit views).

---

## Part 1 — Feature Inventory

Every user-visible feature, with: inputs, math calls, AI calls, RAG sources, outputs.

### 1.1 Vault (profile CRUD)
- **File:** `ui_streamlit/views/vault.py` (211 lines)
- **Storage:** localStorage in browser, synced via `ui_streamlit/state.py`
- **Profile schema:** `{name, date, time (HH:MM), place, lat, lon, tz, gender (M/F), exact_time (bool)}`
- **Engine calls:** `geocode_place_cached`, `timezone_for_latlon_cached`
- **AI:** none
- **Special:** import/export JSON backup; "default profile" star ⭐ auto-loads across the app.

### 1.2 Dashboard
- **File:** `ui_streamlit/views/dashboard.py` (310 lines)
- **Inputs:** default profile, today's local date
- **Engine:** `generate_astrology_dossier` (compact), `get_gochara_overlay`, `build_vimshottari_timeline`, Tara Bala (Janma → Parama Mitra), dasha-shift detector (45d AD / 14d PD)
- **AI:** `fetch_dashboard_data` (Greeting/Energy/Focus/Caution/Window/Summary JSON), `fetch_daily_tarot` (Meaning/Action/Mantra JSON), `build_astro_decide_prompt` (on-demand "Decide" widget)
- **RAG:** `tguide.md` for daily tarot card meaning
- **Outputs:** toggleable widgets — greeting, consult link, forecast, decide, Tara Bala cosmic week, daily tarot, dasha shift alert
- **Cache:** 24h TTL on AI calls

### 1.3 Horoscopes
- **File:** `ui_streamlit/views/horoscopes.py` (128 lines)
- **Tabs:**
  - **Western** — input: DOB (for sun sign). AI: `generate_western_forecast(sun_sign, today_str)`. No RAG.
  - **Vedic** — input: profile (for moon sign). 3 sub-tabs: Daily / Monthly / Yearly. AI: `generate_vedic_forecast(prof_json, timeframe, today_str)`. RAG: `bphs2.md` (gochara chapter), k=10.
- **Outputs:** 3-line forecast (General / Love / Career) + PDF download.
- **Cache:** 24h.

### 1.4 Tarot
- **File:** `ui_streamlit/views/tarot.py` (217 lines)
- **Modes:**
  - **Three-Card Spread** — sub-modes: General Guidance / Love & Dynamics / Decision-Two Paths. Optional reversed cards.
  - **Yes / No Oracle** — 1 card.
  - **Celtic Cross** — 10 cards in fixed positions (`CELTIC_CROSS_POSITIONS`).
  - **Birth Card** — deterministic from DOB via `get_tarot_birth_card`.
- **Randomization:** `secrets.SystemRandom().sample()` (cryptographic).
- **AI:** `build_tarot_prompt`, `build_yesno_prompt`, `build_celtic_cross_prompt`, `build_birth_card_prompt` — all streamed via `stream_ai_with_followup`.
- **RAG:** `tguide.md` only, per-mode k (6/6/10/6).
- **Output:** streamed reading + follow-up Q&A + PDF.

### 1.5 Numerology
- **File:** `ui_streamlit/views/numerology.py` (230 lines)
- **System toggle:** Western (Pythagorean) vs Indian/Vedic (Chaldean).
- **Tabs:**
  - **Full Report** (or Ask-a-Question mode toggle).
  - **Personal Cycles & Pinnacles** — Pinnacles & Challenges by age, Personal Year/Month/Day.
- **Cross-validate option:** "🌌 Cross-validate with Vedic Kundli" checkbox — pulls user's profile, builds dossier (optionally D60), feeds to AI.
- **Numbers:** Life Path, Destiny, Soul Urge, Personality with ★ for master numbers 11/22/33.
- **RAG:** `inum1.md` (Vedic) or `wnum.md` (Western).
- **Output:** AI prose + PDF.
- ⚠️ **Old FastAPI port dropped:** Western/Vedic toggle, cross-validate, question mode. Must be preserved.

### 1.6 Consultation Room
- **File:** `ui_streamlit/views/consultation.py` (197 lines)
- **Inputs:** default profile + chat history.
- **Intent classifier:** TIMING, MARRIAGE, CAREER_WEALTH, HEALTH, CHILDREN, SPIRITUAL, EDUCATION, FOREIGN, GOCHARA, GENERAL — routes to per-intent RAG book set (`_INTENT_RAG_BOOKS`).
- **AI:** Gemini chat, conversational system prompt, first-turn vs follow-up tone differentiation.
- **Output:** streamed reply + PDF per response.
- **Memory key:** `v2_chat_{profile_name}` (per profile).

### 1.7 Kundli
- **File:** `ui_streamlit/views/kundli.py` (904 lines)
- **Shared inputs:** profile + chart style (North/South/East Indian).
- **Free Kundli tab** (in-app, scrollable):
  - D1 Lagna chart SVG
  - Panchanga + Functional Profile, Avakahada Chakra
  - Planetary Positions
  - Vimshottari Dasha (MD/AD tables)
  - Sade Sati Timeline
  - Shadbala, SAV by House, Bhava Bala
  - Lucky Factors, Remedies
  - Manglik Analysis, Kaal Sarp Analysis
  - **Optional** AI Personalised Readings via `generate_kundli_content(tier="free")` — 8 topics, ~₹0.10
  - PDF download (no theming, no AI)
- **Premium PDF tab:**
  - Theme picker (7 themes from `pdf_engine.kundli_pdf.THEMES`)
  - Language: en / hi / ta / te / mr / bn / gu
  - Include Western Appendix (bool)
  - Include AI Narrative (bool) → `kundli_narrative.generate()` (~₹5/kundli)
  - PDF via `build_kundli_pdf(chart, theme_name, chart_style, language, include_western_appendix, include_ai_narrative)`

### 1.8 Palmistry
- **File:** `ui_streamlit/views/palmistry.py` (919 lines)
- **Inputs:** default profile (REQUIRED) + uploaded palm image (jpg/jpeg/png).
- **Pipeline:**
  1. `analyze_palm(file_bytes)` — EXIF orient → quality check → MediaPipe landmarks → mount crops → vitality (HSV) → hand metrics
  2. Premium animated overlay + signals card
  3. On click: `read_palm()` (single Gemini Flash Lite VLM call with full palm + 7 mount crops + reference image)
- **Two knowledge sources stacked:**
  - `get_palm_context` (`ai_engine/palm_knowledge_lookup.py`) — structured JSON: dominant planet + nakshatra + dosha
  - `query_palmistry` (`ai_engine/palmistry_qdrant.py`) — semantic Qdrant search of `palmistry.md`
- **Output:** Phase A (JSON observations) + Phase B (markdown reading) + agreement badge + PDF.

### 1.9 Oracle Hub (6 sub-features)
- **Package:** `ui_streamlit/views/oracle/` (NOT the legacy `oracle.py` file — see Bug #1)
- **Sub-features:**

| Sub-feature | File | Engine | AI agents |
|---|---|---|---|
| Deep Analysis | `deep_analysis.py` | dossier | 3 parallel agents (Parashari / Timing / KP) → Synthesizer |
| Matchmaking | `matchmaking.py` | `calculate_ashta_koota`, `check_manglik_dosha` + cancellations, Compatibility Index | 1 narrative call |
| Marriage Timing | `marriage.py` | `calculate_destiny_confirmation` (Destiny Marriage Matrix) | 1 narrative call |
| Gochara | `gochara.py` | `get_gochara_overlay` live transit | 1 narrative call |
| Compare Profiles | `compare.py` | scoring engine with bands/percentiles/discrimination index; 2-10 profiles; criteria checkboxes + custom criteria | 1 ranking call |
| Prashna | `prashna.py` | horary chart cast at NOW + querent location | 1 reading call |

---

## Part 2 — Backend Module Map (where the logic lives)

```
math_engine/        — Pure computation, no Streamlit, no AI
  astro_calc.py     2064 lines  All ephemeris + dasha + panchanga + dignities
  scoring.py        2171 lines  Ashta Koota, Manglik, Destiny Matrix, Compare scoring
  kundli.py         2507 lines  KundliChart dataclass + compute_chart (premium)
  kundli_text.py     760 lines  Text-only labels (planet glyphs, sign names, etc)
  palm_vision.py     602 lines  MediaPipe + OpenCV pipeline (analyze_palm)
  dossier_builder.py 268 lines  generate_astrology_dossier + get_gochara_overlay
  constants.py       135 lines  Sign names, planet ids, dignities, decks, etc.

ai_engine/          — Pure AI orchestration, no Streamlit
  prompts.py        1427 lines  22 prompt builders + GUARDRAILS
  forecasts.py       222 lines  Daily/Vedic forecasts + dashboard data + daily tarot
  kundli_content.py  373 lines  Per-topic kundli prose (free 1-call / premium 2-call)
  kundli_narrative.py 258 lines Premium PDF narrative (karmic / decades / yogas / transit)
  palm_vision_ai.py  287 lines  Single-call VLM palm reader
  palm_knowledge_lookup.py 276  Static JSON lookup (planet/nakshatra/dosha)
  palmistry_qdrant.py 159       Qdrant semantic search for palmistry.md
  knowledge.py       147 lines  rag_context (Qdrant retrieval for all features)
  gemini_client.py   126 lines  FREE_MODELS list + retry/fallback wrappers

pdf_engine/         — PDF rendering
  kundli_pdf.py      983 lines  ⚠️ Charts + builder mashed together (consolidated)
  theme_art.py       646 lines  Theme decorative SVG art
  generate_theme_assets.py 328  Theme asset pre-renderer
  builder.py         381 lines  ⚠️ DEAD — see Bug #2

ui_streamlit/       — UI only; calls into the three engines above
  views/             9 view files + oracle/ package
  cache.py           @st.cache_data wrappers around AI functions
  components.py      Reusable Streamlit widgets (tarot overlay, etc.)
  state.py           Session-state CRUD + localStorage sync
```

---

## Part 3 — Bugs / Dead Code / Tech Debt Found

### 🔴 Bug 1 — Dead file: `ui_streamlit/views/oracle.py` (349 lines)
**Status:** Replaced by `ui_streamlit/views/oracle/` package. Python's import resolution prefers the package, so this file never executes. Confirmed by grep — zero imports reference `views.oracle` directly (only `views.oracle.deep_analysis` etc.). **Action:** Delete after the migration so no future AI gets confused which one is real.

### 🔴 Bug 2 — Dead file: `pdf_engine/builder.py` (381 lines)
**Status:** `pdf_engine/__init__.py` lazy-imports `build_kundli_pdf` from `pdf_engine/kundli_pdf.py` (the 983-line consolidated module). `builder.py` was the start of a split refactor that was never wired up. Confirmed by grep — no file imports `pdf_engine.builder`. **Action:** Either complete the split (use `builder.py` + `pdf_engine/charts/` and trim `kundli_pdf.py`), or delete `builder.py`. Two competing `build_kundli_pdf` implementations is a maintenance trap.

### 🔴 Bug 3 — Dead prompt: `build_deep_analysis_prompt` in `ai_engine/prompts.py:231`
**Status:** Never called anywhere. The Deep Analysis feature uses the three agent-prompt builders (`build_agent_parashari_prompt`, `build_agent_timing_prompt`, `build_agent_kp_prompt`) + a synthesizer prompt instead. **Action:** Delete.

### 🟡 Bug 4 — Backend purity violation: `ai_engine/palmistry_qdrant.py:14`
**Status:** `import streamlit as st` at line 14, but `st` is never used in the file. Violates the project rule "math_engine, ai_engine, pdf_engine must have ZERO Streamlit dependency." Currently harmless (import doesn't crash), but breaks the mobile-app port: in a FastAPI / Flutter context this file would fail to load if Streamlit isn't installed. **Action:** Remove the import.

### 🟡 Bug 5 — Unused import: `FREE_MODELS` in `ai_engine/forecasts.py:20`
**Status:** Imported but never referenced in the file. Minor cleanup.

### 🟡 Bug 6 — Two `pdf_engine.charts` paths
**Status:** `pdf_engine/charts/` folder exists alongside the inline chart renderers in `kundli_pdf.py` (`render_north`, `render_south`, `render_east`, `render`). The folder appears to be the new split, but `__init__.py` still routes everything to the inline version. Same root cause as Bug #2.

### 🟡 Bug 7 — `api/` folder is the abandoned FastAPI port
**Status:** The previous layer-folder FastAPI attempt dropped features (numerology Western/Vedic toggle, free kundli, etc.). User reverted to Streamlit as canonical spec. **Action:** Delete `api/` before the feature-folder rewrite so no AI accidentally references the old, lossy port.

### 🟢 Minor — `secrets.toml` path duplication
`ai_engine/kundli_content.py` opens `.streamlit/secrets.toml` directly with `tomllib` (lines 277-292) instead of going through the shared Gemini-init pattern in `gemini_client.py`. Works fine in Streamlit, but couples the AI engine to a Streamlit folder layout — same purity issue as Bug #4. **Action:** Add `GEMINI_API_KEY` env-var fallback in the migrated version.

### 🟢 Style — `kundli_pdf.py` at 983 lines is too big for "edit one feature easily"
Contains: 4 chart renderers + degree formatting + theme→SVG mapping + Devanagari transliteration + Jinja env + WeasyPrint orchestrator + 7 themes. Should split (see Part 4).

---

## Part 4 — Proposed Feature-Folder Architecture

### Goal
Each feature is a single folder. To edit Tarot, you open `features/tarot/` and find everything: math (none), AI calls, prompts, RAG sources, PDF, API route, schemas. No archaeology across 4 engines.

### Layout

```
shared/                          ← Code reused by 2+ features
  astro/                         ← Renamed from math_engine
    astro_calc.py                (or split into smaller submodules)
    constants.py
    dossier_builder.py
    scoring.py                   (only the bits used by >1 feature)
  ai/
    gemini_client.py
    knowledge.py                 (rag_context)
  pdf/
    base_renderer.py             (WeasyPrint + Jinja env)
    themes/                      (the 7 theme dicts, one per file)
    chart_svg/                   (render_north/south/east — split from kundli_pdf)
  profile/
    state.py                     (profile CRUD, localStorage sync)
    geocoding.py                 (geocode_place + tz lookup)

features/
  dashboard/
    view.py                      (Streamlit page)
    api.py                       (FastAPI route — added when needed)
    service.py                   (orchestrates engine + AI, no UI)
    prompts.py                   (only dashboard prompts)
    schemas.py                   (Pydantic models for I/O)
    README.md                    (1-pager: what this feature does, contracts)

  vault/                         (profile CRUD)
  horoscopes/                    (Western + Vedic)
  tarot/                         (4 modes)
  numerology/                    (Western/Vedic + cross-validate)
  consultation/                  (intent-routed chat)
  kundli/
    free/                        (free-tier in-app view)
    premium/                     (themed PDF)
    chart_compute.py             (KundliChart pipeline)
    narrative.py                 (kundli_narrative.generate)
    content.py                   (kundli_content.generate_kundli_content)
  palmistry/
    vision_pipeline.py           (palm_vision.analyze_palm)
    vlm_reader.py                (palm_vision_ai.read_palm)
    knowledge_lookup.py
    qdrant_search.py
  oracle/
    deep_analysis/
    matchmaking/
    marriage/
    gochara/
    compare/
    prashna/

app/                             ← Thin orchestrator only
  streamlit_main.py              (sidebar + router → features/*/view.py)
  fastapi_main.py                (mounts each feature's api.py)
```

### Contract per feature folder

Every `features/<feat>/` MUST expose:

1. **`service.py`** — one or more pure functions, e.g. `generate_tarot_reading(question, cards, ...) -> str`. No Streamlit. No `print`. No I/O side effects beyond what's explicit.
2. **`prompts.py`** — only the prompts that this feature owns.
3. **`schemas.py`** — Pydantic models for inputs and outputs.
4. **`view.py`** — Streamlit page. Only calls into `service.py`. Owns layout + state.
5. **`api.py`** — FastAPI router. Mirrors `view.py` flow but returns JSON. Same `service.py` underneath.
6. **`README.md`** — 1 page max. "What this feature does, what it calls, what RAG books it uses, cost estimate, AI model used."

**Editing rule:** to change one feature, you edit only its folder + maybe `shared/`. If you find yourself editing a different feature's folder to fix this feature, the boundary is wrong.

### Why this beats the current 3-engine split

| Current | Proposed |
|---|---|
| Tarot logic spread across `prompts.py` (1427 lines), `forecasts.py`, `cache.py`, `tarot.py` view, `knowledge.py`, `components.py` | All in `features/tarot/` |
| `ai_engine/prompts.py` is 1427 lines — every feature's prompts mashed together | Each feature owns its prompts file (~100-300 lines each) |
| Adding a feature means touching 4 engines | Adding a feature means creating one folder |
| Two `build_kundli_pdf` implementations (Bug 2) | Per-feature ownership prevents this |
| Streamlit/FastAPI duplication (Bug 7) | Both layers thin-wrap the same `service.py` |

### Migration order (smallest risk first)

1. **shared/** skeleton — copy engines, no logic change
2. **tarot** — simplest (no math, only AI + RAG)
3. **horoscopes** — small AI surface
4. **numerology** — preserves Western/Vedic/cross-validate/question-mode
5. **vault** + **dashboard** — UI-heavy but logic-light
6. **consultation** — intent routing isolated
7. **kundli** (free) — then (premium PDF)
8. **palmistry** — vision pipeline is the biggest single chunk
9. **oracle/** sub-features — one at a time
10. **Cleanup:** delete old `math_engine/`, `ai_engine/`, `pdf_engine/`, `ui_streamlit/`, `api/` after verifying everything passes

After each step: app must still run. No multi-feature breakage windows.

---

## Part 5 — What I need from you before starting Phase 1

Two yes/no decisions:

**Q1: Bug fixes — fold into the migration, or do them first as separate small commits?**
- Recommended: **fix first** (delete `oracle.py`, `pdf_engine/builder.py`, `api/`, `build_deep_analysis_prompt`, the stray streamlit import). 5 small commits, app keeps working, then start the migration on a clean slate.

**Q2: Migration cadence — one feature per commit, or full Phase 1 skeleton + then features?**
- Recommended: **one feature per commit**. Each commit ends with the app fully working. You can pause / review / ship at any boundary.

Once approved, I begin with the cleanup commits, then `shared/` skeleton, then tarot.
