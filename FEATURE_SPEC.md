# Myastro — Feature Specification & Architecture

**Last updated:** 2026-05-19 — Phase 3 complete. Final structure live.

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
  palmistry/                    (Single-call VLM palm reading)
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
  ai/                           Gemini client + RAG + cross-cutting prompts
    gemini_client.py            FREE_MODELS + retry/fallback wrappers
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
- Default profile OPTIONAL (cosmic Kundli alignment via checkbox in UI / optional in API).
- Pipeline: EXIF orient → quality check → MediaPipe landmarks → 7 rotation-invariant mount crops (calculated via Euclidean distance) → vitality (HSV) → hand metrics.
- Two-Pass Visual VLM Pipeline with Cosmic Sensory Verification:
  - Pass 1: Cheap visual scan to extract strict structured Phase A JSON observations of lines, mounts, and marks.
  - Pass 2: Local & free context matching (Vedic planets, nakshatras, skin dosha mapping from HSV vitality + user-validated touch textures) + targeted Qdrant semantic search of actual lines/marks (including confirmed sacred Vedic Chinhas: Matsya, Trishul, Yavarekha).
  - Pass 3: Detailed Phase B markdown reading grounded in both pre-confirmed visual findings and verified tactile/symbolic inputs.
- Cosmic Sensory Verification: An optional, collapsed fine-tuning expander in the UI that acts as a human-in-the-loop override for palm touch feeling (for absolute Ayurvedic Sparsha accuracy), thumb flexibility (bypassing camera tilt issues), and rare microscopic sacred signs. By default, the app is 100% automated (relying on vision metrics & HSV color vitality classification), leaving this panel strictly as a premium optional refinement with zero extra API cost.
- Two knowledge sources stacked: `knowledge_lookup.py` (static JSON: planet/nakshatra/dosha) + `qdrant_search.py` (semantic palmistry.md).
- AI cost: ~₹0.35 per reading (extremely cheap, well below the ₹1 target cap).

### 8b. face_reading — `features/face_reading/`
- Vedic face reading (Mukha Samudrika). Upload a front-facing photo → reading. Works for **any** face; **optional** "Link my birth chart" toggle adds a face-vs-chart cross-reference.
- Vision: `shared/astro/face_vision.py` — MediaPipe **Face Mesh** (478 pts), reuses palm engine's image prep. Computes face shape → Pancha Bhoota element, three-zone proportions, eye spacing/tilt, nose ratios, jaw, symmetry; frontal-pose gate; region crops.
- Knowledge: `data/face_knowledge.json` (5 shapes→elements, three zones, feature meanings, moles, planet appearance, optional kundli layer). `knowledge_lookup.py` maps measured geometry → meanings. **No RAG / Qdrant** — JSON-only, lightweight.
- AI: ONE Gemini Flash Lite VLM call (full face + 4 region crops + measured geometry + knowledge + optional dossier) → Phase A JSON + Phase B reading. ~under ₹1.
- Deliberately **excludes line-based reading** (forehead rekha / gait) for accuracy. Respectful, non-diagnostic framing.
- API: `POST /face_reading/read` (`image_base64`, `use_kundli`, optional `profile`).

### 9. oracle — `features/oracle/` (6 sub-features)
- Legacy dropdown router in `__init__.py` + 6 standalone show_*() entry points
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
| 18 | `shared/pdf/builder.py` referenced undefined `render` instead of imported `render_chart_svg` causing NameError when compiling Premium Kundli PDF | ✅ Fixed — updated call to `render_chart_svg` |
| 19 | Palmistry RAG was "blind" (Qdrant search executed before physical lines/marks were visually verified). | ✅ Fixed — re-architected into a Two-Pass visual pipeline (Pass 1: VLM scan to Phase A JSON observations, Pass 2: local/Qdrant lookup based on observed lines, Pass 3: Phase B grounded reading). |
| 20 | Palmistry blocked users without a saved profile by requiring a default profile. | ✅ Fixed — made Birth Chart (Kundli) alignment completely optional via checkbox in Streamlit and optional field in FastAPI. |
| 21 | Ayurvedic Skin Dosha vitality lookup was empty or inaccurate. | ✅ Fixed — upgraded mapping of HSV vitality classes and blended classical default dosha profile contexts. |
| 22 | Mount cropping did not account for tilted or rotated palms (used vertical delta). | ✅ Fixed — calculated crops using mathematical Euclidean distance metrics for full rotation-invariance. |
| 23 | Palmistry VLM calls were expensive (~Rs. 2) and prone to hallucinations. | ✅ Fixed — optimized prompts and orchestration to cost ~Rs. 0.35 per call with extremely high accuracy. |

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
  - `/palmistry/*`    (1)  read
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
