# Numerology

Two systems, two tabs.

## Tabs

**Full Report**
- System toggle: Western (Pythagorean) or Indian/Vedic (Chaldean)
- Mode toggle: Full Report or Ask-a-Question
- "🌌 Cross-validate with Vedic Kundli" checkbox — if on, also feeds the AI a kundli dossier so it reports numerology-vs-astrology agreement points
- Computes Life Path, Destiny, Soul Urge, Personality (★ for master numbers 11/22/33)

**Personal Cycles & Pinnacles**
- Same system toggle
- Personal Year (current), Personal Month, Personal Day
- 4 Pinnacle cycles by age range with their challenge numbers — marks the active one with "◀ YOU ARE HERE"

## What's in this folder

| File | What it holds |
|---|---|
| `prompts.py` | `build_full_report_prompt`, `build_cycles_prompt` |
| `schemas.py` | Pydantic models |
| `view.py`    | Streamlit page (both tabs) |
| `api.py`     | FastAPI router |

## Knowledge / RAG

- Western: `wnum.md`
- Vedic:   `inum1.md`
k=10 for the full report; k=8 for cycles.

## AI cost

1 Gemini Flash Lite call per report. Add 0.10 ₹ if cross-validate with kundli is on (extra dossier in the prompt is essentially free).

## Editing tips

- Pinnacle challenge meanings → `_CHALLENGE_MEANINGS` in `view.py`.
- New master number → update master-number tags in both prompts.py and view.py.
