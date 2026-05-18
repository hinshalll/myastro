# Tarot

Mystic Tarot reading feature. Four modes + a permanent Birth Card.

## What's in this folder

| File | What it holds |
|---|---|
| `constants.py` | The 22-card Major Arcana deck, Celtic Cross position names, asset base URL |
| `service.py`   | Pure-Python: card-drawing (cryptographic RNG), birth-card calculation. No Streamlit, no Gemini. |
| `prompts.py`   | The 5 prompt builders sent to Gemini (Three-Card, Yes/No, Celtic Cross, Birth Card, Daily Card) |
| `schemas.py`   | Pydantic models for the FastAPI request/response shapes |
| `view.py`      | The Streamlit page — the UI the user sees on the web app |
| `api.py`       | The FastAPI router — the endpoints the mobile app + website call |

## Modes

- **Three-Card Spread** — 3 random cards. Sub-modes: General Guidance / Love & Dynamics / Decision-Two Paths.
- **Yes / No Oracle** — 1 random card → clear verdict.
- **Celtic Cross** — 10 cards in fixed positions.
- **Birth Card** — deterministic from DOB (digit-sum → 1 of 22 Major Arcana). Never changes.

All modes accept "Include Reversed Cards" — when on, each card has a 50/50 chance of being upside-down.

## Knowledge / RAG

Single book: `tguide.md` (in Qdrant). Per-mode k:
- Three-Card: k=8
- Yes/No: k=6
- Celtic Cross: k=10
- Birth Card: k=6
- Daily Card (used by Dashboard): k=6

## AI cost

Gemini Flash Lite, free-tier friendly. ~₹0.05 per reading.

## Editing tips

- New tarot mode → add the prompt builder to `prompts.py`, the draw function to `service.py`, the tab to `view.py`, the route to `api.py`.
- Change deck → edit `FULL_TAROT_DECK` in `constants.py`.
- Card-image URL change → edit `TAROT_BASE` in `constants.py`.
