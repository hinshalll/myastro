"""
math_engine/kundli/nakshatra_profile.py
=======================================

Builds the birth nakshatra profile + the classical Avakahada Chakra
(the summary table that appears near the front of every Indian kundli).

Data is per-nakshatra and language-neutral (Sanskrit names of categories
are universal). English category descriptions live here; translations for
the other 6 languages will be sourced from the interpretations library
(separate JSON files, loaded at PDF render time — not at compute time).

References:
    - BPHS Ch. 3 (Nakshatra characteristics)
    - "Brihat Samhita" attributions for Yoni
    - "Muhurta Chintamani" for Gana/Tatva/Vashya classifications
    - The compatibility (Ashta-Koota) standard from Daivagya Vallabha
"""

from __future__ import annotations
from math_engine.constants import NAKSHATRAS, NAKSHATRA_LORDS


# ─────────────────────────────────────────────────────────────────────────────
# Per-nakshatra master attribute table
# ─────────────────────────────────────────────────────────────────────────────
#
# Field meanings:
#   deity      — presiding deity (used in remedies + ritual recommendations)
#   symbol     — classical visual symbol
#   gana       — Deva / Manushya / Rakshasa (temperament classification)
#   yoni       — animal pair for sexual/temperamental compatibility (Yoni-Koota)
#                Each nakshatra gets a (animal, gender) pairing. Two nakshatras
#                with the same animal are best matches; enemy yonis are worst.
#   nadi       — Adi / Madhya / Antya (constitution; same Nadi = marriage dosha)
#   varna      — Brahmin / Kshatriya / Vaishya / Shudra (social aptitude)
#   vashya     — Dwipada / Chatushpada / Jalachara / Vanachara / Keeta
#                (which beings the native naturally influences)
#   tatva      — Fire / Earth / Air / Water / Ether (elemental constitution)
#   gender     — Male / Female / Neutral (psychological polarity)
#   guna       — Sattva / Rajas / Tamas (dominant mode)
#   syllables  — 4 starting syllables (one per pada) used for naming children
#                and for Nama-Koota in compatibility matching
#
# Standard sources differ on a few attributions; we use the BPHS+JH consensus.
# ─────────────────────────────────────────────────────────────────────────────

NAKSHATRA_DATA: dict[str, dict] = {
    "Ashwini": {
        "deity": "Ashwini Kumaras (twin healers)",
        "symbol": "Horse's head",
        "gana": "Deva", "yoni": ("Horse", "Male"),
        "nadi": "Adi", "varna": "Vaishya", "vashya": "Chatushpada",
        "tatva": "Earth", "gender": "Male", "guna": "Rajas",
        "syllables": ["Chu", "Che", "Cho", "La"],
    },
    "Bharani": {
        "deity": "Yama (god of death/dharma)",
        "symbol": "Yoni (vulva)",
        "gana": "Manushya", "yoni": ("Elephant", "Male"),
        "nadi": "Madhya", "varna": "Mleccha", "vashya": "Dwipada",
        "tatva": "Earth", "gender": "Female", "guna": "Rajas",
        "syllables": ["Li", "Lu", "Le", "Lo"],
    },
    "Krittika": {
        "deity": "Agni (fire)",
        "symbol": "Razor / flame",
        "gana": "Rakshasa", "yoni": ("Sheep", "Female"),
        "nadi": "Antya", "varna": "Brahmin", "vashya": "Chatushpada",
        "tatva": "Earth", "gender": "Female", "guna": "Rajas",
        "syllables": ["A", "I", "U", "E"],
    },
    "Rohini": {
        "deity": "Brahma / Prajapati",
        "symbol": "Ox cart / banyan tree",
        "gana": "Manushya", "yoni": ("Serpent", "Male"),
        "nadi": "Antya", "varna": "Shudra", "vashya": "Chatushpada",
        "tatva": "Earth", "gender": "Female", "guna": "Rajas",
        "syllables": ["O", "Va", "Vi", "Vu"],
    },
    "Mrigashira": {
        "deity": "Soma / Chandra (Moon)",
        "symbol": "Deer's head",
        "gana": "Deva", "yoni": ("Serpent", "Female"),
        "nadi": "Madhya", "varna": "Sevaka", "vashya": "Chatushpada",
        "tatva": "Earth", "gender": "Neutral", "guna": "Tamas",
        "syllables": ["Ve", "Vo", "Ka", "Ki"],
    },
    "Ardra": {
        "deity": "Rudra (storm form of Shiva)",
        "symbol": "Teardrop / diamond",
        "gana": "Manushya", "yoni": ("Dog", "Female"),
        "nadi": "Adi", "varna": "Butcher", "vashya": "Dwipada",
        "tatva": "Water", "gender": "Female", "guna": "Tamas",
        "syllables": ["Ku", "Kha", "Nga", "Chha"],
    },
    "Punarvasu": {
        "deity": "Aditi (mother of gods)",
        "symbol": "Bow & quiver",
        "gana": "Deva", "yoni": ("Cat", "Female"),
        "nadi": "Adi", "varna": "Vaishya", "vashya": "Dwipada",
        "tatva": "Water", "gender": "Male", "guna": "Sattva",
        "syllables": ["Ke", "Ko", "Ha", "Hi"],
    },
    "Pushya": {
        "deity": "Brihaspati (Jupiter / teacher of gods)",
        "symbol": "Cow's udder / lotus",
        "gana": "Deva", "yoni": ("Sheep", "Male"),
        "nadi": "Madhya", "varna": "Kshatriya", "vashya": "Jalachara",
        "tatva": "Water", "gender": "Male", "guna": "Tamas",
        "syllables": ["Hu", "He", "Ho", "Da"],
    },
    "Ashlesha": {
        "deity": "Naga (serpents)",
        "symbol": "Coiled serpent",
        "gana": "Rakshasa", "yoni": ("Cat", "Male"),
        "nadi": "Antya", "varna": "Mleccha", "vashya": "Keeta",
        "tatva": "Water", "gender": "Female", "guna": "Sattva",
        "syllables": ["Di", "Du", "De", "Do"],
    },
    "Magha": {
        "deity": "Pitris (ancestors)",
        "symbol": "Royal throne",
        "gana": "Rakshasa", "yoni": ("Rat", "Male"),
        "nadi": "Antya", "varna": "Shudra", "vashya": "Chatushpada",
        "tatva": "Fire", "gender": "Female", "guna": "Tamas",
        "syllables": ["Ma", "Mi", "Mu", "Me"],
    },
    "Purva Phalguni": {
        "deity": "Bhaga (delight, luxury)",
        "symbol": "Front legs of a bed / hammock",
        "gana": "Manushya", "yoni": ("Rat", "Female"),
        "nadi": "Madhya", "varna": "Brahmin", "vashya": "Dwipada",
        "tatva": "Fire", "gender": "Female", "guna": "Rajas",
        "syllables": ["Mo", "Ta", "Ti", "Tu"],
    },
    "Uttara Phalguni": {
        "deity": "Aryaman (patronage, contracts)",
        "symbol": "Back legs of a bed / four legs",
        "gana": "Manushya", "yoni": ("Cow", "Male"),
        "nadi": "Adi", "varna": "Kshatriya", "vashya": "Dwipada",
        "tatva": "Fire", "gender": "Female", "guna": "Rajas",
        "syllables": ["Te", "To", "Pa", "Pi"],
    },
    "Hasta": {
        "deity": "Savitar (Sun as inspirer)",
        "symbol": "Open hand / clenched fist",
        "gana": "Deva", "yoni": ("Buffalo", "Female"),
        "nadi": "Adi", "varna": "Vaishya", "vashya": "Dwipada",
        "tatva": "Fire", "gender": "Male", "guna": "Rajas",
        "syllables": ["Pu", "Sha", "Na", "Tha"],
    },
    "Chitra": {
        "deity": "Vishvakarma (celestial architect)",
        "symbol": "Bright jewel / pearl",
        "gana": "Rakshasa", "yoni": ("Tiger", "Female"),
        "nadi": "Madhya", "varna": "Sevaka", "vashya": "Keeta",
        "tatva": "Fire", "gender": "Female", "guna": "Tamas",
        "syllables": ["Pe", "Po", "Ra", "Ri"],
    },
    "Swati": {
        "deity": "Vayu (wind)",
        "symbol": "Young plant blown by wind / coral",
        "gana": "Deva", "yoni": ("Buffalo", "Male"),
        "nadi": "Antya", "varna": "Butcher", "vashya": "Dwipada",
        "tatva": "Fire", "gender": "Female", "guna": "Tamas",
        "syllables": ["Ru", "Re", "Ro", "Ta"],
    },
    "Vishakha": {
        "deity": "Indra & Agni",
        "symbol": "Triumphal archway / potter's wheel",
        "gana": "Rakshasa", "yoni": ("Tiger", "Male"),
        "nadi": "Antya", "varna": "Mleccha", "vashya": "Keeta",
        "tatva": "Fire", "gender": "Female", "guna": "Sattva",
        "syllables": ["Ti", "Tu", "Te", "To"],
    },
    "Anuradha": {
        "deity": "Mitra (friendship)",
        "symbol": "Lotus / triumphal archway",
        "gana": "Deva", "yoni": ("Deer", "Female"),
        "nadi": "Madhya", "varna": "Shudra", "vashya": "Keeta",
        "tatva": "Fire", "gender": "Male", "guna": "Tamas",
        "syllables": ["Na", "Ni", "Nu", "Ne"],
    },
    "Jyeshtha": {
        "deity": "Indra (king of gods)",
        "symbol": "Circular amulet / umbrella",
        "gana": "Rakshasa", "yoni": ("Deer", "Male"),
        "nadi": "Adi", "varna": "Sevaka", "vashya": "Keeta",
        "tatva": "Air", "gender": "Female", "guna": "Sattva",
        "syllables": ["No", "Ya", "Yi", "Yu"],
    },
    "Mula": {
        "deity": "Nirriti (goddess of dissolution)",
        "symbol": "Bundle of roots / lion's tail",
        "gana": "Rakshasa", "yoni": ("Dog", "Male"),
        "nadi": "Adi", "varna": "Butcher", "vashya": "Chatushpada",
        "tatva": "Air", "gender": "Neutral", "guna": "Tamas",
        "syllables": ["Ye", "Yo", "Bha", "Bhi"],
    },
    "Purva Ashadha": {
        "deity": "Apah (cosmic waters)",
        "symbol": "Fan / winnowing basket",
        "gana": "Manushya", "yoni": ("Monkey", "Male"),
        "nadi": "Madhya", "varna": "Brahmin", "vashya": "Dwipada",
        "tatva": "Air", "gender": "Female", "guna": "Rajas",
        "syllables": ["Bhu", "Dha", "Pha", "Dha"],
    },
    "Uttara Ashadha": {
        "deity": "Vishvedevas (10 universal gods)",
        "symbol": "Elephant's tusk / planks of a bed",
        "gana": "Manushya", "yoni": ("Mongoose", "Male"),
        "nadi": "Antya", "varna": "Kshatriya", "vashya": "Chatushpada",
        "tatva": "Air", "gender": "Female", "guna": "Sattva",
        "syllables": ["Bhe", "Bho", "Ja", "Ji"],
    },
    "Shravana": {
        "deity": "Vishnu",
        "symbol": "Ear / three footprints",
        "gana": "Deva", "yoni": ("Monkey", "Female"),
        "nadi": "Antya", "varna": "Mleccha", "vashya": "Chatushpada",
        "tatva": "Air", "gender": "Male", "guna": "Rajas",
        "syllables": ["Ju", "Je", "Jo", "Gha"],
    },
    "Dhanishta": {
        "deity": "Vasus (8 elemental gods)",
        "symbol": "Drum / flute",
        "gana": "Rakshasa", "yoni": ("Lion", "Female"),
        "nadi": "Madhya", "varna": "Sevaka", "vashya": "Chatushpada",
        "tatva": "Ether", "gender": "Female", "guna": "Tamas",
        "syllables": ["Ga", "Gi", "Gu", "Ge"],
    },
    "Shatabhisha": {
        "deity": "Varuna (cosmic waters / law)",
        "symbol": "Empty circle / 100 healers",
        "gana": "Rakshasa", "yoni": ("Horse", "Female"),
        "nadi": "Adi", "varna": "Butcher", "vashya": "Dwipada",
        "tatva": "Ether", "gender": "Neutral", "guna": "Tamas",
        "syllables": ["Go", "Sa", "Si", "Su"],
    },
    "Purva Bhadrapada": {
        "deity": "Aja Ekapada (one-footed goat / dragon)",
        "symbol": "Front legs of a funeral cot / two-faced man",
        "gana": "Manushya", "yoni": ("Lion", "Male"),
        "nadi": "Adi", "varna": "Brahmin", "vashya": "Dwipada",
        "tatva": "Ether", "gender": "Male", "guna": "Sattva",
        "syllables": ["Se", "So", "Da", "Di"],
    },
    "Uttara Bhadrapada": {
        "deity": "Ahir Budhnya (serpent of the deep)",
        "symbol": "Back legs of a funeral cot / two-headed man",
        "gana": "Manushya", "yoni": ("Cow", "Female"),
        "nadi": "Madhya", "varna": "Kshatriya", "vashya": "Jalachara",
        "tatva": "Ether", "gender": "Male", "guna": "Tamas",
        "syllables": ["Du", "Tha", "Jha", "Yna"],
    },
    "Revati": {
        "deity": "Pushan (nourisher; god of travel)",
        "symbol": "Pair of fish / drum",
        "gana": "Deva", "yoni": ("Elephant", "Female"),
        "nadi": "Antya", "varna": "Shudra", "vashya": "Jalachara",
        "tatva": "Ether", "gender": "Female", "guna": "Sattva",
        "syllables": ["De", "Do", "Cha", "Chi"],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Avakahada Chakra — the classical front-page summary
# ─────────────────────────────────────────────────────────────────────────────
#
# A standard Indian kundli prints a 12-row summary table called the
# "Avakahada Chakra" (literally "without-syllable diagram"). It distils the
# entire chart's identity into one screen, and is what an experienced reader
# glances at first.
# ─────────────────────────────────────────────────────────────────────────────

# Hindu calendar / weekday mappings used in the Avakahada Chakra.
_WEEKDAY_DEITY = {
    "Monday":    "Chandra (Moon)",
    "Tuesday":   "Mangal (Mars)",
    "Wednesday": "Budha (Mercury)",
    "Thursday":  "Brihaspati (Jupiter)",
    "Friday":    "Shukra (Venus)",
    "Saturday":  "Shani (Saturn)",
    "Sunday":    "Surya (Sun)",
}

# Sign elements for Tatva fallback (when a nakshatra straddles signs).
_SIGN_TATVA = {
    0: "Fire",   3: "Water", 6: "Air",    9: "Earth",
    1: "Earth",  4: "Fire",  7: "Water", 10: "Air",
    2: "Air",    5: "Earth", 8: "Fire",  11: "Water",
}


def get_nakshatra_attributes(nakshatra: str) -> dict:
    """Lookup the master attribute record for a nakshatra name."""
    return NAKSHATRA_DATA.get(nakshatra, {})


def get_pada_syllables(nakshatra: str, pada: int) -> str:
    """The Sanskrit syllable for the (1-indexed) pada — used for child naming."""
    attrs = NAKSHATRA_DATA.get(nakshatra, {})
    syll = attrs.get("syllables", [])
    if not syll or not 1 <= pada <= 4:
        return ""
    return syll[pada - 1]


def build(chart) -> dict:
    """
    Build the full nakshatra profile + Avakahada Chakra for a KundliChart.

    Returns a dict with the data every PDF section needs:
        - birth nakshatra summary (lord, deity, symbol, pada, syllable)
        - Avakahada Chakra (12 classical rows)
        - tatva, gana, yoni, nadi, varna, vashya, gender, guna
    """
    moon = chart.planets["Moon"]
    nak = moon.nakshatra
    pada = moon.pada
    attrs = get_nakshatra_attributes(nak)
    syll = get_pada_syllables(nak, pada)

    # Tatva fallback to sign element if missing from nakshatra table
    tatva = attrs.get("tatva") or _SIGN_TATVA.get(moon.sign_index, "—")

    avakahada = [
        ("Janma Naam (Name)",        chart.birth_data.name),
        ("Janma Tithi",              chart.panchanga.tithi),
        ("Janma Vara (Weekday)",     chart.panchanga.weekday),
        ("Vara Devta",               _WEEKDAY_DEITY.get(chart.panchanga.weekday, "—")),
        ("Janma Nakshatra",          f"{nak} (Pada {pada})"),
        ("Nakshatra Lord",           moon.nakshatra_lord),
        ("Nakshatra Devta",          attrs.get("deity", "—")),
        ("Janma Rashi (Moon Sign)",  moon.sign),
        ("Rashi Lord",               moon.sign_lord),
        ("Lagna (Ascendant)",        chart.lagna.sign),
        ("Lagna Lord",               chart.lagna.lord),
        ("Yoga",                     chart.panchanga.yoga),
        ("Karana",                   chart.panchanga.karana),
        ("Paksha",                   chart.panchanga.paksha),
        ("Gana",                     attrs.get("gana", "—")),
        ("Yoni",                     "{} ({})".format(*attrs["yoni"]) if attrs.get("yoni") else "—"),
        ("Nadi",                     attrs.get("nadi", "—")),
        ("Varna",                    attrs.get("varna", "—")),
        ("Vashya",                   attrs.get("vashya", "—")),
        ("Tatva (Element)",          tatva),
        ("Gender (Psychological)",   attrs.get("gender", "—")),
        ("Guna",                     attrs.get("guna", "—")),
        ("Naam-akshar (Name letter)", syll),
    ]

    return {
        "birth_nakshatra":     nak,
        "pada":                pada,
        "nakshatra_lord":      moon.nakshatra_lord,
        "deity":               attrs.get("deity"),
        "symbol":              attrs.get("symbol"),
        "gana":                attrs.get("gana"),
        "yoni":                attrs.get("yoni"),
        "nadi":                attrs.get("nadi"),
        "varna":               attrs.get("varna"),
        "vashya":              attrs.get("vashya"),
        "tatva":               tatva,
        "gender":              attrs.get("gender"),
        "guna":                attrs.get("guna"),
        "pada_syllables":      attrs.get("syllables", []),
        "naam_akshar":         syll,
        "avakahada_chakra":    avakahada,
        # Useful for compatibility matching & child-naming modules:
        "lagna_nakshatra":     chart.lagna.nakshatra,
        "lagna_nakshatra_lord": chart.lagna.nakshatra_lord,
    }
