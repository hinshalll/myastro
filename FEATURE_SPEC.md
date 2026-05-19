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
- Service: `draw_three`, `draw_one`, `draw_celtic_cross`, `get_birth_card`
- Constants: `FULL_TAROT_DECK`, `CELTIC_CROSS_POSITIONS`, `TAROT_BASE`
- RAG: `tguide.md`, k=6–10
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
- Default profile REQUIRED (kundli overlay)
- Pipeline: EXIF orient → quality check → MediaPipe landmarks → 7 mount crops → vitality (HSV) → hand metrics
- Single Gemini Flash Lite VLM call (full palm + 7 mount crops + reference image)
- Two-phase output: Phase A JSON observations + Phase B markdown reading
- Two knowledge sources stacked: `knowledge_lookup.py` (static JSON: planet/nakshatra/dosha) + `qdrant_search.py` (semantic palmistry.md)
- AI cost: ~₹2 per reading

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

---

## Future work (only the mobile/website builds remain)

- Build the Flutter mobile app + Next.js website that consume `fastapi_main.py`.
  Backend is ready — all 26 endpoints exposed across 9 features:
  - `/tarot/*`        (4)  three-card, yes-no, celtic-cross, birth-card
  - `/horoscopes/*`   (2)  western, vedic
  - `/numerology/*`   (2)  full-report, cycles
  - `/consultation/*` (1)  ask
  - `/dashboard/*`    (2)  data, decide
  - `/kundli/*`       (3)  compute, free-reading, premium-pdf
  - `/palmistry/*`    (1)  read
  - `/vault/*`        (4)  CRUD + default
  - `/oracle/*`       (6)  deep-analysis, matchmaking, marriage, gochara, compare, prashna
  - Plus `/docs` (Swagger) + `/redoc` (ReDoc) auto-generated by FastAPI.

## Why this layout is better for a vibe coder

- **Want to change tarot?** Open `features/tarot/`. Everything tarot is in there.
- **Want to add a new feature?** Copy any `features/<feat>/` folder and rename it. Six files.
- **Want to wire FastAPI?** Each feature already has `api.py`. Mount them in one file.
- **Want a mobile app?** Each feature already has `schemas.py` with Pydantic models. Generate Swift/Kotlin clients from there.
- **Want to find why X is broken?** The trail is always `view.py → service.py → prompts.py`. No spelunking through 4 engines.
