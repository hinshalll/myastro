"""features.tarot.constants — tarot-only constants.

Moved here from shared.astro/constants.py so the feature is self-contained.
"""

# 22 Major Arcana, deterministic order — used by deterministic birth-card calc.
FULL_TAROT_DECK = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "The Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil",
    "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
]

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
TAROT_BASE = "https://raw.githubusercontent.com/hinshalll/text2kprompt/main/tarot/"


def card_image_filename(card_name: str) -> str:
    """e.g. 'The Fool' -> 'thefool.jpg'."""
    return card_name.lower().replace(" ", "") + ".jpg"
