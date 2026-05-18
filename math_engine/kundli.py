"""
math_engine/kundli — Premium Kundli backend (all modules consolidated)
======================================================================

Zero Streamlit dependency. Pure compute. Single-file layout so the entire
kundli engine is one import away on both Streamlit and the future mobile app.

Public surface (re-exported at module level):
    BirthData           — input dataclass
    KundliChart         — fully-computed chart object
    compute_chart(bd)   — main entry point
    compute_varshaphala(chart, year=None)  — annual chart (called explicitly)
    rectify(chart, events, ...)            — birth-time rectification
    suggest_names(syllable, gender, count) — name bank lookup

Sections (use Ctrl-F):
    FOUNDATION · DIVISIONAL · NAKSHATRA PROFILE · DOSHAS · DASHAS ·
    ASHTAKAVARGA · SHADBALA · YOGAS · TRANSITS · REMEDIES · SUDARSHAN ·
    JAIMINI · KP EXTRAS · VARSHAPHALA · NAMING · WESTERN · RECTIFICATION
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime, time, timedelta
from typing import Optional, Literal
from zoneinfo import ZoneInfo

import swisseph as swe

from math_engine.constants import (
    SIGNS, PLANETS, OUTER_PLANETS, SIGN_LORDS_MAP,
    NATURAL_BENEFICS, NATURAL_MALEFICS,
    NAKSHATRAS, NAKSHATRA_LORDS, YEAR_DAYS, DASHA_YEARS, DASHA_ORDER,
    MOVABLE_SIGNS, FIXED_SIGNS,
)
from math_engine.astro_calc import (
    local_to_julian_day, get_lagna_and_cusps, get_placidus_cusps,
    get_planet_longitude_and_speed, get_rahu_longitude, get_panchanga,
    nakshatra_info, get_baladi_avastha, get_kp_sub_lord, whole_sign_house,
    sign_index_from_lon, sign_name, format_dms, calculate_arudha_lagna,
    calculate_indu_lagna, get_lagna_lord_chain, get_functional_planets,
    get_chara_karakas,
    get_conjunctions as _astro_conj,
    get_mutual_aspects as _astro_mut,
    detect_graha_yuddha as _astro_gy,
    detect_yogas as _legacy_detect_yogas,
    check_manglik_dosha, get_manglik_cancellation_verdict,
    calculate_sade_sati,
    calculate_ashtakavarga as _bav_calc,
    calculate_shadbala as _legacy_shadbala,
    get_kp_4step,
)

__all__ = [
    # Core API
    "BirthData", "KundliChart", "compute_chart",
    # Specialty computes (called explicitly — not auto-attached)
    "compute_varshaphala", "rectify", "suggest_names",
    # Audit + timeline helpers (called from UI / mobile)
    "yoga_audit", "sade_sati_timeline",
    # Universal chart rendering (proxies into pdf_engine for ergonomic single-import)
    "render_chart_svg",
]

Gender = Literal["M", "F"]
ChartStyle = Literal["north_indian", "south_indian", "east_indian"]
Language = Literal["en", "hi", "ta", "te", "mr", "bn", "gu"]


# ══════════════════════════════════════════════════════════════════════════
# FOUNDATION — BirthData, KundliChart, compute_chart
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class BirthData:
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
        return not self.exact_time and self.rectified_offset_minutes == 0.0

    @classmethod
    def from_profile(cls, profile: dict) -> "BirthData":
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
            date=d, time=t,
            place=profile["place"],
            lat=float(profile["lat"]),
            lon=float(profile["lon"]),
            tz=profile["tz"],
            gender=g,
            exact_time=bool(profile.get("exact_time", False)),
            ayanamsha=profile.get("ayanamsha", "lahiri"),
            rectified_offset_minutes=float(profile.get("rectified_offset_minutes", 0.0)),
        )


@dataclass
class PlanetPosition:
    name: str
    longitude: float
    longitude_dms: str
    speed: float
    sign_index: int
    sign: str
    sign_lord: str
    house: int
    nakshatra: str
    nakshatra_lord: str
    pada: int
    sub_lord: str
    avastha: str
    is_retrograde: bool
    is_combust: bool
    combust_orb: Optional[float]
    dignity: Optional[str]
    is_benefic: bool
    is_malefic: bool


@dataclass
class HouseInfo:
    number: int
    sign_index: int
    sign: str
    sign_lord: str
    cusp_degree: float
    occupants: list[str] = field(default_factory=list)
    aspecting_planets: list[str] = field(default_factory=list)


@dataclass
class PanchangaInfo:
    tithi: str
    paksha: str
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
    lord_chain: str
    arudha_house: int
    arudha_sign: str
    indu_sign: str


@dataclass
class FunctionalProfile:
    yogakarakas: list[str]
    benefics: list[str]
    malefics: list[str]
    neutrals: list[str]


@dataclass
class CharaKarakaProfile:
    atmakaraka: str
    atmakaraka_degree: float
    amatyakaraka: str
    amatyakaraka_degree: float
    chain: list[tuple[str, str, float]]


@dataclass
class DivisionalChart:
    name: str
    varga_number: int
    purpose: str
    lagna_sign_index: int
    planet_signs: dict[str, int]


@dataclass
class DashaPeriod:
    lord: str
    start: datetime
    end: datetime
    level: int
    children: list["DashaPeriod"] = field(default_factory=list)


@dataclass
class DashaTimeline:
    system: str
    periods: list[DashaPeriod]


@dataclass
class Yoga:
    name: str
    category: str
    planets_involved: list[str]
    description: str
    activation_dasha: Optional[str] = None


@dataclass
class Dosha:
    name: str
    present: bool
    severity: str
    cause: str
    cancellations: list[str] = field(default_factory=list)
    remedy_summary: str = ""


@dataclass
class KundliChart:
    birth_data: BirthData
    julian_day_ut: float
    datetime_local: datetime
    datetime_utc: datetime
    ayanamsha_used: str
    ayanamsha_value: float

    lagna: LagnaInfo
    panchanga: PanchangaInfo
    planets: dict[str, PlanetPosition]
    houses: dict[int, HouseInfo]
    placidus_cusps: list[float]

    functional: FunctionalProfile
    chara_karakas: CharaKarakaProfile
    conjunctions: list[str]
    mutual_aspects: list[str]
    graha_yuddha: list[tuple[str, str, float]]

    nakshatra_profile: Optional[dict] = None
    divisional_charts: dict[int, DivisionalChart] = field(default_factory=dict)
    dashas: dict[str, DashaTimeline] = field(default_factory=dict)
    yogas: list[Yoga] = field(default_factory=list)
    doshas: list[Dosha] = field(default_factory=list)
    shadbala: Optional[dict] = None
    bhava_bala: Optional[dict] = None
    ashtakavarga: Optional[dict] = None
    sudarshan_chakra: Optional[dict] = None
    transit_forecast: Optional[dict] = None
    varshaphala: Optional[dict] = None
    remedies: Optional[dict] = None
    rectification: Optional[dict] = None
    western_appendix: Optional[dict] = None
    child_naming: Optional[dict] = None
    jaimini: Optional[dict] = None
    kp_extras: Optional[dict] = None
    interpretations: Optional[dict] = None  # premium text payloads (kundli_text.py)

    def to_dict(self) -> dict:
        def _enc(o):
            if isinstance(o, (datetime, date, time)):
                return o.isoformat()
            return o
        return _walk(asdict(self), _enc)


def _walk(obj, fn):
    if isinstance(obj, dict):
        return {k: _walk(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk(v, fn) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_walk(v, fn) for v in obj)
    return fn(obj)


_AYANAMSHA_MAP = {
    "lahiri":         swe.SIDM_LAHIRI,
    "raman":          swe.SIDM_RAMAN,
    "krishnamurti":   swe.SIDM_KRISHNAMURTI,
    "yukteshwar":     swe.SIDM_YUKTESHWAR,
    "fagan_bradley":  swe.SIDM_FAGAN_BRADLEY,
}

_DIGNITY_TABLE = {
    "Sun":     (0,  6,  [4],     4),
    "Moon":    (1,  7,  [3],     1),
    "Mars":    (9,  3,  [0, 7],  0),
    "Mercury": (5, 11,  [2, 5],  5),
    "Jupiter": (3,  9,  [8, 11], 8),
    "Venus":   (11, 5,  [1, 6],  6),
    "Saturn":  (6,  0,  [9, 10], 10),
    "Rahu":    (1,  7,  [],      None),
    "Ketu":    (7,  1,  [],      None),
}

_COMBUST_ORB = {
    "Mercury": 12.0, "Venus": 8.0, "Mars": 17.0,
    "Jupiter": 11.0, "Saturn": 15.0, "Moon": 12.0,
}


def _classify_dignity(planet: str, sign_idx: int) -> Optional[str]:
    t = _DIGNITY_TABLE.get(planet)
    if not t:
        return None
    exalt, debil, own, mool = t
    if sign_idx == exalt:    return "Exalted"
    if sign_idx == debil:    return "Debilitated"
    if mool is not None and sign_idx == mool: return "Mooltrikona"
    if sign_idx in own:      return "Own Sign"
    return None


def _set_ayanamsha(name: str) -> float:
    sid = _AYANAMSHA_MAP.get(name, swe.SIDM_LAHIRI)
    swe.set_sid_mode(sid)
    return float(swe.get_ayanamsa_ut(2451545.0))


def _apply_rectification(bd: BirthData) -> tuple[date, time]:
    if not bd.rectified_offset_minutes:
        return bd.date, bd.time
    base = datetime.combine(bd.date, bd.time)
    shifted = datetime.fromtimestamp(
        base.timestamp() + bd.rectified_offset_minutes * 60.0
    )
    return shifted.date(), shifted.time()


def compute_chart(bd: BirthData) -> KundliChart:
    """Main entry point — build the full KundliChart from BirthData."""
    ayan_value = _set_ayanamsha(bd.ayanamsha)
    eff_date, eff_time = _apply_rectification(bd)
    jd_ut, dt_local, dt_utc = local_to_julian_day(eff_date, eff_time, bd.tz)

    planet_data: dict[str, tuple[float, float]] = {}
    for pname, pid in PLANETS.items():
        plon, pspd = get_planet_longitude_and_speed(jd_ut, pid)
        planet_data[pname] = (plon, pspd)
    r_lon = get_rahu_longitude(jd_ut)
    k_lon = (r_lon + 180.0) % 360
    # Outer planets — Uranus, Neptune, Pluto (modern additions)
    outer_data: dict[str, tuple[float, float]] = {}
    for pname, pid in OUTER_PLANETS.items():
        try:
            plon, pspd = get_planet_longitude_and_speed(jd_ut, pid)
            outer_data[pname] = (plon, pspd)
        except Exception:
            pass  # Pluto pre-1900 may fail; skip silently
    planet_data_full = {
        **planet_data,
        "Rahu": (r_lon, 0.0), "Ketu": (k_lon, 0.0),
        **outer_data,
    }

    lagna_lon, _ = get_lagna_and_cusps(jd_ut, bd.lat, bd.lon)
    placidus_cusps = list(get_placidus_cusps(jd_ut, bd.lat, bd.lon))[:12]
    ls = sign_index_from_lon(lagna_lon)

    sun_lon = planet_data["Sun"][0]
    moon_lon = planet_data["Moon"][0]
    panch_raw = get_panchanga(sun_lon, moon_lon, dt_local)
    tv = (moon_lon - sun_lon) % 360
    paksha = "Shukla" if tv < 180 else "Krishna"
    panchanga = PanchangaInfo(
        tithi=panch_raw["tithi"], paksha=paksha,
        yoga=panch_raw["yoga"], karana=panch_raw["karana"],
        weekday=panch_raw["weekday"],
    )

    planets_out: dict[str, PlanetPosition] = {}
    for pname, (plon, pspd) in planet_data_full.items():
        sidx = sign_index_from_lon(plon)
        nak, nak_lord, pada = nakshatra_info(plon)
        avastha = get_baladi_avastha(plon)
        sub_lord = get_kp_sub_lord(plon)
        dignity = _classify_dignity(pname, sidx)
        is_combust = False
        combust_orb = None
        if pname != "Sun" and pname in _COMBUST_ORB:
            diff = abs(plon - sun_lon)
            diff = min(diff, 360 - diff)
            orb = _COMBUST_ORB[pname]
            if pname == "Mercury" and pspd < 0: orb = 14.0
            elif pname == "Venus" and pspd < 0: orb = 16.0
            if diff <= orb:
                is_combust = True
                combust_orb = orb
        is_retro = pspd < 0 and pname not in ("Sun", "Moon", "Rahu", "Ketu")
        planets_out[pname] = PlanetPosition(
            name=pname, longitude=plon, longitude_dms=format_dms(plon % 30),
            speed=pspd, sign_index=sidx, sign=sign_name(sidx),
            sign_lord=SIGN_LORDS_MAP[sidx],
            house=whole_sign_house(ls, sidx),
            nakshatra=nak, nakshatra_lord=nak_lord, pada=pada,
            sub_lord=sub_lord, avastha=avastha,
            is_retrograde=is_retro, is_combust=is_combust,
            combust_orb=combust_orb, dignity=dignity,
            is_benefic=(pname in NATURAL_BENEFICS),
            is_malefic=(pname in NATURAL_MALEFICS),
        )

    houses_out: dict[int, HouseInfo] = {}
    for h in range(1, 13):
        sidx = (ls + h - 1) % 12
        houses_out[h] = HouseInfo(
            number=h, sign_index=sidx, sign=sign_name(sidx),
            sign_lord=SIGN_LORDS_MAP[sidx],
            cusp_degree=placidus_cusps[h - 1] if h - 1 < len(placidus_cusps) else 0.0,
        )
    for pname, pp in planets_out.items():
        houses_out[pp.house].occupants.append(pname)

    lagna_nak, lagna_nak_lord, lagna_pada = nakshatra_info(lagna_lon)
    arudha_house, arudha_sidx = calculate_arudha_lagna(ls, planet_data, r_lon, k_lon)
    indu_sidx = calculate_indu_lagna(ls, sign_index_from_lon(moon_lon))
    lagna = LagnaInfo(
        longitude=lagna_lon, sign_index=ls, sign=sign_name(ls),
        degree_in_sign_dms=format_dms(lagna_lon % 30),
        lord=SIGN_LORDS_MAP[ls],
        nakshatra=lagna_nak, nakshatra_lord=lagna_nak_lord, pada=lagna_pada,
        sub_lord=get_kp_sub_lord(lagna_lon),
        lord_chain=get_lagna_lord_chain(ls, planet_data, r_lon, k_lon),
        arudha_house=arudha_house, arudha_sign=sign_name(arudha_sidx),
        indu_sign=sign_name(indu_sidx),
    )

    bens, mals, yks, neu = get_functional_planets(ls)
    functional = FunctionalProfile(yogakarakas=yks, benefics=bens, malefics=mals, neutrals=neu)

    ak, ak_deg, amk, amk_deg, chain_dict = get_chara_karakas(planet_data)
    chara = CharaKarakaProfile(
        atmakaraka=ak, atmakaraka_degree=ak_deg,
        amatyakaraka=amk, amatyakaraka_degree=amk_deg,
        chain=[(planet, name, deg) for name, (planet, deg) in (chain_dict or {}).items()],
    )

    conjunctions = _astro_conj(ls, planet_data, r_lon, k_lon)
    mutual = _astro_mut(ls, planet_data, r_lon, k_lon)
    yuddha = _astro_gy(jd_ut, planet_data)

    chart = KundliChart(
        birth_data=bd, julian_day_ut=jd_ut,
        datetime_local=dt_local, datetime_utc=dt_utc,
        ayanamsha_used=bd.ayanamsha, ayanamsha_value=ayan_value,
        lagna=lagna, panchanga=panchanga,
        planets=planets_out, houses=houses_out,
        placidus_cusps=placidus_cusps,
        functional=functional, chara_karakas=chara,
        conjunctions=conjunctions, mutual_aspects=mutual,
        graha_yuddha=yuddha,
    )

    # ─── Layered enrichment — all in this same module ──────────────────
    try: chart.divisional_charts = _compute_divisional(chart)
    except Exception: pass
    try: chart.dashas = _compute_dashas(chart)
    except Exception: pass
    try: chart.yogas = _detect_yogas(chart)
    except Exception: pass
    try: chart.doshas = _detect_doshas(chart)
    except Exception: pass
    # Ashtakavarga must come BEFORE Shadbala (Bhava Bala uses SAV)
    try: chart.ashtakavarga = _compute_ashtakavarga(chart)
    except Exception: pass
    try: chart.shadbala, chart.bhava_bala = _compute_shadbala(chart)
    except Exception: pass
    try: chart.nakshatra_profile = _build_nakshatra_profile(chart)
    except Exception: pass
    try: chart.sudarshan_chakra = _build_sudarshan(chart)
    except Exception: pass
    try: chart.transit_forecast = _twelve_month_forecast(chart)
    except Exception: pass
    try: chart.remedies = _recommend_remedies(chart)
    except Exception: pass
    try: chart.western_appendix = _build_western(chart)
    except Exception: pass
    try: chart.child_naming = _build_naming(chart)
    except Exception: pass
    try: chart.jaimini = _build_jaimini(chart)
    except Exception: pass
    try: chart.kp_extras = _build_kp_extras(chart)
    except Exception: pass
    # Premium interpretation payloads (per-house, per-planet, life-domains,
    # Lal Kitab, year predictions, auspicious dates). Lives in a sibling
    # module to keep this file's size manageable.
    try:
        from math_engine.kundli_text import compute_interpretations
        chart.interpretations = compute_interpretations(chart)
    except Exception:
        pass
    return chart


# ══════════════════════════════════════════════════════════════════════════
# DIVISIONAL CHARTS — All 16 Shodashavarga
# ══════════════════════════════════════════════════════════════════════════

DUAL_SIGNS = {2, 5, 8, 11}


def _slot(lon: float, n_parts: int) -> int:
    deg_in_sign = lon % 30
    return min(int(deg_in_sign * n_parts / 30.0), n_parts - 1)


def d1_si(lon): return sign_index_from_lon(lon)


def d2_si(lon):
    s = sign_index_from_lon(lon)
    first_half = (lon % 30) < 15
    odd_sign = (s % 2 == 0)
    if odd_sign: return 4 if first_half else 3
    return 3 if first_half else 4


def d3_si(lon):
    s = sign_index_from_lon(lon)
    return (s + _slot(lon, 3) * 4) % 12


def d4_si(lon):
    s = sign_index_from_lon(lon)
    return (s + _slot(lon, 4) * 3) % 12


def d7_si(lon):
    s = sign_index_from_lon(lon)
    start = s if (s % 2 == 0) else (s + 6) % 12
    return (start + _slot(lon, 7)) % 12


def d9_si(lon):
    s = sign_index_from_lon(lon)
    slot = _slot(lon, 9)
    if s in MOVABLE_SIGNS: start = s
    elif s in FIXED_SIGNS: start = (s + 8) % 12
    else: start = (s + 4) % 12
    return (start + slot) % 12


def d10_si(lon):
    s = sign_index_from_lon(lon)
    start = s if (s % 2 == 0) else (s + 8) % 12
    return (start + _slot(lon, 10)) % 12


def d12_si(lon):
    s = sign_index_from_lon(lon)
    return (s + _slot(lon, 12)) % 12


def d16_si(lon):
    s = sign_index_from_lon(lon)
    if s in MOVABLE_SIGNS: start = 0
    elif s in FIXED_SIGNS: start = 4
    else: start = 8
    return (start + _slot(lon, 16)) % 12


def d20_si(lon):
    s = sign_index_from_lon(lon)
    if s in MOVABLE_SIGNS: start = 0
    elif s in FIXED_SIGNS: start = 8
    else: start = 4
    return (start + _slot(lon, 20)) % 12


def d24_si(lon):
    s = sign_index_from_lon(lon)
    start = 4 if (s % 2 == 0) else 3
    return (start + _slot(lon, 24)) % 12


def d27_si(lon):
    s = sign_index_from_lon(lon)
    if s in MOVABLE_SIGNS: start = s
    elif s in FIXED_SIGNS: start = (s + 8) % 12
    else: start = (s + 4) % 12
    return (start + _slot(lon, 27)) % 12


def d30_si(lon):
    s = sign_index_from_lon(lon)
    d = lon % 30
    if s % 2 == 0:
        if d < 5:  return 0
        if d < 10: return 10
        if d < 18: return 8
        if d < 25: return 2
        return 6
    else:
        if d < 5:  return 1
        if d < 12: return 5
        if d < 20: return 11
        if d < 25: return 9
        return 7


def d40_si(lon):
    s = sign_index_from_lon(lon)
    start = 0 if (s % 2 == 0) else 6
    return (start + _slot(lon, 40)) % 12


def d45_si(lon):
    s = sign_index_from_lon(lon)
    if s in MOVABLE_SIGNS: start = 0
    elif s in FIXED_SIGNS: start = 4
    else: start = 8
    return (start + _slot(lon, 45)) % 12


def d60_si(lon):
    """BPHS/JH: D60_sign = (natal_sign + part_number) % 12, part = 0..59."""
    s = sign_index_from_lon(lon)
    part = min(int((lon % 30) * 2), 59)
    return (s + part) % 12


VARGA_REGISTRY: list[tuple[int, str, str, callable]] = [
    (1,  "Lagna Chart (Rasi)", "Body, self, overall life",            d1_si),
    (2,  "Hora",              "Wealth and family money",               d2_si),
    (3,  "Drekkana",          "Siblings, courage, short journeys",     d3_si),
    (4,  "Chaturthamsha",     "Property, vehicles, mother's home",     d4_si),
    (7,  "Saptamsha",         "Children",                              d7_si),
    (9,  "Navamsha",          "Marriage and inner strength",           d9_si),
    (10, "Dashamsha",         "Career and profession",                 d10_si),
    (12, "Dvadashamsha",      "Parents and ancestry",                  d12_si),
    (16, "Shodashamsha",      "Vehicles and material comforts",        d16_si),
    (20, "Vimshamsha",        "Religious devotion and practices",      d20_si),
    (24, "Chaturvimshamsha",  "Education and learning",                d24_si),
    (27, "Saptavimshamsha",   "Strengths and weaknesses (Bhamsha)",    d27_si),
    (30, "Trimshamsha",       "Difficulties and obstacles",            d30_si),
    (40, "Khavedamsha",       "Maternal inheritance and effects",      d40_si),
    (45, "Akshavedamsha",     "Paternal inheritance and character",    d45_si),
    (60, "Shashtiamsha",      "Past actions (deepest varga)",          d60_si),
]

VIMSHOPAKA_SAPTA   = {1: 5, 2: 2, 3: 3, 7: 2.5, 9: 4.5, 12: 2, 30: 1}
VIMSHOPAKA_DASA    = {1: 3, 2: 1.5, 3: 1.5, 7: 1.5, 9: 1.5, 10: 1.5,
                      12: 1.5, 16: 1.5, 30: 1.5, 60: 5}
VIMSHOPAKA_SHODASA = {1: 3.5, 2: 1, 3: 1, 4: 0.5, 7: 0.5, 9: 3, 10: 0.5,
                      12: 0.5, 16: 2, 20: 0.5, 24: 0.5, 27: 0.5, 30: 1,
                      40: 0.5, 45: 0.5, 60: 4}


def _compute_divisional(chart) -> dict[int, DivisionalChart]:
    out: dict[int, DivisionalChart] = {}
    lagna_lon = chart.lagna.longitude
    for n, name, purpose, fn in VARGA_REGISTRY:
        planet_signs = {p: fn(pp.longitude) for p, pp in chart.planets.items()}
        out[n] = DivisionalChart(
            name=f"D{n} {name}", varga_number=n, purpose=purpose,
            lagna_sign_index=fn(lagna_lon), planet_signs=planet_signs,
        )
    return out


# ══════════════════════════════════════════════════════════════════════════
# NAKSHATRA PROFILE — Avakahada Chakra + 27-nakshatra attribute table
# ══════════════════════════════════════════════════════════════════════════

NAKSHATRA_DATA: dict[str, dict] = {
    "Ashwini":           {"deity":"Ashwini Kumaras (twin healers)","symbol":"Horse's head","gana":"Deva","yoni":("Horse","Male"),"nadi":"Adi","varna":"Vaishya","vashya":"Chatushpada","tatva":"Earth","gender":"Male","guna":"Rajas","syllables":["Chu","Che","Cho","La"]},
    "Bharani":           {"deity":"Yama (god of death/dharma)","symbol":"Yoni (vulva)","gana":"Manushya","yoni":("Elephant","Male"),"nadi":"Madhya","varna":"Mleccha","vashya":"Dwipada","tatva":"Earth","gender":"Female","guna":"Rajas","syllables":["Li","Lu","Le","Lo"]},
    "Krittika":          {"deity":"Agni (fire)","symbol":"Razor / flame","gana":"Rakshasa","yoni":("Sheep","Female"),"nadi":"Antya","varna":"Brahmin","vashya":"Chatushpada","tatva":"Earth","gender":"Female","guna":"Rajas","syllables":["A","I","U","E"]},
    "Rohini":            {"deity":"Brahma / Prajapati","symbol":"Ox cart / banyan tree","gana":"Manushya","yoni":("Serpent","Male"),"nadi":"Antya","varna":"Shudra","vashya":"Chatushpada","tatva":"Earth","gender":"Female","guna":"Rajas","syllables":["O","Va","Vi","Vu"]},
    "Mrigashira":        {"deity":"Soma / Chandra (Moon)","symbol":"Deer's head","gana":"Deva","yoni":("Serpent","Female"),"nadi":"Madhya","varna":"Sevaka","vashya":"Chatushpada","tatva":"Earth","gender":"Neutral","guna":"Tamas","syllables":["Ve","Vo","Ka","Ki"]},
    "Ardra":             {"deity":"Rudra (storm form of Shiva)","symbol":"Teardrop / diamond","gana":"Manushya","yoni":("Dog","Female"),"nadi":"Adi","varna":"Butcher","vashya":"Dwipada","tatva":"Water","gender":"Female","guna":"Tamas","syllables":["Ku","Kha","Nga","Chha"]},
    "Punarvasu":         {"deity":"Aditi (mother of gods)","symbol":"Bow & quiver","gana":"Deva","yoni":("Cat","Female"),"nadi":"Adi","varna":"Vaishya","vashya":"Dwipada","tatva":"Water","gender":"Male","guna":"Sattva","syllables":["Ke","Ko","Ha","Hi"]},
    "Pushya":            {"deity":"Brihaspati (Jupiter / teacher of gods)","symbol":"Cow's udder / lotus","gana":"Deva","yoni":("Sheep","Male"),"nadi":"Madhya","varna":"Kshatriya","vashya":"Jalachara","tatva":"Water","gender":"Male","guna":"Tamas","syllables":["Hu","He","Ho","Da"]},
    "Ashlesha":          {"deity":"Naga (serpents)","symbol":"Coiled serpent","gana":"Rakshasa","yoni":("Cat","Male"),"nadi":"Antya","varna":"Mleccha","vashya":"Keeta","tatva":"Water","gender":"Female","guna":"Sattva","syllables":["Di","Du","De","Do"]},
    "Magha":             {"deity":"Pitris (ancestors)","symbol":"Royal throne","gana":"Rakshasa","yoni":("Rat","Male"),"nadi":"Antya","varna":"Shudra","vashya":"Chatushpada","tatva":"Fire","gender":"Female","guna":"Tamas","syllables":["Ma","Mi","Mu","Me"]},
    "Purva Phalguni":    {"deity":"Bhaga (delight, luxury)","symbol":"Front legs of a bed / hammock","gana":"Manushya","yoni":("Rat","Female"),"nadi":"Madhya","varna":"Brahmin","vashya":"Dwipada","tatva":"Fire","gender":"Female","guna":"Rajas","syllables":["Mo","Ta","Ti","Tu"]},
    "Uttara Phalguni":   {"deity":"Aryaman (patronage, contracts)","symbol":"Back legs of a bed / four legs","gana":"Manushya","yoni":("Cow","Male"),"nadi":"Adi","varna":"Kshatriya","vashya":"Dwipada","tatva":"Fire","gender":"Female","guna":"Rajas","syllables":["Te","To","Pa","Pi"]},
    "Hasta":             {"deity":"Savitar (Sun as inspirer)","symbol":"Open hand / clenched fist","gana":"Deva","yoni":("Buffalo","Female"),"nadi":"Adi","varna":"Vaishya","vashya":"Dwipada","tatva":"Fire","gender":"Male","guna":"Rajas","syllables":["Pu","Sha","Na","Tha"]},
    "Chitra":            {"deity":"Vishvakarma (celestial architect)","symbol":"Bright jewel / pearl","gana":"Rakshasa","yoni":("Tiger","Female"),"nadi":"Madhya","varna":"Sevaka","vashya":"Keeta","tatva":"Fire","gender":"Female","guna":"Tamas","syllables":["Pe","Po","Ra","Ri"]},
    "Swati":             {"deity":"Vayu (wind)","symbol":"Young plant blown by wind / coral","gana":"Deva","yoni":("Buffalo","Male"),"nadi":"Antya","varna":"Butcher","vashya":"Dwipada","tatva":"Fire","gender":"Female","guna":"Tamas","syllables":["Ru","Re","Ro","Ta"]},
    "Vishakha":          {"deity":"Indra & Agni","symbol":"Triumphal archway / potter's wheel","gana":"Rakshasa","yoni":("Tiger","Male"),"nadi":"Antya","varna":"Mleccha","vashya":"Keeta","tatva":"Fire","gender":"Female","guna":"Sattva","syllables":["Ti","Tu","Te","To"]},
    "Anuradha":          {"deity":"Mitra (friendship)","symbol":"Lotus / triumphal archway","gana":"Deva","yoni":("Deer","Female"),"nadi":"Madhya","varna":"Shudra","vashya":"Keeta","tatva":"Fire","gender":"Male","guna":"Tamas","syllables":["Na","Ni","Nu","Ne"]},
    "Jyeshtha":          {"deity":"Indra (king of gods)","symbol":"Circular amulet / umbrella","gana":"Rakshasa","yoni":("Deer","Male"),"nadi":"Adi","varna":"Sevaka","vashya":"Keeta","tatva":"Air","gender":"Female","guna":"Sattva","syllables":["No","Ya","Yi","Yu"]},
    "Mula":              {"deity":"Nirriti (goddess of dissolution)","symbol":"Bundle of roots / lion's tail","gana":"Rakshasa","yoni":("Dog","Male"),"nadi":"Adi","varna":"Butcher","vashya":"Chatushpada","tatva":"Air","gender":"Neutral","guna":"Tamas","syllables":["Ye","Yo","Bha","Bhi"]},
    "Purva Ashadha":     {"deity":"Apah (cosmic waters)","symbol":"Fan / winnowing basket","gana":"Manushya","yoni":("Monkey","Male"),"nadi":"Madhya","varna":"Brahmin","vashya":"Dwipada","tatva":"Air","gender":"Female","guna":"Rajas","syllables":["Bhu","Dha","Pha","Dha"]},
    "Uttara Ashadha":    {"deity":"Vishvedevas (10 universal gods)","symbol":"Elephant's tusk / planks of a bed","gana":"Manushya","yoni":("Mongoose","Male"),"nadi":"Antya","varna":"Kshatriya","vashya":"Chatushpada","tatva":"Air","gender":"Female","guna":"Sattva","syllables":["Bhe","Bho","Ja","Ji"]},
    "Shravana":          {"deity":"Vishnu","symbol":"Ear / three footprints","gana":"Deva","yoni":("Monkey","Female"),"nadi":"Antya","varna":"Mleccha","vashya":"Chatushpada","tatva":"Air","gender":"Male","guna":"Rajas","syllables":["Ju","Je","Jo","Gha"]},
    "Dhanishta":         {"deity":"Vasus (8 elemental gods)","symbol":"Drum / flute","gana":"Rakshasa","yoni":("Lion","Female"),"nadi":"Madhya","varna":"Sevaka","vashya":"Chatushpada","tatva":"Ether","gender":"Female","guna":"Tamas","syllables":["Ga","Gi","Gu","Ge"]},
    "Shatabhisha":       {"deity":"Varuna (cosmic waters / law)","symbol":"Empty circle / 100 healers","gana":"Rakshasa","yoni":("Horse","Female"),"nadi":"Adi","varna":"Butcher","vashya":"Dwipada","tatva":"Ether","gender":"Neutral","guna":"Tamas","syllables":["Go","Sa","Si","Su"]},
    "Purva Bhadrapada":  {"deity":"Aja Ekapada (one-footed goat / dragon)","symbol":"Front legs of a funeral cot / two-faced man","gana":"Manushya","yoni":("Lion","Male"),"nadi":"Adi","varna":"Brahmin","vashya":"Dwipada","tatva":"Ether","gender":"Male","guna":"Sattva","syllables":["Se","So","Da","Di"]},
    "Uttara Bhadrapada": {"deity":"Ahir Budhnya (serpent of the deep)","symbol":"Back legs of a funeral cot / two-headed man","gana":"Manushya","yoni":("Cow","Female"),"nadi":"Madhya","varna":"Kshatriya","vashya":"Jalachara","tatva":"Ether","gender":"Male","guna":"Tamas","syllables":["Du","Tha","Jha","Yna"]},
    "Revati":            {"deity":"Pushan (nourisher; god of travel)","symbol":"Pair of fish / drum","gana":"Deva","yoni":("Elephant","Female"),"nadi":"Antya","varna":"Shudra","vashya":"Jalachara","tatva":"Ether","gender":"Female","guna":"Sattva","syllables":["De","Do","Cha","Chi"]},
}

_WEEKDAY_DEITY = {
    "Monday":"Chandra (Moon)","Tuesday":"Mangal (Mars)","Wednesday":"Budha (Mercury)",
    "Thursday":"Brihaspati (Jupiter)","Friday":"Shukra (Venus)","Saturday":"Shani (Saturn)",
    "Sunday":"Surya (Sun)",
}

_SIGN_TATVA = {0:"Fire",3:"Water",6:"Air",9:"Earth",1:"Earth",4:"Fire",
               7:"Water",10:"Air",2:"Air",5:"Earth",8:"Fire",11:"Water"}


def get_nakshatra_attributes(nakshatra: str) -> dict:
    return NAKSHATRA_DATA.get(nakshatra, {})


def get_pada_syllables(nakshatra: str, pada: int) -> str:
    attrs = NAKSHATRA_DATA.get(nakshatra, {})
    syll = attrs.get("syllables", [])
    if not syll or not 1 <= pada <= 4:
        return ""
    return syll[pada - 1]


def _build_nakshatra_profile(chart) -> dict:
    moon = chart.planets["Moon"]
    nak, pada = moon.nakshatra, moon.pada
    attrs = get_nakshatra_attributes(nak)
    syll = get_pada_syllables(nak, pada)
    tatva = attrs.get("tatva") or _SIGN_TATVA.get(moon.sign_index, "—")
    avakahada = [
        ("Janma Naam (Name)", chart.birth_data.name),
        ("Janma Tithi", chart.panchanga.tithi),
        ("Janma Vara (Weekday)", chart.panchanga.weekday),
        ("Vara Devta", _WEEKDAY_DEITY.get(chart.panchanga.weekday, "—")),
        ("Janma Nakshatra", f"{nak} (Pada {pada})"),
        ("Nakshatra Lord", moon.nakshatra_lord),
        ("Nakshatra Devta", attrs.get("deity", "—")),
        ("Janma Rashi (Moon Sign)", moon.sign),
        ("Rashi Lord", moon.sign_lord),
        ("Lagna (Ascendant)", chart.lagna.sign),
        ("Lagna Lord", chart.lagna.lord),
        ("Yoga", chart.panchanga.yoga),
        ("Karana", chart.panchanga.karana),
        ("Paksha", chart.panchanga.paksha),
        ("Gana", attrs.get("gana", "—")),
        ("Yoni", "{} ({})".format(*attrs["yoni"]) if attrs.get("yoni") else "—"),
        ("Nadi", attrs.get("nadi", "—")),
        ("Varna", attrs.get("varna", "—")),
        ("Vashya", attrs.get("vashya", "—")),
        ("Tatva (Element)", tatva),
        ("Gender (Psychological)", attrs.get("gender", "—")),
        ("Guna", attrs.get("guna", "—")),
        ("Naam-akshar (Name letter)", syll),
    ]
    return {
        "birth_nakshatra": nak, "pada": pada,
        "nakshatra_lord": moon.nakshatra_lord,
        "deity": attrs.get("deity"), "symbol": attrs.get("symbol"),
        "gana": attrs.get("gana"), "yoni": attrs.get("yoni"),
        "nadi": attrs.get("nadi"), "varna": attrs.get("varna"),
        "vashya": attrs.get("vashya"), "tatva": tatva,
        "gender": attrs.get("gender"), "guna": attrs.get("guna"),
        "pada_syllables": attrs.get("syllables", []),
        "naam_akshar": syll,
        "avakahada_chakra": avakahada,
        "lagna_nakshatra": chart.lagna.nakshatra,
        "lagna_nakshatra_lord": chart.lagna.nakshatra_lord,
    }


# ══════════════════════════════════════════════════════════════════════════
# DOSHAS — Mangal, Kaal Sarp (12), Sade Sati, Pitra, Guru Chandal, etc.
# ══════════════════════════════════════════════════════════════════════════

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
    rahu_h = chart.planets["Rahu"].house
    ketu_h = chart.planets["Ketu"].house
    classical = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    p_houses = {p: chart.planets[p].house for p in classical}

    def arc_houses(start, end):
        houses = []
        h = (start % 12) + 1
        while h != end:
            houses.append(h)
            h = (h % 12) + 1
        return set(houses)

    arc_rk = arc_houses(rahu_h, ketu_h)
    arc_kr = arc_houses(ketu_h, rahu_h)
    in_rk = sum(1 for p in classical if p_houses[p] in arc_rk)
    in_kr = sum(1 for p in classical if p_houses[p] in arc_kr)
    full_one_side = (in_rk == 7) or (in_kr == 7)
    partial_one_side = (in_rk >= 6) or (in_kr >= 6)

    if not partial_one_side:
        return {"present": False, "type": None, "severity": "none",
                "cause": "Planets distributed on both sides of the Rahu–Ketu axis (Kaal Sarp absent).",
                "cancellations": []}

    type_id, (type_name, theme) = rahu_h, KAAL_SARP_NAMES[rahu_h]
    severity = "full" if full_one_side else "partial"
    cancels = []
    for p in classical:
        if p_houses[p] in {rahu_h, ketu_h}:
            cancels.append(f"{p} conjunct {'Rahu' if p_houses[p]==rahu_h else 'Ketu'} — softens")
    jh = p_houses["Jupiter"]
    if rahu_h in {((jh + d - 2) % 12) + 1 for d in (5, 7, 9)}:
        cancels.append("Jupiter aspects Rahu's house — softens")
    lord_planet = chart.lagna.lord
    lord_house = chart.planets[lord_planet].house if lord_planet in chart.planets else None
    if lord_house and lord_house in {1, 4, 5, 7, 9, 10}:
        cancels.append(f"Lagna lord {lord_planet} well-placed in H{lord_house}")
    return {
        "present": True, "type": f"{type_name} Kaal Sarp", "type_id": type_id,
        "severity": severity, "rahu_house": rahu_h, "ketu_house": ketu_h,
        "theme": theme,
        "cause": (f"Rahu in H{rahu_h}, Ketu in H{ketu_h}. "
                  f"All {in_rk if in_rk>=6 else in_kr} of 7 classical planets fall "
                  f"{'between' if in_rk>=6 else 'opposite'} the Rahu–Ketu axis."),
        "cancellations": cancels,
    }


def _detect_mangal(chart) -> dict:
    moon_sidx = chart.planets["Moon"].sign_index
    mars_sidx = chart.planets["Mars"].sign_index
    raw = check_manglik_dosha(chart.lagna.sign_index, moon_sidx, mars_sidx)
    present = bool(raw) and "no" not in raw.lower()
    mars_h = chart.planets["Mars"].house
    severity = "full" if mars_h in {7, 8} else ("partial" if present else "none")
    cancels = []
    if present:
        if chart.planets["Mars"].sign in ("Aries","Scorpio","Capricorn"):
            cancels.append("Mars in own/exalted sign — significantly mitigates")
        if chart.planets["Jupiter"].house in {1,4,7,10}:
            cancels.append("Jupiter in a kendra — mitigates Mangal Dosha")
        jh = chart.planets["Jupiter"].house
        if mars_h in {((jh + d - 2) % 12) + 1 for d in (5, 7, 9)}:
            cancels.append("Jupiter aspects Mars — mitigates")
    return {"present": present, "type": "Mangal Dosha (Kuja Dosha)",
            "severity": severity,
            "cause": raw or "Mars not in 1/2/4/7/8/12 from Lagna, Moon, or Venus.",
            "cancellations": cancels}


def _detect_sade_sati(chart) -> dict:
    moon_sidx = chart.planets["Moon"].sign_index
    raw = calculate_sade_sati(moon_sidx)
    return {"present": True if raw and "not" not in raw.lower() else False,
            "type": "Sade Sati", "severity": "varies", "cause": raw,
            "cancellations": [],
            "note": "Refer to the 12-month transit forecast page for the active window."}


def _detect_pitra(chart) -> dict:
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
    if h9_lord and h9_lord.house in {6,8,12}:
        indicators.append(f"9th lord {h9_lord_name} in dusthana (H{h9_lord.house})")
    if h9_lord and h9_lord.house in (p["Rahu"].house, p["Ketu"].house):
        indicators.append(f"9th lord {h9_lord_name} conjunct Rahu/Ketu")
    if p["Sun"].house == 9 and p["Saturn"].house == 9:
        indicators.append("Sun afflicted by Saturn in 9th house")
    present = len(indicators) >= 1
    severity = "full" if len(indicators) >= 2 else ("partial" if present else "none")
    return {"present": present, "type": "Pitra Dosha", "severity": severity,
            "cause": "; ".join(indicators) if indicators else "9th house and Sun are unafflicted.",
            "cancellations": []}


def _detect_guru_chandal(chart) -> dict:
    p = chart.planets
    same_as_rahu = (p["Jupiter"].house == p["Rahu"].house)
    same_as_ketu = (p["Jupiter"].house == p["Ketu"].house)
    if not (same_as_rahu or same_as_ketu):
        return {"present": False, "type": "Guru Chandal Dosha", "severity": "none",
                "cause": "Jupiter is not conjunct Rahu or Ketu.", "cancellations": []}
    node = "Rahu" if same_as_rahu else "Ketu"
    diff = abs(p["Jupiter"].longitude - p[node].longitude)
    diff = min(diff, 360 - diff)
    tight = diff <= 8.0
    return {"present": True, "type": "Guru Chandal Dosha",
            "severity": "full" if tight else "partial",
            "cause": (f"Jupiter conjunct {node} in H{p['Jupiter'].house} "
                      f"({diff:.1f}° apart). Distorts judgment, faith, and the teacher–"
                      f"student relationship until consciously navigated."),
            "cancellations": []}


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
        return {"present": False, "type": "Grahan Dosha", "severity": "none",
                "cause": "No eclipse axis on Sun or Moon.", "cancellations": []}
    parts, severity = [], "partial"
    for kind, lum, node, h, d in findings:
        parts.append(f"{kind} — {lum} conjunct {node} in H{h} ({d:.1f}°)")
        if d <= 8.0: severity = "full"
    return {"present": True, "type": "Grahan Dosha", "severity": severity,
            "cause": "; ".join(parts), "cancellations": []}


def _detect_shrapit(chart) -> dict:
    p = chart.planets
    findings = []
    if p["Saturn"].house == p["Rahu"].house: findings.append(("Rahu", p["Saturn"].house))
    if p["Saturn"].house == p["Ketu"].house: findings.append(("Ketu", p["Saturn"].house))
    if not findings:
        return {"present": False, "type": "Shrapit Dosha", "severity": "none",
                "cause": "Saturn not conjunct Rahu or Ketu.", "cancellations": []}
    parts = [f"Saturn conjunct {n} in H{h}" for n, h in findings]
    return {"present": True, "type": "Shrapit Dosha", "severity": "partial",
            "cause": "; ".join(parts) + ". Carries karmic-curse signature; "
                     "ancestral propitiation traditionally indicated.",
            "cancellations": []}


def _detect_visha(chart) -> dict:
    p = chart.planets
    if p["Moon"].sign_index != p["Saturn"].sign_index:
        return {"present": False, "type": "Visha Yoga", "severity": "none",
                "cause": "Moon and Saturn not in same sign.", "cancellations": []}
    return {"present": True, "type": "Visha Yoga", "severity": "partial",
            "cause": f"Moon and Saturn both in {p['Moon'].sign}. "
                     "Emotional heaviness, recurring melancholy; deep psychological work "
                     "produces wisdom in maturity.",
            "cancellations": []}


def _detect_kemadruma(chart) -> dict:
    moon_h = chart.planets["Moon"].house
    moon_sidx = chart.planets["Moon"].sign_index
    second_from_moon = (moon_sidx + 1) % 12
    twelfth_from_moon = (moon_sidx + 11) % 12
    others = [n for n in chart.planets if n not in ("Moon","Rahu","Ketu")]
    planet_signs_local = {n: chart.planets[n].sign_index for n in others}
    in_2nd  = any(planet_signs_local[n] == second_from_moon  for n in others)
    in_12th = any(planet_signs_local[n] == twelfth_from_moon for n in others)
    conjoined = any(planet_signs_local[n] == moon_sidx for n in others)
    if in_2nd or in_12th or conjoined:
        return {"present": False, "type": "Kemadruma Yoga", "severity": "none",
                "cause": "Moon flanked or conjoined by other planets — Kemadruma cancelled.",
                "cancellations": []}
    cancels = []
    if chart.planets["Moon"].house in {1,4,7,10}:
        cancels.append("Moon in a kendra — Kemadruma considered cancelled (BPHS)")
    if any(chart.planets[n].house in {1,4,7,10}
           for n in ("Jupiter","Venus","Mercury")):
        cancels.append("Benefic in kendra — Kemadruma considered cancelled")
    return {"present": True, "type": "Kemadruma Yoga",
            "severity": "cancelled" if cancels else "partial",
            "cause": (f"Moon in H{moon_h} ({chart.planets['Moon'].sign}) with no planet "
                      "in the 2nd or 12th from it, nor conjunct. Classical 'isolation' yoga."),
            "cancellations": cancels}


def _detect_angarak(chart) -> dict:
    p = chart.planets
    if p["Mars"].sign_index != p["Rahu"].sign_index:
        return {"present": False, "type": "Angarak Yoga", "severity": "none",
                "cause": "Mars and Rahu not in same sign.", "cancellations": []}
    return {"present": True, "type": "Angarak Yoga", "severity": "partial",
            "cause": f"Mars conjunct Rahu in {p['Mars'].sign} (H{p['Mars'].house}). "
                     "Intensifies temper and impulsivity; channelled, gives extraordinary drive.",
            "cancellations": []}


def _detect_daridra(chart) -> dict:
    h11_sign = (chart.lagna.sign_index + 10) % 12
    h11_lord_name = SIGN_LORDS_MAP[h11_sign]
    h11_lord = chart.planets.get(h11_lord_name)
    if not h11_lord:
        return {"present": False, "type": "Daridra Yoga", "severity": "none",
                "cause": "—", "cancellations": []}
    if h11_lord.house not in {6,8,12}:
        return {"present": False, "type": "Daridra Yoga", "severity": "none",
                "cause": f"11th lord {h11_lord_name} not in a dusthana.",
                "cancellations": []}
    return {"present": True, "type": "Daridra Yoga", "severity": "partial",
            "cause": f"11th lord {h11_lord_name} placed in H{h11_lord.house} "
                     "(dusthana). Resource flows tested; persistence builds wealth slowly.",
            "cancellations": []}


_DOSHA_DETECTORS = [
    _detect_mangal, _detect_kaal_sarp, _detect_sade_sati, _detect_pitra,
    _detect_guru_chandal, _detect_grahan, _detect_shrapit, _detect_visha,
    _detect_kemadruma, _detect_angarak, _detect_daridra,
]


def _detect_doshas(chart) -> list:
    out: list = []
    for fn in _DOSHA_DETECTORS:
        raw = fn(chart)
        out.append(Dosha(
            name=raw["type"], present=bool(raw.get("present")),
            severity=raw.get("severity", "none"),
            cause=raw.get("cause", ""),
            cancellations=raw.get("cancellations", []),
            remedy_summary="",
        ))
    return out


# ══════════════════════════════════════════════════════════════════════════
# DASHAS — Vimshottari, Yogini, Ashtottari, Char (stub)
# ══════════════════════════════════════════════════════════════════════════

def _seq_from(lord: str) -> list[str]:
    i = DASHA_ORDER.index(lord)
    return DASHA_ORDER[i:] + DASHA_ORDER[:i]


def _vimshottari_balance(moon_lon: float) -> tuple[str, float]:
    nak_size = 360.0 / 27.0
    idx = int((moon_lon % 360) // nak_size)
    lord = NAKSHATRA_LORDS[idx]
    progress_in_nak = (moon_lon % 360) - (idx * nak_size)
    remaining_fraction = 1.0 - (progress_in_nak / nak_size)
    return lord, DASHA_YEARS[lord] * remaining_fraction


def _periods(parent_start, parent_years, parent_lord, total_pool_years, level):
    out: list = []
    cursor = parent_start
    seq = _seq_from(parent_lord)
    for sub_lord in seq:
        sub_years = parent_years * DASHA_YEARS[sub_lord] / total_pool_years
        end = cursor + timedelta(days=sub_years * YEAR_DAYS)
        out.append(DashaPeriod(lord=sub_lord, start=cursor, end=end, level=level))
        cursor = end
    return out


def _build(birth_dt: datetime, moon_lon: float, view_dt: datetime | None = None) -> list:
    """Concrete Vimshottari construction. Returns 9 MDs with AD children."""
    start_lord, balance_yrs = _vimshottari_balance(moon_lon)
    md_seq = _seq_from(start_lord)
    md_durations = [balance_yrs] + [DASHA_YEARS[l] for l in md_seq[1:]]
    md_periods = []
    cursor = birth_dt
    for lord, yrs in zip(md_seq, md_durations):
        md_end = cursor + timedelta(days=yrs * YEAR_DAYS)
        md = DashaPeriod(lord=lord, start=cursor, end=md_end, level=1, children=[])
        md.children = _periods(cursor, yrs, lord, 120.0, level=2)
        md_periods.append(md)
        cursor = md_end
    return md_periods


def pratyantar_table(md_period, ad_period) -> list:
    return _periods(ad_period.start,
                    (ad_period.end - ad_period.start).days / YEAR_DAYS,
                    ad_period.lord, 120.0, level=3)


def _vimshottari_timeline(chart) -> DashaTimeline:
    periods = _build(chart.datetime_local, chart.planets["Moon"].longitude)
    return DashaTimeline(system="Vimshottari", periods=periods)


YOGINI_ORDER = ["Mangala","Pingala","Dhanya","Bhramari",
                "Bhadrika","Ulka","Siddha","Sankata"]
YOGINI_PLANET = {"Mangala":"Moon","Pingala":"Sun","Dhanya":"Jupiter","Bhramari":"Mars",
                 "Bhadrika":"Mercury","Ulka":"Saturn","Siddha":"Venus","Sankata":"Rahu"}
YOGINI_YEARS = {"Mangala":1,"Pingala":2,"Dhanya":3,"Bhramari":4,
                "Bhadrika":5,"Ulka":6,"Siddha":7,"Sankata":8}


def _yogini_start_index(nak_index: int) -> int:
    return nak_index % 8


def _yogini_balance(moon_lon: float) -> tuple[int, float]:
    nak_size = 360.0 / 27.0
    nak_idx = int((moon_lon % 360) // nak_size)
    yogini_idx = _yogini_start_index(nak_idx)
    progress_in_nak = (moon_lon % 360) - (nak_idx * nak_size)
    balance = YOGINI_YEARS[YOGINI_ORDER[yogini_idx]] * (1.0 - progress_in_nak / nak_size)
    return yogini_idx, balance


def _yogini_timeline(chart) -> DashaTimeline:
    moon_lon = chart.planets["Moon"].longitude
    start_idx, balance = _yogini_balance(moon_lon)
    cursor = chart.datetime_local
    periods: list = []
    next_idx, duration = start_idx, balance
    for _ in range(32):
        lord_name = YOGINI_ORDER[next_idx]
        end = cursor + timedelta(days=duration * YEAR_DAYS)
        periods.append(DashaPeriod(
            lord=f"{lord_name} ({YOGINI_PLANET[lord_name]})",
            start=cursor, end=end, level=1))
        cursor = end
        next_idx = (next_idx + 1) % 8
        duration = YOGINI_YEARS[YOGINI_ORDER[next_idx]]
    return DashaTimeline(system="Yogini", periods=periods)


ASHTOTTARI_ORDER = ["Sun","Moon","Mars","Mercury","Saturn","Jupiter","Rahu","Venus"]
ASHTOTTARI_YEARS = {"Sun":6,"Moon":15,"Mars":8,"Mercury":17,
                    "Saturn":10,"Jupiter":19,"Rahu":12,"Venus":21}
_ASHTOTTARI_NAK_TO_LORD = [
    "Sun","Sun","Sun","Sun",
    "Moon","Moon","Moon",
    "Mars","Mars","Mars",
    "Mercury","Mercury","Mercury","Mercury",
    "Saturn","Saturn","Saturn",
    "Jupiter","Jupiter","Jupiter","Jupiter",
    "Rahu","Rahu","Rahu",
    "Venus","Venus","Venus",
]


def _ashtottari_balance(moon_lon: float) -> tuple[str, float]:
    nak_size = 360.0 / 27.0
    nak_idx = int((moon_lon % 360) // nak_size)
    lord = _ASHTOTTARI_NAK_TO_LORD[nak_idx]
    progress_in_nak = (moon_lon % 360) - (nak_idx * nak_size)
    balance = ASHTOTTARI_YEARS[lord] * (1.0 - progress_in_nak / nak_size)
    return lord, balance


def _ashtottari_applies(chart) -> bool:
    rahu_h = chart.planets["Rahu"].house
    if rahu_h == 1: return False
    lord_planet = chart.lagna.lord
    lord = chart.planets.get(lord_planet)
    if not lord: return True
    lord_h = lord.house
    kendra_from_lord = {((lord_h + k - 2) % 12) + 1 for k in (1,4,7,10)}
    return rahu_h not in kendra_from_lord


def _ashtottari_timeline(chart) -> DashaTimeline:
    moon_lon = chart.planets["Moon"].longitude
    lord, balance = _ashtottari_balance(moon_lon)
    cursor = chart.datetime_local
    periods: list = []
    seq_start = ASHTOTTARI_ORDER.index(lord)
    seq = ASHTOTTARI_ORDER[seq_start:] + ASHTOTTARI_ORDER[:seq_start]
    duration = balance
    for i in range(16):
        sub_lord = seq[i % 8]
        end = cursor + timedelta(days=duration * YEAR_DAYS)
        periods.append(DashaPeriod(lord=sub_lord, start=cursor, end=end, level=1))
        cursor = end
        duration = ASHTOTTARI_YEARS[seq[(i + 1) % 8]]
    return DashaTimeline(system="Ashtottari", periods=periods)


def _char_dasha(chart) -> DashaTimeline:
    return DashaTimeline(system="Char Dasha (Jaimini)", periods=[])


def _compute_dashas(chart) -> dict[str, DashaTimeline]:
    out: dict = {}
    out["Vimshottari"] = _vimshottari_timeline(chart)
    out["Yogini"] = _yogini_timeline(chart)
    if _ashtottari_applies(chart):
        out["Ashtottari"] = _ashtottari_timeline(chart)
    return out


# ══════════════════════════════════════════════════════════════════════════
# ASHTAKAVARGA — BAV, SAV, Trikona + Ekadhipatya Shodhana, Shodhya Pinda
# ══════════════════════════════════════════════════════════════════════════

TRIKONA_GROUPS: list[list[int]] = [
    [0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11],
]

EKADHIPATYA_PAIRS: dict[str, tuple[int, int]] = {
    "Mars":(0,7), "Venus":(1,6), "Mercury":(2,5),
    "Jupiter":(8,11), "Saturn":(9,10),
}

SHODHYA_PINDA_MULTIPLIER = {
    "Sun":5,"Moon":5,"Mars":8,"Mercury":5,"Jupiter":10,"Venus":7,"Saturn":5,
}


def _trikona_shodhana(bav_by_sign: list[int]) -> list[int]:
    out = list(bav_by_sign)
    for trine in TRIKONA_GROUPS:
        vals = [out[s] for s in trine]
        if min(vals) == 0:
            for s in trine: out[s] = 0
        else:
            m = min(vals)
            for s in trine: out[s] -= m
    return out


def _ekadhipatya_shodhana(bav_by_sign, occupied_signs):
    out = list(bav_by_sign)
    for _planet, (a, b) in EKADHIPATYA_PAIRS.items():
        va, vb = out[a], out[b]
        occ_a, occ_b = a in occupied_signs, b in occupied_signs
        if occ_a and not occ_b: out[b] = 0
        elif occ_b and not occ_a: out[a] = 0
        else:
            if va == vb: out[a] = 0; out[b] = 0
            elif va < vb: out[a] = 0
            else: out[b] = 0
    return out


def _compute_ashtakavarga(chart) -> dict:
    planet_data = {n: (p.longitude, p.speed) for n, p in chart.planets.items()
                   if n not in ("Rahu", "Ketu")}
    r_lon = chart.planets["Rahu"].longitude
    k_lon = chart.planets["Ketu"].longitude
    ls = chart.lagna.sign_index
    bav_house = _bav_calc(ls, planet_data, r_lon, k_lon)

    def by_house_to_by_sign(bindus_by_house):
        out = [0] * 12
        for h in range(1, 13):
            sign_idx = (ls + h - 1) % 12
            out[sign_idx] = bindus_by_house[h - 1]
        return out

    bav_sign = {p: by_house_to_by_sign(v) for p, v in bav_house.items()}

    sav_house = [0] * 12
    for v in bav_house.values():
        for i in range(12): sav_house[i] += v[i]
    sav_sign = by_house_to_by_sign(sav_house)
    ranked = sorted(((sav_house[i], i + 1) for i in range(12)), reverse=True)
    strongest = [(h, b) for b, h in ranked[:3]]
    weakest   = [(h, b) for b, h in ranked[-3:][::-1]]

    occupied = {chart.planets[p].sign_index for p in
                ("Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn")}
    shodhita_bav_sign: dict[str, list[int]] = {}
    shodhya_pinda: dict[str, int] = {}
    shodhita_sav_sign = [0] * 12
    for planet, sign_vals in bav_sign.items():
        after_trikona = _trikona_shodhana(sign_vals)
        after_ekadhi  = _ekadhipatya_shodhana(after_trikona, occupied)
        shodhita_bav_sign[planet] = after_ekadhi
        for i in range(12): shodhita_sav_sign[i] += after_ekadhi[i]
        natal_sign = chart.planets[planet].sign_index
        mult = SHODHYA_PINDA_MULTIPLIER.get(planet, 5)
        shodhya_pinda[planet] = after_ekadhi[natal_sign] * mult

    return {
        "bav_by_house": bav_house, "bav_by_sign": bav_sign,
        "sav_by_house": sav_house, "sav_by_sign": sav_sign,
        "strongest_houses": strongest, "weakest_houses": weakest,
        "shodhita_bav_by_sign": shodhita_bav_sign,
        "shodhita_sav_by_sign": shodhita_sav_sign,
        "shodhya_pinda": shodhya_pinda,
    }


# ══════════════════════════════════════════════════════════════════════════
# SHADBALA — Six-fold strength + Bhava Bala + Vimshopaka Bala
# ══════════════════════════════════════════════════════════════════════════

SHADBALA_MIN_RUPAS = {
    "Sun":6.5,"Moon":6.0,"Mars":5.0,"Mercury":7.0,
    "Jupiter":6.5,"Venus":5.5,"Saturn":5.0,
}


def _build_legacy_facts(chart) -> dict:
    facts = {"planets": {}, "lagna_sign": chart.lagna.sign,
             "lagna_lord": chart.lagna.lord, "neecha_bhanga": set(),
             "manglik": "", "karakas": {}}
    for pname, pp in chart.planets.items():
        tags = set()
        if pp.dignity == "Exalted":      tags.add("Exalted")
        if pp.dignity == "Debilitated":  tags.add("Debilitated")
        if pp.dignity == "Own Sign":     tags.add("Own Sign")
        if pp.dignity == "Mooltrikona":  tags.add("Mooltrikona")
        if pp.is_retrograde:             tags.add("Retrograde")
        if pp.is_combust:                tags.add(f"Combust({pp.combust_orb:.0f}°)")
        facts["planets"][pname] = {
            "house": pp.house, "sign": pp.sign, "tags": tags,
            "nak_lord": pp.nakshatra_lord, "avastha": pp.avastha,
            "kp_sigs": set(), "war": "",
        }
    return facts


def _dignity_factor(planet_sign: int, planet: str) -> float:
    DIG = {"Sun":(4,6),"Moon":(1,7),"Mars":(9,3),"Mercury":(5,11),
           "Jupiter":(3,9),"Venus":(11,5),"Saturn":(6,0)}
    OWN = {"Sun":{4},"Moon":{3},"Mars":{0,7},"Mercury":{2,5},
           "Jupiter":{8,11},"Venus":{1,6},"Saturn":{9,10}}
    if planet not in DIG: return 0.5
    exalt, debil = DIG[planet]
    if planet_sign == exalt: return 1.0
    if planet_sign == debil: return 0.0
    if planet_sign in OWN.get(planet, set()): return 1.0
    return 0.5


def _vimshopaka_for_planet(chart, planet: str) -> float:
    if planet in ("Rahu", "Ketu"): return 10.0
    total = 0.0
    for n, _name, _purpose, fn in VARGA_REGISTRY:
        weight = VIMSHOPAKA_SHODASA.get(n, 0)
        if weight == 0: continue
        planet_long = chart.planets[planet].longitude
        varga_sign = fn(planet_long)
        total += weight * _dignity_factor(varga_sign, planet)
    return round(total, 2)


_NAT_BEN = {"Jupiter","Venus","Mercury","Moon"}
_NAT_MAL = {"Sun","Mars","Saturn","Rahu","Ketu"}


def _compute_bhava_bala(chart, shadbala_totals, sav_by_house) -> dict:
    out = {}
    for h in range(1, 13):
        sign_idx = (chart.lagna.sign_index + h - 1) % 12
        lord = SIGN_LORDS_MAP[sign_idx]
        lord_rupas = float(shadbala_totals.get(lord, 5.0))
        sav = sav_by_house[h - 1] if sav_by_house and h - 1 < len(sav_by_house) else 28
        sav_component = (sav / 56.0) * 1.5 * 5.0
        lord_component = min(lord_rupas, 10.0) * 0.4
        modifier = 0.0
        for pname, pp in chart.planets.items():
            if pp.house == h:
                modifier += 0.5 if pname in _NAT_BEN else -0.5 if pname in _NAT_MAL else 0
        out[h] = round(sav_component + lord_component + modifier, 2)
    return out


def _compute_shadbala(chart) -> tuple[dict, dict]:
    facts = _build_legacy_facts(chart)
    totals = {}
    for pname, pp in chart.planets.items():
        if pname in ("Rahu", "Ketu"):
            totals[pname] = 5.0
            continue
        try:
            rupas = _legacy_shadbala(
                pname, pp.longitude, pp.speed,
                chart.lagna.longitude, chart.lagna.sign_index, facts,
                {n: (p.longitude, p.speed) for n, p in chart.planets.items()
                 if n not in ("Rahu", "Ketu")},
                chart.julian_day_ut,
            )
        except Exception:
            rupas = 5.0
        totals[pname] = round(float(rupas), 2)

    classical = {p for p in totals if p not in ("Rahu", "Ketu")}
    strong = [p for p in classical if totals[p] >= SHADBALA_MIN_RUPAS[p]]
    weak   = [p for p in classical if totals[p] <  SHADBALA_MIN_RUPAS[p]]
    ranked = sorted(((p, r) for p, r in totals.items() if p in classical),
                    key=lambda kv: kv[1], reverse=True)
    strongest, weakest = ranked[0], ranked[-1]
    vimshopaka = {p: _vimshopaka_for_planet(chart, p) for p in chart.planets}

    shadbala_out = {
        "totals": totals, "minimums": dict(SHADBALA_MIN_RUPAS),
        "strong": strong, "weak": weak,
        "vimshopaka": vimshopaka,
        "strongest": strongest, "weakest": weakest,
    }
    sav_by_house = (chart.ashtakavarga or {}).get("sav_by_house", [])
    bhava_bala = _compute_bhava_bala(chart, totals, sav_by_house)
    return shadbala_out, bhava_bala


# ══════════════════════════════════════════════════════════════════════════
# YOGAS — classifier over legacy detector
# ══════════════════════════════════════════════════════════════════════════

_YOGA_CATEGORY_TABLE = {
    "Gajakesari":"Lunar — Jupiter pairing",
    "Adhi":"Lunar — benefics from Moon",
    "Sunapha":"Lunar — planets from Moon",
    "Anapha":"Lunar — planets from Moon",
    "Durudhura":"Lunar — planets from Moon",
    "Kemadruma":"Lunar — affliction",
    "Veshi":"Solar — planets from Sun",
    "Voshi":"Solar — planets from Sun",
    "Ubhayachari":"Solar — planets from Sun",
    "Budha-Aditya":"Solar — Mercury conjunct Sun",
    "Chandra-Mangala":"Mars — Moon-Mars",
    "Ruchaka":"Pancha Mahapurusha — Mars",
    "Bhadra":"Pancha Mahapurusha — Mercury",
    "Hamsa":"Pancha Mahapurusha — Jupiter",
    "Malavya":"Pancha Mahapurusha — Venus",
    "Shasha":"Pancha Mahapurusha — Saturn",
    "Raja":"Raja Yoga — power & authority",
    "Dharma-Karma":"Raja Yoga — career & dharma",
    "Parivartana":"Mutual sign exchange",
    "Viparita":"Viparita Raja Yoga — rise after fall",
    "Neecha Bhanga":"Debilitation cancellation",
    "Lakshmi":"Wealth — prosperity yoga",
    "Saraswati":"Knowledge — wisdom yoga",
    "Amala":"10th house — spotless reputation",
    "Dhana":"Wealth — wealth yoga",
    "Shubha Kartari":"Lagna protection",
}


def _classify_yoga(yoga_name: str) -> str:
    for key, category in _YOGA_CATEGORY_TABLE.items():
        if yoga_name.startswith(key) or key in yoga_name:
            return category
    return "Special yoga"


def _extract_yoga_planets(description: str) -> list[str]:
    out = []
    for p in ("Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"):
        if p in description and p not in out:
            out.append(p)
    return out


def _detect_yogas(chart) -> list:
    planet_data = {n: (p.longitude, p.speed) for n, p in chart.planets.items()
                   if n not in ("Rahu", "Ketu")}
    r_lon = chart.planets["Rahu"].longitude
    k_lon = chart.planets["Ketu"].longitude
    moon_sidx = chart.planets["Moon"].sign_index
    present, _absent = _legacy_detect_yogas(
        chart.lagna.sign_index, moon_sidx, planet_data, r_lon, k_lon,
    )
    out: list = []
    for name, description in present:
        out.append(Yoga(
            name=name, category=_classify_yoga(name),
            planets_involved=_extract_yoga_planets(description),
            description=description, activation_dasha=None,
        ))
    return out


def yoga_audit(chart) -> list[dict]:
    """Return the full classical-yoga audit — every yoga checked with a
    present/absent flag. Mirrors the dosha audit pattern.

    Returns a list of dicts: {name, present, category, description}.
    """
    planet_data = {n: (p.longitude, p.speed) for n, p in chart.planets.items()
                   if n not in ("Rahu", "Ketu")}
    r_lon = chart.planets["Rahu"].longitude
    k_lon = chart.planets["Ketu"].longitude
    moon_sidx = chart.planets["Moon"].sign_index
    try:
        present, absent = _legacy_detect_yogas(
            chart.lagna.sign_index, moon_sidx, planet_data, r_lon, k_lon,
        )
    except Exception:
        return []
    def _unpack(item):
        # Tolerate both (name, desc) tuples and bare-string names from the
        # legacy detector — different yoga functions return slightly different shapes.
        if isinstance(item, str):
            return item, "—"
        if isinstance(item, (tuple, list)):
            if len(item) >= 2:
                return str(item[0]), str(item[1])
            return str(item[0]), "—"
        return str(item), "—"

    rows: list[dict] = []
    for it in present:
        name, desc = _unpack(it)
        rows.append({
            "name": name, "present": True,
            "category": _classify_yoga(name),
            "description": desc,
        })
    for it in (absent or []):
        name, desc = _unpack(it)
        rows.append({
            "name": name, "present": False,
            "category": _classify_yoga(name),
            "description": desc or "—",
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════
# TRANSITS — 12-month forecast (Saturn / Jupiter / Rahu / Ketu)
# ══════════════════════════════════════════════════════════════════════════

def _dt_to_jd(dt: datetime) -> float:
    dt_utc = dt.astimezone(ZoneInfo("UTC"))
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def _sidereal_lon(jd: float, pid: int) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    res, _ = swe.calc_ut(jd, pid, flags)
    return float(res[0]) % 360


def _sign_idx_of(lon: float) -> int:
    return int(lon // 30) % 12


def _house_from(ref_sign: int, planet_sign: int) -> int:
    return ((planet_sign - ref_sign) % 12) + 1


def _sade_sati_phase(saturn_sign: int, moon_sign: int) -> dict:
    twelfth = (moon_sign + 11) % 12
    first   = moon_sign
    second  = (moon_sign + 1) % 12
    if saturn_sign == twelfth:
        return {"in_sade_sati": True, "phase": "Rising (12th from Moon)",
                "note": "Mental restlessness, beginning of seven-and-a-half "
                        "year cycle. Plans seeded now mature later."}
    if saturn_sign == first:
        return {"in_sade_sati": True, "phase": "Peak (1st from Moon)",
                "note": "Most intense phase — physical, financial, relational "
                        "tests. Discipline + austerity transmute the load."}
    if saturn_sign == second:
        return {"in_sade_sati": True, "phase": "Setting (2nd from Moon)",
                "note": "Reaping phase — wealth/family lessons consolidate."}
    return {"in_sade_sati": False, "phase": "None", "note": ""}


def _ashtama_shani(saturn_sign, moon_sign): return saturn_sign == (moon_sign + 7) % 12
def _kantaka_shani(saturn_sign, moon_sign):
    return saturn_sign in {(moon_sign + d) % 12 for d in (3, 6, 9)}
def _guru_chandra_yoga(jup_sign, moon_sign):
    return jup_sign in {(moon_sign + d - 1) % 12 for d in (2, 5, 7, 9, 11)}


def _find_sign_changes(pid: int, start_dt, end_dt, step_days: float = 1.0):
    out = []
    cursor = start_dt
    jd_prev = _dt_to_jd(cursor)
    sign_prev = _sign_idx_of(_sidereal_lon(jd_prev, pid))
    while cursor < end_dt:
        cursor = cursor + timedelta(days=step_days)
        jd_now = _dt_to_jd(cursor)
        sign_now = _sign_idx_of(_sidereal_lon(jd_now, pid))
        if sign_now != sign_prev:
            out.append((cursor, sign_prev, sign_now))
            sign_prev = sign_now
    return out


def sade_sati_timeline(chart, years_back: int = 30, years_forward: int = 30) -> list[dict]:
    """Compute the past + present + future Sade Sati windows for `chart`.

    Sade Sati is the 7.5-year period when Saturn transits the 12th, 1st,
    and 2nd signs from the native's natal Moon. Each phase is ~2.5 years.

    Returns a list of phase dicts ordered chronologically:
        [{phase, sign_idx, sign_name, start, end, is_current}, ...]

    Where each entry is one of the three target signs (12th / 1st / 2nd
    from Moon). Grouping consecutive entries reconstructs each full
    7.5-year Sade Sati cycle.
    """
    moon_sidx = chart.planets["Moon"].sign_index
    target_signs = {
        (moon_sidx + 11) % 12: "Rising (12th from Moon)",
        moon_sidx: "Peak (1st from Moon)",
        (moon_sidx + 1) % 12: "Setting (2nd from Moon)",
    }
    tz = ZoneInfo(chart.birth_data.tz)
    now = datetime.now(tz)
    start = now - timedelta(days=int(years_back * 365.25))
    end   = now + timedelta(days=int(years_forward * 365.25))

    # Coarse 30-day scan over Saturn's sidereal sign, bisecting at boundaries
    # to pin the change date to ±1 day.
    cursor = start
    jd_prev = _dt_to_jd(cursor)
    sign_prev = _sign_idx_of(_sidereal_lon(jd_prev, swe.SATURN))
    changes: list[tuple[datetime, int, int]] = []
    while cursor < end:
        next_cursor = cursor + timedelta(days=30)
        jd_now = _dt_to_jd(next_cursor)
        sign_now = _sign_idx_of(_sidereal_lon(jd_now, swe.SATURN))
        if sign_now != sign_prev:
            lo, hi = cursor, next_cursor
            # Bisect to ±1 day
            for _ in range(20):
                if (hi - lo).total_seconds() < 86400:
                    break
                mid = lo + (hi - lo) / 2
                jd_mid = _dt_to_jd(mid)
                s_mid = _sign_idx_of(_sidereal_lon(jd_mid, swe.SATURN))
                if s_mid == sign_prev:
                    lo = mid
                else:
                    hi = mid
            changes.append((hi, sign_prev, sign_now))
            sign_prev = sign_now
        cursor = next_cursor

    # Convert sign-change events into phase windows for the 3 target signs.
    windows: list[dict] = []
    for i, (dt_change, from_s, to_s) in enumerate(changes):
        if to_s not in target_signs:
            continue
        # Exit = next change that leaves `to_s`
        exit_dt = None
        for j in range(i + 1, len(changes)):
            if changes[j][1] == to_s:
                exit_dt = changes[j][0]
                break
        windows.append({
            "phase": target_signs[to_s],
            "sign_idx": to_s,
            "sign_name": SIGNS[to_s],
            "start": dt_change,
            "end": exit_dt,
            "is_current": (dt_change <= now and (exit_dt is None or now <= exit_dt)),
        })
    return windows


def render_chart_svg(chart, *, varga: int = 1, style: str = "north_indian",
                     size: int = 400, theme_name: str = "classic_vedic",
                     theme: dict | None = None, show_degrees: bool | None = None,
                     show_house_numbers: bool = True, title: str = "") -> str:
    """Universal chart-rendering API — render any varga of a computed chart
    as a self-contained SVG. Lazy import to avoid pulling in WeasyPrint
    when the consumer only needs SVG.

    Use this anywhere in the app (free view, compatibility feature,
    transit overlay, mobile renderer) to display the same accurate chart.
    """
    from pdf_engine.kundli_pdf import render_chart_for_chart
    return render_chart_for_chart(
        chart, varga=varga, style=style, size=size,
        theme_name=theme_name, theme=theme,
        show_degrees=show_degrees, show_house_numbers=show_house_numbers,
        title=title,
    )


def _twelve_month_forecast(chart) -> dict:
    tz = ZoneInfo(chart.birth_data.tz)
    now = datetime.now(tz)
    end = now + timedelta(days=365)
    natal_lagna_sign = chart.lagna.sign_index
    natal_moon_sign = chart.planets["Moon"].sign_index

    targets = {"Saturn": PLANETS["Saturn"], "Jupiter": PLANETS["Jupiter"],
               "Rahu": swe.TRUE_NODE}
    current_transit: dict[str, dict] = {}
    sign_changes: dict[str, list] = {}

    jd_now = _dt_to_jd(now)
    for name, pid in targets.items():
        lon = _sidereal_lon(jd_now, pid)
        sidx = _sign_idx_of(lon)
        current_transit[name] = {
            "sign": SIGNS[sidx], "sign_index": sidx, "longitude": lon,
            "house_from_lagna": _house_from(natal_lagna_sign, sidx),
            "house_from_moon":  _house_from(natal_moon_sign, sidx),
            "sign_lord": SIGN_LORDS_MAP[sidx],
        }
        sign_changes[name] = []
        for dc, fs, ts in _find_sign_changes(pid, now, end):
            sign_changes[name].append({
                "date": dc, "from": SIGNS[fs], "to": SIGNS[ts],
                "to_house_from_lagna": _house_from(natal_lagna_sign, ts),
                "to_house_from_moon":  _house_from(natal_moon_sign, ts),
            })
    rahu_sidx = current_transit["Rahu"]["sign_index"]
    ketu_sidx = (rahu_sidx + 6) % 12
    current_transit["Ketu"] = {
        "sign": SIGNS[ketu_sidx], "sign_index": ketu_sidx,
        "longitude": (current_transit["Rahu"]["longitude"] + 180) % 360,
        "house_from_lagna": _house_from(natal_lagna_sign, ketu_sidx),
        "house_from_moon":  _house_from(natal_moon_sign, ketu_sidx),
        "sign_lord": SIGN_LORDS_MAP[ketu_sidx],
    }
    sat_sidx = current_transit["Saturn"]["sign_index"]
    jup_sidx = current_transit["Jupiter"]["sign_index"]
    return {
        "period": {"start": now, "end": end},
        "current_transit": current_transit,
        "sign_changes": sign_changes,
        "sade_sati": _sade_sati_phase(sat_sidx, natal_moon_sign),
        "ashtama_shani": _ashtama_shani(sat_sidx, natal_moon_sign),
        "kantaka_shani": _kantaka_shani(sat_sidx, natal_moon_sign),
        "guru_chandra_yoga": _guru_chandra_yoga(jup_sidx, natal_moon_sign),
    }


# ══════════════════════════════════════════════════════════════════════════
# REMEDIES — Mantra, Ratna, Yantra, Rudraksha, Daan, Lal Kitab
# ══════════════════════════════════════════════════════════════════════════

PLANET_REMEDIES: dict[str, dict] = {
    "Sun": {
        "beej_mantra": "Om Hrām Hrīm Hraum Saḥ Sūryāya Namaḥ",
        "japa_count": 7000,
        "vedic_mantra": "Ādityāya vidmahe sahasrakirṇāya dhīmahi tanno sūryaḥ pracodayāt",
        "stotra": "Aditya Hridaya Stotra",
        "ratna": {"primary":"Ruby (Manik)","substitute":"Red Garnet / Red Spinel",
                  "finger":"Ring","day_to_wear":"Sunday at sunrise",
                  "metal":"Gold or Copper","carat_range":"3–7 ct"},
        "yantra": "Surya Yantra",
        "rudraksha": "1-mukhi (or 12-mukhi)",
        "daan": ["Wheat","Jaggery (gur)","Copper","Red cloth","Ruby (if affordable)"],
        "daan_day": "Sunday before sunset",
        "vrat": "Sunday (Ravivar)",
        "colors": ["Red","Saffron","Orange"],
        "deity": "Surya / Shri Ram",
        "lal_kitab": ["Offer water to the Sun at sunrise (Arghya). "
                      "Bury a copper coin in the earth near a temple."],
    },
    "Moon": {
        "beej_mantra": "Om Śrām Śrīm Śraum Saḥ Candrāya Namaḥ",
        "japa_count": 11000,
        "vedic_mantra": "Padmadhvajāya vidmahe hema rūpāya dhīmahi tanno candraḥ pracodayāt",
        "stotra": "Chandra Stotra",
        "ratna": {"primary":"Natural Pearl (Moti)","substitute":"White Moonstone",
                  "finger":"Little finger","day_to_wear":"Monday after moonrise",
                  "metal":"Silver","carat_range":"4–7 ct"},
        "yantra": "Chandra Yantra",
        "rudraksha": "2-mukhi",
        "daan": ["Rice","Milk","White cloth","Silver","Camphor"],
        "daan_day": "Monday evening",
        "vrat": "Monday (Somvar)",
        "colors": ["White","Cream","Silver"],
        "deity": "Shiva / Parvati",
        "lal_kitab": ["Drink water from a silver glass. Keep a small silver "
                      "square at home. Respect mother and elderly women."],
    },
    "Mars": {
        "beej_mantra": "Om Krām Krīm Kraum Saḥ Bhaumāya Namaḥ",
        "japa_count": 10000,
        "vedic_mantra": "Aṅgārakāya vidmahe śaktihastāya dhīmahi tanno bhaumaḥ pracodayāt",
        "stotra": "Hanuman Chalisa, Mangal Stotra",
        "ratna": {"primary":"Red Coral (Moonga)","substitute":"Carnelian",
                  "finger":"Ring","day_to_wear":"Tuesday at sunrise",
                  "metal":"Gold or Copper","carat_range":"5–9 ct"},
        "yantra": "Mangal Yantra",
        "rudraksha": "3-mukhi",
        "daan": ["Red lentils (masoor)","Jaggery","Red cloth","Copper","Sweets"],
        "daan_day": "Tuesday before sunset",
        "vrat": "Tuesday (Mangalvar)",
        "colors": ["Red","Crimson","Coral"],
        "deity": "Hanuman / Subramanya / Mangal",
        "lal_kitab": ["Plant a neem tree. Feed sweets to younger siblings. "
                      "Donate red lentils on Tuesdays."],
    },
    "Mercury": {
        "beej_mantra": "Om Brām Brīm Braum Saḥ Budhāya Namaḥ",
        "japa_count": 9000,
        "vedic_mantra": "Sauṁyarūpāya vidmahe vāṇeśvarāya dhīmahi tanno budhaḥ pracodayāt",
        "stotra": "Vishnu Sahasranama, Budh Stotra",
        "ratna": {"primary":"Emerald (Panna)","substitute":"Green Tourmaline / Peridot",
                  "finger":"Little finger","day_to_wear":"Wednesday at sunrise",
                  "metal":"Gold","carat_range":"3–6 ct"},
        "yantra": "Budh Yantra",
        "rudraksha": "4-mukhi",
        "daan": ["Green moong dal","Green cloth","Bronze items","Books / pens"],
        "daan_day": "Wednesday afternoon",
        "vrat": "Wednesday (Budhvar)",
        "colors": ["Green","Emerald"],
        "deity": "Vishnu / Ganesha",
        "lal_kitab": ["Feed green grass to cows. Keep a green handkerchief. "
                      "Avoid speaking harshly."],
    },
    "Jupiter": {
        "beej_mantra": "Om Grām Grīm Graum Saḥ Guruve Namaḥ",
        "japa_count": 19000,
        "vedic_mantra": "Vṛṣabhadhvajāya vidmahe gṛṇātmajāya dhīmahi tanno guruḥ pracodayāt",
        "stotra": "Guru Stotra, Vishnu Sahasranama",
        "ratna": {"primary":"Yellow Sapphire (Pukhraj)","substitute":"Yellow Topaz / Citrine",
                  "finger":"Index","day_to_wear":"Thursday at sunrise",
                  "metal":"Gold","carat_range":"5–9 ct"},
        "yantra": "Guru Yantra / Sri Yantra",
        "rudraksha": "5-mukhi",
        "daan": ["Yellow lentils (chana dal)","Turmeric","Yellow cloth","Saffron","Gold (modest)"],
        "daan_day": "Thursday morning",
        "vrat": "Thursday (Guruvar)",
        "colors": ["Yellow","Gold","Saffron"],
        "deity": "Brihaspati / Vishnu / Krishna",
        "lal_kitab": ["Apply saffron tilak. Feed gram/chickpeas to horses. "
                      "Respect teachers and elders."],
    },
    "Venus": {
        "beej_mantra": "Om Drām Drīm Draum Saḥ Śukrāya Namaḥ",
        "japa_count": 16000,
        "vedic_mantra": "Aśvadhvajāya vidmahe dhanurhastāya dhīmahi tanno śukraḥ pracodayāt",
        "stotra": "Shukra Stotra, Lakshmi Stotra",
        "ratna": {"primary":"Diamond (Heera)","substitute":"White Sapphire / White Topaz / Zircon",
                  "finger":"Middle","day_to_wear":"Friday at sunrise",
                  "metal":"Platinum or White Gold","carat_range":"0.5–2 ct (diamond)"},
        "yantra": "Shukra Yantra",
        "rudraksha": "6-mukhi",
        "daan": ["White rice","Curd","White sugar","White cloth","Perfume","Silver"],
        "daan_day": "Friday evening",
        "vrat": "Friday (Shukravar)",
        "colors": ["White","Pink","Pastel shades"],
        "deity": "Lakshmi / Saraswati",
        "lal_kitab": ["Donate clothes on Fridays. Respect women. "
                      "Avoid harsh language with spouse."],
    },
    "Saturn": {
        "beej_mantra": "Om Prām Prīm Praum Saḥ Śanaiścarāya Namaḥ",
        "japa_count": 23000,
        "vedic_mantra": "Kāka dhvajāya vidmahe khaḍga hastāya dhīmahi tanno mandaḥ pracodayāt",
        "stotra": "Shani Stotra, Dasharatha Krit Shani Stotra",
        "ratna": {"primary":"Blue Sapphire (Neelam)","substitute":"Amethyst / Lapis Lazuli",
                  "finger":"Middle","day_to_wear":"Saturday at sunset",
                  "metal":"Iron, Silver, or Panchadhatu","carat_range":"4–7 ct"},
        "yantra": "Shani Yantra",
        "rudraksha": "7-mukhi or 14-mukhi",
        "daan": ["Black sesame (til)","Mustard oil","Black gram (urad)","Iron","Black cloth"],
        "daan_day": "Saturday evening",
        "vrat": "Saturday (Shanivar)",
        "colors": ["Black","Dark blue","Indigo"],
        "deity": "Shani / Hanuman / Bhairava",
        "lal_kitab": ["Feed crows or black dogs. Light a mustard-oil lamp under "
                      "a peepal tree on Saturdays. Serve the poor."],
    },
    "Rahu": {
        "beej_mantra": "Om Bhrām Bhrīm Bhraum Saḥ Rāhave Namaḥ",
        "japa_count": 18000,
        "vedic_mantra": "Naka dhvajāya vidmahe padma hastāya dhīmahi tanno rāhuḥ pracodayāt",
        "stotra": "Rahu Stotra, Durga Saptashati",
        "ratna": {"primary":"Hessonite (Gomed)","substitute":"Orange Zircon",
                  "finger":"Middle","day_to_wear":"Saturday at sunset",
                  "metal":"Silver or Panchadhatu","carat_range":"5–9 ct"},
        "yantra": "Rahu Yantra",
        "rudraksha": "8-mukhi or 10-mukhi",
        "daan": ["Black/brown blanket","Coconut","Mustard oil","Lead"],
        "daan_day": "Saturday or eclipse days",
        "vrat": "Saturday + Eclipse fasting",
        "colors": ["Smoky grey","Dark brown"],
        "deity": "Durga / Kali / Bhairava",
        "lal_kitab": ["Carry a piece of silver. Donate barley to a temple. "
                      "Avoid alcohol and adulterous company."],
    },
    "Ketu": {
        "beej_mantra": "Om Strām Strīm Straum Saḥ Ketave Namaḥ",
        "japa_count": 17000,
        "vedic_mantra": "Padma hastāya vidmahe amṛta hastāya dhīmahi tanno ketuḥ pracodayāt",
        "stotra": "Ketu Stotra, Ganesha Stotra",
        "ratna": {"primary":"Cat's Eye (Lehsunia)","substitute":"Chrysoberyl",
                  "finger":"Middle","day_to_wear":"Tuesday at sunset",
                  "metal":"Silver or Panchadhatu","carat_range":"5–9 ct"},
        "yantra": "Ketu Yantra",
        "rudraksha": "9-mukhi",
        "daan": ["Multi-coloured cloth","Sesame","Coconut","Goat / blanket"],
        "daan_day": "Tuesday or eclipse days",
        "vrat": "Tuesday + Eclipse fasting",
        "colors": ["Multi-colour","Smoky"],
        "deity": "Ganesha / Subramanya",
        "lal_kitab": ["Keep a dog as a pet or feed stray dogs. Wear silver. "
                      "Respect grandparents."],
    },
}

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


def _afflicting_planets(chart) -> list[str]:
    out: list[str] = []
    seen = set()
    def add(p):
        if p not in seen and p in chart.planets:
            out.append(p); seen.add(p)
    for p, pp in chart.planets.items():
        if pp.dignity == "Debilitated": add(p)
    for p, pp in chart.planets.items():
        if pp.is_combust and p != "Sun": add(p)
    for p, pp in chart.planets.items():
        if pp.house in (6,8,12) and p not in ("Rahu","Ketu"): add(p)
    for p in chart.functional.malefics: add(p)
    h8_lord = SIGN_LORDS_MAP[(chart.lagna.sign_index + 7) % 12]
    h12_lord = SIGN_LORDS_MAP[(chart.lagna.sign_index + 11) % 12]
    add(h8_lord); add(h12_lord)
    return out


def _recommend_remedies(chart) -> dict:
    priorities = _afflicting_planets(chart)
    per_planet = {p: PLANET_REMEDIES[p] for p in priorities if p in PLANET_REMEDIES}
    per_dosha = {}
    for d in chart.doshas:
        if d.present and d.name in DOSHA_REMEDIES:
            per_dosha[d.name] = DOSHA_REMEDIES[d.name]
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
    gemstone_chart = {p: PLANET_REMEDIES[p]["ratna"] for p in PLANET_REMEDIES}
    return {
        "priority_planets": priorities,
        "per_planet": per_planet,
        "per_dosha": per_dosha,
        "gemstone_chart": gemstone_chart,
        "daily_practice": daily,
    }


# ══════════════════════════════════════════════════════════════════════════
# SUDARSHAN CHAKRA — triple view (Lagna / Moon / Sun)
# ══════════════════════════════════════════════════════════════════════════

def _sud_whole_sign_house(ref_sign: int, planet_sign: int) -> int:
    return ((planet_sign - ref_sign) % 12) + 1


def _build_sudarshan(chart) -> dict:
    refs = {
        "lagna": chart.lagna.sign_index,
        "moon":  chart.planets["Moon"].sign_index,
        "sun":   chart.planets["Sun"].sign_index,
    }
    planet_views: dict[str, dict[str, int]] = {}
    house_occupants: dict[str, dict[int, list[str]]] = {
        f"from_{key}": {h: [] for h in range(1, 13)} for key in refs
    }
    for pname, pp in chart.planets.items():
        view = {
            "from_lagna": _sud_whole_sign_house(refs["lagna"], pp.sign_index),
            "from_moon":  _sud_whole_sign_house(refs["moon"],  pp.sign_index),
            "from_sun":   _sud_whole_sign_house(refs["sun"],   pp.sign_index),
        }
        planet_views[pname] = view
        house_occupants["from_lagna"][view["from_lagna"]].append(pname)
        house_occupants["from_moon"][view["from_moon"]].append(pname)
        house_occupants["from_sun"][view["from_sun"]].append(pname)
    GOOD = {1,4,5,7,9,10,11}
    BAD  = {6,8,12}
    triple_strong: list[str] = []
    triple_weak:   list[str] = []
    for pname, v in planet_views.items():
        if v["from_lagna"] in GOOD and v["from_moon"] in GOOD and v["from_sun"] in GOOD:
            triple_strong.append(pname)
        if v["from_lagna"] in BAD and v["from_moon"] in BAD and v["from_sun"] in BAD:
            triple_weak.append(pname)
    return {
        "references": refs, "planet_views": planet_views,
        "house_occupants": house_occupants,
        "triple_strong": triple_strong, "triple_weak": triple_weak,
    }


# ══════════════════════════════════════════════════════════════════════════
# JAIMINI — Pada Lagnas, Upapada, Karakamsa
# ══════════════════════════════════════════════════════════════════════════

def _pada_sign(house_num: int, lagna_sign_idx: int, planet_signs: dict[str, int]) -> int:
    house_sign = (lagna_sign_idx + house_num - 1) % 12
    house_lord = SIGN_LORDS_MAP[house_sign]
    lord_sign = planet_signs.get(house_lord, house_sign)
    distance = ((lord_sign - house_sign) % 12) + 1
    pada = (lord_sign + distance - 1) % 12
    if pada == house_sign:
        pada = (house_sign + 9) % 12
    elif pada == (house_sign + 6) % 12:
        pada = (house_sign + 3) % 12
    return pada


def _build_jaimini(chart) -> dict:
    planet_signs_local = {n: p.sign_index for n, p in chart.planets.items()}
    ls = chart.lagna.sign_index
    SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    pada_lagnas = {}
    for h in range(1, 13):
        sidx = _pada_sign(h, ls, planet_signs_local)
        label = "AL" if h == 1 else f"A{h}"
        pada_lagnas[h] = {
            "label": label, "sign": SIGN_NAMES[sidx], "sign_index": sidx,
            "house_from_lagna": ((sidx - ls) % 12) + 1,
        }
    upapada = pada_lagnas[12]
    ak_planet = chart.chara_karakas.atmakaraka
    d9 = chart.divisional_charts.get(9)
    if d9:
        karakamsa_sign_idx = d9.planet_signs.get(ak_planet, 0)
    else:
        karakamsa_sign_idx = chart.planets[ak_planet].sign_index
    karakamsa = {
        "atmakaraka": ak_planet,
        "d9_sign": SIGN_NAMES[karakamsa_sign_idx],
        "d9_sign_index": karakamsa_sign_idx,
        "house_from_lagna": ((karakamsa_sign_idx - ls) % 12) + 1,
    }
    return {
        "pada_lagnas": pada_lagnas,
        "upapada": upapada,
        "karakamsa": karakamsa,
        "chara_karakas": [
            {"karaka": name, "planet": planet, "degree": deg}
            for (planet, name, deg) in chart.chara_karakas.chain
        ],
    }


# ══════════════════════════════════════════════════════════════════════════
# KP EXTRAS — cuspal table + significators
# ══════════════════════════════════════════════════════════════════════════

def _cusp_lords(cusp_lon: float) -> dict:
    sign_idx = int(cusp_lon // 30) % 12
    nak, nak_lord, _pada = nakshatra_info(cusp_lon)
    sub = get_kp_sub_lord(cusp_lon)
    return {"sign": sign_idx, "sign_lord": SIGN_LORDS_MAP[sign_idx],
            "nakshatra": nak, "star_lord": nak_lord, "sub_lord": sub}


def _build_kp_extras(chart) -> dict:
    planet_data = {n: (p.longitude, p.speed) for n, p in chart.planets.items()
                   if n not in ("Rahu","Ketu")}
    r_lon = chart.planets["Rahu"].longitude
    k_lon = chart.planets["Ketu"].longitude
    ls = chart.lagna.sign_index
    cusps = []
    for i, cusp_lon in enumerate(chart.placidus_cusps[:12], start=1):
        lords = _cusp_lords(cusp_lon)
        cusps.append({"cusp": i, "longitude": cusp_lon, **lords})
    significators = {}
    for pname in list(chart.planets.keys()):
        sigs = get_kp_4step(pname, ls, planet_data, r_lon, k_lon)
        significators[pname] = sigs
    return {"cusps": cusps, "significators": significators, "ruling_planets": None}


# ══════════════════════════════════════════════════════════════════════════
# VARSHAPHALA — Solar Return + Muntha + 8 Sahams (PUBLIC API)
# ══════════════════════════════════════════════════════════════════════════

def _find_solar_return(chart, year: int) -> datetime:
    target = chart.planets["Sun"].longitude
    bd = chart.birth_data
    bd_dt = datetime(year, bd.date.month, bd.date.day,
                     bd.time.hour, bd.time.minute, tzinfo=ZoneInfo(bd.tz))
    lo = bd_dt - timedelta(days=5)
    hi = bd_dt + timedelta(days=5)

    def sun_lon_at(dt):
        utc = dt.astimezone(ZoneInfo("UTC"))
        jd = swe.julday(utc.year, utc.month, utc.day,
                        utc.hour + utc.minute / 60 + utc.second / 3600)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        res, _ = swe.calc_ut(jd, swe.SUN, flags)
        return float(res[0]) % 360

    def diff(dt):
        d = (sun_lon_at(dt) - target + 180) % 360 - 180
        return d

    for _ in range(40):
        mid = lo + (hi - lo) / 2
        d_lo = diff(lo)
        d_mid = diff(mid)
        if abs(d_mid) < 1e-5:
            return mid
        if d_lo * d_mid < 0: hi = mid
        else: lo = mid
    return mid


def _saham(a_lon, b_lon, asc_lon): return (a_lon - b_lon + asc_lon) % 360


def _compute_sahams(chart) -> dict:
    p = chart.planets
    asc = chart.lagna.longitude
    sahams_raw = {
        "Punya":   _saham(p["Moon"].longitude, p["Sun"].longitude, asc),
        "Vidya":   _saham(p["Sun"].longitude,  p["Moon"].longitude, asc),
        "Karya":   _saham(p["Saturn"].longitude, p["Sun"].longitude, asc),
        "Yashas":  _saham(p["Jupiter"].longitude, p["Sun"].longitude, asc),
        "Mitra":   _saham(p["Jupiter"].longitude, p["Moon"].longitude, asc),
        "Bhratri": _saham(p["Mars"].longitude, p["Saturn"].longitude, asc),
        "Pitri":   _saham(p["Saturn"].longitude, p["Sun"].longitude, asc),
        "Matri":   _saham(p["Moon"].longitude, p["Venus"].longitude, asc),
    }
    out = {}
    for name, lon in sahams_raw.items():
        sidx = int(lon // 30) % 12
        out[name] = {"longitude": lon, "sign": SIGNS[sidx],
                     "sign_lord": SIGN_LORDS_MAP[sidx],
                     "house_from_lagna": ((sidx - chart.lagna.sign_index) % 12) + 1}
    return out


def _muntha(chart, year: int) -> dict:
    years_lived = year - chart.birth_data.date.year
    muntha_sidx = (chart.lagna.sign_index + years_lived) % 12
    return {"year": year, "age": years_lived, "sign": SIGNS[muntha_sidx],
            "sign_lord": SIGN_LORDS_MAP[muntha_sidx],
            "house_from_lagna": ((muntha_sidx - chart.lagna.sign_index) % 12) + 1}


def compute_varshaphala(chart, year: int | None = None) -> dict:
    """Public — Varshaphala (Tajik annual chart) for given year. Default: current."""
    tz = ZoneInfo(chart.birth_data.tz)
    if year is None:
        year = datetime.now(tz).year
    sr_utc = _find_solar_return(chart, year)
    sr_local = sr_utc.astimezone(tz)
    return {"year": year, "solar_return_utc": sr_utc, "solar_return_local": sr_local,
            "muntha": _muntha(chart, year), "sahams": _compute_sahams(chart)}


# ══════════════════════════════════════════════════════════════════════════
# NAMING — child-name suggestions by nakshatra pada
# ══════════════════════════════════════════════════════════════════════════

NAME_BANK: dict[str, dict[str, list[tuple[str, str]]]] = {
    "chu": {"M":[("Chunmay","blissful"),("Churchit","celebrated")],
            "F":[("Churni","river/sacred"),("Chumki","spark")]},
    "che": {"M":[("Chetan","consciousness"),("Chetas","intellect")],
            "F":[("Chetana","awakening"),("Chetali","lively")]},
    "cho": {"M":[("Chodit","inspired"),("Chokhilal","pure")],
            "F":[("Chokhi","pure"),("Chouki","watcher")]},
    "la":  {"M":[("Lakshya","goal"),("Latit","noble"),("Lalit","graceful")],
            "F":[("Lavanya","elegance"),("Lata","vine"),("Lakshmi","auspicious")]},
    "li":  {"M":[("Litesh","supreme"),("Lipin","writer")],
            "F":[("Lipika","scribe"),("Lila","divine play")]},
    "lu":  {"M":[("Luckie","fortunate"),("Lukesh","ruler of light")],
            "F":[("Luna","moon"),("Lubdha","yearning")]},
    "le":  {"M":[("Lekhraj","writer king"),("Leesh","majestic")],
            "F":[("Leela","divine play"),("Lekha","writing")]},
    "lo":  {"M":[("Lohit","ruddy/Mars"),("Lokesh","lord of the world")],
            "F":[("Lochan","eye"),("Lopa","secret")]},
    "a":   {"M":[("Arjun","white/pure"),("Aarav","peaceful"),("Aditya","Sun"),
                 ("Akshay","indestructible"),("Anant","infinite")],
            "F":[("Aarya","noble"),("Aditi","boundless"),("Anushka","favor"),
                 ("Ananya","incomparable"),("Aishwarya","prosperity")]},
    "i":   {"M":[("Ishaan","Lord Shiva"),("Indra","king of devas"),("Ishan","Sun")],
            "F":[("Isha","goddess"),("Indira","Lakshmi"),("Iravati","river")]},
    "u":   {"M":[("Umang","joy"),("Utsav","festival"),("Udit","risen")],
            "F":[("Ujjwala","luminous"),("Urmila","wave"),("Uma","Parvati")]},
    "e":   {"M":[("Ekansh","whole"),("Eklavya","single-pointed")],
            "F":[("Eesha","goddess"),("Eshana","desire")]},
    "o":   {"M":[("Om","sacred sound"),("Omkar","primal sound")],
            "F":[("Omkari","divine"),("Oorja","energy")]},
    "va":  {"M":[("Varun","water deity"),("Vansh","lineage"),("Vamsi","flute")],
            "F":[("Vanya","of the forest"),("Varsha","rain"),("Vasudha","earth")]},
    "vi":  {"M":[("Vikram","valor"),("Vishal","vast"),("Vivek","wisdom"),
                 ("Vinay","humility"),("Vihaan","dawn")],
            "F":[("Vidya","knowledge"),("Vinita","modest"),("Vishakha","starlike")]},
    "vu":  {"M":[("Vusan","shining")], "F":[("Vuna","tender")]},
}


def _normalize_syl(syll: str) -> str:
    return (syll or "").strip().lower()


def suggest_names(syllable: str, gender: str = "M", count: int = 10) -> list[tuple[str, str]]:
    """Public — return up to `count` names beginning with `syllable` for gender M/F."""
    bank = NAME_BANK.get(_normalize_syl(syllable), {})
    items = bank.get(gender.upper(), [])
    return items[:count]


def _build_naming(chart) -> dict:
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
        "owner_nakshatra": nak, "owner_pada": pada, "owner_syllable": own_syll,
        "names_male": suggest_names(own_syll, "M", 10),
        "names_female": suggest_names(own_syll, "F", 10),
        "all_pada_syllables": [get_pada_syllables(nak, p) for p in range(1, 5)],
        "by_pada": by_pada,
    }


# ══════════════════════════════════════════════════════════════════════════
# WESTERN — tropical positions + Ptolemaic aspects
# ══════════════════════════════════════════════════════════════════════════

TROPICAL_SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
ELEMENTS = {"Aries":"Fire","Leo":"Fire","Sagittarius":"Fire",
            "Taurus":"Earth","Virgo":"Earth","Capricorn":"Earth",
            "Gemini":"Air","Libra":"Air","Aquarius":"Air",
            "Cancer":"Water","Scorpio":"Water","Pisces":"Water"}
MODALITIES = {"Aries":"Cardinal","Cancer":"Cardinal","Libra":"Cardinal","Capricorn":"Cardinal",
              "Taurus":"Fixed","Leo":"Fixed","Scorpio":"Fixed","Aquarius":"Fixed",
              "Gemini":"Mutable","Virgo":"Mutable","Sagittarius":"Mutable","Pisces":"Mutable"}
RULERS = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
          "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars/Pluto",
          "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn/Uranus",
          "Pisces":"Jupiter/Neptune"}


def _tropical_long(jd: float, pid: int) -> tuple[float, float]:
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    res, _ = swe.calc_ut(jd, pid, flags)
    return float(res[0]) % 360, float(res[3])


def _tropical_lagna(jd: float, lat: float, lon: float) -> float:
    flags = swe.FLG_SWIEPH
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", flags)
    return float(ascmc[0]) % 360


def _aspect_between(a, b, orb_luminary=8.0, orb_other=6.0, is_luminary=False):
    sep = abs((a - b + 180.0) % 360.0 - 180.0)
    orb = orb_luminary if is_luminary else orb_other
    targets = [("Conjunction",0.0),("Sextile",60.0),("Square",90.0),
               ("Trine",120.0),("Opposition",180.0)]
    for name, deg in targets:
        if abs(sep - deg) <= orb:
            return name, sep
    return None


def _build_western(chart) -> dict:
    jd = chart.julian_day_ut
    bd = chart.birth_data
    tropical_positions: dict[str, dict] = {}
    longs: dict[str, float] = {}
    for pname, pid in PLANETS.items():
        lon, spd = _tropical_long(jd, pid)
        sign_idx = int(lon // 30) % 12
        sign = TROPICAL_SIGNS[sign_idx]
        tropical_positions[pname] = {
            "longitude": lon, "longitude_dms": format_dms(lon % 30),
            "sign": sign, "sign_index": sign_idx,
            "element": ELEMENTS[sign], "modality": MODALITIES[sign],
            "speed": spd, "is_retrograde": spd < 0 and pname not in ("Sun","Moon"),
        }
        longs[pname] = lon
    res, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH)
    rahu_lon = float(res[0]) % 360
    ketu_lon = (rahu_lon + 180.0) % 360
    for pname, plon in (("Rahu", rahu_lon), ("Ketu", ketu_lon)):
        sign_idx = int(plon // 30) % 12
        sign = TROPICAL_SIGNS[sign_idx]
        tropical_positions[pname] = {
            "longitude": plon, "longitude_dms": format_dms(plon % 30),
            "sign": sign, "sign_index": sign_idx,
            "element": ELEMENTS[sign], "modality": MODALITIES[sign],
            "speed": 0.0, "is_retrograde": False,
        }
        longs[pname] = plon
    asc = _tropical_lagna(jd, bd.lat, bd.lon)
    asc_sign_idx = int(asc // 30) % 12
    asc_sign = TROPICAL_SIGNS[asc_sign_idx]
    for pname, plon in longs.items():
        sign_idx = int(plon // 30) % 12
        tropical_positions[pname]["house"] = ((sign_idx - asc_sign_idx) % 12) + 1
    aspects: list[dict] = []
    names = list(longs.keys())
    for i, p1 in enumerate(names):
        for p2 in names[i+1:]:
            is_lum = p1 in ("Sun","Moon") or p2 in ("Sun","Moon")
            r = _aspect_between(longs[p1], longs[p2], is_luminary=is_lum)
            if r:
                aspects.append({"p1": p1, "p2": p2, "aspect": r[0], "separation": r[1]})
    sun_sign  = tropical_positions["Sun"]["sign"]
    moon_sign = tropical_positions["Moon"]["sign"]
    return {
        "sun_sign": sun_sign, "sun_element": ELEMENTS[sun_sign],
        "sun_modality": MODALITIES[sun_sign],
        "moon_sign": moon_sign, "moon_element": ELEMENTS[moon_sign],
        "rising_sign": asc_sign, "rising_element": ELEMENTS[asc_sign],
        "rising_modality": MODALITIES[asc_sign], "rising_ruler": RULERS[asc_sign],
        "ascendant_longitude": asc, "ascendant_dms": format_dms(asc % 30),
        "planets": tropical_positions, "aspects": aspects,
    }


# ══════════════════════════════════════════════════════════════════════════
# RECTIFICATION — event-based BTR (PUBLIC API)
# ══════════════════════════════════════════════════════════════════════════

EVENT_SIGNIFICATORS = {
    "marriage":    {"planets":["Venus","Moon"],          "houses":[7]},
    "child":       {"planets":["Jupiter"],               "houses":[5]},
    "career":      {"planets":["Sun","Saturn"],          "houses":[10]},
    "promotion":   {"planets":["Sun","Jupiter"],         "houses":[10,11]},
    "accident":    {"planets":["Mars","Saturn","Rahu"],  "houses":[8,6]},
    "parent_loss": {"planets":["Sun","Moon"],            "houses":[4,9]},
    "education":   {"planets":["Mercury","Jupiter"],     "houses":[4,5]},
    "property":    {"planets":["Mars","Venus"],          "houses":[4]},
    "travel":      {"planets":["Mercury","Rahu"],        "houses":[3,12]},
}


def _score_event(event_date, life_area, vim_periods, house_lord_map) -> float:
    sig = EVENT_SIGNIFICATORS.get(life_area)
    if not sig: return 0.0
    md_lord = ad_lord = None
    for md in vim_periods:
        if md.start <= event_date <= md.end:
            md_lord = md.lord
            for ad in md.children:
                if ad.start <= event_date <= ad.end:
                    ad_lord = ad.lord
                    break
            break
    if not md_lord: return 0.0
    score = 0.0
    significator_planets = set(sig["planets"])
    significator_houses = sig["houses"]
    for h in significator_houses:
        if h in house_lord_map:
            significator_planets.add(house_lord_map[h])
    if md_lord in significator_planets: score += 3.0
    if ad_lord in significator_planets: score += 2.0
    return score


def rectify(chart, events: list[dict],
            window_minutes: int = 60, step_minutes: int = 1) -> dict:
    """Public — find best birth-time offset (±window_minutes) explaining events."""
    if not events:
        return {"best_offset_minutes": 0.0, "best_score": 0.0,
                "scores": [], "confidence": "low"}
    ls = chart.lagna.sign_index
    house_lord_map = {h: SIGN_LORDS_MAP[(ls + h - 1) % 12] for h in range(1, 13)}
    base_dt = chart.datetime_local
    moon_lon_base = chart.planets["Moon"].longitude
    scores: list[tuple[float, float]] = []
    for offset_min in range(-window_minutes, window_minutes + 1, step_minutes):
        candidate_dt = base_dt + timedelta(minutes=offset_min)
        moon_shift = offset_min * 0.00915
        moon_lon = (moon_lon_base + moon_shift) % 360
        try:
            periods = _build(candidate_dt, moon_lon)
        except Exception:
            continue
        total = sum(_score_event(ev["date"], ev["area"], periods, house_lord_map)
                    for ev in events)
        scores.append((offset_min, total))
    if not scores:
        return {"best_offset_minutes": 0.0, "best_score": 0.0,
                "scores": [], "confidence": "low"}
    scores.sort(key=lambda x: x[1], reverse=True)
    best_offset, best_score = scores[0]
    max_possible = len(events) * 5.0
    confidence = "high" if best_score >= 0.7 * max_possible else (
                 "medium" if best_score >= 0.4 * max_possible else "low")
    return {
        "best_offset_minutes": float(best_offset),
        "best_score": best_score, "max_possible": max_possible,
        "scores": scores, "confidence": confidence,
    }
