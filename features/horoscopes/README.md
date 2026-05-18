# Horoscopes

Two daily-forecast modes:

| Tab | Input | What it does |
|---|---|---|
| **Western** | DOB | Sun-sign daily forecast based on today's tropical transits |
| **Vedic**   | Profile (date+time+place) | Moon-sign daily/monthly/yearly forecast based on gochara from natal Moon |

## What's in this folder

| File | What it holds |
|---|---|
| `service.py` | `generate_western_forecast(sun_sign, today_str)` and `generate_vedic_forecast(prof_json, timeframe, today_str)` |
| `prompts.py` | The two Gemini prompts used by the forecasts |
| `schemas.py` | Pydantic models |
| `view.py`    | Streamlit page |
| `api.py`     | FastAPI router |

## Knowledge / RAG

- Western: none — uses Gemini's tropical-astrology knowledge.
- Vedic: `bphs2.md` (gochara/transit chapter), k=10.

## AI cost

- Western: 1 Gemini Flash Lite call.
- Vedic: 1 call per timeframe (Daily/Monthly/Yearly). 3 calls if user opens all three.

Cached 24h per profile + date.

## Editing tips

- Vedic timeframe rules → edit `_TIMEFRAME_RULES` in `prompts.py`.
- Add a new Western or Vedic format → edit the FORMAT block in the prompt builder.
