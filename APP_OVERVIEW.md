# ASTRO SUITE beta — Complete App Structure & Architecture

> Comprehensive reference document. Send this to any AI and it has enough context to make accurate changes to any feature of this app.

---

## 1. PRODUCT OVERVIEW

**ASTRO SUITE beta** is a Streamlit-based Vedic-astrology + AI divination web app, designed for eventual port to a **mobile app**. It is monetised through a premium kundli (birth-chart) report; free features are gateway/discovery; paid features wrap an AI layer over real Swiss-Ephemeris math.

### Features (top-level nav)
1. **Dashboard** — entry hub
2. **Consultation Room** — chat with an AI astrologer (Gemini), feeding it a built "dossier" of the user's chart
3. **The Oracle** — AI-driven life-question Q&A with chart context
4. **Mystic Tarot** — tarot draws + AI interpretation
5. **Horoscopes** — daily / monthly / yearly
6. **Numerology** — numerology profile
7. **Palm Reading** — upload palm photo → Gemini Vision analysis
8. **Kundli** — TWO tabs:
   - **Free Kundli** (in-app scrollable view, AI behind a button)
   - **Premium PDF** (themed 60-115pp PDF with AI prose)
9. **Saved Profiles** — multi-profile management (localStorage on web, will be a DB on mobile)

### Strategic constraints (CRITICAL)
- **Backend purity**: `math_engine`, `ai_engine`, `pdf_engine` must have **zero Streamlit dependency**. These will become a backend API for the mobile app.
- **Cost caps**: Free kundli ≤ ₹1 / kundli. Premium kundli ≤ ₹5 / kundli.
- **No hallucination**: AI prose must reference ONLY chart facts provided in the prompt. Strict accuracy contract enforced in system rules.

---

## 2. DIRECTORY LAYOUT

```
AIS/
├── .streamlit/secrets.toml          # GEMINI_API_KEY lives here
├── ephe/                            # Swiss Ephemeris .se1 files (precomputed)
├── requirements.txt                 # Python deps (weasyprint, swisseph, jinja2, etc.)
├── packages.txt                     # Linux system deps (libpango, libcairo for WeasyPrint)
│
├── math_engine/                     # ── PURE COMPUTE LAYER (no Streamlit) ──
│   ├── constants.py                 # PLANETS, OUTER_PLANETS, SIGNS, NAKSHATRAS,
│   │                                #   DASHA_YEARS, DASHA_ORDER, YEAR_DAYS=365.25,
│   │                                #   SIGN_LORDS_MAP, NAV_PAGES, etc.
│   ├── astro_calc.py                # Low-level Swiss Ephemeris wrappers:
│   │                                #   local_to_julian_day, get_lagna_and_cusps,
│   │                                #   get_placidus_cusps, get_panchanga,
│   │                                #   nakshatra_info, calculate_ashtakavarga,
│   │                                #   calculate_shadbala, detect_yogas, etc.
│   ├── scoring.py                   # Numerology / compatibility math
│   ├── dossier_builder.py           # Builds the chart "dossier" for AI consult
│   ├── palm_vision.py               # Palm-reading numeric scoring
│   │
│   ├── kundli/                      # ── CONSOLIDATED KUNDLI ENGINE ──
│   │   └── __init__.py              # ~1700 lines, merged from 17 sub-modules.
│   │                                # Sub-files (chart.py, divisional.py, doshas.py,
│   │                                # dashas.py, etc.) are now back-compat stubs
│   │                                # that re-export from __init__.
│   │                                # PUBLIC API:
│   │                                #   BirthData, KundliChart, compute_chart
│   │                                #   yoga_audit, sade_sati_timeline
│   │                                #   render_chart_svg, compute_varshaphala
│   │                                #   rectify, suggest_names
│   │
│   └── kundli_text.py               # Per-house / per-planet interpretation library
│                                    # + Lal Kitab text + life-domain rules + naming
│                                    # bank. Static, deterministic, no AI.
│
├── ai_engine/                       # ── AI LAYER (Gemini) ──
│   ├── gemini_client.py             # Centralised Gemini init + model fallback chain
│   │                                #   LIGHT_MODELS: gemini-3.1-flash-lite-preview, gemini-2.5-flash
│   │                                #   HEAVY_MODELS: gemma-4-31b-it, gemma-4-26b-a4b-it
│   ├── knowledge.py                 # Vedic knowledge files for AI prompts
│   ├── prompts.py                   # System prompts per feature
│   ├── forecasts.py                 # Horoscope generation
│   ├── kundli_narrative.py          # Original karmic-story / decade-predictions (1 call)
│   ├── kundli_content.py            # ★ NEW: multi-call personalised kundli prose
│   ├── palm_vision_ai.py            # Gemini Vision for palm images
│   ├── palm_knowledge_lookup.py     # Palmistry knowledge retrieval
│   └── palmistry_qdrant.py          # Qdrant vector search for palmistry
│
├── pdf_engine/                      # ── PDF GENERATION (WeasyPrint) ──
│   ├── kundli_pdf.py                # ★ CONSOLIDATED main file. Contains:
│   │                                #   - THEMES dict (6 themes — see §5)
│   │                                #   - North/South/East Indian chart SVG renderers
│   │                                #   - render() dispatcher
│   │                                #   - render_chart_for_chart() universal API
│   │                                #   - build_kundli_pdf() main entry point
│   ├── theme_art.py                 # ★ Per-theme SVG glyphs + page borders +
│   │                                # ornament dividers + watermark logic
│   ├── generate_theme_assets.py     # Pollinations.ai-based image generator (CLI script)
│   ├── builder.py                   # Back-compat re-export of kundli_pdf
│   ├── charts/                      # Back-compat re-exports of chart renderers
│   │
│   ├── static/themes/<theme>/       # AI-generated deity images per theme
│   │   ├── cover.png                # Hero image on cover page
│   │   └── watermark.png            # (optional, not currently used in pages)
│   │
│   └── templates/                   # Jinja2 templates
│       ├── base.html                # Master template — CSS, @page, fonts
│       └── sections/                # One template per kundli section
│           ├── cover.html                  # Page 1 — hero
│           ├── birth_details.html          # Page 2 — identity, panchanga
│           ├── nakshatra_profile.html      # Avakahada Chakra
│           ├── planetary_positions.html    # Planet table + conjunctions
│           ├── panchanga.html              # Five-limb panchanga
│           ├── rasi_chart.html             # D1 hero chart + houses table
│           ├── divisional_charts.html      # 16-varga grid
│           ├── dasha_vimshottari.html      # MD/AD/PD timeline
│           ├── yogas.html                  # Yoga library + audit
│           ├── doshas.html                 # 11-dosha detection
│           ├── shadbala.html               # 6-fold strength + Bhava Bala
│           ├── ashtakavarga.html           # BAV + SAV + Shodhya Pinda
│           ├── sudarshan.html              # Triple-view chart
│           ├── per_house_analysis.html     # 12 PAGES — one per house +
│           │                               #   AI personalised reading per house
│           ├── per_planet_analysis.html    # 9 PAGES — one per planet +
│           │                               #   AI personalised reading per planet
│           ├── life_domains.html           # 8 PAGES — Career/Wealth/Health/etc.
│           ├── life_predictions.html       # AI life-prediction prose pages
│           ├── year_predictions.html       # Current + next 2 years AI prose
│           ├── lal_kitab.html              # 12 houses Lal Kitab text
│           ├── auspicious_dates.html       # 12-month favourable-days calendar
│           ├── varshaphala.html            # Tajik annual chart
│           ├── transit_forecast.html       # 12-month forecast
│           ├── jaimini.html                # Pada Lagnas + Karakamsa
│           ├── kp_extras.html              # KP cuspal table + significators
│           ├── remedies.html               # Mantras/ratnas/yantras/daan
│           ├── child_naming.html           # Name suggestions by nakshatra pada
│           ├── karmic_story.html           # AI-generated D60/Rahu-Ketu narrative
│           ├── decade_predictions.html     # AI-generated decade outlooks
│           └── western_appendix.html       # Tropical positions + Ptolemaic aspects
│
└── ui_streamlit/                    # ── STREAMLIT UI LAYER (web only) ──
    ├── app.py                       # Entry point. Routes nav_page → show_*()
    ├── state.py                     # Session state + LocalStorage sync
    ├── components.py                # Sidebar, bottom nav, profile form, theme CSS
    ├── cache.py                     # @st.cache_data wrappers
    ├── helpers.py                   # Shared UI helpers
    │
    └── views/                       # One file per feature page
        ├── dashboard.py
        ├── consultation.py
        ├── oracle.py
        ├── tarot.py
        ├── horoscopes.py
        ├── numerology.py
        ├── palmistry.py
        ├── kundli.py                # ★ Has Free + Premium tabs
        ├── vault.py                 # Saved Profiles
        ├── astro_pdf.py             # Old astro-PDF generator (pre-kundli)
        └── palm_pdf.py              # Palm PDF generator
```

---

## 3. DATA FLOW — KUNDLI

```
User profile (name, DOB, time, place, lat, lon, tz)
    │
    ▼
BirthData (dataclass in math_engine.kundli)
    │
    ▼
compute_chart(birth_data)   ← single entry point, pure compute
    │
    ▼  produces a KundliChart with everything:
    │     - planets:           Sun..Saturn + Rahu/Ketu + Uranus/Neptune/Pluto
    │     - houses:            12 houses with sign, lord, occupants, cusps
    │     - lagna:             ascendant + nakshatra + sub-lord chain
    │     - panchanga:         tithi, paksha, yoga, karana, weekday
    │     - divisional_charts: 16 vargas (D1, D2, ..., D60)
    │     - dashas:            Vimshottari, Yogini, Ashtottari timelines
    │     - yogas:             list of detected classical yogas
    │     - doshas:            11-dosha detection (Mangal, Kaal Sarp, etc.)
    │     - shadbala:          six-fold strength + Vimshopaka
    │     - bhava_bala:        per-house strength
    │     - ashtakavarga:      BAV + SAV + Shodhita + Shodhya Pinda
    │     - nakshatra_profile: 23-row Avakahada Chakra + attributes
    │     - sudarshan_chakra:  triple-view (Lagna/Moon/Sun)
    │     - transit_forecast:  12-month sign-change calendar
    │     - jaimini:           A1-A12 padas + Upapada + Karakamsa
    │     - kp_extras:         cuspal table + significators
    │     - remedies:          per-planet mantras/ratnas/etc.
    │     - chara_karakas:     Atmakaraka..Darakaraka
    │     - interpretations:   static personalised paragraphs (kundli_text.py)
    │
    ▼
┌───────────────────────────┬─────────────────────────────────────┐
│  FREE KUNDLI               │  PREMIUM KUNDLI (PDF)               │
│  ui_streamlit/views/       │  pdf_engine/                        │
│    kundli.py               │    kundli_pdf.py                    │
│  (in-app scrollable view)  │    build_kundli_pdf(chart, ...)    │
│                            │                                     │
│  Optional AI section       │  Optional AI section                │
│  behind a BUTTON           │  via include_ai_narrative=True      │
│  (8 topics, ~₹0.10)        │  → ai_engine.kundli_content         │
└───────────────────────────┴─────────────────────────────────────┘
                                          │
                                          ▼
                            Jinja2 renders sections/*.html
                                          │
                                          ▼
                            WeasyPrint → PDF bytes
                                          │
                                          ▼
                            User downloads .pdf
```

---

## 4. AI CONTENT ARCHITECTURE — `ai_engine/kundli_content.py`

### Multi-call focused architecture (anti-hallucination)
```
Free tier    → 1 call  (~90s)
              FREE_TOPICS = [personality, career, health, wealth, marriage,
                            education, family, spirituality]   # 8 topics

Premium tier → 2 calls (~4-6 min)
              Call 1: GENERAL_PREMIUM (17 topics: above 8 + children, love_life,
                      manglik_analysis, sade_sati_narrative, kaal_sarp_narrative,
                      major_dasha, next_dasha, lucky_factors, remedies_narrative)
              Call 2: PER-ELEMENT BATCH (24 topics):
                       12 houses (house_1 .. house_12)
                       +  9 planets (planet_Sun .. planet_Ketu)
                       +  3 years (year_<current>, year_<+1>, year_<+2>)
              → 41 personalised paragraphs total
```

### Toggles at top of `kundli_content.py`
```python
RESPECT_FREE_TIER_LIMITS = True   # waits 4s between calls — Gemini free-tier safe
FREE_TIER_DELAY_SECONDS  = 4      # flip to False on paid API
```

### Strict accuracy contract (in `_SYSTEM_RULES`)
- Use ONLY chart facts in the JSON
- For `house_N`: read only `facts.houses[N]`
- For `planet_X`: read only `facts.planets[X]`
- For `year_YYYY`: read only `facts.year_dashas[YYYY]`
- If a dosha/yoga is absent, explain favourable absence — don't force negative tone
- Output strict JSON `{"topic_key": "paragraph", ...}`

### Cost (gemini-3.1-flash-lite-preview)
- Free   ≈ ₹0.10/kundli  (~3K output tokens)
- Premium ≈ ₹0.40-0.55/kundli (~12K output tokens across 2 calls)
- Both comfortably under the user-stated caps.

---

## 5. THEMING SYSTEM

### 6 themes (in `pdf_engine/kundli_pdf.py:THEMES`)
| Theme | Mood | Primary | Accent | Deity glyph |
|---|---|---|---|---|
| `classic_vedic` | Warm parchment | Sienna | Cardinal red | Om symbol |
| `ganesha` | Warm terracotta | Terracotta | Coral | Stylised Ganesha head |
| `krishna` | Deep midnight blue | Ocean blue | Antique gold | Peacock feather |
| `shiva` | Indigo-silver, ascetic | Deep indigo | Silver-lilac | Trishul + crescent |
| `durga` | Crimson + saffron, regal | Deep crimson | Saffron-orange | Trishul on lotus |
| `lakshmi` | Rose-gold + blush | Rose-gold | Blush pink | Open lotus |

### Theme system structure
1. **Color palette** — `primary`, `accent`, `secondary`, `ink`, `paper`, `paper_alt`, `muted`, `soft_bg`, `card_border`. Each theme defines all of these.
2. **Per-theme deity glyphs** — `theme_art.py:_GLYPH_FN` maps theme ornament name → SVG-drawing function. Used in:
   - Section header icons (small circle on every H2)
   - Ornament dividers (between subsections)
   - Border corners (4 corner dots on every page)
3. **AI-generated cover & watermark images** — `pdf_engine/static/themes/<theme>/cover.png`. Generated via `generate_theme_assets.py` using Pollinations.ai (FREE — no API key required) with Gemini/Imagen fallbacks. Run once: `python -m pdf_engine.generate_theme_assets [--theme NAME] [--force]`.
4. **Page borders** — drawn via `position:fixed` divs with NEGATIVE offsets that push the border OUTSIDE @page content area into the margin strip. 1.2pt theme-primary outer line + 0.4pt theme-muted inner line + 4 corner accent dots. Repeats on every page via WeasyPrint position:fixed.
5. **Background watermark** — currently disabled (was unreliable on every page; user accepted skipping it).

---

## 6. CHART RENDERING — `pdf_engine/kundli_pdf.py`

### Three Indian-chart styles
- `render_north(...)` — Diamond layout, 12 polygonal cells
- `render_south(...)` — 4×4 grid, fixed-sign positions, planets move
- `render_east(...)`  — Bengali-style — like South but with inscribed-diamond corners

### Key features (all 3 renderers)
- **Adaptive font sizing** — `_fit_planet_labels()` calculates exact-fit font + optionally drops degree suffix to avoid cell overflow
- **Per-cell usable areas** — `NI_CELL_USABLE` defines max-width × max-height per house
- **House numbers** (`H1`...`H12`) — bigger, bolder, positioned in outer corners
- **Sign abbreviations** (`Ar`,`Ta`,...,`Pi`) — italicised, at outer cell edge
- **Planet labels** — `Mo 16°R`, `Su 2°`, etc. with retrograde/combust markers
- **Outer planets supported** — Uranus, Neptune, Pluto with `Ur`,`Ne`,`Pl` abbreviations
- **Minimal mode** (`minimal=True`) — hides sign abbrs + house numbers for the tiny varga thumbnails

### Universal chart-rendering API
```python
from math_engine.kundli import render_chart_svg
svg = render_chart_svg(chart, varga=1, style='north_indian',
                       size=400, theme_name='lakshmi')
```
Use this anywhere in the app (free view, mobile app, transit overlay, compatibility feature) to display the user's accurate chart.

---

## 7. PUBLIC API SURFACE (for mobile-app backend)

### From `math_engine.kundli`:
```python
BirthData(name, date, time, place, lat, lon, tz, gender='M', exact_time=False)
BirthData.from_profile(profile_dict)
compute_chart(birth_data) → KundliChart
compute_varshaphala(chart, year=None) → dict
rectify(chart, events, window_minutes=60) → dict
yoga_audit(chart) → list[dict]
sade_sati_timeline(chart, years_back=30, years_forward=30) → list[dict]
suggest_names(syllable, gender='M', count=10) → list[(name, meaning)]
render_chart_svg(chart, varga=1, style='north_indian', ...) → str  (SVG)
```

### From `pdf_engine`:
```python
build_kundli_pdf(chart, *, theme_name='classic_vedic',
                 chart_style='north_indian', language='en',
                 sections=None, include_western_appendix=True,
                 include_ai_narrative=True) → bytes
                 # Returns PDF bytes; HTML bytes if WeasyPrint unavailable
                 # Detect: data[:4] == b'%PDF'
THEMES → dict[str, dict]  # all 6 theme palettes
render(style, **kwargs) → str  # chart-style dispatcher
```

### From `ai_engine.kundli_content`:
```python
generate_kundli_content(chart, *, tier='free'|'premium',
                        language='en') → dict[topic_key, prose]
is_available() → bool  # checks GEMINI_API_KEY
```

### Output dict shape (premium tier):
```python
{
    "personality": "...",       # general topics
    "career": "...",
    ...
    "manglik_analysis": "...",  # dosha narratives
    "house_1": "...", "house_2": "...", ..., "house_12": "...",
    "planet_Sun": "...", ..., "planet_Ketu": "...",
    "year_2026": "...", "year_2027": "...", "year_2028": "...",
}
```

---

## 8. KEY TECHNICAL DECISIONS

| Decision | Why |
|---|---|
| **Whole-sign houses** for Vedic | Classical default; matches BPHS |
| **Lahiri Ayanamsha** default | Most-used in modern India |
| **YEAR_DAYS = 365.25** in Vimshottari | Julian year — industry standard (AstroSage, JH, Parashara's Light) |
| **D60 using BPHS/JH count-from-sign formula** | Most authoritative; matches Jagannatha Hora |
| **Swiss Ephemeris (pyswisseph)** | Sub-second accuracy; required for D60 |
| **Whole 9-graha set in chart.planets** | Sun..Saturn + Rahu/Ketu (+ 3 outer planets) |
| **`compute_chart` is pure** | No side-effects, no I/O, no Streamlit |
| **WeasyPrint** for PDF | HTML/CSS → print-quality PDF; SVG-native |
| **Inline SVG charts** in PDF | Zero image dependencies; mobile-portable |
| **Position:fixed border** | WeasyPrint repeats on every page; works in margin strip via negative offsets |
| **AI multi-call** (vs one batched call) | Better accuracy per topic class; less context drift |
| **`RESPECT_FREE_TIER_LIMITS` toggle** | Adds 4s wait between AI calls on free tier; flip to False for paid |
| **Pollinations.ai for images** | Free, no API key, FLUX model — user's daily Gemini image quota was capped |
| **One-file consolidation** | `math_engine/kundli/__init__.py` (~1700 lines, 17 modules merged); `pdf_engine/kundli_pdf.py` (charts + builder). Easier mobile-API extraction. |

---

## 9. PREMIUM PDF SECTION ORDER (114 pages for full premium)

Default ordering in `build_kundli_pdf()`:
1. cover
2. birth_details
3. panchanga
4. nakshatra_profile
5. planetary_positions
6. rasi_chart
7. divisional_charts (16-varga grid)
8. dasha_vimshottari
9. yogas
10. doshas
11. karmic_story (AI)
12. decade_predictions (AI)
13. per_house_analysis (12 PAGES — one per house, with AI prose)
14. per_planet_analysis (9 PAGES — one per planet, with AI prose)
15. life_domains (8 PAGES — Career/Wealth/Health/Marriage/Children/Education/Travel/Spirituality)
16. life_predictions (AI: general topics + year predictions)
17. shadbala
18. ashtakavarga
19. remedies
20. lal_kitab (12-house Lal Kitab text)
21. transit_forecast
22. varshaphala
23. year_predictions (5-year outlook)
24. auspicious_dates (12-month calendar)
25. jaimini
26. kp_extras
27. sudarshan
28. child_naming
29. western_appendix (tropical positions + Ptolemaic aspects)

---

## 10. FREE KUNDLI VIEW STRUCTURE — `ui_streamlit/views/kundli.py`

Single Streamlit view with **two tabs**: `📜 Free Kundli (in-app)` and `✨ Premium PDF`.

### Free Kundli (top → bottom):
1. Identity strip (name + DOB + place + Lagna/Moon/Sun)
2. D1 Lagna Chart (large, 460pt size, with all labels)
3. Panchanga at Birth + Functional Profile (2 cols)
4. Avakahada Chakra (23-row classical summary)
5. Planetary Positions table (all planets including outer)
6. 16 Divisional Charts grid (expandable, minimal-label mode)
7. Vimshottari Dasha (current MD+AD highlighted, 9-MD timeline)
8. Yogas — name+category+description inline (matches Doshas format) + audit (present-only)
9. Doshas — name+severity+cause inline + audit (present-only)
10. Sade Sati Timeline (current + full -40y..+25y windows)
11. Bhava Bala house-strength heatmap (12-cell strip)
12. Lucky Factors (Naam-akshar, Gana, Yoni, Nadi, Varna, Vashya, Tatva, Guna + focus planet's day/colour/metal/gemstone)
13. **Manglik Analysis** — dedicated card with prose narrative
14. **Kaal Sarp Analysis** — dedicated card with prose narrative
15. Friendship Table (Naisargika permanent friendships, collapsible)
16. Shadbala — six-fold strength table
17. Sarvashtakavarga heatmap
18. Sudarshan Chakra (triple view, collapsible)
19. Remedies (top priority planets + daily practice + per-planet remedies)
20. ── divider ──
21. **🔮 Personalised AI Readings** — behind a BUTTON. User clicks → 1 AI call generates 8 topics → cached in session. "Regenerate" button to refresh.
22. ── divider ──
23. PDF download button (basic free-tier PDF, no theming/AI)

### Premium PDF tab:
- Theme picker (6 cards)
- Chart style picker (NI/SI/EI)
- Language picker (7 languages)
- Western appendix toggle
- AI narrative toggle (~2 min for full premium)
- "Generate Premium Kundli PDF" button
- On success: download .pdf + inline preview iframe

---

## 11. FILES TO TOUCH FOR COMMON CHANGES

| Need to change... | Edit this file |
|---|---|
| Theme palette (colors) | `pdf_engine/kundli_pdf.py` → `THEMES` dict |
| Deity glyph for a theme | `pdf_engine/theme_art.py` → `_<theme>_glyph()` |
| AI cover image for a theme | `pdf_engine/static/themes/<theme>/cover.png` (or regenerate via `generate_theme_assets.py`) |
| Section page content / layout | `pdf_engine/templates/sections/<section>.html` |
| Global page styling (fonts, margins, border) | `pdf_engine/templates/base.html` |
| Section ordering in premium PDF | `pdf_engine/kundli_pdf.py` → `sections` list inside `build_kundli_pdf()` |
| Free kundli view content | `ui_streamlit/views/kundli.py` → `_render_free_kundli()` |
| AI prompt rules | `ai_engine/kundli_content.py` → `_SYSTEM_RULES` |
| AI topics covered | `ai_engine/kundli_content.py` → `FREE_TOPICS`, `GENERAL_PREMIUM`, etc. |
| AI rate-limit toggle | `ai_engine/kundli_content.py` → `RESPECT_FREE_TIER_LIMITS` (top of file) |
| Chart math (yogas, doshas, dashas) | `math_engine/kundli/__init__.py` (single consolidated file) |
| Chart SVG rendering | `pdf_engine/kundli_pdf.py` → `render_north/south/east` |
| Static per-house/per-planet text | `math_engine/kundli_text.py` |
| Add a new section to the PDF | (1) create `pdf_engine/templates/sections/<name>.html`, (2) add `<name>` to the sections list in `build_kundli_pdf()` |
| Add a new theme | (1) add entry to `THEMES`, (2) add glyph fn in `theme_art.py:_GLYPH_FN`, (3) optionally run `generate_theme_assets.py --theme <name>` for AI cover image |
| Add a new AI topic | (1) add to `FREE_TOPICS` or `GENERAL_PREMIUM`, (2) tell the prompt how to handle it via `focus_hint`, (3) display it in the appropriate template |

---

## 12. SECRETS & EXTERNAL SERVICES

- **`.streamlit/secrets.toml`** — `GEMINI_API_KEY` only. No other secrets.
- **Pollinations.ai** — free AI image generation (no key)
- **Google Gemini** — text generation. Models tried: `gemini-3.1-flash-lite-preview` → `gemini-3.1-flash` → `gemini-2.5-flash`
- **Qdrant** — used only for palmistry knowledge search (separate from kundli)
- **Swiss Ephemeris** — local `.se1` files in `ephe/`

---

## 13. MOBILE-APP MIGRATION PATH

When porting to a mobile app:
1. **Keep**: `math_engine/`, `ai_engine/`, `pdf_engine/` as-is (zero Streamlit dependency)
2. **Wrap** as a REST API (FastAPI / Flask) with endpoints:
   - `POST /api/chart/compute` → JSON of `compute_chart()` output
   - `POST /api/chart/render` → SVG string
   - `POST /api/kundli/premium-pdf` → PDF bytes
   - `POST /api/kundli/ai-content?tier=free|premium` → JSON of prose
3. **Replace** `ui_streamlit/` with native mobile UI consuming the API
4. **Free kundli on mobile** — replace the AI call with a bigger static-personalisation library (already partially in `kundli_text.py`) so free kundlis generate instantly without API cost
5. **Premium kundli on mobile** — user-facing message: "Your premium kundli will be delivered shortly" — backend job, ~5-6 min total for AI + PDF

---

## 14. PERFORMANCE NUMBERS

| Operation | Time | Cost |
|---|---|---|
| `compute_chart()` | ~0.5s | free |
| `render_chart_svg()` | <0.1s | free |
| Free kundli view render | ~1s | free |
| Free kundli AI (1 call, button-triggered) | ~90s | ~₹0.10 |
| Premium PDF (no AI) | ~3-5s | free |
| Premium PDF (with AI, 2 calls) | ~3-4 min | ~₹0.40-0.55 |
| Pollinations image gen (per image) | ~30-60s | free |

---

## 15. CURRENT STATE

- 6 themes, all with AI-generated deity cover images
- 51 unique PDF sections, 114 pages on a full premium build
- All AI prose chart-grounded (strict anti-hallucination contract)
- Multi-call AI with free-tier rate-limit toggle
- Zero Streamlit dependency in backend layers
- Page borders + theme-paper page background visible on every page
- Free kundli has 22 in-app sections + AI optional behind a button

Last major changes (most recent first):
1. Cover redesign — centered vertical layout, key-points grid, no flexbox cluster bug
2. Multi-call AI architecture (2 calls for premium, focused per-class accuracy)
3. AI-generated deity cover art (Pollinations.ai, 6 themes)
4. Position:fixed page borders with theme deity-color corner dots
5. Outer planets (Uranus/Neptune/Pluto) added to chart compute + rendering
6. Adaptive chart text-fitting (no cell overflow)
7. Free Kundli enhancements — Yoga audit, Sade Sati timeline, Manglik/Kaal Sarp prose cards, AI behind a button
