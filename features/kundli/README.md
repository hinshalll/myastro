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
| `api.py`        | FastAPI router (compute + free + premium) |

## Engines used (shared)

- `math_engine.kundli` — `BirthData`, `compute_chart`, `yoga_audit`, `sade_sati_timeline` (will be renamed to `shared/astro/kundli` in Phase 3)
- `pdf_engine` — `build_kundli_pdf`, `THEMES`, `render_chart_svg` (will be renamed to `shared/pdf/`)

## AI cost

- Free tier: 1 Gemini Flash Lite call, ~₹0.10 per generation. 8 topics covered.
- Premium tier: 2 calls. Call 1 = general life topics. Call 2 = per-element batch (12 houses + 9 planets + 3 years). ~₹0.40–0.55 per kundli, plus ~₹5 for the premium narrative call. Total under user's ₹5 budget cap.

Free-tier rate-limit toggle lives at top of `content.py`: `RESPECT_FREE_TIER_LIMITS = True`. Flip to False after paid-API switch.

## Editing tips

- Add a new free-tier topic → append to `FREE_TOPICS` in `content.py`, add render block in `view.py`.
- Add a premium theme → add a dict entry to `THEMES` in `pdf_engine/kundli_pdf.py` (becomes `shared/pdf` later).
- Change premium narrative sections → edit `_SYSTEM_RULES` schema in `narrative.py`.
