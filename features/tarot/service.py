"""features.tarot.service — pure-Python tarot logic.

No Streamlit, no FastAPI, no Gemini. Just card draws, the interactive
draw-session/reveal flow, and the birth-card formula. Both view.py and api.py
call into this.

Two ways to draw:

  1. Legacy auto-draw (`draw_three` / `draw_one` / `draw_celtic_cross`) — the
     backend instantly picks the cards. Kept for the old API routes.

  2. Interactive picker (`create_draw_session` -> `reveal_session`) — the
     backend shuffles a hidden 78-card deck and hands the frontend an opaque,
     signed, short-lived token. The frontend shows N face-down cards, the user
     taps positions, and `reveal_session` maps those tapped positions back to
     the real cards. This is the React-Native-ready, stateless flow: nothing is
     stored server-side between the two calls — the token *is* the state.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

from features.tarot.constants import (
    FULL_TAROT_DECK, FULL_78_DECK, card_image_url, card_back_url,
)


# ── Spread definitions ─────────────────────────────────────────────────────────
# Internal spread keys -> required number of picks. The frontend asks for one of
# these keys; the token records it so reveal can't be tricked into the wrong
# pick count.
SPREADS = {
    "three": 3,    # Three-Card Spread
    "yes_no": 1,   # Yes / No Oracle
    "celtic": 10,  # Celtic Cross
}

DECK_SIZE = len(FULL_78_DECK)  # 78
_TOKEN_TTL_SECONDS = 30 * 60   # a draw session is valid for 30 minutes


class TarotDrawError(Exception):
    """Raised when a draw session is invalid, expired, tampered, or mis-picked.

    api.py maps this to an HTTP 400; view.py shows it as a friendly error.
    """


# ── Signing secret (env first, secrets.toml fallback, ephemeral last) ──────────

def _load_secret(key: str) -> str | None:
    """env var first (FastAPI / Render / mobile backend), then secrets.toml."""
    v = os.environ.get(key)
    if v:
        return v
    sp = Path(__file__).resolve().parents[2] / ".streamlit" / "secrets.toml"
    if sp.exists():
        try:
            import tomllib
            with open(sp, "rb") as f:
                return tomllib.load(f).get(key)
        except Exception:
            return None
    return None


# Generated once per process so local dev works with no configured secret.
# Tokens signed with an ephemeral key stop validating when the process restarts
# — fine for a 30-minute session. Set TAROT_DRAW_SECRET in production so tokens
# stay valid across multiple server instances / restarts.
_EPHEMERAL_SECRET = secrets.token_hex(32)


def _signing_key() -> bytes:
    return (_load_secret("TAROT_DRAW_SECRET") or _EPHEMERAL_SECRET).encode("utf-8")


# ── Token encode / decode (HMAC-SHA256 signed, URL-safe base64) ────────────────

def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _sign(payload_b64: str) -> str:
    sig = hmac.new(_signing_key(), payload_b64.encode("ascii"), hashlib.sha256).digest()
    return _b64e(sig)


def _encode_token(payload: dict) -> str:
    payload_b64 = _b64e(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return f"{payload_b64}.{_sign(payload_b64)}"


def _decode_token(token: str) -> dict:
    """Validate signature + expiry and return the payload, or raise TarotDrawError."""
    try:
        payload_b64, sig = token.split(".", 1)
    except (ValueError, AttributeError):
        raise TarotDrawError("Malformed draw token.")
    if not hmac.compare_digest(sig, _sign(payload_b64)):
        raise TarotDrawError("Draw token failed verification (tampered or wrong server key).")
    try:
        payload = json.loads(_b64d(payload_b64))
    except Exception:
        raise TarotDrawError("Draw token could not be read.")
    if payload.get("exp", 0) < int(time.time()):
        raise TarotDrawError("This draw has expired — please shuffle again.")
    return payload


# ── Interactive draw session ───────────────────────────────────────────────────

def create_draw_session(spread: str, include_reversed: bool = False) -> dict:
    """Shuffle a hidden 78-card deck and return a signed session token.

    The returned dict is mobile-ready JSON:
      token         opaque signed string — pass it back to reveal_session()
      spread        echoed spread key
      pick_count    how many cards the user must tap
      deck_size     78
      card_back_url image to render for every face-down card
      expires_in    seconds until the token is no longer valid

    Card identities and upright/reversed states are fixed *now* (inside the
    token) but never exposed to the client until reveal.
    """
    if spread not in SPREADS:
        raise TarotDrawError(f"Unknown spread '{spread}'.")
    rng = secrets.SystemRandom()
    order = list(range(DECK_SIZE))
    rng.shuffle(order)  # position -> index into FULL_78_DECK
    # Reversed state fixed per position at shuffle time (1 = Reversed).
    states = [1 if (include_reversed and rng.random() < 0.5) else 0 for _ in range(DECK_SIZE)]
    now = int(time.time())
    payload = {
        "v": 1,
        "sp": spread,
        "pc": SPREADS[spread],
        "ds": DECK_SIZE,
        "o": order,
        "s": states,
        "iat": now,
        "exp": now + _TOKEN_TTL_SECONDS,
    }
    return {
        "token": _encode_token(payload),
        "spread": spread,
        "pick_count": SPREADS[spread],
        "deck_size": DECK_SIZE,
        "card_back_url": card_back_url(),
        "expires_in": _TOKEN_TTL_SECONDS,
    }


def reveal_session(token: str, picks: list[int], spread: str | None = None) -> dict:
    """Resolve the user's tapped positions into real cards.

    picks  — hidden-deck positions the user tapped, IN TAP ORDER. Tap order is
             the spread order (1st tap = position 1 of the spread, etc.).
    spread — optional sanity check; if given, must match the token's spread.

    Returns {spread, cards, states, positions, image_urls}. Raises
    TarotDrawError on any validation failure. Does NOT call the AI — the caller
    builds the prompt from cards/states/positions.
    """
    payload = _decode_token(token)
    tok_spread = payload["sp"]
    if spread is not None and spread != tok_spread:
        raise TarotDrawError("Reveal spread does not match the shuffled deck.")

    pick_count = payload["pc"]
    deck_size = payload["ds"]

    if not isinstance(picks, list) or len(picks) != pick_count:
        raise TarotDrawError(f"This spread needs exactly {pick_count} card(s).")
    if any((not isinstance(p, int)) or p < 0 or p >= deck_size for p in picks):
        raise TarotDrawError("A picked position is outside the deck.")
    if len(set(picks)) != len(picks):
        raise TarotDrawError("The same card position was picked twice.")

    order = payload["o"]
    state_flags = payload["s"]
    cards = [FULL_78_DECK[order[p]] for p in picks]
    states = ["Reversed" if state_flags[p] else "Upright" for p in picks]
    return {
        "spread": tok_spread,
        "cards": cards,
        "states": states,
        "positions": picks,
        "image_urls": [card_image_url(c) for c in cards],
    }


# ── Legacy auto-draw (used by the compatibility API routes) ────────────────────

def _maybe_reverse(rng: secrets.SystemRandom, include_reversed: bool) -> str:
    return rng.choice(["Upright", "Reversed"]) if include_reversed else "Upright"


def draw_three(include_reversed: bool = False) -> tuple[list[str], list[str]]:
    """Three unique cards from the full 78-card deck. Returns (cards, states)."""
    rng = secrets.SystemRandom()
    cards = rng.sample(FULL_78_DECK, 3)
    states = [_maybe_reverse(rng, include_reversed) for _ in range(3)]
    return cards, states


def draw_one(include_reversed: bool = False) -> tuple[str, str]:
    """One card from the full 78-card deck. Returns (card, state)."""
    rng = secrets.SystemRandom()
    return rng.choice(FULL_78_DECK), _maybe_reverse(rng, include_reversed)


def draw_celtic_cross(include_reversed: bool = False) -> tuple[list[str], list[str]]:
    """Ten unique cards from the full 78-card deck. Returns (cards, states)."""
    rng = secrets.SystemRandom()
    cards = rng.sample(FULL_78_DECK, 10)
    states = [_maybe_reverse(rng, include_reversed) for _ in range(10)]
    return cards, states


# ── Birth card (deterministic, Major Arcana only) ──────────────────────────────

def get_birth_card(dob_iso: str) -> str:
    """
    Tarot Birth Card — soul archetype determined by the digit sum of DOB.

    Sum every digit in DOB. If >22, recursively sum until ≤22.
    Map total → Major Arcana index. 0 or 22 → The Fool.

    Pure function. Same DOB always returns the same card. Uses the 22-card
    Major Arcana deck only — Minor Arcana never apply to the birth card.
    """
    digits = [int(c) for c in dob_iso.replace("-", "") if c.isdigit()]
    total = sum(digits)
    while total > 22:
        total = sum(int(d) for d in str(total))
    if total == 22 or total == 0:
        return FULL_TAROT_DECK[0]
    return FULL_TAROT_DECK[total - 1]
