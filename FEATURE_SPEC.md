# Myastro — Feature Specification & Architecture

**Last updated:** 2026-06-03 — Supabase data-layer foundation wired (client + auth + `/me` CRUD).

> **For the deep code map** (engine functions, every endpoint, Streamlit-vs-mobile, what's
> built vs new) see **`SYSTEM_REFERENCE.md`**. Note: the mobile app is **React Native/Expo**,
> not Flutter — the "Future work" section below predates that decision and is stale.

### Recent changes (2026-06-03) — Supabase data-layer foundation (the keystone)
- **`shared/db/` — the Streamlit-free data layer.** `secrets.py` (env→secrets.toml, never
  hardcoded), `supabase_client.py` (service client = service_role, **server-only**, bypasses
  RLS; user client = anon key + the user's JWT so **RLS enforces owner-only**; JWT verification;
  CRUD for profiles/checkins/journal/streaks), `cache.py` (`cached_daily` + `cached_chart`).
  supabase-py is lazily imported so the backend boots even before the lib/keys exist.
- **`features/me/` — first feature on the live DB.** JWT-gated `/me/*`: `GET/POST /me/profiles`,
  `PUT/DELETE /me/profiles/{id}`, `GET/POST /me/checkins` (POST upserts + bumps the check-in
  streak), `GET/POST /me/journal`, `GET /me/streaks/{kind}`. `auth.get_current_user` verifies
  the Supabase JWT and yields a user-scoped client (reusable by future features). Mounted at
  `/me` in `fastapi_main.py`.
- **Schema hardened** (`supabase/schema.sql`): added the **Diyas** currency (`coin_wallets` +
  signed-ledger `coin_transactions`, server-write-only), `referrals`, `gifts`, `ad_rewards`
  (dedup-safe), `app_users.depth_mode`, auto-`updated_at` triggers. `supabase>=2.7` added to
  requirements. **Owner still to do:** create the live Supabase project + paste the 3 keys.
- **Out of scope** (later sessions): Pattern-Engine correlation, social graph, payment/IAP.

### Recent changes (2026-06-03) — free Skyfield ephemeris wired in (SE-free runtime)
- **The whole app now gets every celestial number from the adapter `shared.astro.ephemeris`**
  (default provider = the free Skyfield + JPL DE440s + pyERFA engine), never from Swiss
  Ephemeris directly. `astro_calc`, `kundli`, `scoring`, `muhurta`, `dossier_builder`, the
  `features/*` routers and both entry points (Streamlit `app.py`, `fastapi_main.py`) were
  rerouted; **no `swe` in the runtime path.** Validated 0 sign/nakshatra/house mismatches vs
  Swiss Ephemeris (dual-provider chart compare) + `scripts/validate_ephemeris.py`.
- **All 5 ayanamshas on the free engine** — `lahiri` (default), `raman`, `krishnamurti` (KP),
  `yukteshwar`, `fagan_bradley`, each a frozen J2000 anchor + shared IAU-2006 precession
  (≤0.001″ vs SE). `bd.ayanamsha` now actually drives the whole chart.
- **Rahu/Ketu unified to the Mean node everywhere** (was TRUE in astro_calc/kundli, MEAN in
  scoring). **Western/tropical chart** also runs on the free engine (tropical positions +
  Placidus + ascendant + Mean node, ≤2.4″ vs SE). **Graha Yuddha** uses real ecliptic latitude.
- **`pyswisseph` is now dev-only** (`requirements-dev.txt`) — kept solely as the validation
  reference. The Lahiri/other anchors are frozen constants (no `swisseph` import at runtime).
  `constants.PLANETS` are NAME strings. Docker bakes in `de440s.bsp`; the old `ephe/` SE data
  is excluded from the image. See `docs/ephemeris-decision.md`.

### Recent changes (2026-05-27) — AI-free quick-decide + clearer timing
- **New endpoint `POST /dashboard/decide-quick`** — an AI-FREE one-tap "should I do X right
  now?" for the Ask sheet's quick yes/no mode. Pure Tara-Bala math (the current moment's
  Moon read from the natal Moon) + a templated plain line — **no Gemini call**, instant and
  free. Returns `{ verdict (Yes/Wait/Proceed gently), reason, why, sanskrit, tara, question }`.
  Moon-based, so it works at unknown birth time. The deeper, question-aware answer stays in
  the AI Ask (`/decide`, `/consultation`).
- **`/dashboard/timing` now carries plain-English `tip`s** on each avoid window (Rahu Kaal /
  Yamaganda / Gulika), the good window (Abhijit), and every Choghadiya segment (per quality)
  — so the "Good/Avoid times" strip reads clearly, not just colour bars. Pure math.

### Recent changes (2026-05-27) — Today tab "next 7 days" forecast rail
- **New endpoint `POST /dashboard/week`** powers the Today tab's "next N days" peek (a
  horizontal date rail under the hero; tapping a day re-renders the hero with that date).
  **FREE: pure math + lookup, NO AI, no new deps.** Reuses `daily_moon_forecast` for each of
  N days (default 7) and adds a coarse `band` (`good` ≥0.60 / `neutral` / `difficult` <0.45)
  for the rail colour + an `is_today` flag. Each entry is the FULL daily forecast (vibe_word,
  vibe_score, mood, opportunity, caution, action, why, sanskrit), so tapping a day needs zero
  extra calls. Input `{ profile, start_date?, days? }` (same `profile` shape as
  `/kundli/compute`; `start_date` defaults to today in the profile's tz). Moon-based → works
  at every birth-time tier; deterministic. New `weekly_moon_forecast` + `_band` in
  `shared/astro/forecast.py`.

### Recent changes (2026-05-27) — Explore tab Event Timing Planner (Muhurta)
- **New endpoint `POST /dashboard/muhurta`** powers the Explore tab's "best dates & times
  to do X" planner (travel, signing/business, naming, vehicle, housewarming, general…).
  **FREE + cheap (cost rule): pure math + a pre-baked classical Muhurta lookup, NO AI, no
  new dependencies.** **Date- and location-based** (panchanga + sunrise/sunset), so **no
  birth chart is needed**. Input `{ event_type, start_date, end_date, lat, lon, tz, top_n? }`
  (unknown `event_type` → `general`). Deterministic for the same inputs.
- **Method (all classical rules VERIFIED across multiple reputable sources** — Brihat
  Samhita / Muhurta Chintamani tradition, drikpanchang, mpanchang, astrobix, astroccult,
  astrosight, anytimeastro): for each day it reads the panchanga **at local sunrise** and
  scores the five limbs against the event's rules —
  - **Nakshatra** = the core gate; each event has its own favourable-star set (e.g.
    housewarming → the fixed Dhruva stars + soft ones; travel → light/movable stars;
    business → Pushya + the steady Uttaras). See `_EVENT_RULES` source notes.
  - **Tithi:** penalise Rikta (4/9/14) + Amavasya; reward the broadly auspicious tithis.
  - **Weekday:** per-event good / avoid days. **Yoga:** strongly avoid Vyatipata & Vaidhriti
    (milder for other harsh yogas), small bonus for auspicious ones. **Karana:** avoid
    Vishti (Bhadra).
  Then it picks the best clear daytime window — **Abhijit Muhurta** first, else the first
  "good" Choghadiya — that steps clear of **Rahu Kaal / Yamaganda / Gulika Kaal** (reuses
  `daily_timing_windows`). A day must carry a favourable star AND clear a min score to be
  recommended; **if nothing qualifies, `found:false` + a plain message — no forced pick.**
- **Output:** `{ event_type, event_label, range, found, message, recommendations:[ { date,
  start, end, score (0..1), reason, why, sanskrit, + debug: nakshatra, tithi, weekday,
  yoga, karana, window, window_clear } ] }`. Warm, jargon-free; Sanskrit only in
  `why`/`sanskrit`; gentle guidance, never fate (blueprint §2).
- **New module `shared/astro/muhurta.py`:** `plan_muhurta(...)` + the static `_EVENT_RULES`
  table (easy to expand — add an event entry). Reuses `get_panchanga`, `nakshatra_info`,
  `sun_rise_set`, `daily_timing_windows` (`astro_calc.py`) and `NAK_NATURES`
  (`constants.py`). Pure math + lookup — no AI, no new dependencies, no streamlit.

### Recent changes (2026-05-27) — People tab daily "relationship weather"
- **New endpoint `POST /dashboard/relationship-weather`** powers the People tab's daily
  per-person guidance for how today feels between the user and ONE saved person. **FREE +
  cheap (cost rule): pure math + a pre-baked meaning lookup, NO AI, no new dependencies.**
  **Moon-based**, so it works even when **either person's birth time is unknown** (noon
  placeholder per person). Input `{ profile_a, profile_b, date? }` — both profiles use the
  `/kundli/compute` shape (`profile_a` = user, `profile_b` = saved person); `date` defaults
  to today in `profile_a`'s tz. Deterministic for the same two profiles + date.
- **Two classical layers (sourced — verified across multiple reputable sources):**
  1. **Baseline ("how these two mesh"):** the RELATIONSHIP-NEUTRAL kootas only —
     **Graha Maitri** (minds/temperaments, /5) + **Gana** (temperament, /6) via
     `scoring.py::calculate_ashta_koota` — blended 50/50 with the **Rashi (Moon-sign)
     relationship** flavour (same sign = mirrored moods; 2-12 = give-and-take; 3-11 = easy
     companions; 4-10 = respect/practical care; **5-9 Nava-Pancham = natural warmth**;
     **6-8 Shad-Ashtaka = friction/needs patience**; 7-7 = complementary opposites). The
     full 36-guna Ashta Koota *total* is deliberately NOT used here — it's a MARRIAGE tool
     (Yoni/Nadi score sexual compatibility/progeny; its Bhakoot factor penalises the warm
     5-9 pairing, a contradiction). Full Ashta Koota stays in the Compatibility & Marriage
     feature.
  2. **Daily ("how today feels"):** the **Tara Bala** of today's transiting Moon read from
     **each** person's natal Moon (favourable 2/4/6/8/9, neutral/restless 1, challenging
     3/5/7), combined into one day-tone. Kept deliberately modest + framed as gentle
     guidance — no single classical "daily formula for a pair" exists, so it does not
     overclaim a natal meaning as a transit result.
- **Output (display-ready):** `tone_word`, `summary`, `good_for`, `avoid`, `score` (0..1,
  today weighted 0.6 / durable baseline 0.4, clamped [0.08, 0.96]), `why` (plain English),
  `sanskrit` (Devanagari only), plus `astro_state_key` (cacheable) and debug fields
  (`maitri`, `gana`, `baseline_score`, `rashi_relation`, `moon_sign_distance`, `moon_nakshatra`,
  `moon_sign`, `tara_a`/`tara_b` + qualities, `day_state`). Framing: warm, jargon-free,
  gentle guidance, never fate (blueprint §2).
- **New module `shared/astro/relationship_weather.py`:** `daily_relationship_weather(
  profile_a, profile_b, on_date)` + the `_RASHI_FLAVOUR` (7) and `_DAY` (6) static tables.
  Reuses `forecast.py`'s Moon-longitude helpers (+ unknown-time fallback) and only the
  **Graha Maitri + Gana** kootas from `scoring.py` (NOT the full 36-guna marriage total).
  Pure math + lookup — no AI, no new dependencies, no streamlit.

### Recent changes (2026-05-26) — forecast accuracy + tone fix
- **Corrected the Chandra Gochara meaning table** in `shared/astro/forecast.py`. The
  build had mislabelled the **5th house from the natal Moon as "Playful / good"** — that's
  the *natal* 5th-house meaning, NOT the Moon's *transit* result. Per the classical rule
  (Phaladeepika / Brihat Jataka, cross-checked across multiple sources), the Moon's transit
  is **favourable in 1, 3, 6, 7, 10, 11** and **challenging in 2, 4, 5, 8, 9, 12** from the
  natal Moon. Rewrote all 12 entries so `base` scores + framing match (favourable
  ≈0.60–0.84, challenging ≈0.32–0.46; 11th strongest, 8th hardest), each keeping its domain
  flavour. Still a pure static lookup — no AI, no cost.
- **Softer, jargon-free `why` text.** Removed the code-dumpy `"Tara Bala is Janma (Birth)
  (neutral)"`; the depth line now reads in plain warm English. Sanskrit stays only in the
  `sanskrit` field. Beginner-first per blueprint §2.

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
  `sun_rise_set` (sunrise/sunset via the free ephemeris adapter, ≤21s vs SE), plus the classical weekday segment
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
  chart API runs with only the free ephemeris engine (skyfield + jplephem + pyerfa +
  `de440s.bsp`) installed — no Swiss Ephemeris, no AI/PDF libs required. Powers the
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
  vault/                        (Saved profiles CRUD + import/export — client-side storage)
  me/                           (Authenticated user data on Supabase: profiles/checkins/journal/streaks + JWT auth)

shared/                         ← Backend plumbing shared by every feature.
  astro/                        free Skyfield ephemeris (adapter) + dasha + scoring + chart compute
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
  db/                           Supabase data layer (Streamlit-free)
    secrets.py                  Supabase creds — env first, then .streamlit/secrets.toml
    supabase_client.py          service + user(RLS) clients, JWT verify, CRUD (profiles/checkins/journal/streaks)
    cache.py                    cached_daily + cached_chart helpers (cost rule)
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
- Storage: browser localStorage in Streamlit. **The persisted, authenticated equivalent for
  the mobile app is `features/me` (`/me/profiles`, Supabase + RLS).**

### 3b. me — `features/me/` (Supabase-backed, the data-layer foundation)
- JWT-gated per-user CRUD: profiles, check-ins (Pattern Engine input), journal (the Mirror),
  streaks. `POST /me/checkins` upserts the day's check-in **and** bumps the check-in streak.
- Auth: `Authorization: Bearer <Supabase JWT>` → `auth.get_current_user` verifies + yields a
  user-scoped client; **Postgres RLS enforces owner-only**.
- Data layer: `shared/db/` (service + user clients, CRUD, cache helpers). No AI.
- See `features/me/README.md`. Out of scope (later): correlation logic, social, payments.

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
  - Pass 1: Cheap visual scan to extract strict structured Phase A JSON observations of lines, mounts, marks, and `capture_guidance`. Gemini vision runs this pass in JSON-response mode where supported so malformed scans are less likely. Visual calibration is enhanced by passing two Supabase-hosted diagrams alongside the hand images: `book_image_18.jpg` as `REFERENCE 1` (mounts/gunas) and `reference_grid_3.jpg` as `REFERENCE 2` (a 25-box template grid detailing line defects like islands, breaks, and chains) to serve as a physical calibration stencil.
  - VLM Visual Self-Correction: Integrates a 100% automated visual scan check at the end of Pass 1. The VLM evaluates finger proportions (`"index_vs_ring_length"`) and palm color tone (`"vitality_visual_class"`), dynamically overriding noisy MediaPipe physical landmark ratios and HSV skin color heuristics.
  - State & UI Synchronization: Write VLM-corrected hand metrics (e.g. ring finger taller, setting ruling planet to Sun) and vitality (e.g. Subdued) back into Streamlit's session state (`st.session_state.palm_analysis`) before the final rerun. This forces the UI signals list and ruling planet card to update instantly to match the visual scan and Phase B reading text.
  - Pass 2: Local & free context gathering (Vedic planets, nakshatras, skin dosha mapping from HSV vitality) + targeted Qdrant semantic search of the actual lines/marks confirmed by Phase A. Blind pre-scan retrieval is not used.
  - Pass 3: Detailed Phase B markdown reading grounded in pre-confirmed visual findings. Phase B is now text-only by design: it receives the Phase A JSON, Vedic context, and targeted passages, but not the palm images again. This lowers image-token cost and prevents the final prose call from re-interpreting the photo differently from the verified scan. Invalid Phase A JSON, a poor Phase A photo judgment, or `general_reading_ready = False` skips Phase B to avoid a fluent but weakly grounded second AI call.
- Accuracy Evidence Rules: after Phase A, Python builds a deterministic `accuracy_guardrails` bundle inside `phase_a` with `strong_claims_allowed`, `cautious_claims_only`, `forbidden_claims`, and `section_rules`. Phase B receives this as `<accuracy_claim_rules>` and must obey it. This adds zero AI calls and prevents faint, absent, blocked, or capture-missing observations from becoming confident prose.
- Hidden Streamlit Palm Accuracy Lab: when `PALMISTRY_EVAL_MODE=1` is set, the palmistry page shows a private tester panel after a reading. It summarizes Phase A, accepts plain-English corrections, and downloads an accuracy packet JSON to pair with the original photo. This is for the temporary 5-photo manual evaluation loop only; normal users never see it and FastAPI remains unchanged.
- Planet Dominance Refinement: Middle finger (Saturn) is physically always the longest finger in human hands. Excluded Saturn from dominant finger relative height comparisons, letting active personality/character traits (Jupiter/index, Sun/ring, Mercury/little) correctly dictate the ruling planet.
- Mount dominance guardrail: neutral/moderate mounts no longer select the dominant planet or drive Qdrant retrieval as "prominent". A mount must be clearly prominent and meaningfully ahead of the others before it steers the planet context.
- Conservative front-photo limits: backend evidence gates now force marriage/relationship lines to `not_assessable` unless a `mercury_edge` capture is supplied, and force thumb flexibility to `not_assessable` unless a `thumb_flex` capture is supplied. This protects accuracy even if the model tries to overread a normal front-palm photo. Mount fullness remains conservative because one flat image cannot prove 3D elevation from lighting alone.
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
  - `/vault/*`        (4)  CRUD + default (client-side storage)
  - `/oracle/*`       (6)  deep-analysis, matchmaking, marriage, gochara, compare, prashna
  - `/me/*`           (7)  profiles (GET/POST/PUT/DELETE), checkins (GET/POST), journal
                            (GET/POST), streaks (GET) — **Supabase-backed, JWT-gated, RLS**
  - Plus `/docs` (Swagger) + `/redoc` (ReDoc) auto-generated by FastAPI.

## Why this layout is better for a vibe coder

- **Want to change tarot?** Open `features/tarot/`. Everything tarot is in there.
- **Want to add a new feature?** Copy any `features/<feat>/` folder and rename it. Six files.
- **Want to wire FastAPI?** Each feature already has `api.py`. Mount them in one file.
- **Want a mobile app?** Each feature already has `schemas.py` with Pydantic models. Generate Swift/Kotlin clients from there.
- **Want to find why X is broken?** The trail is always `view.py → service.py → prompts.py`. No spelunking through 4 engines.
