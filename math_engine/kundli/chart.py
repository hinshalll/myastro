"""
math_engine/kundli/chart.py
===========================

The foundation: BirthData (input) → KundliChart (the single object every
downstream module — PDF builder, AI narrator, mobile app — consumes).

Design rule: this file wraps existing astro_calc.py functions into a clean,
typed object. It does NOT reimplement any math. Pieces not yet in astro_calc
(D16/D20/D24/D27/D40/D45, Yogini/Ashtottari dashas, secondary doshas, etc.)
are filled in by sibling modules and attached to the chart in compute_chart().

Zero Streamlit. Zero side effects. Pure compute.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime, time
from typing import Optional, Literal
from zoneinfo import ZoneInfo

import swisseph as swe

from math_engine.constants import (
    SIGNS,
    PLANETS,
    SIGN_LORDS_MAP,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
)
from math_engine.astro_calc import (
    local_to_julian_day,
    get_lagna_and_cusps,
    get_placidus_cusps,
    get_planet_longitude_and_speed,
    get_rahu_longitude,
    get_panchanga,
    nakshatra_info,
    get_baladi_avastha,
    get_kp_sub_lord,
    whole_sign_house,
    sign_index_from_lon,
    sign_name,
    format_dms,
    calculate_arudha_lagna,
    calculate_indu_lagna,
    get_lagna_lord_chain,
    get_functional_planets,
    get_chara_karakas,
)


Gender = Literal["M", "F"]
ChartStyle = Literal["north_indian", "south_indian", "east_indian"]
Language = Literal["en", "hi", "ta", "te", "mr", "bn", "gu"]


# ─────────────────────────────────────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class BirthData:
    """
    Everything required to compute an accurate kundli.

    Schema matches the existing AIS profile dict
    ({name, date, time, place, lat, lon, tz, gender, exact_time}) so
    `BirthData.from_profile(profile_dict)` works as a drop-in.

    Required:
        name, date, time, place, lat, lon, tz

    Optional:
        gender             — 'M' or 'F'. Required for Trimshamsha (D30)
                             interpretation and gender-specific remedies.
                             Defaults to 'M' (matches existing schema default).
        exact_time         — Whether the user is confident in their birth time.
                             When False, the BTR module is offered downstream.
        ayanamsha          — 'lahiri' (default) | 'raman' | 'krishnamurti' |
                             'yukteshwar' | 'fagan_bradley'.
        rectified_offset_minutes — Set by the BTR module after rectification.
                             Applied to birth time during chart computation.
    """
    name: str
    date: date
    time: time
    place: str
    lat: float
    lon: float
    tz: str

    gender: Gender = "M"
    exact_time: bool = False
    ayanamsha: str = "lahiri"
    rectified_offset_minutes: float = 0.0

    @property
    def needs_rectification(self) -> bool:
        """True when the user wasn't sure of their birth time and BTR hasn't run yet."""
        return not self.exact_time and self.rectified_offset_minutes == 0.0

    @classmethod
    def from_profile(cls, profile: dict) -> "BirthData":
        """
        Build a BirthData from the existing AIS profile dict.
        Tolerates string or native date/time.
        """
        d = profile["date"]
        t = profile["time"]
        if isinstance(d, str):
            d = date.fromisoformat(d)
        if isinstance(t, str):
            parts = t.split(":")
            if len(parts) == 2:
                t = time(int(parts[0]), int(parts[1]))
            else:
                t = time(int(parts[0]), int(parts[1]), int(parts[2]))
        g = profile.get("gender", "M")
        if g not in ("M", "F"):
            g = "M"
        return cls(
            name=profile["name"],
            date=d,
            time=t,
            place=profile["place"],
            lat=float(profile["lat"]),
            lon=float(profile["lon"]),
            tz=profile["tz"],
            gender=g,
            exact_time=bool(profile.get("exact_time", False)),
            ayanamsha=profile.get("ayanamsha", "lahiri"),
            rectified_offset_minutes=float(profile.get("rectified_offset_minutes", 0.0)),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Output building blocks
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlanetPosition:
    """Everything you need to render one row of the planetary positions table."""
    name: str
    longitude: float          # sidereal, 0-360
    longitude_dms: str        # "12°34'" within sign
    speed: float              # deg/day; negative = retrograde
    sign_index: int           # 0..11
    sign: str                 # "Aries"
    sign_lord: str            # "Mars"
    house: int                # 1..12 (whole sign)
    nakshatra: str
    nakshatra_lord: str
    pada: int                 # 1..4
    sub_lord: str             # KP sub-lord
    avastha: str              # Baladi
    is_retrograde: bool
    is_combust: bool
    combust_orb: Optional[float]
    dignity: Optional[str]    # "Exalted" | "Debilitated" | "Own Sign" | "Mooltrikona" | None
    is_benefic: bool          # natural
    is_malefic: bool


@dataclass
class HouseInfo:
    """One row of the bhava table — whole-sign + chalit + occupants."""
    number: int                   # 1..12
    sign_index: int
    sign: str
    sign_lord: str
    cusp_degree: float            # Placidus cusp (KP-style chalit)
    occupants: list[str] = field(default_factory=list)
    aspecting_planets: list[str] = field(default_factory=list)


@dataclass
class PanchangaInfo:
    tithi: str
    paksha: str           # "Shukla" | "Krishna"
    yoga: str
    karana: str
    weekday: str
    sunrise: Optional[time] = None
    sunset: Optional[time] = None
    moonrise: Optional[time] = None
    moonset: Optional[time] = None
    rahu_kaal: Optional[str] = None
    yamaganda: Optional[str] = None
    gulika_kaal: Optional[str] = None
    abhijit_muhurta: Optional[str] = None


@dataclass
class LagnaInfo:
    longitude: float
    sign_index: int
    sign: str
    degree_in_sign_dms: str
    lord: str
    nakshatra: str
    nakshatra_lord: str
    pada: int
    sub_lord: str
    lord_chain: str           # "Mars → H4 (Cancer [Debilitated]) → dispositor Moon in H3"
    arudha_house: int
    arudha_sign: str
    indu_sign: str


@dataclass
class FunctionalProfile:
    """Functional benefics/malefics/yogakarakas computed from lagna."""
    yogakarakas: list[str]
    benefics: list[str]
    malefics: list[str]
    neutrals: list[str]


@dataclass
class CharaKarakaProfile:
    """Jaimini Chara karakas — Atmakaraka, Amatyakaraka, etc."""
    atmakaraka: str
    atmakaraka_degree: float
    amatyakaraka: str
    amatyakaraka_degree: float
    chain: list[tuple[str, str, float]]  # [(planet, karaka_name, degree)]


# Place-holders for sibling-module outputs. Each is computed by its own file
# and attached to KundliChart by compute_chart(). They're declared here so the
# KundliChart shape is visible in one place.

@dataclass
class DivisionalChart:
    name: str                     # "D9 Navamsa"
    varga_number: int             # 9
    purpose: str                  # "Marriage, dharma"
    lagna_sign_index: int
    planet_signs: dict[str, int]  # {"Sun": 4, "Moon": 9, ...}


@dataclass
class DashaPeriod:
    lord: str
    start: datetime
    end: datetime
    level: int                    # 1 = MD, 2 = AD, 3 = PD, 4 = sookshma, 5 = prana
    children: list["DashaPeriod"] = field(default_factory=list)


@dataclass
class DashaTimeline:
    system: str                   # "Vimshottari" | "Yogini" | "Ashtottari" | "Char"
    periods: list[DashaPeriod]


@dataclass
class Yoga:
    name: str
    category: str                 # "Raja" | "Dhana" | "Pancha Mahapurusha" | ...
    planets_involved: list[str]
    description: str              # static text from interpretations library
    activation_dasha: Optional[str] = None  # "Activates during Jupiter MD"


@dataclass
class Dosha:
    name: str                     # "Mangal" | "Kaal Sarp - Anant" | ...
    present: bool
    severity: str                 # "none" | "partial" | "full" | "cancelled"
    cause: str
    cancellations: list[str] = field(default_factory=list)
    remedy_summary: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# The single output object
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class KundliChart:
    """
    The single object every downstream consumer reads.

    A PDF template, an AI narrator, the mobile app's renderer — all of them
    take a KundliChart and produce their output. Computed once, used many.
    """

    # — Identity & timing —
    birth_data: BirthData
    julian_day_ut: float
    datetime_local: datetime
    datetime_utc: datetime
    ayanamsha_used: str
    ayanamsha_value: float        # degrees

    # — Top-level chart —
    lagna: LagnaInfo
    panchanga: PanchangaInfo
    planets: dict[str, PlanetPosition]   # {"Sun": ..., ..., "Rahu": ..., "Ketu": ...}
    houses: dict[int, HouseInfo]         # {1: ..., ..., 12: ...}
    placidus_cusps: list[float]          # 12 cusps in order (KP / Bhava Chalit)

    # — Classical analyses —
    functional: FunctionalProfile
    chara_karakas: CharaKarakaProfile
    conjunctions: list[str]
    mutual_aspects: list[str]
    graha_yuddha: list[tuple[str, str, float]]  # (winner, loser, separation_deg)

    # — Built by sibling modules; attached in compute_chart() —
    nakshatra_profile: Optional[dict] = None         # nakshatra_profile.py
    divisional_charts: dict[int, DivisionalChart] = field(default_factory=dict)
    dashas: dict[str, DashaTimeline] = field(default_factory=dict)
    yogas: list[Yoga] = field(default_factory=list)
    doshas: list[Dosha] = field(default_factory=list)
    shadbala: Optional[dict] = None
    bhava_bala: Optional[dict] = None
    ashtakavarga: Optional[dict] = None              # both BAV and SAV
    sudarshan_chakra: Optional[dict] = None
    transit_forecast: Optional[dict] = None          # 12-month
    varshaphala: Optional[dict] = None               # current solar return
    remedies: Optional[dict] = None                  # mantras / gems / yantras / rudraksha / daan
    rectification: Optional[dict] = None             # BTR result
    western_appendix: Optional[dict] = None
    child_naming: Optional[dict] = None              # nakshatra pada syllables
    jaimini: Optional[dict] = None                   # Pada Lagnas + Upapada + Karakamsa
    kp_extras: Optional[dict] = None                 # cuspal + significators tables

    def to_dict(self) -> dict:
        """Serialise for templating / API responses. Handles datetimes."""
        def _enc(o):
            if isinstance(o, (datetime, date, time)):
                return o.isoformat()
            return o
        d = asdict(self)
        return _walk(d, _enc)


def _walk(obj, fn):
    if isinstance(obj, dict):
        return {k: _walk(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk(v, fn) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_walk(v, fn) for v in obj)
    return fn(obj)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

# Map of supported ayanamsha → swisseph constant
_AYANAMSHA_MAP = {
    "lahiri":         swe.SIDM_LAHIRI,
    "raman":          swe.SIDM_RAMAN,
    "krishnamurti":   swe.SIDM_KRISHNAMURTI,
    "yukteshwar":     swe.SIDM_YUKTESHWAR,
    "fagan_bradley":  swe.SIDM_FAGAN_BRADLEY,
}

# Planet → exaltation/debilitation/own/mooltrikona sign indices
# (mooltrikona ranges are degree-bounded; we keep them simple here.)
_DIGNITY_TABLE = {
    # name:       exalt_sign, debil_sign, own_signs,        mooltrikona_sign
    "Sun":       (0,          6,           [4],              4),   # Aries / Libra / Leo
    "Moon":      (1,          7,           [3],              1),   # Taurus / Scorpio / Cancer
    "Mars":      (9,          3,           [0, 7],           0),
    "Mercury":   (5,          11,          [2, 5],           5),
    "Jupiter":   (3,          9,           [8, 11],          8),
    "Venus":     (11,         5,           [1, 6],           6),
    "Saturn":    (6,          0,           [9, 10],          10),
    # Rahu & Ketu — debated. We use a common scheme; can be overridden in v2.
    "Rahu":      (1,          7,           [],               None),
    "Ketu":      (7,          1,           [],               None),
}

_COMBUST_ORB = {
    "Mercury": 12.0,
    "Venus":   8.0,
    "Mars":    17.0,
    "Jupiter": 11.0,
    "Saturn":  15.0,
    "Moon":    12.0,
}


def _classify_dignity(planet: str, sign_idx: int) -> Optional[str]:
    t = _DIGNITY_TABLE.get(planet)
    if not t:
        return None
    exalt, debil, own, mool = t
    if sign_idx == exalt:
        return "Exalted"
    if sign_idx == debil:
        return "Debilitated"
    if mool is not None and sign_idx == mool:
        return "Mooltrikona"
    if sign_idx in own:
        return "Own Sign"
    return None


def _set_ayanamsha(name: str) -> float:
    """Set swisseph ayanamsha mode and return its current value in degrees."""
    sid = _AYANAMSHA_MAP.get(name, swe.SIDM_LAHIRI)
    swe.set_sid_mode(sid)
    # ayanamsha_ut needs a JD; we read at J2000 for a stable reference value.
    return float(swe.get_ayanamsa_ut(2451545.0))


def _apply_rectification(bd: BirthData) -> tuple[date, time]:
    """Apply the rectified-offset (in minutes) to birth date+time."""
    if not bd.rectified_offset_minutes:
        return bd.date, bd.time
    base = datetime.combine(bd.date, bd.time.replace(second=bd.birth_seconds))
    shifted = base.fromtimestamp(
        base.timestamp() + bd.rectified_offset_minutes * 60.0
    )
    return shifted.date(), shifted.time()


def compute_chart(bd: BirthData) -> KundliChart:
    """
    Compute the full foundational chart from BirthData.

    This is the foundation pass — it produces a KundliChart populated with
    everything astro_calc.py already supports. Sibling modules then layer
    on divisional charts, dashas, yogas, doshas, shadbala, etc.
    """
    # Ayanamsha
    ayan_value = _set_ayanamsha(bd.ayanamsha)

    # Rectification
    eff_date, eff_time = _apply_rectification(bd)

    # Julian day
    jd_ut, dt_local, dt_utc = local_to_julian_day(eff_date, eff_time, bd.tz)

    # Planets (Sun..Saturn from PLANETS, Rahu+Ketu via true node)
    planet_data: dict[str, tuple[float, float]] = {}
    for pname, pid in PLANETS.items():
        plon, pspd = get_planet_longitude_and_speed(jd_ut, pid)
        planet_data[pname] = (plon, pspd)
    r_lon = get_rahu_longitude(jd_ut)
    k_lon = (r_lon + 180.0) % 360
    # Nodes don't have a meaningful retrograde speed in this convention; mark as 0
    planet_data_full = {**planet_data, "Rahu": (r_lon, 0.0), "Ketu": (k_lon, 0.0)}

    # Lagna + Placidus cusps
    lagna_lon, _ = get_lagna_and_cusps(jd_ut, bd.lat, bd.lon)
    placidus_cusps = list(get_placidus_cusps(jd_ut, bd.lat, bd.lon))[:12]
    ls = sign_index_from_lon(lagna_lon)

    # Panchanga
    sun_lon = planet_data["Sun"][0]
    moon_lon = planet_data["Moon"][0]
    panch_raw = get_panchanga(sun_lon, moon_lon, dt_local)
    tv = (moon_lon - sun_lon) % 360
    paksha = "Shukla" if tv < 180 else "Krishna"
    panchanga = PanchangaInfo(
        tithi=panch_raw["tithi"],
        paksha=paksha,
        yoga=panch_raw["yoga"],
        karana=panch_raw["karana"],
        weekday=panch_raw["weekday"],
    )

    # Planet positions table
    planets_out: dict[str, PlanetPosition] = {}
    for pname, (plon, pspd) in planet_data_full.items():
        sidx = sign_index_from_lon(plon)
        nak, nak_lord, pada = nakshatra_info(plon)
        avastha = get_baladi_avastha(plon)
        sub_lord = get_kp_sub_lord(plon)
        dignity = _classify_dignity(pname, sidx)
        # Combust: distance to Sun within orb (Sun itself skipped)
        is_combust = False
        combust_orb = None
        if pname != "Sun" and pname in _COMBUST_ORB:
            diff = abs(plon - sun_lon)
            diff = min(diff, 360 - diff)
            orb = _COMBUST_ORB[pname]
            # Mercury & Venus have different orbs when retrograde
            if pname == "Mercury" and pspd < 0:
                orb = 14.0
            elif pname == "Venus" and pspd < 0:
                orb = 16.0
            if diff <= orb:
                is_combust = True
                combust_orb = orb
        is_retro = pspd < 0 and pname not in ("Sun", "Moon", "Rahu", "Ketu")
        planets_out[pname] = PlanetPosition(
            name=pname,
            longitude=plon,
            longitude_dms=format_dms(plon % 30),
            speed=pspd,
            sign_index=sidx,
            sign=sign_name(sidx),
            sign_lord=SIGN_LORDS_MAP[sidx],
            house=whole_sign_house(ls, sidx),
            nakshatra=nak,
            nakshatra_lord=nak_lord,
            pada=pada,
            sub_lord=sub_lord,
            avastha=avastha,
            is_retrograde=is_retro,
            is_combust=is_combust,
            combust_orb=combust_orb,
            dignity=dignity,
            is_benefic=(pname in NATURAL_BENEFICS),
            is_malefic=(pname in NATURAL_MALEFICS),
        )

    # House table
    houses_out: dict[int, HouseInfo] = {}
    for h in range(1, 13):
        sidx = (ls + h - 1) % 12
        houses_out[h] = HouseInfo(
            number=h,
            sign_index=sidx,
            sign=sign_name(sidx),
            sign_lord=SIGN_LORDS_MAP[sidx],
            cusp_degree=placidus_cusps[h - 1] if h - 1 < len(placidus_cusps) else 0.0,
        )
    # Fill occupants
    for pname, pp in planets_out.items():
        houses_out[pp.house].occupants.append(pname)

    # Lagna info
    lagna_nak, lagna_nak_lord, lagna_pada = nakshatra_info(lagna_lon)
    arudha_house, arudha_sidx = calculate_arudha_lagna(ls, planet_data, r_lon, k_lon)
    indu_sidx = calculate_indu_lagna(ls, sign_index_from_lon(moon_lon))
    lagna = LagnaInfo(
        longitude=lagna_lon,
        sign_index=ls,
        sign=sign_name(ls),
        degree_in_sign_dms=format_dms(lagna_lon % 30),
        lord=SIGN_LORDS_MAP[ls],
        nakshatra=lagna_nak,
        nakshatra_lord=lagna_nak_lord,
        pada=lagna_pada,
        sub_lord=get_kp_sub_lord(lagna_lon),
        lord_chain=get_lagna_lord_chain(ls, planet_data, r_lon, k_lon),
        arudha_house=arudha_house,
        arudha_sign=sign_name(arudha_sidx),
        indu_sign=sign_name(indu_sidx),
    )

    # Functional planets
    bens, mals, yks, neu = get_functional_planets(ls)
    functional = FunctionalProfile(
        yogakarakas=yks, benefics=bens, malefics=mals, neutrals=neu,
    )

    # Chara karakas (existing helper returns: ak, ak_deg, amk, amk_deg,
    # karaka_chain = {karaka_name: (planet, degree)})
    ak, ak_deg, amk, amk_deg, chain_dict = get_chara_karakas(planet_data)
    chara = CharaKarakaProfile(
        atmakaraka=ak,
        atmakaraka_degree=ak_deg,
        amatyakaraka=amk,
        amatyakaraka_degree=amk_deg,
        chain=[(planet, name, deg) for name, (planet, deg) in (chain_dict or {}).items()],
    )

    # Conjunctions / mutual aspects / graha yuddha — reuse existing helpers
    from math_engine.astro_calc import (
        get_conjunctions as _conj,
        get_mutual_aspects as _mut,
        detect_graha_yuddha as _gy,
    )
    conjunctions = _conj(ls, planet_data, r_lon, k_lon)
    mutual = _mut(ls, planet_data, r_lon, k_lon)
    yuddha = _gy(jd_ut, planet_data)

    chart = KundliChart(
        birth_data=bd,
        julian_day_ut=jd_ut,
        datetime_local=dt_local,
        datetime_utc=dt_utc,
        ayanamsha_used=bd.ayanamsha,
        ayanamsha_value=ayan_value,
        lagna=lagna,
        panchanga=panchanga,
        planets=planets_out,
        houses=houses_out,
        placidus_cusps=placidus_cusps,
        functional=functional,
        chara_karakas=chara,
        conjunctions=conjunctions,
        mutual_aspects=mutual,
        graha_yuddha=yuddha,
    )

    # ── Layered enrichment (sibling modules) ────────────────────────────
    # Each enricher is import-guarded so the foundation file works on its own
    # while siblings are still being built.
    try:
        from math_engine.kundli import divisional as _div
        chart.divisional_charts = _div.compute_all(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import dashas as _das
        chart.dashas = _das.compute_all(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import yogas as _yog
        chart.yogas = _yog.detect(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import doshas as _dos
        chart.doshas = _dos.detect_all(chart)
    except ImportError:
        pass

    # Ashtakavarga must be computed BEFORE Shadbala — Bhava Bala uses SAV.
    try:
        from math_engine.kundli import ashtakavarga as _av
        chart.ashtakavarga = _av.compute(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import shadbala as _sb
        chart.shadbala, chart.bhava_bala = _sb.compute(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import nakshatra_profile as _np
        chart.nakshatra_profile = _np.build(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import sudarshan as _sd
        chart.sudarshan_chakra = _sd.build(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import transits as _tr
        chart.transit_forecast = _tr.twelve_month_forecast(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import remedies as _rem
        chart.remedies = _rem.recommend(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import western as _west
        chart.western_appendix = _west.build(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import naming as _nm
        chart.child_naming = _nm.suggest(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import jaimini as _ja
        chart.jaimini = _ja.build(chart)
    except ImportError:
        pass

    try:
        from math_engine.kundli import kp_extras as _kpx
        chart.kp_extras = _kpx.build(chart)
    except ImportError:
        pass

    # Varshaphala intentionally NOT auto-attached — it takes a `year` arg
    # and the PDF builder calls it explicitly with the current civil year.
    # Birth-time rectification is also explicit (needs user events).

    return chart
