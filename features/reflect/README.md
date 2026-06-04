# features/reflect — the big-picture reflective readings

Two warm, **pure-math** (no live AI) readings that step back from the daily loop
to the whole life and the whole year. Chart math goes through `shared/astro/`
(`compute_chart`, `compute_varshaphala`); the slow-transit reads reuse
`shared/astro/retrospect.py`; the meanings are a finite, classically-sourced
static table (`meanings.py`). Both are **stateless** and **deterministic** (same
profile → same reading), so the app can cache them.

## Endpoints

| Method & path | What it does |
|---|---|
| `POST /reflect/purpose` | **Your Purpose** — a soul/career blueprint. |
| `POST /reflect/year` | **Year in Review** ("Cosmic Wrapped") — a shareable yearly recap. |

Both need a profile in the `/kundli/compute` shape **with `lat`/`lon`** (for the
Lagna, houses and D10). An unknown birth time falls back to a midday estimate and
attaches a `precision_note` (the house-based parts can shift). Missing lat/lon →
**422**.

### `POST /reflect/purpose` — Your Purpose
Built from four classical layers:
* **Atmakaraka** (the Jaimini soul-planet) → the soul's strongest desire + the
  karma it's here to resolve, and the house it works through.
* **10th house + its lord** → your karma/career in the world, and where its lord
  sits (where your work-energy flows).
* **D10 Dashamsha** (the career divisional chart) → the flavour you lead with at work.
* **Dharma trikona** (1/5/9) → where your sense of meaning lives.

```jsonc
{ "ok":true,
  "soul":{ "planet":"Moon","theme":"to feel deeply and stay connected …","sign":"Sagittarius","house":7,"house_theme":"…","sanskrit":"चन्द्र आत्मकारक" },
  "calling":{ "tenth_sign":"Pisces","tenth_lord":"Jupiter","lord_in_house":1,"line":"Your work in the world tends to be carried compassionately …" },
  "career_chart":{ "d10_lagna":"Libra","line":"In the deeper picture of career …" },
  "dharma":{ "line":"Your sense of meaning gathers around …","occupants":{…} },
  "headline":"You're here to nurture and stay open-hearted, and to express it through …",
  "summary":"…", "why":"…", "sanskrit":"…", "precision_note":null }
```

### `POST /reflect/year` — Year in Review (Cosmic Wrapped)
Built from the **Varshaphala** (Tajik annual chart — the **Muntha** spotlight +
solar return), the **Vimshottari dasha chapter** that ran across the year (with
any sub-period shift noted), and the year's **slow transits** (Jupiter's gift,
Saturn's lesson, nodes over the Moon). Includes a punchy `share_text` for the
"Wrapped" card.

```jsonc
{ "ok":true, "year":2025,
  "chapter":{ "mahadasha":"Rahu","antardasha":"Venus","line":"You spent 2025 inside your Rahu chapter, in its Venus sub-stretch." },
  "muntha":{ "sign":"Taurus","house":12,"line":"this year asked for release and rest …" },
  "gifts":[{ "what":"Jupiter in a supportive angle to your birth Moon","meaning":"…" }],
  "lessons":[{ "what":"Saturn sitting in the fourth from your birth Moon","meaning":"…" }],
  "headline":"Your 2025: a Rahu year with a Venus undercurrent.",
  "share_text":"My 2025 was a Rahu chapter with a little grace from Jupiter — …",
  "summary":"…", "why":"…", "sanskrit":"वर्षफल · मुन्था · महादशा", "precision_note":null }
```

## Sourcing & voice (blueprint §2)
Standard significations only — Jaimini Atmakaraka natures, the 12-house bhava
life-areas, the 12 sign temperaments, Varshaphala/Muntha. Nothing improvised.
Warm/plain primary text; Sanskrit only in the `sanskrit` fields and `why`; framed
as a **compass, not a cage** — gentle guidance, never fate.
