# Myastro — Feature Specification & Architecture

**Last updated:** 2026-05-26 — Mobile build underway (see `MOBILE_APP_BLUEPRINT.md`).

### Recent changes (2026-05-26) — "Today" day-alert cards (Chandra Sandhi + eclipse)
- **New endpoint `POST /dashboard/day-alerts`** powers two mobile "Today" heads-up cards.
  Pure Swiss-Ephemeris math, Moon/Sun based — no birth time, no AI, no profile. Input
  `{ date, tz }` (optional `lat`/`lon`). Returns `{ chandra_sandhi, eclipse }`, each with
  its own `present` flag so the app shows/hides the card.
  - **Chandra Sandhi** (blueprint §6.6): scans the transiting Moon across the local day;
    when within ~1° of a 30° sign boundary returns `{present, start, end, from_sign,
    to_sign, label, note, why, sanskrit}` (else `present:false`). The Moon crosses at most
    one sign boundary per day → at most one window.
  - **Eclipse**: soonest upcoming solar/lunar eclipse on/after the date (global search via
    `sol_eclipse_when_glob` / `lun_eclipse_when`). Returns `{present, type:"Surya
    Grahan"|"Chandra Grahan", date, days_until, sutak_start, sutak_note, why, sanskrit}`;
    `present` only within the next 30 days. Sutak ≈ 12h before solar / 9h before lunar.
- **New pure functions in `shared/astro/astro_calc.py`:** `chandra_sandhi_window(d, tz)`
  and `next_eclipse(d, tz, lat, lon)`. No AI, no new deps, no streamlit. Distinct from
  `kundli._detect_grahan` (a natal eclipse-axis dosha, not an upcoming calendar eclipse).

### Recent changes (2026-05-26) — daily "Cosmic Weather" forecast hero
- **New endpoint `POST /dashboard/forecast`** powers the mobile Today tab's hero card.
  **FREE + cheap (cost rule): pure math + a pre-baked meaning lookup, NO AI call.**
  **Moon-based**, so it works at every birth-time tier (unknown time → noon placeholder).
  Same `{ profile }` contract as `/kundli/compute`, plus optional `date` (defaults to
  today). Computes the transiting Moon at **local noon** (deterministic / cacheable), its
  nakshatra+sign, its house from the **natal Moon** (Chandra house 1..12), and **Tara
  Bala** quality via `calculate_tara_bala`, then maps that state through a static table.
  Returns `vibe_word`, `vibe_score` (0..1), `mood`, `opportunity`, `caution`, `action`,
  `why` (plain English), `sanskrit`, and `astro_state_key` (cacheable), plus debug fields.
  Framing is actionable + reflective, never hard fate claims (blueprint §2).
- **New module `shared/astro/forecast.py`:** `daily_moon_forecast(profile, on_date)` +
  the `_CHANDRA_HOUSE` meaning table (12 entries, easy to expand). Pure math + lookup —
  no AI, no PDF, no new dependencies, no streamlit. Reuses `calculate_tara_bala` and the
  ephemeris helpers from `astro_calc.py` (does NOT use `get_gochara_overlay`, which needs
  a birth time and returns AI prose).

### Recent changes (2026-05-26) — daily Good/Avoid timing strip
- **New endpoint `POST /dashboard/timing`** powers the mobile "Today → Good / Avoid
  times" strip. **Date- and location-based** (weekday + sunrise/sunset), NOT birth-chart
  based, so no profile is needed. Input `{ date, lat, lon, tz }`. Returns display-ready
  `avoid` (Rahu Kaal, Yamaganda, Gulika Kaal), `good` (Abhijit Muhurta) — each
  `{name, start, end}` in 24h `HH:MM` — plus `choghadiya` (8 day + 8 night segments
  tiling sunrise→next sunrise, each `{name, start, end, quality, period}`,
  `quality ∈ good|neutral|avoid`), a one-line `summary`, and `weekday`/`sunrise`/`sunset`.
- **New pure functions in `shared/astro/astro_calc.py`:** `daily_timing_windows`,
  `sun_rise_set` (Swiss Ephemeris sunrise/sunset), plus the classical weekday segment
  tables for Rahu/Yamaganda/Gulika and the Choghadiya wheel. Pure math — no AI, no PDF,
  no new dependencies. (The kaal fields on `PanchangaInfo` were only ever declared, never
  populated; this is the first code that actually computes them.)

### Recent changes (2026-05-26) — Life Chapters dasha timeline
- **New endpoint `POST /kundli/dasha-timeline`** powers the mobile "Life Chapters"
  screen (a visual Vimshottari Dasha timeline). Same `{ "profile": {...} }` contract as
  `/kundli/compute`. Returns a compact, display-ready JSON: a `mahadashas` array (full
  birth→~120 yr sequence, each `{planet, start_date, end_date, start_age, end_age,
  is_balance, is_current}` with ISO dates), plus `current_md` / `current_ad`,
  `birth_nakshatra`, `start_lord`, and `time_precision` / `dates_exact`. Pure math —
  reuses `build_lifetime_dasha_sequence` + `build_vimshottari_timeline` from
  `shared/astro/astro_calc.py` (no AI, no PDF). Thin `dasha_timeline(chart)` helper added
  to `features/kundli/service.py`.
- **Works at every birth-time tier (blueprint §6.6).** Dasha is Moon-based, so the
  endpoint never fails on an unknown time (the engine uses a noon placeholder). The
  sequence/order is always correct; only the exact transition **dates** firm up with an
  exact time, signalled by `dates_exact` (True only when `time_precision == 'exact'`).

### Recent changes (2026-05-25) — mobile/backend wiring
- **`/kundli/compute` enriched** to return a compact, display-ready summary: `moon`,
  `sun`, `ascendant_sign`/`ascendant_nakshatra`, a 9-body `planets` array, plus the
  precision flags. Moon-based fields populate at every tier; ascendant/houses are `null`
  unless `houses_reliable`. (Backward compatible — only added fields.)
- **Lean math path.** `features/kundli/service.py` now imports the PDF builder
  (jinja2/weasyprint) and AI content/narrative helpers **lazily** (module `__getattr__`),
  and `fastapi_main._init_backend()` guards Gemini/DeepSeek init in try/except. The
  chart API runs with only `pyswisseph` installed — no AI/PDF libs required. Powers the
  React Native app (`mobile/`), which reaches the API over LAN in dev.
- **RAG embeddings → ONNX (PyTorch removed).** `qdrant_utils.py` now produces dense
  vectors via a `FastEmbedDense` class (FastEmbed / ONNX) instead of
  `HuggingFaceEmbeddings` (sentence-transformers + PyTorch). Same model
  (`BAAI/bge-base-en-v1.5`, 768-dim, cosine), so the Qdrant collection layout is
  unchanged — but re-ingest the books once with the chunker tool so stored vectors are
  ONNX-consistent. Dropped `sentence-transformers` + `langchain-huggingface` from
  `requirements.txt`. Result: no torch anywhere → the full backend (chart, PDF, vision,
  AI text, AND hybrid RAG search) fits free-tier RAM for Docker hosting on Render.

---

## How the codebase is organised

```
features/                       ← ALL user-visible features. One folder each.
  consultation/                 (Ask the Astrologer chat)
  dashboard/                    (Cosmic Compass landing page)
  horoscopes/                   (Western + Vedic forecasts)
  kundli/                       (Free in-app chart + Premium PDF)
  numerology/                   (Western + Vedic + cross-validate)
  oracle/                       (6 sub-features: deep_analysis, matchmaking, marriage, gochara, compare, prashna)
  palmistry/                    (AI-first multi-capture VLM palm reading)
  face_reading/                 (Single-call VLM face reading; Face Mesh; optional kundli)
  tarot/                        (Three-Card, Yes/No, Celtic Cross, Birth Card)
  vault/                        (Saved profiles CRUD + import/export)

shared/                         ← Backend plumbing shared by every feature.
  astro/                        Swiss Ephemeris + dasha + scoring + chart compute
    astro_calc.py               Ephemeris + dasha + panchanga
    constants.py                Signs, planets, dignities
    dossier_builder.py          generate_astrology_dossier + get_gochara_overlay
    kundli.py                   KundliChart dataclass + compute_chart
    kundli_text.py              Text labels (planet glyphs, etc.)
    palm_vision.py              MediaPipe + OpenCV pipeline
    scoring.py                  Ashta Koota, Manglik, Destiny Matrix, Compare scoring
  ai/                           Provider-agnostic AI layer + RAG + cross-cutting prompts
    config.py                   THE ONE FILE to change models — per-task model names
                                (default/chat/json/agent/vision) + fallback ladder.
                                Provider (Gemini/DeepSeek) auto-detected from the
                                model-name prefix; type a new model name to switch.
    __init__.py                 Front door — import AI helpers from `shared.ai`
    gemini_client.py            Gemini adapter + retry/fallback router (FREE_MODELS)
    deepseek_client.py          DeepSeek adapter (OpenAI-compatible, same interface)
    knowledge.py                rag_context (Qdrant retrieval)
    prompts.py                  Oracle prompts + GUARDRAILS (only cross-cutting bits)
  pdf/                          WeasyPrint + premium themes + PDF helpers
    themes.py                   Premium palette dicts (classic_vedic, ganesha, krishna, ...)
    charts.py                   SVG renderers — North / South / East Indian + dispatcher
    builder.py                  Jinja2 + WeasyPrint orchestrator (build_kundli_pdf)
    theme_art.py                Decorative SVG art
    generate_theme_assets.py    Theme asset pre-renderer
    astro_pdf.py                Generic markdown→PDF (used by every feature with downloads)
    palm_pdf.py                 Palm-reading-specific PDF builder

fastapi_main.py                 ← FastAPI backend entry. Mounts every
                                  features/<feat>/api.py router under /<feat>/*

ui_streamlit/                   ← Streamlit shell only — NOT feature-specific
  app.py                        Streamlit entry + router
  cache.py                      @st.cache_data wrappers
  components.py                 Reusable Streamlit widgets
  helpers.py                    UI helpers
  state.py                      Session + localStorage CRUD
```

## The contract — what every `features/<feat>/` folder looks like

```
features/<feature>/
  __init__.py        Empty (or minimal docstring). Prevents circular imports.
  README.md          Plain-English: what this feature does, AI cost, RAG books, editing tips.
  prompts.py         The Gemini prompts owned by this feature.
  service.py         Pure-Python business logic. No Streamlit, no FastAPI.
  schemas.py         Pydantic models for FastAPI I/O.
  view.py            The Streamlit page (calls service.py).
  api.py             The FastAPI router (also calls service.py).
```

**Editing rule:** To change one feature, you edit only its folder + maybe a shared engine. If you find yourself editing a different feature's folder to fix this feature, the boundary is wrong.

---

## Per-feature summary

### 1. tarot — `features/tarot/`
- 4 modes: Three-Card / Yes-No / Celtic Cross (10) / Birth Card
- **78-card reading deck.** Three-Card / Yes-No / Celtic Cross draw from the full
  78-card deck (`FULL_78_DECK` = 22 Major + 56 Minor). Birth Card and the
  Dashboard daily card stay on the 22-card `FULL_TAROT_DECK` (Major only).
- **Interactive picker (the user picks their own cards).** Two-step, stateless,
  React-Native-ready flow — the backend is the single source of truth:
  1. `create_draw_session(spread, include_reversed)` → shuffles a hidden deck,
     fixes each card's Upright/Reversed state, and returns an opaque **signed
     token** (HMAC-SHA256, `TAROT_DRAW_SECRET` env/secrets, 30-min expiry) plus
     `pick_count`, `deck_size` (78) and the card-back URL. No card identities
     are exposed to the client.
  2. `reveal_session(token, picks)` → maps the tapped hidden-deck positions
     (in tap order = spread order) back to real cards + states. Validates pick
     count, range, duplicates, spread match, signature and expiry.
- Service: `create_draw_session`, `reveal_session`, `TarotDrawError` (new);
  `draw_three`, `draw_one`, `draw_celtic_cross` (legacy auto-draw, now 78-card,
  used by the compatibility API routes); `get_birth_card`
- Constants: `FULL_TAROT_DECK` (22), `MINOR_ARCANA` (56), `FULL_78_DECK` (78),
  `CELTIC_CROSS_POSITIONS`, `TAROT_BASE`, `card_image_url`, `card_back_url`
- API: `POST /tarot/draw-session` + `POST /tarot/reveal` (recommended path for
  mobile); legacy `/three-card`, `/yes-no`, `/celtic-cross`, `/birth-card` kept
- RAG: `tguide.md`, k=6–10 (covers all 78 cards, Major + Minor)
- AI cost: ~₹0.05 per reading
- Cryptographic randomization via `secrets.SystemRandom`

### 2. horoscopes — `features/horoscopes/`
- Western (sun sign by DOB) + Vedic (moon sign by profile, 3 timeframes Daily/Monthly/Yearly)
- Service: `generate_western_forecast`, `generate_vedic_forecast`
- RAG (Vedic only): `bphs2.md` gochara chapter, k=10
- Cached 24h per profile+date

### 3. vault — `features/vault/`
- Profile CRUD + import/export JSON + ⭐ default profile
- Pure CRUD, no AI
- Schema: name, date, time (24h HH:MM), place, lat, lon, tz, gender, exact_time
- Storage: browser localStorage in Streamlit; per-user DB in mobile app

### 4. numerology — `features/numerology/`
- Two systems: Western (Pythagorean) + Indian/Vedic (Chaldean)
- Two tabs: Full Report + Personal Cycles & Pinnacles
- Full Report sub-modes: Full Report / Ask-a-Question
- "🌌 Cross-validate with Vedic Kundli" checkbox — uses profile dossier
- Numbers: Life Path, Destiny, Soul Urge, Personality (★ master numbers 11/22/33)
- Personal Year/Month/Day + 4 Pinnacle cycles with Challenges
- RAG: `inum1.md` (Vedic) or `wnum.md` (Western)

### 5. consultation — `features/consultation/`
- Open chat — "Ask the Astrologer"
- Uses default profile only
- Intent classifier: TIMING / MARRIAGE / CAREER_WEALTH / HEALTH / CHILDREN / SPIRITUAL / EDUCATION / FOREIGN / GOCHARA / GENERAL
- Per-intent RAG book selection (`INTENT_RAG_BOOKS`)
- First-turn vs follow-up turn-style hint
- Streams via Gemini Flash Lite at temperature 0.5 (conversational)

### 6. dashboard — `features/dashboard/`
- Toggleable widgets: greeting / consult link / energy tiles / Astro-Decide / cosmic week / daily tarot / dasha shift alert
- AI calls: `fetch_data` (greeting + tiles), `fetch_daily_tarot`, Astro-Decide
- Tara Bala for cosmic week (Janma → Parama Mitra colors)
- Dasha shift alert: 45 days for AD, 14 days for PD
- Cached 24h

### 7. kundli — `features/kundli/`
- **Free Kundli** in-app scrollable: D1 SVG, Panchanga, Functional Profile, Avakahada, Planetary Positions, Vimshottari MD/AD, Sade Sati, Shadbala, SAV, Bhava Bala, Remedies, Manglik, Kaal Sarp
  - Optional 8-topic AI prose (~₹0.10)
- **Premium PDF**:
  - 7 themes (classic_vedic, ganesha, krishna, shiva, durga, lakshmi, saraswati, royal_gold)
  - Languages: en/hi/ta/te/mr/bn/gu
  - Optional Western Appendix
  - Optional AI Narrative (~₹5: karmic story + 8 decade predictions + per-yoga + transit synthesis)
- `content.py` + `narrative.py` hold the two AI batches

### 8. palmistry — `features/palmistry/`
- Default profile OPTIONAL (cosmic Kundli alignment via checkbox in UI / optional in API). Premium Palm PDF generator (in `shared/pdf/palm_pdf.py`) has been updated to conditionally render cover subtitles ("A cosmic reading..." vs "A sacred reading...") and suppress planetary alignment notes when `used_kundli` is `False`.
- Pipeline: dominant full-palm photo (plus optional role-labelled mobile detail captures) → EXIF orient → quality check → MediaPipe landmarks → 7 rotation-invariant mount crops (calculated via Euclidean distance) → palm tone (HSV) → hand metrics. Python remains a guardrail/crop layer; AI remains the visual palmist.
- Two-Pass Visual VLM Pipeline with VLM Self-Correction & Calibration:
  - Pass 1: Cheap visual scan to extract strict structured Phase A JSON observations of lines, mounts, marks, and `capture_guidance`. Visual calibration is enhanced by passing two Supabase-hosted diagrams alongside the hand images: `book_image_18.jpg` as `REFERENCE 1` (mounts/gunas) and `reference_grid_3.jpg` as `REFERENCE 2` (a 25-box template grid detailing line defects like islands, breaks, and chains) to serve as a physical calibration stencil.
  - VLM Visual Self-Correction: Integrates a 100% automated visual scan check at the end of Pass 1. The VLM evaluates finger proportions (`"index_vs_ring_length"`) and palm color tone (`"vitality_visual_class"`), dynamically overriding noisy MediaPipe physical landmark ratios and HSV skin color heuristics.
  - State & UI Synchronization: Write VLM-corrected hand metrics (e.g. ring finger taller, setting ruling planet to Sun) and vitality (e.g. Subdued) back into Streamlit's session state (`st.session_state.palm_analysis`) before the final rerun. This forces the UI signals list and ruling planet card to update instantly to match the visual scan and Phase B reading text.
  - Pass 2: Local & free context gathering (Vedic planets, nakshatras, skin dosha mapping from HSV vitality) + targeted Qdrant semantic search of the actual lines/marks confirmed by Phase A. Blind pre-scan retrieval is not used.
  - Pass 3: Detailed Phase B markdown reading grounded in pre-confirmed visual findings (with calibration). Invalid Phase A JSON, a poor Phase A photo judgment, or `general_reading_ready = False` skips Phase B to avoid a fluent but weakly grounded second AI call.
- Planet Dominance Refinement: Middle finger (Saturn) is physically always the longest finger in human hands. Excluded Saturn from dominant finger relative height comparisons, letting active personality/character traits (Jupiter/index, Sun/ring, Mercury/little) correctly dictate the ruling planet.
- Conservative front-photo limits: Phase A must mark marriage/relationship lines `not_assessable` unless the Mercury side edge is clearly visible, must not infer thumb flexibility from a neutral open-palm pose, and must treat mount fullness conservatively because one flat image cannot prove 3D elevation from lighting alone.
- Two knowledge sources stacked: `knowledge_lookup.py` (static JSON: planet/nakshatra/dosha) + `qdrant_search.py` (semantic palmistry.md).
- AI cost: ~₹0.35 per reading (extremely cheap, well below the ₹1 target cap).
- FastAPI mobile contract: `POST /palmistry/read` keeps legacy single `image_base64` support and also accepts `captures` with one `dominant_full` plus optional `dominant_line_closeup`, `mercury_edge`, `thumb_flex`, or `non_dominant_full`. `POST /palmistry/scan` returns the one-call visual observations and capture guidance only.


### 8b. face_reading — `features/face_reading/`
- Vedic face reading (Mukha Samudrika). Upload a front-facing photo → reading. Works for **any** face; **optional** "Link my birth chart" toggle adds a face-vs-chart cross-reference.
- Vision: `shared/astro/face_vision.py` — MediaPipe **Face Mesh** (478 pts), reuses palm engine's image prep. Computes face shape → Pancha Bhoota element, three-zone proportions, eye spacing/tilt, nose ratios, jaw, symmetry; frontal-pose gate; region crops.
  - **Pose Pitch Gating**: Added relative vertical pitch pose check: $\text{pitch} = \frac{\text{nose\_y} - \text{eye\_y}}{\text{mouth\_y} - \text{eye\_y}}$. Reject photos tilted upward (`pitch < 0.35`) or tilted downward (`pitch > 0.60`) to prevent 2D projection distortion from distorting zone measurements.
- Knowledge: `data/face_knowledge.json` (5 shapes→elements, three zones, feature meanings, moles, planet appearance, optional kundli layer). `knowledge_lookup.py` maps measured geometry → meanings. **No RAG / Qdrant** — JSON-only, lightweight, grounded directly in classical samudrika shastra and Dharmender Kumar Bansal Patwari's D-1 Kundli mapping.
- AI: ONE Gemini VLM call (full face + 4 region crops + measured geometry + knowledge + optional dossier) → Phase A JSON + Phase B reading.
  - **VLM Visual Self-Correction**: VLM visually confirms face shape and dominant zone (`"dominant_zone"` added to Phase A JSON observations), dynamically overriding noisy landmark coordinates in `vlm_reader.py`.
  - **High-Availability Fallbacks**: Implemented client model fallback ladder (`gemini-3.1-flash-lite-preview` -> `gemini-2.5-flash` -> `gemini-1.5-flash`) for robust availability under rate limits.
- State & UI/API Sync: VLM-corrected metrics are synchronized back to Streamlit (`view.py`) and return payloads (`api.py`), ensuring visual cards in the UI instantly match the generated prose.
- Deliberately **excludes line-based reading** (forehead rekha / gait) for accuracy. Respectful, non-diagnostic framing.
- API: `POST /face_reading/read` (`image_base64`, `use_kundli`, optional `profile`).

### 9. oracle — `features/oracle/` (6 sub-features)
- Pure FastAPI router in `api.py` (Streamlit-free; the mobile app calls this) + legacy Streamlit dropdown in `_dropdown.py`. Package `__init__.py` is a lazy loader so importing `features.oracle.api` never pulls in Streamlit.
- 6 standalone show_*() Streamlit entry points
- `deep_analysis.py` — Full Life Reading: 3 parallel agents (Parashari/Timing/KP) → Synthesizer
- `matchmaking.py` — Ashta Koota + Manglik + Compatibility Index for boy/girl
- `marriage.py` — Destiny Marriage Matrix via `calculate_destiny_confirmation`
- `gochara.py` — Live transit overlay
- `compare.py` — 2-10 profile ranking with criteria + bands/percentiles/discrimination index
- `prashna.py` — Horary chart cast at NOW + querent location

---

## Bug audit — status

| # | Issue | Status |
|---|---|---|
| 1 | Dead `views/oracle.py` (349 lines) | ✅ Deleted |
| 2 | Dead `pdf_engine/builder.py` (381 lines) + `pdf_engine/charts/` | ✅ Deleted |
| 3 | Dead `build_deep_analysis_prompt` | ✅ Deleted |
| 4 | `palmistry_qdrant.py` had unused `import streamlit` (purity violation) | ✅ Fixed |
| 5 | Unused `FREE_MODELS` import in `forecasts.py` | ✅ Fixed (file later deleted entirely) |
| 6 | `pdf_engine/charts/` half-done split | ✅ Deleted |
| 7 | `api/` folder = abandoned lossy FastAPI port | ✅ Deleted |
| 8 | `kundli_content.py` reads `.streamlit/secrets.toml` directly | ✅ Fixed — env-var fallback |
| 9 | `get_filename` duplicated in `helpers.py` and `state.py` | ✅ Fixed — single source: `features.tarot.constants.card_image_filename` |
| 10 | Stale folders: `tarot/` (local images, unused), `palm_images/` (unused), `kundli/` (throwaway smoke test) | ✅ Deleted |
| 11 | Stale doc files: `APP_OVERVIEW.md`, `ARCHITECTURE.md` (replaced by FEATURE_SPEC.md + per-feature READMEs) | ✅ Deleted |
| 12 | `kundli_pdf.py` at 983 lines mashes chart-renderers + builder | ✅ Split — `shared/pdf/{themes,charts,builder}.py` |
| 13 | `google.generativeai` is deprecated, needs migration to `google.genai` | ✅ Migrated — wrapper class preserves the same call sites |
| 14 | Oracle had no FastAPI routes (was Streamlit-only) | ✅ Added — `features/oracle/api.py` with all 6 endpoints |
| 15 | Palmistry `palm_knowledge.json` path was broken after Phase 2 move | ✅ Fixed — moved JSON next to the code in `features/palmistry/data/` |
| 16 | Stale aiguide JSONs (palm_glossary, palm_miner_output — build artifacts) | ✅ Deleted (4.8 MB freed) |
| 17 | Tarot was auto-draw only (22 Major Arcana); not how real readings work and not mobile-friendly | ✅ Reworked — full **78-card deck** + **interactive picker**: stateless signed-token `draw-session`→`reveal` flow (backend is source of truth), swipe-picker Streamlit component, new `/tarot/draw-session` + `/tarot/reveal` FastAPI routes (legacy routes kept). Birth Card + Dashboard daily card unchanged. Optional `TAROT_DRAW_SECRET` for token signing in prod. |
| 18 | No face-reading feature | ✅ Added **face_reading** — Vedic Mukha Samudrika reader. MediaPipe Face Mesh → deterministic geometry (shape→element, zones, features) fed as ground truth to ONE Flash Lite VLM call; JSON knowledge base (no RAG, under ₹1). Works for any face; optional kundli cross-reference. Line-based reading excluded for accuracy. New `/face_reading/read` route + nav entry. |
| 19 | `shared/pdf/builder.py` referenced undefined `render` instead of imported `render_chart_svg` causing NameError when compiling Premium Kundli PDF | ✅ Fixed — updated call to `render_chart_svg` |
| 20 | Palmistry RAG was "blind" (Qdrant search executed before physical lines/marks were visually verified). | ✅ Fixed — re-architected into a Two-Pass visual pipeline (Pass 1: VLM scan to Phase A JSON observations, Pass 2: local/Qdrant lookup based on observed lines, Pass 3: Phase B grounded reading). |
| 21 | AI provider/model was hardcoded to Gemini across many call sites; no way to switch models or try DeepSeek without editing feature code | ✅ Added provider-agnostic AI layer. New `shared/ai/config.py` is the single place to set per-task model names (`default`/`chat`/`json`/`agent`/`vision`) + a fallback ladder. Provider (Gemini/DeepSeek) is auto-detected from the model-name prefix, so switching or adopting a new model = typing its name. New `shared/ai/deepseek_client.py` adapter mirrors the Gemini wrapper (text + streaming + JSON); `shared/ai/__init__.py` is the provider-neutral front door. Optional `DEEPSEEK_API_KEY` wired in Streamlit + FastAPI entry points. Caller sites (palmistry, face_reading, consultation, kundli content, oracle agents) now read their model from config. Vision-on-DeepSeek not yet supported (Gemini image format) — falls back to Gemini. |
| 22 | Birth time was effectively required; only `exact_time` (bool) distinguished confirmed vs approximate, and there was no way to handle a user with NO birth time (needed for mobile onboarding conversion) | ✅ Added a 3-tier birth-time precision model in `shared/astro/kundli.py`. `BirthData` now has `birth_time_known` (+ existing `exact_time`) → derived `time_precision` (`exact`/`approximate`/`unknown`) plus `houses_reliable` (needs a time) and `divisionals_reliable` (needs *exact* time — D9/D60 are minute-sensitive). When time is `unknown`, the chart computes with a noon placeholder so nothing downstream breaks; consumers gate time-sensitive output via the flags. `/kundli/compute` now returns `time_precision` + the two reliability flags for the mobile app. Fully backward compatible (flag defaults preserve old behavior). Birth Time Rectification (narrowing approximate→exact) deferred to v2. |
| 21 | Palmistry blocked users without a saved profile by requiring a default profile. | ✅ Fixed — made Birth Chart (Kundli) alignment completely optional via checkbox in Streamlit and optional field in FastAPI. |
| 22 | Ayurvedic Skin Dosha vitality lookup was empty or inaccurate. | ✅ Fixed — upgraded mapping of HSV vitality classes and blended classical default dosha profile contexts. |
| 23 | Mount cropping did not account for tilted or rotated palms (used vertical delta). | ✅ Fixed — calculated crops using mathematical Euclidean distance metrics for full rotation-invariance. |
| 24 | Palmistry VLM calls were expensive (~Rs. 2) and prone to hallucinations. | ✅ Fixed — optimized prompts and orchestration to cost ~Rs. 0.35 per call while reducing the hallucination surface. |
| 25 | Supabase images not fully leveraged for VLM physical line calibration. | ✅ Fixed — fetched, cached, and passed `reference_grid_3.jpg` (REFERENCE 2) for visual calibration in Pass 1 VLM prompt. |
| 26 | Noise in MediaPipe landmarks and HSV color space caused incorrect finger proportions, ruling planet calculation, and skin vitality, creating UI-reading mismatches. | ✅ Fixed — excluded Saturn from the dominant comparative check so active traits (Jupiter, Sun, Mercury) determine the ruling planet. Implemented a 100% automated VLM Visual Self-Correction override in Pass 1 to correct noisy MediaPipe index-vs-ring ratios and skin tone HSV metrics, and synchronized these corrections back to `st.session_state.palm_analysis` to instantly update UI widgets. |
| 27 | Palmistry still accepted blind pre-scan retrieval and overconfident one-photo claims. | ✅ Fixed — all Vedic/Qdrant context retrieval now waits for valid Phase A observations; unusable visual scans skip the second AI call; Phase A no longer invents Kundli agreement, thumb flexibility, relationship-line counts, or mount fullness beyond what the photo supports. |
| 28 | Smartphone backend contract only accepted one palm image and could not ask for material extra evidence smoothly. | ✅ Fixed — palmistry now accepts role-labelled optional captures, exposes a scan-only FastAPI route, and returns AI capture guidance in Phase A while preserving the old single-photo `/read` contract. |
| 29 | `/oracle` failed to mount on the deployed backend (`ModuleNotFoundError: No module named 'ui_streamlit'`) because `features/oracle/__init__.py` eagerly `import streamlit` + the six Streamlit `show_*` views, so any `import features.oracle.api` pulled in Streamlit (absent on the Render server). | ✅ Fixed — moved the Streamlit dropdown body into `features/oracle/_dropdown.py` and turned `__init__.py` into a PEP 562 lazy loader (`__getattr__`). `api.py`/`schemas.py` were already pure; now importing the package is Streamlit-free, so all 6 endpoints mount. Streamlit app's `from features.oracle import show_oracle` still works (loads lazily). |

---

## Future work (only the mobile/website builds remain)

- Build the Flutter mobile app + Next.js website that consume `fastapi_main.py`.
  Backend is ready — endpoints exposed across 10 features:
  - `/tarot/*`        (6)  draw-session, reveal (interactive picker),
                            three-card, yes-no, celtic-cross, birth-card
  - `/horoscopes/*`   (2)  western, vedic
  - `/numerology/*`   (2)  full-report, cycles
  - `/consultation/*` (1)  ask
  - `/dashboard/*`    (2)  data, decide
  - `/kundli/*`       (3)  compute, free-reading, premium-pdf
  - `/palmistry/*`    (2)  scan, read
  - `/face_reading/*` (1)  read (photo; optional kundli cross-ref)
  - `/vault/*`        (4)  CRUD + default
  - `/oracle/*`       (6)  deep-analysis, matchmaking, marriage, gochara, compare, prashna
  - Plus `/docs` (Swagger) + `/redoc` (ReDoc) auto-generated by FastAPI.

## Why this layout is better for a vibe coder

- **Want to change tarot?** Open `features/tarot/`. Everything tarot is in there.
- **Want to add a new feature?** Copy any `features/<feat>/` folder and rename it. Six files.
- **Want to wire FastAPI?** Each feature already has `api.py`. Mount them in one file.
- **Want a mobile app?** Each feature already has `schemas.py` with Pydantic models. Generate Swift/Kotlin clients from there.
- **Want to find why X is broken?** The trail is always `view.py → service.py → prompts.py`. No spelunking through 4 engines.
