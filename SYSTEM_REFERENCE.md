# Myastro — System Reference (deep map of the real product)

**Last updated:** 2026-05-30
**Purpose:** The single deep reference so no human or AI has to re-read the code to
understand what exists. This complements `FEATURE_SPEC.md` (high-level source of
truth). When code changes, update this file too (see `feedback_doc_sync` rule).

> **Read me first — the two-surface reality**
> - **Streamlit web app** (`ui_streamlit/app.py`) = the **real, finished, working
>   product.** Every tool is wired to the engine + AI. This is what actually runs today.
> - **React Native / Expo mobile app** (`mobile/`) = a **visual mockup.** Almost every
>   screen shows hardcoded placeholder data. Only the birth chart is wired. The job is
>   to wire the mockup to the FastAPI endpoints below.
> - **FastAPI** (`fastapi_main.py`) = the backend that exposes the shared engine to the
>   mobile app + future website. Mounts every `features/<feat>/api.py` router.
> - **Why wiring is cheap:** all real logic lives in `service.py` + `shared/`. Streamlit
>   `view.py` and FastAPI `api.py` are both thin callers of the same brain. No rewrite.
>
> ⚠️ **Accuracy note:** the endpoint inventory in §8 is verified ground truth (read from the
> `@router` decorators). Trust §8 over any prose if they ever disagree.

---

## 0. Architecture in one picture

```
                ┌─────────────────────────┐
                │   shared/  (the BRAIN)   │   pure compute, zero UI
                │     astro/ · ai/ · pdf/   │
                └────────────┬────────────┘
            ┌────────────────┴────────────────┐
   features/<feat>/service.py  (per-feature business logic, no UI)
            │                                  │
   features/<feat>/view.py            features/<feat>/api.py
   (Streamlit screen)                 (FastAPI route)
            │                                  │
   ui_streamlit/app.py                fastapi_main.py
   (web app — REAL)                   (mobile/website backend)
                                              │
                                       mobile/ (Expo — MOCKUP)
```

Per-feature folder contract (every feature has these):
`__init__.py · README.md · prompts.py · service.py · schemas.py · view.py · api.py`

---

## 1. The shared engine — `shared/astro/`

This is the part that makes the whole product defensible: a full, classically-accurate
Vedic compute engine. **Zero Streamlit/FastAPI imports.** Sidereal, Lahiri ayanamsha
(default; 4 more available), Whole-Sign houses + KP Placidus cusps.

**Ephemeris = the free, owned Skyfield engine** (MIT + JPL DE440s public-domain + pyERFA
BSD) reached through a one-file **adapter seam** — the runtime is **fully Swiss-Ephemeris-
free**. See §1.0 below and `docs/ephemeris-decision.md`.

### 1.0 Ephemeris adapter seam — `ephemeris.py` + `ephem_skyfield.py`
The whole app gets every raw celestial number from **`shared.astro.ephemeris`** (the
adapter), never from a specific engine directly. The provider is chosen by the
`EPHEMERIS_PROVIDER` env var:
- **`skyfield`** (DEFAULT) — the free shipping engine in `ephem_skyfield.py` (Skyfield +
  JPL `de440s.bsp` + pyERFA). No Swiss Ephemeris.
- **`swisseph`** — Swiss Ephemeris, **dev cross-validation only** (`pyswisseph` lives in
  `requirements-dev.txt`, not installed in production).

Adapter surface (all return plain Python floats/lists): `ayanamsa(jd, mode)`,
`planet_lon(_speed)(jd, name, mode)`, `planet_lat`, `node_lon` (**Mean** node — unified
convention), `ascendant`, `houses(system, mode)`, tropical variants
(`planet_lon_tropical`, `ascendant_tropical`, `houses_tropical`, `node_lon_tropical`) for
the Western chart, calendar helpers (`julday`, `jd_to_utc`), `sun_rise_set`,
`moon_rise_set`, `next_eclipse(s)`. **Planet IDs are NAME STRINGS** ("Moon", "Mars" …).
- **Ayanamsha `mode`** — all five implemented on the free engine via frozen J2000 anchors
  + shared IAU-2006 precession: `lahiri` (default), `raman`, `krishnamurti` (KP),
  `yukteshwar`, `fagan_bradley`. Validated to ≤0.001″ vs Swiss Ephemeris.
- **Validation:** `scripts/validate_ephemeris.py` diffs the free engine vs Swiss Ephemeris
  (positions, ayanamshas, ascendant, houses, tropical, latitude, calendar, all 16 vargas,
  panchanga) → 0 mismatches except the irreducible D60 boundary rate (~0.1%).

### 1.1 `constants.py` (the lookup tables everything keys on)
- `SIGNS` (12), `PLANETS` (7 classical → **name strings**, passed to the ephemeris adapter),
  `OUTER_PLANETS` (Uranus/Neptune/Pluto, display + Western only — skipped by
  dasha/yoga/dignity logic). *(No `swisseph` import — IDs became names when the engine
  moved off Swiss Ephemeris.)*
- `DIGNITIES` (exalt/debil sign per planet), `OWN_SIGNS`, `SIGN_LORDS_MAP`, `COMBUST_DEGREES`.
- `NAKSHATRAS` (27), `NAKSHATRA_LORDS` (Vimshottari order ×3), `NAK_NATURES` (Fixed/Movable/
  Fierce/Mixed/Swift/Tender/Sharp → which stars), `NAK_ADVICE` (plain-English per nature).
- `DASHA_YEARS` + `DASHA_ORDER` (Vimshottari 120-yr cycle), `YOGA_NAMES` (27 Panchanga yogas).
- `YEAR_DAYS = 365.25` (dasha year length — matched to AstroSage/JHora to avoid drift).
- `PYTH_MAP` / `CHALDEAN_MAP` (numerology letter values).
- House sets: `DUSTHANAS {6,8,12}`, `KENDRAS {1,4,7,10}`, `TRIKONAS {1,5,9}`.
- `COMPARISON_CRITERIA` (9 life areas for multi-profile compare), `PERSONAL_YEAR_MEANINGS`,
  `NAV_PAGES` (Streamlit nav).

### 1.2 `astro_calc.py` (~110 KB — the ephemeris + classical-rules workhorse)
Key public functions (by purpose):
- **Time/position:** `local_to_julian_day`, `get_planet_longitude_and_speed`,
  `get_rahu_longitude`, `sign_index_from_lon`, `sign_name`, `format_dms`, `nakshatra_info`
  (→ nakshatra, lord, pada), `get_baladi_avastha`.
- **Houses/Lagna:** `whole_sign_house`, `get_lagna_and_cusps`, `get_placidus_cusps`,
  `get_placidus_house`.
- **KP system:** `get_kp_sub_lord`, `get_kp_4step`, `get_kp_cusp_promise`
  (does a cusp's sub-lord promise the event?), `get_kp_marriage_timing_clues`.
- **Special lagnas:** `calculate_arudha_lagna`, `calculate_indu_lagna` (wealth),
  `get_lagna_lord_chain`.
- **Strength/relationships:** `get_functional_planets` (benefic/malefic/yogakaraka per
  lagna), `get_house_strength_summary`, `get_conjunctions`, `get_mutual_aspects`,
  `detect_graha_yuddha` (planetary war), `check_neecha_bhanga`.
- **Yogas/doshas:** `detect_yogas` (broad detector, present/absent lists),
  `check_manglik_dosha`, `get_manglik_cancellation_verdict`, `calculate_sade_sati`.
- **Dasha:** `build_vimshottari_timeline` (current MD/AD/PD + start lord + balance),
  `get_antardasha_table`, `build_lifetime_dasha_sequence`.
- **Daily/transit (powers the mobile daily loop):** `calculate_tara_bala` (9-fold day-star
  quality from natal vs transit Moon → Go/Stop/Caution), `daily_timing_windows` +
  `sun_rise_set` (Rahu Kaal / Yamaganda / Gulika / Abhijit + the 16-segment Choghadiya
  wheel), `chandra_sandhi_window` (Moon at sign junction = low window),
  `next_eclipse` (soonest solar/lunar + Sutak).
- **Bala:** `calculate_ashtakavarga` (SAV/BAV bindus), `calculate_shadbala` (6-fold planet
  strength), `get_bhava_bala`, `get_chara_karakas` (Jaimini Atmakaraka→chain).
- **The big "answer" builder:** `build_event_timing_atlas` — precomputed "at what age will X
  happen" windows by walking the lifetime dasha against event significators. This is what
  lets the chat answer timing questions with a real age range.
- **Numerology helpers:** `calculate_numerology_core`, `get_personal_year/month/day`,
  `get_pinnacle_cycles`.
- **Western:** `get_western_sign`, `get_western_transits_today`. **Geo:** `geocode_place`,
  `timezone_for_latlon`.

### 1.3 `kundli.py` (2,545 lines — the full chart object)
The flagship. `BirthData` (input) → `compute_chart(bd)` → `KundliChart` (everything).

- **`BirthData`** — dataclass; `.from_profile(dict)` builds it from the standard profile
  shape. The **3-tier birth-time model** lives here:
  - `time_precision` → `exact` / `approximate` / `unknown`.
  - `houses_reliable` (needs any time), `divisionals_reliable` (needs *exact* time).
  - Unknown time → **noon placeholder** so the chart never crashes; only Moon-based output
    is shown. This is why every mobile daily endpoint works at any birth-time tier.
- **`compute_chart`** pipeline: pick ayanamsha (`bd.ayanamsha`, default lahiri — threaded
  through every position/lagna/cusp call) → julian day → all 9 planets + outer (Rahu/Ketu =
  **Mean** node) → Lagna + Placidus cusps → Panchanga → per-planet `PlanetPosition`
  (sign, house, nakshatra,
  pada, sub-lord, avastha, retrograde, **combustion** with retro-aware orbs, **dignity**) →
  houses with occupants → `LagnaInfo` (incl. Arudha + Indu) → functional profile → Chara
  Karakas → conjunctions/aspects/graha-yuddha. Then **layered enrichment** (each in its own
  try/except so one failure can't break the chart):
  - `divisional_charts` — **all 16 Shodashavarga D1–D60** (each varga has its own
    `dN_si(lon)` function; `VARGA_REGISTRY` lists number/name/purpose/fn; Vimshopaka weights).
  - `dashas`, `yogas`, `doshas`, `ashtakavarga` (before shadbala), `shadbala` + `bhava_bala`,
    `nakshatra_profile` (Avakahada Chakra — 24-row table), `sudarshan_chakra`,
    `transit_forecast` (12-month), `remedies`, `western_appendix`, `child_naming`, `jaimini`,
    `kp_extras`, and premium `interpretations` (from `kundli_text.py`).
- **Doshas implemented** (each returns present/severity/cause/cancellations): Kaal Sarp
  (all 12 named types), Mangal/Kuja, Sade Sati, Pitra, Guru Chandal, Grahan, Shrapit, Visha,
  Kemadruma, Angarak — with classical cancellation logic.
- **Other public computes (called explicitly, not auto-attached):**
  `compute_varshaphala(chart, year)` (annual/Tajika chart — Muntha, year-lord, Sahams),
  `rectify(chart, events, …)` (birth-time rectification by back-testing events — the raw
  material for a future "Proof / Karmic Audit" feature),
  `suggest_names(syllable, gender, count)` (nakshatra-pada name bank).
- **Helpers used by the API:** `yoga_audit`, `sade_sati_timeline`, `render_chart_svg`.

### 1.4 `dossier_builder.py` (the AI's eyes — feeds the chat & oracle)
- `generate_astrology_dossier(profile, include_d60, compact)` → a huge **plain-text** chart
  report the LLM reads: birth data, lagna foundation, full planetary positions with tags
  (Retrograde, Combust, Exalted/Debilitated, **Vargottama**, D9 dignities, **Gandanta**,
  **Papa-Kartari**, Bhava-Chalit shift), KP 4-step per planet, conjunctions/mutual aspects/
  graha-yuddha, **Neecha Bhanga** checks, yogas present/absent, Jaimini karaka chain, house
  strength summary, Ashtakavarga, house rulership map, KP cusp promises, KP marriage timing,
  divisional charts (D2–D60), Vimshottari MD/AD/PD + full antardasha table, and — the key bit
  — the **EVENT TIMING ATLAS** (`build_event_timing_atlas`): precomputed "at what age will X
  happen" windows, so timing questions get a real age-range, not a dodge.
- `get_gochara_overlay(profile)` → natal vs **live transit** positions (houses moved).
- **Note:** these two are the most powerful pieces — they are why the chat is genuinely
  chart-aware, not a generic horoscope bot.

### 1.5 The mobile daily-loop math modules (all FREE, no AI, no new deps)
Built specifically to power mobile tabs. Pure math + static lookup tables. All Moon-based,
so they work at every birth-time tier. **Deterministic + cacheable.**
- **`forecast.py`** — `daily_moon_forecast(profile, date)` (Today hero "Cosmic Weather":
  transiting Moon's house-from-natal-Moon + Tara Bala → `_CHANDRA_HOUSE` table → vibe word,
  score, mood, opportunity, caution, action, why, sanskrit). `weekly_moon_forecast` (the
  7-day rail; each day carries the full forecast + a colour `band` + `is_today`).
- **`muhurta.py`** — `plan_muhurta(event_type, start, end, lat, lon, tz, top_n)` (Explore
  "best dates to do X"). Scores each day's panchanga at sunrise against per-event classical
  rules (`_EVENT_RULES`: travel/signing/naming/vehicle/housewarming/general), picks a clear
  window (Abhijit, else good Choghadiya) that dodges Rahu Kaal. Sourced + verified.
- **`relationship_weather.py`** — `daily_relationship_weather(profile_a, profile_b, date)`
  (People tab daily per-person). Baseline = relationship-NEUTRAL kootas only (Graha Maitri +
  Gana) + Rashi-axis flavour (Nava-Pancham warm, Shad-Ashtaka friction…); daily = Tara Bala
  of today's Moon from each person. Deliberately NOT the 36-guna marriage total.
- **`face_vision.py`** / **`palm_vision.py`** — MediaPipe geometry pipelines (see features).

### 1.6 `scoring.py` (~118 KB — compatibility, comparison, destiny)
- `calculate_ashta_koota(moon_a, moon_b)` — full **36-guna** marriage match (Varna, Vashya,
  Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi). This is the MARRIAGE tool; the daily
  relationship-weather deliberately uses only the neutral subset.
- `calculate_destiny_confirmation`, `calculate_matchmaking_synastry`,
  `calculate_compatibility_index`, `calculate_marital_analysis`.
- The Oracle "Full Life Reading" per-topic scorers: wealth, relationship, career, struggles,
  health, happiness, luck, spiritual, hidden-pitfalls (each `calculate_*_score`), plus
  `calculate_custom_aspect_score` and `get_prashna_python_verdict` (horary).
- Multi-profile compare: `calculate_and_rank_profiles` + cohort stats / tie detection /
  bands / generational-placement detection / per-criterion drivers.

### 1.7 `kundli_text.py` (52 KB) — premium interpretation prose payloads
Per-house, per-planet, life-domain, Lal Kitab, year predictions, auspicious dates. Attached
to `chart.interpretations`. Imported lazily so `/kundli/compute` stays light.

---

## 2. The AI layer — `shared/ai/`

- **`config.py` — THE ONE FILE to change models.** Per-task model names:
  `default / chat / json / agent / vision`, each with a fallback ladder. Provider
  (Gemini / DeepSeek) is **auto-detected from the model-name prefix** — switch models by
  typing a new name. `model_for(task)` returns the name.
- `gemini_client.py` — Gemini adapter + retry/fallback router; `FREE_MODELS` ladder,
  `get_ai_model_by_name(custom_system_rules=…)`, `generate_content_with_fallback`.
- `deepseek_client.py` — OpenAI-compatible DeepSeek adapter, same interface (text+stream+JSON).
  Vision still Gemini-only.
- `knowledge.py` — `rag_context` (Qdrant hybrid retrieval). **Embeddings = FastEmbed/ONNX**
  (`BAAI/bge-base-en-v1.5`, 768-dim, cosine) — no PyTorch, fits free-tier RAM. ⚠️ Books must
  be **re-ingested with the ONNX chunker** so stored vectors match (open task #9).
- `reranker.py` — optional **cross-encoder reranker** (second-stage filter: re-scores the
  Qdrant top-N so the most relevant passages lead). Uses FastEmbed's `TextCrossEncoder` (ONNX,
  no new dep). Default `Xenova/ms-marco-MiniLM-L-12-v2`; **on by default**, fails safe to the
  vector order. Config (env-first then secrets.toml): `RERANK_DISABLE="1"` to turn off,
  `RERANKER_MODEL` to override. Streamlit-free.
- `prompts.py` — cross-cutting Oracle prompts + GUARDRAILS only.
- **RAG books** (Qdrant collections): `bphs1/2` (Brihat Parashara), `kp2/3/4/6` (KP),
  `htrh1/2` (Hindu astrology), `tguide` (tarot), `wnum`/`inum1` (numerology),
  `palmistry`. Routed per-feature/per-intent.

---

## 3. The data layer — FULL SCHEMA DESIGNED, NOT WIRED (task #12 half-done)

The **complete Supabase schema exists** as `supabase/schema.sql` (Postgres + Supabase Auth +
RLS on every table; design ref = `MOBILE_APP_BLUEPRINT.md §8.4`). It's far more than a stub —
it anticipates the whole product. Tables:
- **`app_users`** — extends `auth.users` (language, Expo `push_token`, settings jsonb).
- **`profiles`** — self + saved people (`source` = self/friend/manual, `relation_tag`,
  `birth_time_known`, `exact_time` → the 3-tier model).
- **`connections`** — friend requests + `share_tier` (acquaintance/close) = **the People-tab
  social growth loop.**
- **`checkins`** — the 3-tap mood log (`mood`, `energy`, `clarity`, `astro_state` jsonb, one
  per day) = **the Pattern-Engine wedge input.**
- **`patterns`** — stored personal correlations (`pattern_text`, `evidence`) = **the Pattern-
  Engine payoff.**
- **`journal_entries`**, **`streaks`** (checkin/ritual), **`subscriptions`** + **`purchases`**
  (monetization), **`groups`** + **`group_members`** (Family grid / Couple space),
  **`ritual_journeys`** (21/40-day gamified remedy journeys), **`rewards`** (badges/milestones),
  **`ai_conversations`** (Ask/Prashna history).
- **Cost-discipline caches:** `cached_daily` (shared, keyed by `date`+`astro_state_key` — one
  generation read by everyone in the same state), `cached_chart` (per-profile, keyed incl.
  `precision` so unknown→exact recomputes once), `usage_counters` (freemium soft caps per
  user/day/kind).
- A trigger auto-creates an `app_users` row on signup.

But there is **no Python client and no API wiring**: zero `supabase` references in any `.py`,
no `shared/db/` package. Nothing reads or writes these tables yet. **The schema is the plan;
the integration is unbuilt.** Consequence: the Pattern Engine, journaling, streaks, social
connections, groups, subscriptions, and caching all have designed tables but **no working
backend.** Profiles today live client-side only (browser localStorage on web). ⚠️ The
service_role key is server-only — never ship it to the app; the app uses the anon key + RLS.

---

## 4. Features — per feature: what it does · Streamlit · API · engine · AI/RAG

### 4.1 consultation — "Ask the Astrologer"
- **Streamlit (`view.py`):** open streaming chat. Per message: build dossier (incl. Event
  Timing Atlas) → `classify_intent` (TIMING/MARRIAGE/CAREER_WEALTH/HEALTH/CHILDREN/SPIRITUAL/
  EDUCATION/FOREIGN/GOCHARA/GENERAL) → per-intent RAG books (`INTENT_RAG_BOOKS`) →
  system prompt (answer-first, **anti-fatalism**, timing-Qs must give an age window) →
  last-4-turns memory + first-vs-followup hint → stream `chat` model (temp 0.5) with fallback
  ladder → PDF export.
- **FastAPI (`api.py`) — 1 route:** `/ask` (non-streaming, mobile-friendly; same dossier +
  intent + RAG + history pipeline, returns `{intent, reading}` with a FREE_MODELS fallback
  ladder). That's the **only** consultation endpoint — no mood/journal/dream routes exist.
- **AI cost:** ~1 cheap call per message (Gemini Flash Lite default).

### 4.2 dashboard — "Cosmic Compass" landing + the mobile daily endpoints
- **Streamlit (`view.py`):** toggleable widgets — AI greeting, consult link, 4-tile energy
  (Energy/Focus/Caution/Best Time), **Astro-Decide** (Tara Bala verdict + AI explainer),
  7-day Tara Bala "cosmic week", daily Tarot, **dasha-shift alert** (≤45d AD / ≤14d PD).
- **FastAPI (`api.py`) — 9 routes:**
  - AI: `/data` (greeting+tiles), `/decide` (chart-aware yes/no). **The rest are FREE/no-AI:**
  - `/forecast` (Today hero) · `/week` (7-day rail) · `/timing` (good/avoid + Choghadiya) ·
    `/muhurta` (event planner) · `/relationship-weather` (People daily) · `/day-alerts`
    (Chandra Sandhi + eclipse) · `/decide-quick` (Tara-Bala-only instant yes/no, no AI).
- See §1.5 for the math behind the free ones.

### 4.3 kundli — the flagship chart (free in-app) + premium PDF
- **Streamlit:** full scrollable free chart (D1 SVG, Panchanga, Avakahada, planetary
  positions, Vimshottari MD/AD, Sade Sati, Shadbala, SAV, Bhava Bala, remedies, Manglik,
  Kaal Sarp) + optional 8-topic AI prose (~₹0.10). Premium PDF: 7 themes, 7 languages
  (en/hi/ta/te/mr/bn/gu), optional Western appendix, optional AI narrative (~₹5).
- **FastAPI:** `/compute` (compact summary — what the app renders), `/dasha-timeline`
  (Life Chapters), `/free-reading`, `/premium-pdf`.
- **Engine:** `kundli.py` (§1.3). Lazy heavy imports → `/compute` needs only the free
  ephemeris engine (skyfield + jplephem + pyerfa + the `de440s.bsp` kernel), no SE.

### 4.4 oracle — 6 premium sub-features (Streamlit-free `api.py`, lazy `__init__`)
- `/deep-analysis` (Full Life Reading — 3 parallel agents Parashari/Timing/KP → synthesizer),
  `/matchmaking` (Ashta Koota + Manglik + index), `/marriage` (Destiny Matrix),
  `/gochara` (live transit overlay), `/compare` (2–10 profile ranking), `/prashna` (horary
  cast at NOW + querent location).

### 4.5 horoscopes — `/western` (sun-sign by DOB) + `/vedic` (Moon-sign, Daily/Monthly/Yearly)
RAG: Vedic uses `bphs2` gochara chapter. Cached 24h.

### 4.6 numerology — `/full-report` + `/cycles`
Western (Pythagorean) + Indian (Chaldean); Life Path/Destiny/Soul Urge/Personality (master
11/22/33); Personal Year/Month/Day + 4 Pinnacles; optional kundli cross-validate. RAG: `wnum`/`inum1`.

### 4.7 tarot — `/draw-session` → `/reveal` (interactive picker) + legacy auto-draws + `/birth-card`
Stateless signed-token flow (HMAC, `TAROT_DRAW_SECRET`, 30-min expiry) — backend is the source
of truth, client only sends tapped positions. 78-card deck for spreads, 22 Major for birth/daily.
RAG: `tguide`. ~₹0.05/reading.

### 4.8 palmistry — `/scan` (one-call observe) + `/read` (full)
Two-pass VLM: Pass 1 visual scan → Phase A JSON (with Supabase reference-grid calibration);
Pass 2 local + Qdrant lookup of confirmed features; Pass 3 grounded Phase B reading. MediaPipe
landmarks + 7 rotation-invariant mount crops + HSV vitality + VLM self-correction. Optional
kundli alignment. ~₹0.35/reading. RAG: `palmistry`.

### 4.9 face_reading — `/read`
Mukha Samudrika. MediaPipe Face Mesh (478 pts) → geometry (shape→Pancha Bhoota element, zones,
features) → ONE Gemini VLM call. JSON knowledge base, **no RAG**. Optional kundli cross-ref.
Pose-pitch gating; line-based reading excluded for accuracy.

### 4.10 vault — `GET/POST /{user_id}` + `POST /{user_id}/default/{idx}`
Profile CRUD + dedupe. Storage: browser localStorage (web) / per-user DB (mobile, once the
data layer is wired). Profile schema: `{name, date(YYYY-MM-DD), time(HH:MM), place, lat, lon,
tz, gender, exact_time}` (+ `birth_time_known` for the unknown-time tier). No AI.

---

## 5. Mobile app (`mobile/`) — the mockup, tab by tab

Expo SDK 54 (pinned), expo-router v6. Tabs: **Today / People / Explore / You** + floating
**Ask** FAB (on every tab) + onboarding + paywall. **All data is currently fake** (e.g.
`AskOverlay.tsx` has 4 canned answers + regex "decide"; `today.tsx` uses placeholder
constants). Only the birth chart is wired. Screens already exist for: timing, rituals, mala,
person-detail, add-person, household, couple, compat, people-compare, tarot, numerology,
chart, chapters, past-date, patterns, year, purpose, reading, widget, settings.
**→ The work is wiring these to the §4 endpoints, not building new screens.**

---

## 6. What's genuinely NEW vs already-built (the honest wedge list)

| Idea discussed | Reality in code |
|---|---|
| Grounded AI companion ("it knows my chart") | **Built** — consultation `/ask` + dossier+Atlas |
| Daily loop (hero, week, timing, decide) | **Built** — dashboard free endpoints |
| Relationship daily weather | **Built** — `/relationship-weather` |
| Persistence / data layer (Supabase) | **Full schema only** — `supabase/schema.sql` (17 tables incl. checkins/patterns/connections/groups/streaks/subscriptions/caches + RLS); no Python client or wiring (task #12 half-done) |
| Pattern Engine (mood ↔ planets over time) | **Schema only** — `checkins` + `patterns` tables designed for it; no client, no endpoints, no correlation code |
| Journaling / mantra | **Not built** — no endpoints (mockup screens only); `journal_entries` table designed |
| Proof / Karmic Audit (back-test past events) | **Engine partial** — `rectify()` + Event Timing Atlas exist; no user-facing flow or endpoint (task #16) |
| Rituals / calm CHANI-style space | **Mockup screens + `ritual_journeys` table** — no backend feed/endpoints |
| Social People (friends/share/family grid) | **Schema only** — `connections` + `groups` tables designed; only one-shot matchmaking + daily weather endpoints exist (task #17) |

**Bottom line:** the **compute engine + the read-only daily/chart/oracle endpoints are real
and strong.** What's genuinely missing is everything **stateful**: the Supabase schema is
designed but not wired, so the Pattern Engine, journaling, and any "remembers me over time"
feature are unbuilt. Plus the Proof back-test flow, a rituals feed, and the social layer.
Then wire it all into the mobile mockup and re-aim presentation.

---

## 7. Known doc/staleness flags (verify before trusting)
- `FEATURE_SPEC.md` "Future work" still says **Flutter/Next.js** — actual app is React
  Native/Expo. Stale.
- Task list shows Supabase (#12) "in progress" — accurate but partial: the **full schema
  exists** (`supabase/schema.sql`, 17 tables + RLS), but **no Python client / no endpoints**
  use it yet.
- RAG vectors need ONNX re-ingest (task #9) before hybrid search is fully consistent.

## 8. Verified endpoint inventory (ground truth, from `@router` decorators)
- **vault:** `GET /{user_id}` · `POST /{user_id}` · `POST /{user_id}/default/{idx}`
- **horoscopes:** `/western` · `/vedic`
- **tarot:** `/three-card` · `/yes-no` · `/celtic-cross` · `/birth-card` · `/draw-session` · `/reveal`
- **numerology:** `/full-report` · `/cycles`
- **palmistry:** `/scan` · `/read`
- **consultation:** `/ask` (only)
- **oracle:** `/deep-analysis` · `/matchmaking` · `/marriage` · `/gochara` · `/compare` · `/prashna`
- **kundli:** `/compute` · `/dasha-timeline` · `/free-reading` · `/premium-pdf`
- **face_reading:** `/read`
- **dashboard:** `/data` · `/forecast` · `/week` · `/relationship-weather` · `/day-alerts` ·
  `/muhurta` · `/decide-quick` · `/timing` · `/decide`
