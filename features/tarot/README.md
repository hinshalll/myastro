# Tarot

Mystic Tarot reading feature. Four modes + a permanent Birth Card.

## What's in this folder

| File | What it holds |
|---|---|
| `constants.py` | The 22-card Major Arcana, the 56 Minor Arcana, the full 78-card deck, Celtic Cross position names, asset URLs |
| `service.py`   | Pure-Python: the interactive draw-session/reveal flow (signed tokens), legacy card-drawing (cryptographic RNG), birth-card calculation. No Streamlit, no Gemini. |
| `prompts.py`   | The 5 prompt builders sent to Gemini (Three-Card, Yes/No, Celtic Cross, Birth Card, Daily Card) |
| `schemas.py`   | Pydantic models for the FastAPI request/response shapes |
| `view.py`      | The Streamlit page — the UI the user sees on the web app |
| `api.py`       | The FastAPI router — the endpoints the mobile app + website call |

## Modes

- **Three-Card Spread** — pick 3 cards. Sub-modes: General Guidance / Love & Dynamics / Decision-Two Paths.
- **Yes / No Oracle** — pick 1 card → clear verdict.
- **Celtic Cross** — pick 10 cards in fixed positions.
- **Birth Card** — deterministic from DOB (digit-sum → 1 of 22 Major Arcana). Never changes.

All picker modes accept "Include Reversed Cards" — when on, each card has a 50/50 chance of being upside-down (fixed at shuffle time).

## Decks

- `FULL_TAROT_DECK` (22 Major Arcana) — used by **Birth Card** (digit-sum math) and the Dashboard daily card. Order must stay stable.
- `FULL_78_DECK` (22 Major + 56 Minor) — used by the three interactive spreads.

## How the interactive picker works (the user picks their own cards)

A two-step, **stateless** flow so it works identically on the web and the future React Native app. The backend is the single source of truth:

1. **`create_draw_session(spread, include_reversed)`** — shuffles a hidden 78-card deck, fixes each position's Upright/Reversed state, and returns an opaque **signed token** plus `pick_count`, `deck_size` (78) and the card-back URL. The card identities are *not* sent to the client.
2. The frontend shows the face-down deck, the user taps `pick_count` positions.
3. **`reveal_session(token, picks)`** — re-opens the token, maps the tapped positions (in tap order = spread order) to the real cards + states, and returns them. The AI then interprets only those revealed cards.

The token is HMAC-SHA256 signed with `TAROT_DRAW_SECRET` (env var → `.streamlit/secrets.toml`; a random per-process key if unset) and expires after 30 minutes. Reveal rejects wrong pick counts, duplicate picks, out-of-range positions, spread mismatches, and tampered/expired tokens — all raised as `TarotDrawError`.

API: `POST /tarot/draw-session` then `POST /tarot/reveal`. The older `/three-card`, `/yes-no`, `/celtic-cross` auto-draw routes are kept as compatibility wrappers.

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
- Change the **birth-card** deck → edit `FULL_TAROT_DECK` (keep its order stable). Change the **spread** deck → edit `MINOR_ARCANA` / `FULL_78_DECK`.
- New picker spread → add it to `SPREADS` in `service.py` and to the `SpreadKey` literal in `schemas.py`.
- Card-image URL change → edit `TAROT_BASE` in `constants.py`.
