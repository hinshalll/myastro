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

## AI

- `fetch_data` — 1 Gemini Flash Lite call returning JSON tiles (~₹0.02). Cached 24h.
- `fetch_daily_tarot` — 1 Gemini Flash Lite call returning {MEANING, ACTION, MANTRA}. Cached 24h.
- Astro-Decide — 1 Gemini call per click. Verdict is Python-determined by Tara Bala; AI only explains.

## Editing tips

- Add a new tile → add a key to `build_data_prompt`'s JSON schema + render block in `view.py`.
- Change Tara Bala themes → edit the `themes` dict in `view.py`.
- Change the 45d / 14d shift alert thresholds → edit `view.py` (dasha_alert section).
