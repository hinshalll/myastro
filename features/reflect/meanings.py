"""features.reflect.meanings — static, classically-sourced interpretation tables
for the big-picture reflective readings (Your Purpose + Year in Review).

These are FINITE, well-established significations (Jaimini Atmakaraka natures;
the standard 12-house life-areas; the 12 sign styles), written warm and plain.
Sanskrit/technical terms live only in the `sanskrit` fields and the `why` strings
the service builds. Nothing here is improvised — each entry is the universally
taught meaning. Gentle guidance, never fate (blueprint §2).
"""
from __future__ import annotations

# ── Atmakaraka (the soul-planet, Jaimini): the soul's strongest desire + the
#    karma it's here to resolve. Standard AK significations.
ATMAKARAKA: dict[str, dict] = {
    "Sun":     {"theme": "to stand in your own authority and be truly seen — your deeper work is around selfhood, integrity and earning real recognition",
                "verb": "lead and be seen with integrity", "sanskrit": "सूर्य आत्मकारक"},
    "Moon":    {"theme": "to feel deeply and stay connected — your deeper work is around the heart, caring for others, and finding emotional security",
                "verb": "nurture and stay open-hearted", "sanskrit": "चन्द्र आत्मकारक"},
    "Mars":    {"theme": "to act with courage and protect what matters — your deeper work is around strength, drive, and channelling anger into purpose",
                "verb": "act with courage", "sanskrit": "मंगल आत्मकारक"},
    "Mercury": {"theme": "to learn, connect and communicate — your deeper work is around the mind, clear discrimination, and finding your true voice",
                "verb": "learn and communicate", "sanskrit": "बुध आत्मकारक"},
    "Jupiter": {"theme": "to seek wisdom, guide others and grow — your deeper work is around meaning, faith, teaching and generosity",
                "verb": "seek wisdom and guide", "sanskrit": "गुरु आत्मकारक"},
    "Venus":   {"theme": "to love, relate and create beauty — your deeper work is around relationship, what you truly value, and balancing desire",
                "verb": "love and create beauty", "sanskrit": "शुक्र आत्मकारक"},
    "Saturn":  {"theme": "to serve, endure and master things through time — your deeper work is around discipline, responsibility, and meeting fear with patience",
                "verb": "serve and master through patience", "sanskrit": "शनि आत्मकारक"},
    "Rahu":    {"theme": "to break new ground and master worldly desire — your deeper work is around bold ambition and the unconventional, without losing yourself in the chase",
                "verb": "break new ground", "sanskrit": "राहु आत्मकारक"},
    "Ketu":    {"theme": "to let go and turn inward — your deeper work is around detachment, the spiritual, and completing old karma",
                "verb": "let go and go inward", "sanskrit": "केतु आत्मकारक"},
}

# ── The 12 houses as plain life-areas (the bhava significations everyone agrees
#    on). Used for "the soul planet sits in your Nth house", the 10th-lord's
#    placement, the dharma trikona, and the year's Muntha house.
HOUSE_THEME: dict[int, str] = {
    1:  "your own self, identity and the path you walk",
    2:  "family, resources and your voice",
    3:  "courage, skill and your own effort",
    4:  "home, roots and inner peace",
    5:  "creativity, love and self-expression",
    6:  "service, daily work and overcoming obstacles",
    7:  "partnership and close one-to-one bonds",
    8:  "depth, change and the hidden side of life",
    9:  "meaning, belief, fortune and higher learning",
    10: "career, standing and your action in the world",
    11: "community, networks and the rewards of effort",
    12: "solitude, release, spirituality and faraway places",
}

# Short phrase for "through X" / "in the area of X".
HOUSE_THROUGH: dict[int, str] = {
    1:  "your own self and the path you walk",
    2:  "what you build, hold and speak",
    3:  "your own effort, courage and skill",
    4:  "home, family and inner peace",
    5:  "creativity, love and self-expression",
    6:  "service, problem-solving and daily work",
    7:  "partnership and one-to-one relationships",
    8:  "deep change and the things beneath the surface",
    9:  "meaning, teaching, travel and belief",
    10: "your public work and visible standing",
    11: "community, networks and big aspirations",
    12: "quiet, retreat, the spiritual and the faraway",
}

# ── The 12 signs as a short style/flavour (their classical temperaments).
SIGN_STYLE: dict[str, str] = {
    "Aries":       "boldly and head-on",
    "Taurus":      "steadily and patiently",
    "Gemini":      "curiously and with lots of words and ideas",
    "Cancer":      "caringly, led by feeling",
    "Leo":         "warmly and from the heart, wanting to shine",
    "Virgo":       "carefully and with an eye for detail",
    "Libra":       "fairly and through relationship",
    "Scorpio":     "intensely and all the way down",
    "Sagittarius": "expansively, always seeking the bigger picture",
    "Capricorn":   "with discipline and the long game in mind",
    "Aquarius":    "originally and a little against the grain",
    "Pisces":      "compassionately and imaginatively",
}

# ── Muntha (Varshaphala): the year's moving "spotlight" point. Its house from the
#    natal Lagna colours the year's main theme — read as the same bhava life-areas.
MUNTHA_LINE: dict[int, str] = {
    1:  "this year turned the spotlight onto you — your health, your direction, a fresh start in how you show up",
    2:  "this year leaned into money, family and what you were building and saying",
    3:  "this year asked for your own effort and courage — skills, short trips, siblings, putting yourself out there",
    4:  "this year drew you home — to roots, family, property and your own peace of mind",
    5:  "this year lit up creativity, romance, children and self-expression",
    6:  "this year was a working year — service, health, sorting problems and out-discipling obstacles",
    7:  "this year centred on partnership — relationships, other people, give-and-take",
    8:  "this year went deep — change, the unexpected, shared resources, and what lay beneath the surface",
    9:  "this year opened up meaning, fortune, travel, teachers and belief",
    10: "this year put career and your standing in the world front and centre",
    11: "this year was about gains, friendships, networks and big hopes coming closer",
    12: "this year asked for release and rest — letting go, the spiritual, foreign places, closing a chapter",
}
