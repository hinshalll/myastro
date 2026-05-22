"""features.tarot.constants — tarot-only constants.

Moved here from shared.astro/constants.py so the feature is self-contained.
"""

# 22 Major Arcana, deterministic order.
# IMPORTANT: keep this list and its order STABLE — the deterministic birth-card
# calc maps a digit-sum onto these indices, and the Dashboard daily card draws
# from it. Adding Minor Arcana here would silently change both. The interactive
# spread draws use FULL_78_DECK (below) instead.
FULL_TAROT_DECK = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "The Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil",
    "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
]

# 56 Minor Arcana — 4 suits x (Ace, 2-10, Page, Knight, Queen, King).
# Ranks are spelled out so the image-filename helper produces the names that
# already exist in the Supabase bucket (e.g. "Two of Cups" -> "twoofcups.jpg").
_MINOR_RANKS = [
    "Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
    "Page", "Knight", "Queen", "King",
]
_MINOR_SUITS = ["Wands", "Cups", "Swords", "Pentacles"]

MINOR_ARCANA = [f"{rank} of {suit}" for suit in _MINOR_SUITS for rank in _MINOR_RANKS]

# The full 78-card reading deck — Major Arcana followed by the four Minor suits.
# This powers the interactive spread draws (Three-Card / Yes-No / Celtic Cross).
# Birth Card and the Dashboard daily card deliberately stay on FULL_TAROT_DECK.
FULL_78_DECK = FULL_TAROT_DECK + MINOR_ARCANA

CELTIC_CROSS_POSITIONS = [
    "1. The Present — Core issue or central energy",
    "2. The Challenge — What crosses or complicates",
    "3. The Foundation — Unconscious influences, deep roots",
    "4. The Past — What is passing or recently passed",
    "5. The Crown — Potential outcome or conscious goal",
    "6. The Near Future — What approaches in coming weeks",
    "7. The Self — Your attitude, how you show up",
    "8. External Influences — Others or environment",
    "9. Hopes & Fears — Inner tension",
    "10. The Outcome — Most likely resolution",
]

# Asset base — front images, video loops, card back.
TAROT_BASE = "https://hmspryhmyhegraqccnsh.supabase.co/storage/v1/object/public/palmistry-images/tarot/"


def card_image_filename(card_name: str) -> str:
    """e.g. 'The Fool' -> 'thefool.jpg'."""
    return card_name.lower().replace(" ", "") + ".jpg"


def card_image_url(card_name: str) -> str:
    """Full public URL of a card's front image. Handy for the mobile client."""
    return TAROT_BASE + card_image_filename(card_name)


def card_back_url() -> str:
    """Full public URL of the face-down card back."""
    return TAROT_BASE + "tarotrear.png"
