"""
math_engine/kundli/doshas.py
============================

Comprehensive dosha (affliction) detection for the kundli PDF.

A standard premium kundli's dosha section answers, for each classical
affliction, three questions:

    1. Is it present?
    2. How severe? (partial / full / cancelled)
    3. What's the cause and what cancels it?

Doshas detected here (solo-chart only; compatibility doshas like Nadi /
Bhakoot live in a future `compatibility.py`):

    - Mangal Dosha (Kuja)        — Mars in 1/2/4/7/8/12 from Lagna / Moon / Venus
    - Kaal Sarp Dosha (12 named) — All planets on one side of Rahu-Ketu axis
    - Sade Sati                  — Saturn through 12th/1st/2nd from natal Moon
    - Pitra Dosha                — Sun/9th-lord afflicted by Rahu/Saturn
    - Guru Chandal Dosha         — Jupiter conjunct Rahu / Ketu
    - Grahan Dosha (Solar/Lunar) — Sun/Moon conjunct Rahu / Ketu
    - Shrapit Dosha              — Rahu+Saturn or Ketu+Saturn conjunction
    - Visha Yoga                 — Moon + Saturn in same sign
    - Kemadruma Yoga             — Moon with no planet in 2nd/12th from it
                                   and no planet conjunct (poverty/isolation)
    - Angarak Yoga               — Mars + Rahu conjunction (anger / accidents)
    - Chandal Yoga               — Synonym group: Jupiter+Rahu, captured in
                                   Guru Chandal above.
    - Daridra Yoga               — 11th lord in dusthana from Lagna

References:
    - BPHS Ch. 87-89 (yogas & doshas)
    - "Saravali" Ch. 24 (lunar yogas — Kemadruma)
    - "Hora Sara" (Kaal Sarp variants)
    - Practical conventions from Parashara's Light / Jagannatha Hora
"""

from __future__ import annotations

from math_engine.constants import SIGN_LORDS_MAP
from math_engine.astro_calc import (
    whole_sign_house,
    sign_index_from_lon,
    check_manglik_dosha,
    get_manglik_cancellation_verdict,
    calculate_sade_sati,
)


# ─────────────────────────────────────────────────────────────────────────────
# Kaal Sarp Dosha — 12 named variants
# ─────────────────────────────────────────────────────────────────────────────
#
# Kaal Sarp is named after the serpent (sarp) of time (kaal). It manifests
# when all 7 grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn) lie
# on one side of the Rahu-Ketu axis. The 12 types differ by which houses
# Rahu and Ketu occupy.
#
# Full (Poorna) — every classical planet strictly between Rahu and Ketu
#                 going one direction around the wheel.
# Partial (Ardha) — one or two planets on the "wrong" side, weakening
#                 (but not erasing) the dosha. Common in modern charts.
#
# Cancellations: planet conjunct Rahu (or Ketu) within 5°, Jupiter aspecting
# Rahu, well-placed Lagna lord — all reduce the dosha. Most modern texts
# treat the dosha itself as life-shaping but the cancellations make it
# manageable, not invalidate it.
# ─────────────────────────────────────────────────────────────────────────────

KAAL_SARP_NAMES = {
    1:  ("Anant",       "Restlessness, legal entanglements, but eventual recognition"),
    2:  ("Kulik",       "Financial volatility, family disputes, speech challenges"),
    3:  ("Vasuki",      "Communication / siblings tested; strong willpower develops"),
    4:  ("Shankhpal",   "Mother/home/property delays; emotional volatility"),
    5:  ("Padma",       "Children / education delays; creative breakthroughs after struggle"),
    6:  ("Mahapadma",   "Hidden enemies, chronic-health watchpoints; service success"),
    7:  ("Takshak",     "Marriage / partnership instability; sudden gains via partners"),
    8:  ("Karkotak",    "Sudden events, occult interests, longevity tests"),
    9:  ("Shankhachud", "Fortune / dharma awakens late; spiritual elevation"),
    10: ("Ghatak",      "Career detours then a defining destiny shift"),
    11: ("Vishdhar",    "Income fluctuations; large network of contacts"),
    12: ("Sheshnaag",   "Expenses, foreign connections, isolation periods, moksha urge"),
}


def _detect_kaal_sarp(chart) -> dict:
    """Return Kaal Sarp findings: present, type-name, severity, cancellations."""
    rahu_h = chart.planets["Rahu"].house
    ketu_h = chart.planets["Ketu"].house

    # 7 classical grahas (no nodes)
    classical = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    p_houses = {p: chart.planets[p].house for p in classical}

    # Compute the arc of houses from Rahu → Ketu (going forward).
    # Two arcs exist: Rahu→Ketu (going +1, +2, ...) and Ketu→Rahu (going +1, +2, ...).
    # If all 7 fall in ONE arc (exclusive of Rahu/Ketu's own houses), Kaal Sarp.
    def arc_houses(start, end):
        houses = []
        h = (start % 12) + 1
        while h != end:
            houses.append(h)
            h = (h % 12) + 1
        return set(houses)

    arc_rk = arc_houses(rahu_h, ketu_h)        # houses strictly between R→K
    arc_kr = arc_houses(ketu_h, rahu_h)        # houses strictly between K→R

    in_rk = sum(1 for p in classical if p_houses[p] in arc_rk)
    in_kr = sum(1 for p in classical if p_houses[p] in arc_kr)
    in_nodes = 7 - in_rk - in_kr               # planets at the Rahu/Ketu houses themselves

    full_one_side = (in_rk == 7) or (in_kr == 7)
    partial_one_side = (in_rk >= 6) or (in_kr >= 6)  # 1 planet on the wrong side

    if not partial_one_side:
        return {
            "present": False, "type": None, "severity": "none",
            "cause": "Planets distributed on both sides of the Rahu–Ketu axis (Kaal Sarp absent).",
            "cancellations": [],
        }

    type_id, (type_name, theme) = rahu_h, KAAL_SARP_NAMES[rahu_h]
    severity = "full" if full_one_side else "partial"

    # Cancellations (modern convention)
    cancels = []
    for p in classical:
        # planet conjunct (same house as) Rahu OR Ketu — softens
        if p_houses[p] in {rahu_h, ketu_h}:
            cancels.append(f"{p} conjunct {'Rahu' if p_houses[p]==rahu_h else 'Ketu'} — softens")
    # Jupiter aspect on Rahu's house (5th, 7th, 9th from Jupiter)
    jh = p_houses["Jupiter"]
    if rahu_h in {((jh + d - 2) % 12) + 1 for d in (5, 7, 9)}:
        cancels.append("Jupiter aspects Rahu's house — softens")
    # Lagna lord well-placed (in kendra or trikona, not in dusthana)
    lord_planet = chart.lagna.lord
    lord_house = chart.planets[lord_planet].house if lord_planet in chart.planets else None
    if lord_house and lord_house in {1, 4, 5, 7, 9, 10}:
        cancels.append(f"Lagna lord {lord_planet} well-placed in H{lord_house}")

    return {
        "present": True,
        "type": f"{type_name} Kaal Sarp",
        "type_id": type_id,
        "severity": severity,
        "rahu_house": rahu_h, "ketu_house": ketu_h,
        "theme": theme,
        "cause": (f"Rahu in H{rahu_h}, Ketu in H{ketu_h}. "
                  f"All {in_rk if in_rk>=6 else in_kr} of 7 classical planets fall "
                  f"{'between' if in_rk>=6 else 'opposite'} the Rahu–Ketu axis."),
        "cancellations": cancels,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Mangal (Kuja) Dosha
# ─────────────────────────────────────────────────────────────────────────────

def _detect_mangal(chart) -> dict:
    """Wrap the existing astro_calc helper into a structured dosha record."""
    moon_sidx = chart.planets["Moon"].sign_index
    mars_sidx = chart.planets["Mars"].sign_index
    raw = check_manglik_dosha(chart.lagna.sign_index, moon_sidx, mars_sidx)

    present = bool(raw) and "no" not in raw.lower()  # function returns text
    mars_h = chart.planets["Mars"].house
    severity = "full" if mars_h in {7, 8} else ("partial" if present else "none")

    cancels = []
    if present:
        # Classical cancellations
        if chart.planets["Mars"].sign in ("Aries", "Scorpio", "Capricorn"):
            cancels.append("Mars in own/exalted sign — significantly mitigates")
        if chart.planets["Jupiter"].house in {1, 4, 7, 10}:
            cancels.append("Jupiter in a kendra — mitigates Mangal Dosha")
        # Mars aspected by Jupiter
        jh = chart.planets["Jupiter"].house
        if mars_h in {((jh + d - 2) % 12) + 1 for d in (5, 7, 9)}:
            cancels.append("Jupiter aspects Mars — mitigates")
        # Second Mangalik partner cancels (compatibility-specific; noted only)

    return {
        "present": present,
        "type": "Mangal Dosha (Kuja Dosha)",
        "severity": severity,
        "cause": raw or "Mars not in 1/2/4/7/8/12 from Lagna, Moon, or Venus.",
        "cancellations": cancels,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Sade Sati (Saturn 7.5-year cycle through 12th/1st/2nd from natal Moon)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_sade_sati(chart) -> dict:
    moon_sidx = chart.planets["Moon"].sign_index
    raw = calculate_sade_sati(moon_sidx)  # existing helper produces a verdict string
    # `raw` is descriptive text; we wrap it as a dosha record. The transits.py
    # module will compute the actual current-Saturn position vs natal Moon and
    # produce dated windows.
    return {
        "present": True if raw and "not" not in raw.lower() else False,
        "type": "Sade Sati",
        "severity": "varies",      # filled in by transits.py with current window
        "cause": raw,
        "cancellations": [],
        "note": "Refer to the 12-month transit forecast page for the active window.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Pitra Dosha — ancestral karma affliction
# ─────────────────────────────────────────────────────────────────────────────

def _detect_pitra(chart) -> dict:
    """
    Pitra Dosha indicators (any one strongly suggests; multiple = definite):
        - Sun in 9th house conjunct Rahu or Ketu
        - Rahu in 9th house
        - 9th lord in 6/8/12 from Lagna
        - 9th lord conjunct Rahu or Ketu
        - Sun afflicted by Saturn in 9th
    """
    p = chart.planets
    h9_sign = (chart.lagna.sign_index + 8) % 12
    h9_lord_name = SIGN_LORDS_MAP[h9_sign]
    h9_lord = p.get(h9_lord_name)

    indicators = []
    if p["Sun"].house == 9 and p["Rahu"].house == 9:
        indicators.append("Sun conjunct Rahu in 9th house")
    if p["Sun"].house == 9 and p["Ketu"].house == 9:
        indicators.append("Sun conjunct Ketu in 9th house")
    if p["Rahu"].house == 9:
        indicators.append("Rahu in 9th house")
    if h9_lord and h9_lord.house in {6, 8, 12}:
        indicators.append(f"9th lord {h9_lord_name} in dusthana (H{h9_lord.house})")
    if h9_lord and h9_lord.house in (p["Rahu"].house, p["Ketu"].house):
        indicators.append(f"9th lord {h9_lord_name} conjunct Rahu/Ketu")
    if p["Sun"].house == 9 and p["Saturn"].house == 9:
        indicators.append("Sun afflicted by Saturn in 9th house")

    present = len(indicators) >= 1
    severity = "full" if len(indicators) >= 2 else ("partial" if present else "none")

    return {
        "present": present,
        "type": "Pitra Dosha",
        "severity": severity,
        "cause": "; ".join(indicators) if indicators else "9th house and Sun are unafflicted.",
        "cancellations": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Guru Chandal Dosha — Jupiter (Guru) conjunct Rahu or Ketu (Chandal)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_guru_chandal(chart) -> dict:
    p = chart.planets
    same_as_rahu = (p["Jupiter"].house == p["Rahu"].house)
    same_as_ketu = (p["Jupiter"].house == p["Ketu"].house)
    if not (same_as_rahu or same_as_ketu):
        return {
            "present": False, "type": "Guru Chandal Dosha", "severity": "none",
            "cause": "Jupiter is not conjunct Rahu or Ketu.", "cancellations": [],
        }
    node = "Rahu" if same_as_rahu else "Ketu"
    # Tightness — by longitude difference
    diff = abs(p["Jupiter"].longitude - p[node].longitude)
    diff = min(diff, 360 - diff)
    tight = diff <= 8.0
    return {
        "present": True, "type": "Guru Chandal Dosha",
        "severity": "full" if tight else "partial",
        "cause": (f"Jupiter conjunct {node} in H{p['Jupiter'].house} "
                  f"({diff:.1f}° apart). Distorts judgment, faith, and the teacher–"
                  f"student relationship until consciously navigated."),
        "cancellations": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Grahan Dosha — Sun or Moon conjunct Rahu / Ketu (eclipse yoga)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_grahan(chart) -> dict:
    p = chart.planets
    findings = []
    for luminary in ("Sun", "Moon"):
        for node in ("Rahu", "Ketu"):
            if p[luminary].house == p[node].house:
                diff = abs(p[luminary].longitude - p[node].longitude)
                diff = min(diff, 360 - diff)
                kind = "Surya Grahan" if luminary == "Sun" else "Chandra Grahan"
                findings.append((kind, luminary, node, p[luminary].house, diff))
    if not findings:
        return {
            "present": False, "type": "Grahan Dosha", "severity": "none",
            "cause": "No eclipse axis on Sun or Moon.", "cancellations": [],
        }
    parts = []
    severity = "partial"
    for kind, lum, node, h, d in findings:
        parts.append(f"{kind} — {lum} conjunct {node} in H{h} ({d:.1f}°)")
        if d <= 8.0:
            severity = "full"
    return {
        "present": True, "type": "Grahan Dosha", "severity": severity,
        "cause": "; ".join(parts), "cancellations": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Shrapit Dosha — Rahu+Saturn or Ketu+Saturn conjunction
# ─────────────────────────────────────────────────────────────────────────────

def _detect_shrapit(chart) -> dict:
    p = chart.planets
    findings = []
    if p["Saturn"].house == p["Rahu"].house:
        findings.append(("Rahu", p["Saturn"].house))
    if p["Saturn"].house == p["Ketu"].house:
        findings.append(("Ketu", p["Saturn"].house))
    if not findings:
        return {
            "present": False, "type": "Shrapit Dosha", "severity": "none",
            "cause": "Saturn not conjunct Rahu or Ketu.", "cancellations": [],
        }
    parts = [f"Saturn conjunct {n} in H{h}" for n, h in findings]
    return {
        "present": True, "type": "Shrapit Dosha", "severity": "partial",
        "cause": "; ".join(parts) + ". Carries karmic-curse signature; "
                 "ancestral propitiation traditionally indicated.",
        "cancellations": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Visha Yoga — Moon + Saturn in same sign (poison yoga)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_visha(chart) -> dict:
    p = chart.planets
    if p["Moon"].sign_index != p["Saturn"].sign_index:
        return {
            "present": False, "type": "Visha Yoga", "severity": "none",
            "cause": "Moon and Saturn not in same sign.", "cancellations": [],
        }
    return {
        "present": True, "type": "Visha Yoga", "severity": "partial",
        "cause": f"Moon and Saturn both in {p['Moon'].sign}. "
                 "Emotional heaviness, recurring melancholy; deep psychological work "
                 "produces wisdom in maturity.",
        "cancellations": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Kemadruma Yoga — Moon isolated (no planet in 2/12 from Moon, no conjunct)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_kemadruma(chart) -> dict:
    """Kemadruma classical rule + cancellations from BPHS."""
    moon_h = chart.planets["Moon"].house
    moon_sidx = chart.planets["Moon"].sign_index
    second_from_moon = (moon_sidx + 1) % 12
    twelfth_from_moon = (moon_sidx + 11) % 12

    others = [n for n in chart.planets if n not in ("Moon", "Rahu", "Ketu")]
    planet_signs = {n: chart.planets[n].sign_index for n in others}

    in_2nd  = any(planet_signs[n] == second_from_moon  for n in others)
    in_12th = any(planet_signs[n] == twelfth_from_moon for n in others)
    conjoined = any(planet_signs[n] == moon_sidx for n in others)

    if in_2nd or in_12th or conjoined:
        return {
            "present": False, "type": "Kemadruma Yoga", "severity": "none",
            "cause": "Moon flanked or conjoined by other planets — Kemadruma cancelled.",
            "cancellations": [],
        }

    # Cancellations even when Kemadruma is technically present
    cancels = []
    if chart.planets["Moon"].house in {1, 4, 7, 10}:
        cancels.append("Moon in a kendra — Kemadruma considered cancelled (BPHS)")
    if any(chart.planets[n].house in {1, 4, 7, 10}
           for n in ("Jupiter", "Venus", "Mercury")):
        cancels.append("Benefic in kendra — Kemadruma considered cancelled")

    return {
        "present": True,
        "type": "Kemadruma Yoga",
        "severity": "cancelled" if cancels else "partial",
        "cause": (f"Moon in H{moon_h} ({chart.planets['Moon'].sign}) with no planet "
                  "in the 2nd or 12th from it, nor conjunct. Classical 'isolation' yoga."),
        "cancellations": cancels,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Angarak Yoga — Mars + Rahu conjunction (fiery anger / accidents)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_angarak(chart) -> dict:
    p = chart.planets
    if p["Mars"].sign_index != p["Rahu"].sign_index:
        return {
            "present": False, "type": "Angarak Yoga", "severity": "none",
            "cause": "Mars and Rahu not in same sign.", "cancellations": [],
        }
    return {
        "present": True, "type": "Angarak Yoga", "severity": "partial",
        "cause": f"Mars conjunct Rahu in {p['Mars'].sign} (H{p['Mars'].house}). "
                 "Intensifies temper and impulsivity; channelled, gives extraordinary drive.",
        "cancellations": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Daridra Yoga — 11th lord in dusthana (poverty yoga)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_daridra(chart) -> dict:
    """11th lord placed in 6/8/12 from Lagna."""
    h11_sign = (chart.lagna.sign_index + 10) % 12
    h11_lord_name = SIGN_LORDS_MAP[h11_sign]
    h11_lord = chart.planets.get(h11_lord_name)
    if not h11_lord:
        return {"present": False, "type": "Daridra Yoga", "severity": "none",
                "cause": "—", "cancellations": []}
    if h11_lord.house not in {6, 8, 12}:
        return {"present": False, "type": "Daridra Yoga", "severity": "none",
                "cause": f"11th lord {h11_lord_name} not in a dusthana.",
                "cancellations": []}
    return {
        "present": True, "type": "Daridra Yoga", "severity": "partial",
        "cause": f"11th lord {h11_lord_name} placed in H{h11_lord.house} "
                 "(dusthana). Resource flows tested; persistence builds wealth slowly.",
        "cancellations": [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

_DETECTORS = [
    _detect_mangal,
    _detect_kaal_sarp,
    _detect_sade_sati,
    _detect_pitra,
    _detect_guru_chandal,
    _detect_grahan,
    _detect_shrapit,
    _detect_visha,
    _detect_kemadruma,
    _detect_angarak,
    _detect_daridra,
]


def detect_all(chart) -> list:
    """Run every dosha detector and return the list as Dosha records."""
    from math_engine.kundli.chart import Dosha

    out: list = []
    for fn in _DETECTORS:
        raw = fn(chart)
        out.append(Dosha(
            name=raw["type"],
            present=bool(raw.get("present")),
            severity=raw.get("severity", "none"),
            cause=raw.get("cause", ""),
            cancellations=raw.get("cancellations", []),
            remedy_summary="",  # filled by remedies.py
        ))
    return out
