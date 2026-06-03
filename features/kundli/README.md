# Kundli

The flagship feature — full Vedic birth chart with two tabs.

## Tabs

**Free Kundli (in-app scrollable)**
- D1 Lagna chart SVG
- Panchanga + Functional Profile + Avakahada Chakra
- Planetary Positions
- Vimshottari Dasha (MD/AD tables)
- Sade Sati Timeline
- Shadbala + SAV-by-house + Bhava Bala
- Lucky Factors, Remedies
- Manglik Analysis, Kaal Sarp Analysis
- Optional 8-topic AI Personalised Readings (~₹0.10 per generation)
- PDF download (no theming, no AI narrative)

**Premium PDF**
- Theme picker (7 themes from `pdf_engine.kundli_pdf.THEMES`)
- Language: en / hi / ta / te / mr / bn / gu
- Optional Western Appendix
- Optional AI Narrative (~₹5 per kundli — karmic story + 8 decade predictions + per-yoga paragraphs + transit synthesis)

## What's in this folder

| File | What it holds |
|---|---|
| `content.py`    | Free + Premium personalised topic prose (was `ai_engine/kundli_content.py`) |
| `narrative.py`  | Premium-PDF batched narrative call (was `ai_engine/kundli_narrative.py`) |
| `schemas.py`    | Pydantic models |
| `view.py`       | Streamlit page (904 lines — both tabs) |
| `api.py`        | FastAPI router (compute + dasha-timeline + free + premium) |

## Birth-time precision (3 tiers)

`BirthData.time_precision` (in `shared/astro/kundli.py`) reports how much of the chart to
trust, from the `birth_time_known` + `exact_time` flags:

- **`exact`** (Exact Time Known checkbox) — everything reliable, incl. divisional charts.
- **`approximate`** — time given but unconfirmed; Ascendant/houses usually OK, but
  divisionals (D9/D60) are NOT reliable (`divisionals_reliable` is False).
- **`unknown`** — no birth time; chart is computed with a **noon placeholder** so it never
  crashes, but Ascendant/houses/divisionals are flagged unreliable (`houses_reliable` False).
  Only Moon-based output (Moon sign, dasha, transits) should be shown.

Helper flags: `houses_reliable` (needs any time), `divisionals_reliable` (needs *exact*
time). Adding/confirming a time later → recompute once.

### `/kundli/compute` response (compact, display-ready)

`POST /kundli/compute` returns a small JSON summary the mobile app renders directly
(no client-side chart parsing):

- `moon`, `sun` — `{name, sign, house, nakshatra, nakshatra_lord, degree, retrograde}`
  (`house` is `null` when houses aren't reliable).
- `ascendant_sign`, `ascendant_nakshatra` — `null` unless `houses_reliable`.
- `planets` — the same planet shape for Sun→Ketu (9 bodies).
- `time_precision` + `houses_reliable` + `divisionals_reliable` — so the app hides/locks
  the right sections. Moon-based fields are always populated (work at any tier).

### `/kundli/dasha-timeline` response (powers the mobile "Life Chapters" screen)

`POST /kundli/dasha-timeline` takes the **same `{ "profile": {...} }` contract as
`/compute`** and returns a compact Vimshottari Mahadasha timeline. Dasha is Moon-based,
so it works at **every** birth-time tier (the engine uses a noon placeholder when the time
is unknown — it never fails).

- `mahadashas` — array of the full birth→~120 yr sequence, each
  `{planet, start_date, end_date, start_age, end_age, is_balance, is_current}`
  (ISO dates, ages in years to 1 dp; `is_balance` marks the partial opening period;
  `is_current` marks the period running now).
- `current_md`, `current_ad` — the Mahadasha / Antardasha lords running today.
- `birth_nakshatra`, `start_lord` — Moon's nakshatra and the dasha-starting lord.
- `time_precision` + `dates_exact` — `dates_exact` is True only for an **exact** birth
  time. The *sequence and order* are always correct; the exact transition **dates** firm
  up only with an exact time (an unknown/approximate time shifts them slightly).

Reuses `build_lifetime_dasha_sequence` + `build_vimshottari_timeline` from
`shared/astro/astro_calc.py` (no AI, no PDF — pure math).

## Engines used (shared)

- `math_engine.kundli` — `BirthData`, `compute_chart`, `yoga_audit`, `sade_sati_timeline` (will be renamed to `shared/astro/kundli` in Phase 3)
- `pdf_engine` — `build_kundli_pdf`, `THEMES`, `render_chart_svg` (will be renamed to `shared/pdf/`)

**Lazy heavy imports:** `service.py` imports the PDF builder (jinja2/weasyprint) and the
AI content/narrative helpers **lazily** via module `__getattr__`. Computing a chart only
needs the free ephemeris engine (skyfield + jplephem + pyerfa + the `de440s.bsp` kernel) —
**no Swiss Ephemeris** — so `/kundli/compute` (and any lean deploy serving just the chart)
runs without PDF or AI libraries installed. The chart honours `profile.ayanamsha` (any of
`lahiri`/`raman`/`krishnamurti`/`yukteshwar`/`fagan_bradley`, default lahiri). Likewise
`fastapi_main._init_backend()` guards the Gemini/DeepSeek init in try/except — a missing AI
lib no longer crashes the math-only API.

## AI cost

- Free tier: 1 Gemini Flash Lite call, ~₹0.10 per generation. 8 topics covered.
- Premium tier: 2 calls. Call 1 = general life topics. Call 2 = per-element batch (12 houses + 9 planets + 3 years). ~₹0.40–0.55 per kundli, plus ~₹5 for the premium narrative call. Total under user's ₹5 budget cap.

Free-tier rate-limit toggle lives at top of `content.py`: `RESPECT_FREE_TIER_LIMITS = True`. Flip to False after paid-API switch.

The personalised-prose model defaults to the `json` task in `shared/ai/config.py` (provider auto-detected from the name). The premium narrative call uses the default model ladder.

## Editing tips

- Add a new free-tier topic → append to `FREE_TOPICS` in `content.py`, add render block in `view.py`.
- Add a premium theme → add a dict entry to `THEMES` in `pdf_engine/kundli_pdf.py` (becomes `shared/pdf` later).
- Change premium narrative sections → edit `_SYSTEM_RULES` schema in `narrative.py`.
