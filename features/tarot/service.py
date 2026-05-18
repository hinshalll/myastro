"""features.tarot.service — pure-Python tarot logic.

No Streamlit, no FastAPI, no Gemini. Just card draws and the birth-card
formula. Both view.py and api.py call into this.
"""

import secrets

from features.tarot.constants import FULL_TAROT_DECK


# ── Card drawing ─────────────────────────────────────────────────────────────

def _maybe_reverse(rng: secrets.SystemRandom, include_reversed: bool) -> str:
    return rng.choice(["Upright", "Reversed"]) if include_reversed else "Upright"


def draw_three(include_reversed: bool = False) -> tuple[list[str], list[str]]:
    """Three unique cards. Returns (cards, states)."""
    rng = secrets.SystemRandom()
    cards = rng.sample(FULL_TAROT_DECK, 3)
    states = [_maybe_reverse(rng, include_reversed) for _ in range(3)]
    return cards, states


def draw_one(include_reversed: bool = False) -> tuple[str, str]:
    """One card. Returns (card, state)."""
    rng = secrets.SystemRandom()
    return rng.choice(FULL_TAROT_DECK), _maybe_reverse(rng, include_reversed)


def draw_celtic_cross(include_reversed: bool = False) -> tuple[list[str], list[str]]:
    """Ten unique cards. Returns (cards, states)."""
    rng = secrets.SystemRandom()
    cards = rng.sample(FULL_TAROT_DECK, 10)
    states = [_maybe_reverse(rng, include_reversed) for _ in range(10)]
    return cards, states


# ── Birth card (deterministic) ───────────────────────────────────────────────

def get_birth_card(dob_iso: str) -> str:
    """
    Tarot Birth Card — soul archetype determined by the digit sum of DOB.

    Sum every digit in DOB. If >22, recursively sum until ≤22.
    Map total → Major Arcana index. 0 or 22 → The Fool.

    Pure function. Same DOB always returns the same card.
    """
    digits = [int(c) for c in dob_iso.replace("-", "") if c.isdigit()]
    total = sum(digits)
    while total > 22:
        total = sum(int(d) for d in str(total))
    if total == 22 or total == 0:
        return FULL_TAROT_DECK[0]
    return FULL_TAROT_DECK[total - 1]
