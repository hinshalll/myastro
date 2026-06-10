"""features.wallet.prices — single source of truth for the Diya economy.

SERVER-AUTHORITATIVE. Feature prices, earn rules, caps, bundles, and Plus perks
live here and ONLY here. The client never sends a price; it asks to do feature
X, and the server looks up X here, applies the Plus discount, and debits. This
is what stops a client from spoofing a cheaper price.

Locked 2026-06-08 (see MOBILE_APP_BLUEPRINT.md §7). Tune with real usage data.
"""
from __future__ import annotations

from math import ceil

# Plus members pay 25% less on Diya features (and some are free for them).
PLUS_DISCOUNT = 0.25

# Base Diya price of every paid feature (before the Plus discount).
PRICES: dict[str, int] = {
    # Permanent artifacts (kept forever / saved to vault)
    "full_life_reading":   60,   # the 4-agent flagship + PDF
    "premium_kundli_pdf":  60,   # self OR each other person
    "marriage_report":     40,
    "purpose_report":      40,
    "varshaphal":          40,
    "matching_full_report":30,   # quick guna score is free
    "palmistry_deep":      25,   # 1 free taste, then this
    "face_reading_deep":   25,   # 1 free taste, then this
    "couple_forecast_7day":25,   # one-off for non-Plus (Plus gets couple space)
    # Small one-offs
    "prashna":             15,
    "numerology_deep":     15,   # basic numerology is free
    "muhurta_deep":        10,   # basic "best dates" is free
    "proof_extra":         10,   # 1 free/month, then this
    "cross_reference_addon":10,  # free for Plus
    "extra_saved_person":  10,
    "ai_chat_message":      3,   # after the 1 free/day
    "tarot_extra":          5,   # after the 1 free/week
}

# Features that are simply FREE for Plus members (not just discounted).
PLUS_FREE: set[str] = {"cross_reference_addon"}

# Free-tier allowances (informational for the UI; enforced via usage counters).
FREE_ALLOWANCE: dict[str, str] = {
    "ai_chat_message": "1/day",
    "tarot": "1/week",
    "palmistry": "1 taste",
    "face_reading": "1 taste",
    "proof": "1/month",
    "saved_people": "3",
    # the whole daily loop + every shareable (incl. Wrapped) is fully free
}

# Earn rules (Diyas in).
EARN: dict[str, int] = {
    "welcome": 25,
    "checkin": 1,
    "ritual": 2,
    "meditation": 2,
    "streak_7": 10,
    "streak_21": 25,
    "streak_50": 60,
    "referral": 25,
    "referral_plus_bonus": 50,   # extra if the referee subscribes to Plus
}
# Max Diyas/day from routine activity (keeps earning stingy so people still buy).
DAILY_EARN_CAP = 5
# One-offs / milestones exempt from the daily cap.
EARN_CAP_EXEMPT: set[str] = {
    "welcome", "streak_7", "streak_21", "streak_50", "referral", "referral_plus_bonus",
}

# Diya purchase bundles (INR base; the store prices tier-1 geos 3-4x).
BUNDLES = [
    {"id": "glow",     "inr": 99,  "diyas": 110},
    {"id": "blaze",    "inr": 299, "diyas": 380},
    {"id": "festival", "inr": 799, "diyas": 1150},
]

# The Plus membership (one membership, not a second currency).
SUBSCRIPTION = {
    "name": "Plus",
    "plans_inr": {"weekly": 49, "monthly": 199, "yearly": 999},
    "trial_days": 7,
    "perks": [
        "Unlimited AI chat (fair use)",
        "Couple space, family grid, and deep Patterns",
        "Cross-reference with your kundli, free",
        "25% off every Diya feature",
    ],
}


def price_for(feature: str, is_plus: bool = False) -> int:
    """Server-authoritative Diya cost of a feature, after the Plus discount.

    Raises KeyError for an unknown feature (never silently free)."""
    if feature not in PRICES:
        raise KeyError(f"unknown feature: {feature}")
    if is_plus and feature in PLUS_FREE:
        return 0
    base = PRICES[feature]
    return int(ceil(base * (1.0 - PLUS_DISCOUNT))) if is_plus else base


def earn_for(source: str) -> int:
    return EARN.get(source, 0)
