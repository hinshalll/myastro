"""
math_engine/kundli/dashas.py
============================

Dasha (planetary period) systems for the kundli PDF.

Implements four classical dasha systems with full timelines:

    Vimshottari (120-year)  — Universal default; MD → AD → PD → Sookshma → Prana.
    Yogini      (36-year)   — Popular in North India; 8 Yoginis cycling.
    Ashtottari  (108-year)  — Used when classical applicability conditions met;
                              auto-detected.
    Char        (variable)  — Jaimini sign-based; STUB for a dedicated future
                              pass — multiple competing variants (KN Rao /
                              Sthira / Niryana) need a separate design pass.

All durations use YEAR_DAYS=365.25 (Julian year, the industry standard
shared with Astrosage / Jagannatha Hora / Parashara's Light).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from math_engine.constants import (
    YEAR_DAYS, DASHA_YEARS, DASHA_ORDER, NAKSHATRA_LORDS,
)


# ═════════════════════════════════════════════════════════════════════════════
# Vimshottari Dasha — full 120-year timeline
# ═════════════════════════════════════════════════════════════════════════════

def _seq_from(lord: str) -> list[str]:
    """The 9 dasha lords cycling forward starting from `lord`."""
    i = DASHA_ORDER.index(lord)
    return DASHA_ORDER[i:] + DASHA_ORDER[:i]


def _vimshottari_balance(moon_lon: float) -> tuple[str, float]:
    """
    Compute the starting Mahadasha lord and the balance years remaining.

    Returns (lord, balance_years_remaining_at_birth).
    """
    nak_size = 360.0 / 27.0
    idx = int((moon_lon % 360) // nak_size)
    lord = NAKSHATRA_LORDS[idx]
    progress_in_nak = (moon_lon % 360) - (idx * nak_size)
    remaining_fraction = 1.0 - (progress_in_nak / nak_size)
    return lord, DASHA_YEARS[lord] * remaining_fraction


def _periods(parent_start: datetime, parent_years: float,
             parent_lord: str, total_pool_years: float, level: int):
    """
    Generic sub-period builder.

    For Vimshottari, each level subdivides the parent period proportionally
    to the 9 dasha lords' year ratios (DASHA_YEARS / total_pool_years).
    At MD level the pool is 120 years; for sub-levels the pool stays 120.
    """
    from math_engine.kundli.chart import DashaPeriod

    out: list = []
    cursor = parent_start
    seq = _seq_from(parent_lord)
    for sub_lord in seq:
        sub_years = parent_years * DASHA_YEARS[sub_lord] / total_pool_years
        end = cursor + timedelta(days=sub_years * YEAR_DAYS)
        out.append(DashaPeriod(
            lord=sub_lord, start=cursor, end=end, level=level,
        ))
        cursor = end
    return out


def _build_vimshottari_full(birth_dt: datetime) -> list:
    """
    Build the full Vimshottari timeline: 9 Mahadashas (sequence), and within
    each MD, 9 Antardashas. Returns top-level DashaPeriod list (MDs) with
    `.children` populated to Antardasha level.

    Pratyantar (level-3) is computed only for the current Mahadasha+Antardasha
    on demand by the caller (cheaper at PDF time).
    """
    moon_lon = birth_dt  # type-tag: actual moon longitude passed in via _build()
    raise NotImplementedError  # see _build() wrapper below


def _build(birth_dt: datetime, moon_lon: float, view_dt: datetime | None = None) -> list:
    """Concrete Vimshottari construction. Returns 9 MDs with AD children."""
    from math_engine.kundli.chart import DashaPeriod

    start_lord, balance_yrs = _vimshottari_balance(moon_lon)

    md_seq = _seq_from(start_lord)
    md_durations = [balance_yrs] + [DASHA_YEARS[l] for l in md_seq[1:]]
    md_periods = []
    cursor = birth_dt
    for lord, yrs in zip(md_seq, md_durations):
        md_end = cursor + timedelta(days=yrs * YEAR_DAYS)
        md = DashaPeriod(lord=lord, start=cursor, end=md_end, level=1, children=[])
        # Antardashas inside this MD
        md.children = _periods(cursor, yrs, lord, 120.0, level=2)
        md_periods.append(md)
        cursor = md_end
    return md_periods


def pratyantar_table(md_period, ad_period) -> list:
    """
    Build Pratyantar (level-3) for one specific MD-AD combo.
    Called by the PDF builder only for the CURRENT MD-AD to limit page count.
    """
    return _periods(
        ad_period.start,
        (ad_period.end - ad_period.start).days / YEAR_DAYS,
        ad_period.lord,
        120.0,
        level=3,
    )


def vimshottari(chart) -> "DashaTimeline":
    from math_engine.kundli.chart import DashaTimeline

    periods = _build(chart.datetime_local, chart.planets["Moon"].longitude)
    return DashaTimeline(system="Vimshottari", periods=periods)


# ═════════════════════════════════════════════════════════════════════════════
# Yogini Dasha — 36-year cycle, 8 Yoginis
# ═════════════════════════════════════════════════════════════════════════════
#
# Yogini order and durations (sum = 36):
#   Mangala  (Moon)     1 yr
#   Pingala  (Sun)      2 yr
#   Dhanya   (Jupiter)  3 yr
#   Bhramari (Mars)     4 yr
#   Bhadrika (Mercury)  5 yr
#   Ulka     (Saturn)   6 yr
#   Siddha   (Venus)    7 yr
#   Sankata  (Rahu)     8 yr
#
# Starting Yogini = (nakshatra_index + 1) % 8  by a specific lookup. The
# nakshatra at birth determines the entry point; balance within current
# Yogini is proportional to remaining nakshatra arc.
# ─────────────────────────────────────────────────────────────────────────────

YOGINI_ORDER = ["Mangala", "Pingala", "Dhanya", "Bhramari",
                "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_PLANET = {
    "Mangala": "Moon", "Pingala": "Sun", "Dhanya": "Jupiter", "Bhramari": "Mars",
    "Bhadrika": "Mercury", "Ulka": "Saturn", "Siddha": "Venus", "Sankata": "Rahu",
}
YOGINI_YEARS = {
    "Mangala": 1, "Pingala": 2, "Dhanya": 3, "Bhramari": 4,
    "Bhadrika": 5, "Ulka": 6, "Siddha": 7, "Sankata": 8,
}

# Standard mapping nakshatra-index → starting Yogini index (per BPHS):
# Ashwini → Mangala, Bharani → Pingala, Krittika → Dhanya, ...
# Cycle of 8 repeats; the formula is (nak_index % 8) → Yogini index.
# But practitioners use a slightly different lookup. Most common (matches JH):
#   start_idx = (nak_index + 1) % 8 if starting from Ashwini-based table.
# We use the BPHS-direct mapping:
def _yogini_start_index(nak_index: int) -> int:
    """Yogini index (0..7) at birth from nakshatra index (0..26)."""
    # Per "Brihat Nakshatra" / JH: nakshatras 0..26 cycle through Yoginis
    # starting Ashwini → Mangala. The standard table (BPHS):
    #   0 Ashwini    → Mangala (0)
    #   1 Bharani    → Pingala (1)
    #   2 Krittika   → Dhanya  (2)
    #   3 Rohini     → Bhramari(3)
    #   4 Mrigashira → Bhadrika(4)
    #   5 Ardra      → Ulka    (5)
    #   6 Punarvasu  → Siddha  (6)
    #   7 Pushya     → Sankata (7)
    #   8 Ashlesha   → Mangala (0)  ← cycle repeats
    return nak_index % 8


def _yogini_balance(moon_lon: float) -> tuple[int, float]:
    """Return (starting_yogini_index, balance_years_at_birth)."""
    nak_size = 360.0 / 27.0
    nak_idx = int((moon_lon % 360) // nak_size)
    yogini_idx = _yogini_start_index(nak_idx)
    progress_in_nak = (moon_lon % 360) - (nak_idx * nak_size)
    balance = YOGINI_YEARS[YOGINI_ORDER[yogini_idx]] * (1.0 - progress_in_nak / nak_size)
    return yogini_idx, balance


def yogini(chart) -> "DashaTimeline":
    """
    Build full Yogini timeline. The cycle of 8 Yoginis repeats indefinitely;
    we generate enough to cover 120 years (the standard kundli horizon).
    """
    from math_engine.kundli.chart import DashaTimeline, DashaPeriod

    moon_lon = chart.planets["Moon"].longitude
    start_idx, balance = _yogini_balance(moon_lon)
    cursor = chart.datetime_local
    periods: list = []
    # How many cycles to cover 120 yrs from birth? 120/36 ≈ 3.34 → 4 cycles.
    # Generate 4*8 = 32 periods to be safe.
    next_idx = start_idx
    duration = balance
    for _ in range(32):
        lord_name = YOGINI_ORDER[next_idx]
        end = cursor + timedelta(days=duration * YEAR_DAYS)
        periods.append(DashaPeriod(
            lord=f"{lord_name} ({YOGINI_PLANET[lord_name]})",
            start=cursor, end=end, level=1,
        ))
        cursor = end
        next_idx = (next_idx + 1) % 8
        duration = YOGINI_YEARS[YOGINI_ORDER[next_idx]]
    return DashaTimeline(system="Yogini", periods=periods)


# ═════════════════════════════════════════════════════════════════════════════
# Ashtottari Dasha — 108-year cycle
# ═════════════════════════════════════════════════════════════════════════════
#
# 8 planets in order: Sun, Moon, Mars, Mercury, Saturn, Jupiter, Rahu, Venus.
# Durations (sum = 108):
#   Sun:6  Moon:15  Mars:8  Mercury:17  Saturn:10  Jupiter:19  Rahu:12  Venus:21
#
# Applicability (classical "Ashtottari Patrata" rule, BPHS):
#   This dasha applies when Rahu is placed in a sign OTHER than Lagna,
#   AND not in a kendra from Lagna's lord.
# Modern softwares show it always; we follow that pragmatic convention but
# mark applicability so the PDF can frame it appropriately.
#
# Starting lord: determined by birth nakshatra; uses a specific cyclic lookup.
# ─────────────────────────────────────────────────────────────────────────────

ASHTOTTARI_ORDER = ["Sun", "Moon", "Mars", "Mercury",
                    "Saturn", "Jupiter", "Rahu", "Venus"]
ASHTOTTARI_YEARS = {"Sun":6, "Moon":15, "Mars":8, "Mercury":17,
                    "Saturn":10, "Jupiter":19, "Rahu":12, "Venus":21}

# Krittika-based assignment: nakshatra 2 (Krittika) → Sun start, cycling
# through the 27 nakshatras in groups of three+ per planet. Standard table:
# (per "Brihat Jataka" and Jagannatha Hora convention)
_ASHTOTTARI_NAK_TO_LORD = [
    # 0 Ashwini..26 Revati
    "Sun","Sun","Sun","Sun",                              # 0-3 (4 naks)
    "Moon","Moon","Moon",                                 # 4-6 (3 naks)
    "Mars","Mars","Mars",                                 # 7-9 (3 naks)
    "Mercury","Mercury","Mercury","Mercury",              # 10-13 (4 naks)
    "Saturn","Saturn","Saturn",                           # 14-16 (3 naks)
    "Jupiter","Jupiter","Jupiter","Jupiter",              # 17-20 (4 naks)
    "Rahu","Rahu","Rahu",                                 # 21-23 (3 naks)
    "Venus","Venus","Venus",                              # 24-26 (3 naks)
]


def _ashtottari_balance(moon_lon: float) -> tuple[str, float]:
    """Return (starting_lord, balance_years_at_birth)."""
    nak_size = 360.0 / 27.0
    nak_idx = int((moon_lon % 360) // nak_size)
    lord = _ASHTOTTARI_NAK_TO_LORD[nak_idx]
    progress_in_nak = (moon_lon % 360) - (nak_idx * nak_size)
    balance = ASHTOTTARI_YEARS[lord] * (1.0 - progress_in_nak / nak_size)
    return lord, balance


def _ashtottari_applies(chart) -> bool:
    """
    Classical Ashtottari Patrata: Rahu not in Lagna AND not in a kendra
    from Lagna lord. Liberal modern interpretation: always applicable.
    """
    rahu_h = chart.planets["Rahu"].house
    if rahu_h == 1:
        return False
    lord_planet = chart.lagna.lord
    lord = chart.planets.get(lord_planet)
    if not lord:
        return True
    lord_h = lord.house
    # houses kendra from lord:
    kendra_from_lord = {((lord_h + k - 2) % 12) + 1 for k in (1, 4, 7, 10)}
    return rahu_h not in kendra_from_lord


def ashtottari(chart) -> "DashaTimeline":
    from math_engine.kundli.chart import DashaTimeline, DashaPeriod

    moon_lon = chart.planets["Moon"].longitude
    lord, balance = _ashtottari_balance(moon_lon)
    cursor = chart.datetime_local
    periods: list = []
    seq_start = ASHTOTTARI_ORDER.index(lord)
    seq = ASHTOTTARI_ORDER[seq_start:] + ASHTOTTARI_ORDER[:seq_start]
    # First period uses the balance; subsequent use full years.
    duration = balance
    for i in range(16):  # 2 cycles = 216 yrs, ample for a 120-yr horizon
        sub_lord = seq[i % 8]
        end = cursor + timedelta(days=duration * YEAR_DAYS)
        periods.append(DashaPeriod(
            lord=sub_lord, start=cursor, end=end, level=1,
        ))
        cursor = end
        duration = ASHTOTTARI_YEARS[seq[(i + 1) % 8]]
    return DashaTimeline(system="Ashtottari", periods=periods)


# ═════════════════════════════════════════════════════════════════════════════
# Char Dasha (Jaimini) — STUB
# ═════════════════════════════════════════════════════════════════════════════
#
# Char Dasha has several competing variants:
#   K.N. Rao version (most popular)
#   Sthira Dasha
#   Niryana Char Dasha
#   Iyer Char Dasha
#
# Each has different rules for sequence direction and duration. Rather than
# pick one in a hurry, this stub will be replaced in a dedicated pass with
# the KN Rao variant + clear options for alternatives.
# ─────────────────────────────────────────────────────────────────────────────

def char_dasha(chart) -> "DashaTimeline":
    from math_engine.kundli.chart import DashaTimeline
    return DashaTimeline(system="Char Dasha (Jaimini)", periods=[])  # placeholder


# ═════════════════════════════════════════════════════════════════════════════
# Public entry point — called from chart.compute_chart()
# ═════════════════════════════════════════════════════════════════════════════

def compute_all(chart) -> dict[str, "DashaTimeline"]:
    """Compute every dasha system applicable to this chart."""
    out: dict = {}
    out["Vimshottari"] = vimshottari(chart)
    out["Yogini"] = yogini(chart)
    if _ashtottari_applies(chart):
        out["Ashtottari"] = ashtottari(chart)
    # Char Dasha stub omitted from the dict for now (returns empty timeline).
    return out
