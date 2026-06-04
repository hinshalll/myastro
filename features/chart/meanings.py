"""features.chart.meanings — the warm, plain-English voice layer for the chart.

The "front room": every meaning here is written like a thoughtful friend who
happens to know astrology — second person, concrete, no jargon, never AI-sounding.
The classical SUBSTANCE behind each line is the standard, verified signification
(cross-checked against BPHS / Phaladeepika / Saravali / Brihat Jataka, and — for
the atoms reused from the engine — shared.astro.kundli_text's HOUSE_MEANINGS /
SIGN_QUALITIES / PLANET_KARAKAS). The machinery (Sanskrit, house numbers, planet
names) stays OUT of the primary text and lives only in `sanskrit` / `why`.

Design (same as kundli_text.py, to avoid a 200-combo hand-write while staying
accurate): warm ATOMS for the finite sets (12 signs, 12 houses, 9 planets),
COMPOSED into sentences by service.py. Gentle guidance, never fate (blueprint §2).
"""
from __future__ import annotations

# ── The 12 signs as a warm core temperament. Faithful to SIGN_QUALITIES.nature,
#    written as a plain phrase that can follow "you're …" / "you come across as …".
SIGN_ESSENCE: dict[str, str] = {
    "Aries":       "bold, direct, and quick to act — you'd rather start than sit and wait",
    "Taurus":      "steady, patient, and grounded — you like things solid, comfortable, and built to last",
    "Gemini":      "curious, quick, and talkative — your mind is always moving and reaching for the next thing",
    "Cancer":      "caring and deeply feeling — you lead with your heart and look after your own",
    "Leo":         "warm, proud, and generous — you're meant to be seen, and you shine when you are",
    "Virgo":       "precise, helpful, and sharp-eyed — you notice the details everyone else misses",
    "Libra":       "fair, charming, and people-minded — you're at your best in balance and good company",
    "Scorpio":     "intense, private, and all-or-nothing — you feel everything deeply, even when you don't show it",
    "Sagittarius": "open, restless, and meaning-seeking — you need room to roam and a bigger picture to believe in",
    "Capricorn":   "disciplined, ambitious, and patient — you play the long game and earn what you get",
    "Aquarius":    "original, independent, and a little against the grain — you think for yourself",
    "Pisces":      "gentle, imaginative, and compassionate — you feel the world more than you ever let on",
}

# Sanskrit (Devanagari) sign names — for the `sanskrit` field only.
SIGN_SANSKRIT: dict[str, str] = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुम्भ", "Pisces": "मीन",
}

# ── The 12 houses as a warm "part of life". Faithful to HOUSE_MEANINGS, written
#    as a plain noun phrase that can follow "around …" / "shows up in …".
HOUSE_LIFE: dict[int, str] = {
    1:  "yourself — your body, your energy, and how you meet the world",
    2:  "family, money, and the things and people you hold close",
    3:  "your own effort, your voice, and your everyday courage",
    4:  "home, family, and your private inner world",
    5:  "creativity, romance, play, and children",
    6:  "your daily work, your health, and the problems you quietly solve",
    7:  "your closest partnerships and the people you commit to",
    8:  "deep bonds, shared things, and what stays beneath the surface",
    9:  "travel, learning, faith, and the search for meaning",
    10: "your work, your reputation, and your place in the world",
    11: "friends, community, and the things you're hoping for",
    12: "rest, solitude, faraway places, and your inner and spiritual life",
}

# Classical house names — for the `sanskrit` / `why` strings only.
HOUSE_SANSKRIT: dict[int, str] = {
    1: "लग्न (तनु भाव)", 2: "धन भाव", 3: "सहज भाव", 4: "सुख भाव",
    5: "पुत्र भाव", 6: "अरि भाव", 7: "कलत्र भाव", 8: "आयु भाव",
    9: "भाग्य भाव", 10: "कर्म भाव", 11: "लाभ भाव", 12: "व्यय भाव",
}

# ── The 9 planets as a warm "part of you" — the life-area each one speaks for.
#    Faithful to PLANET_KARAKAS. Used to frame planet-in-sign / planet-in-house.
PLANET_DOMAIN: dict[str, dict] = {
    "Sun":     {"of": "your core self — your confidence, your pride, and your sense of purpose",
                "lead": "At your core", "sanskrit": "सूर्य"},
    "Moon":    {"of": "your inner emotional world — what you need to feel safe and settled",
                "lead": "Your inner world", "sanskrit": "चन्द्र"},
    "Mars":    {"of": "your drive — how you go after what you want, and how you handle a fight",
                "lead": "Your drive", "sanskrit": "मंगल"},
    "Mercury": {"of": "how your mind works — the way you think, learn, and talk",
                "lead": "How you think", "sanskrit": "बुध"},
    "Jupiter": {"of": "what you believe in — how you grow, find meaning, and stay hopeful",
                "lead": "What you believe", "sanskrit": "गुरु"},
    "Venus":   {"of": "how you love — what you find beautiful, and what you most enjoy",
                "lead": "How you love", "sanskrit": "शुक्र"},
    "Saturn":  {"of": "where you work hardest — your discipline, your patience, and your fears",
                "lead": "Where you grow", "sanskrit": "शनि"},
    "Rahu":    {"of": "what you hunger for — the place you're restless and never quite satisfied",
                "lead": "What you chase", "sanskrit": "राहु"},
    "Ketu":    {"of": "what you're quietly letting go of — where you've already been, lifetimes over",
                "lead": "What you release", "sanskrit": "केतु"},
}

# How a sign's essence gets framed for a few specific, hero-card domains, so the
# composed line reads naturally instead of mechanically.
DOMAIN_FRAME: dict[str, str] = {
    "identity": "You come across as {essence}.",
    "emotion":  "Inside, you're {essence}.",
    "love":     "In love, you're {essence}.",
    "mind":     "The way you think is {essence}.",
    "drive":    "When you go after something, you're {essence}.",
}
