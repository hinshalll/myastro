"""
math_engine/kundli/remedies.py
==============================

Rule-based remedy (upaya) engine.

Maps detected chart conditions (dosha presence, functional malefics, weak
shadbala planets) to a structured remedy set covering five classical paths
plus Lal Kitab:

    1. Mantra        — Beej, Vedic, and Stotra mantras with japa count.
    2. Ratna (gem)   — Primary + substitute, finger, day, metal, carat range.
    3. Yantra        — Per-planet & per-dosha yantras with activation mantra.
    4. Rudraksha     — Mukhi (faceting) recommendations.
    5. Daan          — Specific donation items + day of week.
    Plus:
    6. Lal Kitab     — North-Indian alternate remedy system (accessible
                       household-level remedies; user confirmed in scope).
    7. Vrat          — Fasting day per affliction.
    8. Color/clothing — Auspicious colors for the week.

Output is structured so the PDF templates can present a focused, prioritised
remedy programme rather than overwhelming the reader with everything.
"""

from __future__ import annotations
from math_engine.constants import SIGN_LORDS_MAP


# ─────────────────────────────────────────────────────────────────────────────
# Per-planet remedy library (the spine — every other remedy refers here)
# ─────────────────────────────────────────────────────────────────────────────

PLANET_REMEDIES: dict[str, dict] = {
    "Sun": {
        "beej_mantra": "Om Hrām Hrīm Hraum Saḥ Sūryāya Namaḥ",
        "japa_count": 7000,
        "vedic_mantra": "Ādityāya vidmahe sahasrakirṇāya dhīmahi tanno sūryaḥ pracodayāt",
        "stotra": "Aditya Hridaya Stotra",
        "ratna": {"primary": "Ruby (Manik)", "substitute": "Red Garnet / Red Spinel",
                  "finger": "Ring", "day_to_wear": "Sunday at sunrise",
                  "metal": "Gold or Copper", "carat_range": "3–7 ct"},
        "yantra": "Surya Yantra",
        "rudraksha": "1-mukhi (or 12-mukhi)",
        "daan": ["Wheat", "Jaggery (gur)", "Copper", "Red cloth", "Ruby (if affordable)"],
        "daan_day": "Sunday before sunset",
        "vrat": "Sunday (Ravivar)",
        "colors": ["Red", "Saffron", "Orange"],
        "deity": "Surya / Shri Ram",
        "lal_kitab": ["Offer water to the Sun at sunrise (Arghya). "
                      "Bury a copper coin in the earth near a temple."],
    },
    "Moon": {
        "beej_mantra": "Om Śrām Śrīm Śraum Saḥ Candrāya Namaḥ",
        "japa_count": 11000,
        "vedic_mantra": "Padmadhvajāya vidmahe hema rūpāya dhīmahi tanno candraḥ pracodayāt",
        "stotra": "Chandra Stotra",
        "ratna": {"primary": "Natural Pearl (Moti)", "substitute": "White Moonstone",
                  "finger": "Little finger", "day_to_wear": "Monday after moonrise",
                  "metal": "Silver", "carat_range": "4–7 ct"},
        "yantra": "Chandra Yantra",
        "rudraksha": "2-mukhi",
        "daan": ["Rice", "Milk", "White cloth", "Silver", "Camphor"],
        "daan_day": "Monday evening",
        "vrat": "Monday (Somvar)",
        "colors": ["White", "Cream", "Silver"],
        "deity": "Shiva / Parvati",
        "lal_kitab": ["Drink water from a silver glass. Keep a small silver "
                      "square at home. Respect mother and elderly women."],
    },
    "Mars": {
        "beej_mantra": "Om Krām Krīm Kraum Saḥ Bhaumāya Namaḥ",
        "japa_count": 10000,
        "vedic_mantra": "Aṅgārakāya vidmahe śaktihastāya dhīmahi tanno bhaumaḥ pracodayāt",
        "stotra": "Hanuman Chalisa, Mangal Stotra",
        "ratna": {"primary": "Red Coral (Moonga)", "substitute": "Carnelian",
                  "finger": "Ring", "day_to_wear": "Tuesday at sunrise",
                  "metal": "Gold or Copper", "carat_range": "5–9 ct"},
        "yantra": "Mangal Yantra",
        "rudraksha": "3-mukhi",
        "daan": ["Red lentils (masoor)", "Jaggery", "Red cloth", "Copper", "Sweets"],
        "daan_day": "Tuesday before sunset",
        "vrat": "Tuesday (Mangalvar)",
        "colors": ["Red", "Crimson", "Coral"],
        "deity": "Hanuman / Subramanya / Mangal",
        "lal_kitab": ["Plant a neem tree. Feed sweets to younger siblings. "
                      "Donate red lentils on Tuesdays."],
    },
    "Mercury": {
        "beej_mantra": "Om Brām Brīm Braum Saḥ Budhāya Namaḥ",
        "japa_count": 9000,
        "vedic_mantra": "Sauṁyarūpāya vidmahe vāṇeśvarāya dhīmahi tanno budhaḥ pracodayāt",
        "stotra": "Vishnu Sahasranama, Budh Stotra",
        "ratna": {"primary": "Emerald (Panna)", "substitute": "Green Tourmaline / Peridot",
                  "finger": "Little finger", "day_to_wear": "Wednesday at sunrise",
                  "metal": "Gold", "carat_range": "3–6 ct"},
        "yantra": "Budh Yantra",
        "rudraksha": "4-mukhi",
        "daan": ["Green moong dal", "Green cloth", "Bronze items", "Books / pens"],
        "daan_day": "Wednesday afternoon",
        "vrat": "Wednesday (Budhvar)",
        "colors": ["Green", "Emerald"],
        "deity": "Vishnu / Ganesha",
        "lal_kitab": ["Feed green grass to cows. Keep a green handkerchief. "
                      "Avoid speaking harshly."],
    },
    "Jupiter": {
        "beej_mantra": "Om Grām Grīm Graum Saḥ Guruve Namaḥ",
        "japa_count": 19000,
        "vedic_mantra": "Vṛṣabhadhvajāya vidmahe gṛṇātmajāya dhīmahi tanno guruḥ pracodayāt",
        "stotra": "Guru Stotra, Vishnu Sahasranama",
        "ratna": {"primary": "Yellow Sapphire (Pukhraj)", "substitute": "Yellow Topaz / Citrine",
                  "finger": "Index", "day_to_wear": "Thursday at sunrise",
                  "metal": "Gold", "carat_range": "5–9 ct"},
        "yantra": "Guru Yantra / Sri Yantra",
        "rudraksha": "5-mukhi",
        "daan": ["Yellow lentils (chana dal)", "Turmeric", "Yellow cloth", "Saffron", "Gold (modest)"],
        "daan_day": "Thursday morning",
        "vrat": "Thursday (Guruvar)",
        "colors": ["Yellow", "Gold", "Saffron"],
        "deity": "Brihaspati / Vishnu / Krishna",
        "lal_kitab": ["Apply saffron tilak. Feed gram/chickpeas to horses. "
                      "Respect teachers and elders."],
    },
    "Venus": {
        "beej_mantra": "Om Drām Drīm Draum Saḥ Śukrāya Namaḥ",
        "japa_count": 16000,
        "vedic_mantra": "Aśvadhvajāya vidmahe dhanurhastāya dhīmahi tanno śukraḥ pracodayāt",
        "stotra": "Shukra Stotra, Lakshmi Stotra",
        "ratna": {"primary": "Diamond (Heera)", "substitute": "White Sapphire / White Topaz / Zircon",
                  "finger": "Middle", "day_to_wear": "Friday at sunrise",
                  "metal": "Platinum or White Gold", "carat_range": "0.5–2 ct (diamond)"},
        "yantra": "Shukra Yantra",
        "rudraksha": "6-mukhi",
        "daan": ["White rice", "Curd", "White sugar", "White cloth", "Perfume", "Silver"],
        "daan_day": "Friday evening",
        "vrat": "Friday (Shukravar)",
        "colors": ["White", "Pink", "Pastel shades"],
        "deity": "Lakshmi / Saraswati",
        "lal_kitab": ["Donate clothes on Fridays. Respect women. "
                      "Avoid harsh language with spouse."],
    },
    "Saturn": {
        "beej_mantra": "Om Prām Prīm Praum Saḥ Śanaiścarāya Namaḥ",
        "japa_count": 23000,
        "vedic_mantra": "Kāka dhvajāya vidmahe khaḍga hastāya dhīmahi tanno mandaḥ pracodayāt",
        "stotra": "Shani Stotra, Dasharatha Krit Shani Stotra",
        "ratna": {"primary": "Blue Sapphire (Neelam)", "substitute": "Amethyst / Lapis Lazuli",
                  "finger": "Middle", "day_to_wear": "Saturday at sunset",
                  "metal": "Iron, Silver, or Panchadhatu", "carat_range": "4–7 ct"},
        "yantra": "Shani Yantra",
        "rudraksha": "7-mukhi or 14-mukhi",
        "daan": ["Black sesame (til)", "Mustard oil", "Black gram (urad)", "Iron", "Black cloth"],
        "daan_day": "Saturday evening",
        "vrat": "Saturday (Shanivar)",
        "colors": ["Black", "Dark blue", "Indigo"],
        "deity": "Shani / Hanuman / Bhairava",
        "lal_kitab": ["Feed crows or black dogs. Light a mustard-oil lamp under "
                      "a peepal tree on Saturdays. Serve the poor."],
    },
    "Rahu": {
        "beej_mantra": "Om Bhrām Bhrīm Bhraum Saḥ Rāhave Namaḥ",
        "japa_count": 18000,
        "vedic_mantra": "Naka dhvajāya vidmahe padma hastāya dhīmahi tanno rāhuḥ pracodayāt",
        "stotra": "Rahu Stotra, Durga Saptashati",
        "ratna": {"primary": "Hessonite (Gomed)", "substitute": "Orange Zircon",
                  "finger": "Middle", "day_to_wear": "Saturday at sunset",
                  "metal": "Silver or Panchadhatu", "carat_range": "5–9 ct"},
        "yantra": "Rahu Yantra",
        "rudraksha": "8-mukhi or 10-mukhi",
        "daan": ["Black/brown blanket", "Coconut", "Mustard oil", "Lead"],
        "daan_day": "Saturday or eclipse days",
        "vrat": "Saturday + Eclipse fasting",
        "colors": ["Smoky grey", "Dark brown"],
        "deity": "Durga / Kali / Bhairava",
        "lal_kitab": ["Carry a piece of silver. Donate barley to a temple. "
                      "Avoid alcohol and adulterous company."],
    },
    "Ketu": {
        "beej_mantra": "Om Strām Strīm Straum Saḥ Ketave Namaḥ",
        "japa_count": 17000,
        "vedic_mantra": "Padma hastāya vidmahe amṛta hastāya dhīmahi tanno ketuḥ pracodayāt",
        "stotra": "Ketu Stotra, Ganesha Stotra",
        "ratna": {"primary": "Cat's Eye (Lehsunia)", "substitute": "Chrysoberyl",
                  "finger": "Middle", "day_to_wear": "Tuesday at sunset",
                  "metal": "Silver or Panchadhatu", "carat_range": "5–9 ct"},
        "yantra": "Ketu Yantra",
        "rudraksha": "9-mukhi",
        "daan": ["Multi-coloured cloth", "Sesame", "Coconut", "Goat / blanket"],
        "daan_day": "Tuesday or eclipse days",
        "vrat": "Tuesday + Eclipse fasting",
        "colors": ["Multi-colour", "Smoky"],
        "deity": "Ganesha / Subramanya",
        "lal_kitab": ["Keep a dog as a pet or feed stray dogs. Wear silver. "
                      "Respect grandparents."],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Dosha-specific remedies (in addition to the planet of the affliction)
# ─────────────────────────────────────────────────────────────────────────────

DOSHA_REMEDIES: dict[str, dict] = {
    "Mangal Dosha (Kuja Dosha)": {
        "primary": "Hanuman Chalisa daily (especially Tuesdays).",
        "puja": "Mangal Shanti puja / Kumbh Vivah symbolic marriage before "
                "actual marriage (for severe Manglik).",
        "mantra": "Om Aṁ Aṅgārakāya Namaḥ — 108 × 7 = 756 daily for 40 days.",
        "fasting": "Tuesday fast for 21 weeks.",
        "donation": "Red lentils, jaggery, red cloth — to a young man.",
        "lal_kitab": "Throw a piece of red coral into a flowing river.",
    },
    "Pitra Dosha": {
        "primary": "Pind Daan at Gaya / Trimbakeshwar / Kashi — once-in-a-lifetime ideally.",
        "puja": "Pitra Tarpan during Pitru Paksha (Shraddh fortnight).",
        "mantra": "Om Pitr̥bhyaḥ Namaḥ — daily Tarpan.",
        "fasting": "Amavasya (new moon) fasts for ancestor propitiation.",
        "donation": "Food to Brahmins, cows, and the poor; clothing to elderly men.",
        "lal_kitab": "Plant a peepal tree and water it regularly. "
                     "Respect father-figures and male elders.",
    },
    "Grahan Dosha": {
        "primary": "Maha Mrityunjaya Mantra + Surya/Chandra Mantra together "
                   "(per which luminary is afflicted).",
        "puja": "Grahan Shanti puja during solar / lunar eclipses.",
        "mantra": "Maha Mrityunjaya — 108 × 11 = 1188, monthly on Trayodashi.",
        "fasting": "Strict fast on every eclipse day.",
        "donation": "Sesame seeds, blanket, food — at sunset on eclipse days.",
        "lal_kitab": "Bathe in the Ganges or any river on eclipse days; "
                     "keep silent for the duration of the eclipse.",
    },
    "Guru Chandal Dosha": {
        "primary": "Vishnu Sahasranama daily + Jupiter Yantra worship.",
        "puja": "Brihaspati Shanti puja on Thursdays.",
        "mantra": "Om Gurave Namaḥ — 108 × 5 = 540 daily for 41 days.",
        "fasting": "Thursday fast for 16 weeks.",
        "donation": "Yellow lentils + saffron + yellow cloth — to a learned brahmin.",
        "lal_kitab": "Apply saffron tilak daily. Respect teachers without exception.",
    },
    "Shrapit Dosha": {
        "primary": "Hanuman Chalisa + Maha Mrityunjaya — Saturday evening pairing.",
        "puja": "Shrapit Dosh Nivaran puja (Trimbakeshwar specialty).",
        "mantra": "Om Śaṁ Śanaiścarāya Namaḥ + Om Bhrāṁ Rāhave Namaḥ — alternating.",
        "fasting": "Saturday + Tuesday fasts.",
        "donation": "Mustard oil + black sesame + iron — to a labourer on Saturday.",
        "lal_kitab": "Light a mustard-oil lamp under a peepal on Saturday evening.",
    },
    "Shankhpal Kaal Sarp": {
        "primary": "Naga Devata abhishek + Kaal Sarp Shanti puja.",
        "puja": "Annual Kaal Sarp Shanti at Trimbakeshwar / Ujjain.",
        "mantra": "Om Nāgakulāya Vidmahe Viṣadantāya Dhīmahi Tanno Sarpaḥ Pracodayāt.",
        "fasting": "Panchami (5th day) fast monthly.",
        "donation": "Silver naga-pratima at a Shiva temple; milk for snakes.",
        "lal_kitab": "Float coconut + black sesame in a flowing river on a "
                     "Saturday during eclipse season.",
    },
    "Visha Yoga": {
        "primary": "Soma Stotra + Hanuman Chalisa pairing.",
        "puja": "Soma-Shani Shanti puja.",
        "mantra": "Om Saṁ Somāya Namaḥ — 108 × 11 daily for 27 days.",
        "fasting": "Monday + Saturday fasts paired.",
        "donation": "Milk + black sesame — to elderly.",
        "lal_kitab": "Keep silver and iron items together in a clean cloth.",
    },
    "Angarak Yoga": {
        "primary": "Hanuman Chalisa daily + Mangal Yantra worship.",
        "puja": "Mangal-Rahu Shanti.",
        "mantra": "Om Krāṁ Krīṁ Krauṁ Saḥ Bhaumāya Namaḥ.",
        "fasting": "Tuesday fast for 21 weeks.",
        "donation": "Red lentils + coral piece — Tuesday.",
        "lal_kitab": "Avoid weapons & sharp tools as gifts. "
                     "Channel anger through physical exercise daily.",
    },
    "Daridra Yoga": {
        "primary": "Lakshmi Stotra / Sri Suktam on Fridays.",
        "puja": "Lakshmi Kuber puja on Akshaya Tritiya and Diwali.",
        "mantra": "Om Śrīṁ Mahālakṣmyai Namaḥ — 108 × 9 daily.",
        "fasting": "Friday fast — break with kheer & white food.",
        "donation": "Food + clothing to truly needy, never as charity-for-show.",
        "lal_kitab": "Keep a small silver Lakshmi yantra in your wallet.",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Selection logic
# ─────────────────────────────────────────────────────────────────────────────

def _afflicting_planets(chart) -> list[str]:
    """
    Pick the planets most in need of remedies:
        - Functional malefics ruling key houses
        - Debilitated planets
        - Combust planets (except Sun)
        - Planets in 6/8/12
    Returns a deduplicated list ordered by severity.
    """
    out: list[str] = []
    seen = set()

    def add(p):
        if p not in seen and p in chart.planets:
            out.append(p); seen.add(p)

    # Debilitated > Combust > In dusthana > Functional malefic
    for p, pp in chart.planets.items():
        if pp.dignity == "Debilitated":
            add(p)
    for p, pp in chart.planets.items():
        if pp.is_combust and p != "Sun":
            add(p)
    for p, pp in chart.planets.items():
        if pp.house in (6, 8, 12) and p not in ("Rahu", "Ketu"):
            add(p)
    for p in chart.functional.malefics:
        add(p)

    # Always include 8th/12th lords (karmic markers)
    h8_lord = SIGN_LORDS_MAP[(chart.lagna.sign_index + 7) % 12]
    h12_lord = SIGN_LORDS_MAP[(chart.lagna.sign_index + 11) % 12]
    add(h8_lord); add(h12_lord)

    return out


def recommend(chart) -> dict:
    """
    Build the full remedies payload.

    Returns:
        {
          "priority_planets": [...],
          "per_planet": {planet: {...remedy fields...}},
          "per_dosha":  {dosha_name: {...remedy fields...}},
          "gemstone_chart": {planet: ratna_subdict},
          "daily_practice": [str, ...],         # consolidated daily routine
        }
    """
    priorities = _afflicting_planets(chart)
    per_planet = {p: PLANET_REMEDIES[p] for p in priorities if p in PLANET_REMEDIES}
    per_dosha = {}
    for d in chart.doshas:
        if d.present and d.name in DOSHA_REMEDIES:
            per_dosha[d.name] = DOSHA_REMEDIES[d.name]

    # Consolidated daily practice — readable, actionable bullets
    daily: list[str] = []
    daily.append("Begin the day with the Maha Mrityunjaya Mantra (3 or 11 rounds).")
    if priorities:
        first = priorities[0]
        if first in PLANET_REMEDIES:
            daily.append(f"Chant the Beej mantra of {first}: "
                         f"{PLANET_REMEDIES[first]['beej_mantra']} — 108 times.")
    daily.append("Offer water to the Sun at sunrise (Surya Arghya) — 5 minutes.")
    daily.append("Light a ghee lamp at home before sundown.")
    if any(d.name.startswith("Shankhpal") or d.name.endswith("Kaal Sarp")
           for d in chart.doshas if d.present):
        daily.append("Hanuman Chalisa once daily until major dasha shift.")

    gemstone_chart = {p: PLANET_REMEDIES[p]["ratna"]
                      for p in PLANET_REMEDIES}

    return {
        "priority_planets": priorities,
        "per_planet":       per_planet,
        "per_dosha":        per_dosha,
        "gemstone_chart":   gemstone_chart,
        "daily_practice":   daily,
    }
