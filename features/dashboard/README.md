# Dashboard — "Cosmic Compass"

Daily landing page. All widgets are toggleable from the ⚙️ popover.

## Widgets

| Toggle | What it shows |
|---|---|
| `greeting`    | Personalized 2-sentence transit insight (AI) |
| `consult`     | Quick-link card to the Consultation Room |
| `forecast`    | 4-tile grid: Energy / Focus / Caution / Best Time |
| `decide`      | Astro-Decide widget: ask a yes/no, Tara Bala verdict + AI explainer |
| `calendar`    | 7-day Tara Bala "cosmic week" cards |
| `tarot`       | Daily Tarot card (deterministic from name+date) + interpretation |
| `dasha_alert` | Major dasha shift warning if next AD ≤ 45 days or PD ≤ 14 days |

## What's in this folder

| File | What it holds |
|---|---|
| `prompts.py` | `build_data_prompt` (greeting + tiles) + `build_decide_prompt` |
| `service.py` | `fetch_data` and `fetch_daily_tarot` (AI orchestration) |
| `schemas.py` | Pydantic models |
| `view.py`    | Streamlit page (toggle-driven render) |
| `api.py`     | FastAPI router |

## `/dashboard/timing` — Good / Avoid times strip (no AI)

`POST /dashboard/timing` powers the mobile "Today → Good / Avoid times" strip. It is
**date- and location-based** (weekday + sunrise/sunset), NOT birth-chart based, so it
needs no profile.

- **Input:** `{ "date": "YYYY-MM-DD", "lat": <float>, "lon": <float>, "tz": "<IANA tz>" }`
- **Output (display-ready):**
  - `avoid` — Rahu Kaal, Yamaganda, Gulika Kaal — each `{name, start, end}` (24h `HH:MM`).
  - `good` — Abhijit Muhurta — `{name, start, end}`.
  - `choghadiya` — the 8 daytime + 8 nighttime segments tiling sunrise→next sunrise,
    each `{name, start, end, quality, period}` where `quality ∈ good|neutral|avoid`
    (Amrit/Shubh/Labh = good, Char = neutral, Udveg/Kaal/Rog = avoid).
  - `summary` — one-line plain-English hint (e.g. "Strong window 11:50 am–12:45 pm…").
  - plus `weekday`, `sunrise`, `sunset`.

Pure math, no AI, no new dependencies. All logic lives in `shared/astro/astro_calc.py`
(`daily_timing_windows`, `sun_rise_set` via Swiss Ephemeris + classical weekday segment
rules). Day windows split sunrise→sunset into 8 equal parts; the kaal periods pick the
weekday's segment; Choghadiya walks the 7-fold wheel from the weekday's starting period.

## AI

- `fetch_data` — 1 Gemini Flash Lite call returning JSON tiles (~₹0.02). Cached 24h.
- `fetch_daily_tarot` — 1 Gemini Flash Lite call returning {MEANING, ACTION, MANTRA}. Cached 24h.
- Astro-Decide — 1 Gemini call per click. Verdict is Python-determined by Tara Bala; AI only explains.

## Editing tips

- Add a new tile → add a key to `build_data_prompt`'s JSON schema + render block in `view.py`.
- Change Tara Bala themes → edit the `themes` dict in `view.py`.
- Change the 45d / 14d shift alert thresholds → edit `view.py` (dasha_alert section).
