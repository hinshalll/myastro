"""shared.astro.ephemeris — THE single ephemeris interface the app should call.

Goal of the "adapter seam": the rest of the app calls THESE functions, never
`swisseph` or `skyfield` directly — so the engine is swappable in exactly one place.

Provider is chosen by the env var EPHEMERIS_PROVIDER:
  * "skyfield"  (DEFAULT) — the free, owned engine (Skyfield + JPL + pyERFA).
                Validated 0-mismatch vs Swiss Ephemeris (see docs/ephemeris-decision.md).
  * "swisseph"  — Swiss Ephemeris (AGPL/paid). Use only if you buy the SE license
                later, or to cross-validate. Set EPHEMERIS_PROVIDER=swisseph.

Conventions (both providers): sidereal, Lahiri (Chitrapaksha) ayanamsa, **Mean node**
for Rahu/Ketu, whole-sign houses by default (Placidus available for KP).

INTEGRATION NOTE (next step): `shared/astro/astro_calc.py` + `kundli.py` still call
`swe` directly. Reroute their low-level helpers to call this module so the whole app
runs on the chosen provider. This file is additive and changes nothing until then.
"""
from __future__ import annotations

import os

from shared.astro import ephem_skyfield as _sky
from shared.astro import config as _config

_PROVIDER = os.environ.get("EPHEMERIS_PROVIDER", "skyfield").lower()

# Supported sidereal ayanamshas. The Skyfield engine implements all five
# (frozen J2000 anchors + shared IAU-2006 precession). Default = lahiri.
DEFAULT_AYANAMSHA = "lahiri"
SUPPORTED_AYANAMSHAS = ("lahiri", "raman", "krishnamurti", "yukteshwar", "fagan_bradley")

_SWE_IDS = {}
_SWE_SIDM = {}  # ayanamsha name → swe.SIDM_* (only built under the swisseph provider)


def provider() -> str:
    return _PROVIDER


def _swe(mode: str = DEFAULT_AYANAMSHA):
    """Swiss Ephemeris handle (cross-validation provider only). Sets the sidereal
    mode for `mode` so the swisseph branch honours the requested ayanamsha."""
    import swisseph as swe
    if not _SWE_IDS:
        _SWE_IDS.update({
            "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
            "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
        })
        _SWE_SIDM.update({
            "lahiri": swe.SIDM_LAHIRI, "raman": swe.SIDM_RAMAN,
            "krishnamurti": swe.SIDM_KRISHNAMURTI, "yukteshwar": swe.SIDM_YUKTESHWAR,
            "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
        })
    swe.set_sid_mode(_SWE_SIDM.get((mode or DEFAULT_AYANAMSHA).lower(), swe.SIDM_LAHIRI))
    return swe


# ── Core numeric calculations (both providers; engine-swap matters here) ──────

def ayanamsa(jd_ut: float, mode: str = DEFAULT_AYANAMSHA) -> float:
    if _PROVIDER == "swisseph":
        return float(_swe(mode).get_ayanamsa_ut(jd_ut))
    return _sky.ayanamsa(jd_ut, mode)


def planet_lon(jd_ut: float, planet: str, mode: str = DEFAULT_AYANAMSHA) -> float:
    if _PROVIDER == "swisseph":
        swe = _swe(mode)
        r, _ = swe.calc_ut(jd_ut, _SWE_IDS[planet], swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        return r[0] % 360.0
    return _sky.planet_sidereal_lon(jd_ut, planet, mode)


def planet_lon_speed(jd_ut: float, planet: str, mode: str = DEFAULT_AYANAMSHA):
    if _PROVIDER == "swisseph":
        swe = _swe(mode)
        r, _ = swe.calc_ut(jd_ut, _SWE_IDS[planet],
                           swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
        return r[0] % 360.0, r[3]
    return _sky.planet_sidereal_lon_speed(jd_ut, planet, mode)


def planet_lat(jd_ut: float, planet: str) -> float:
    """Apparent geocentric ecliptic latitude in degrees [-90,90].
    Same for tropical and sidereal — used for Graha Yuddha (planetary war
    winner is whoever has higher latitude)."""
    if _PROVIDER == "swisseph":
        swe = _swe()
        r, _ = swe.calc_ut(jd_ut, _SWE_IDS[planet], swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        return float(r[1])
    return _sky.planet_ecliptic_lat(jd_ut, planet)


def planet_lon_tropical(jd_ut: float, planet: str) -> float:
    """Tropical (apparent of-date) planet longitude in degrees [0,360).
    Used for Western chart computations."""
    if _PROVIDER == "swisseph":
        swe = _swe()
        r, _ = swe.calc_ut(jd_ut, _SWE_IDS[planet], swe.FLG_SWIEPH)
        return r[0] % 360.0
    return _sky.planet_tropical_lon(jd_ut, planet)


def planet_lon_speed_tropical(jd_ut: float, planet: str):
    """(tropical longitude, speed deg/day) — for Western charts."""
    if _PROVIDER == "swisseph":
        swe = _swe()
        r, _ = swe.calc_ut(jd_ut, _SWE_IDS[planet], swe.FLG_SWIEPH | swe.FLG_SPEED)
        return r[0] % 360.0, r[3]
    return _sky.planet_tropical_lon_speed(jd_ut, planet)


def node_lon(jd_ut: float, mode: str = DEFAULT_AYANAMSHA,
             node_type: str | None = None) -> float:
    """Lunar node (Rahu), sidereal. Ketu = +180.

    node_type: 'mean' (default convention, matches Indian panchangs) or 'true'
    (osculating). None -> the backend default from shared.astro.config.node_type()
    (currently 'mean'). The frontend may hide the choice; the engine keeps both."""
    nt = (node_type or _config.node_type()).lower()
    if _PROVIDER == "swisseph":
        swe = _swe(mode)
        nid = swe.TRUE_NODE if nt == "true" else swe.MEAN_NODE
        r, _ = swe.calc_ut(jd_ut, nid, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        return r[0] % 360.0
    if nt == "true":
        return _sky.true_node_sidereal(jd_ut, mode)
    return _sky.mean_node_sidereal(jd_ut, mode)


def node_lon_tropical(jd_ut: float, node_type: str | None = None) -> float:
    """Lunar node (Rahu), tropical — for Western chart Rahu/Ketu.
    node_type: 'mean' (default) or 'true'. None -> config.node_type()."""
    nt = (node_type or _config.node_type()).lower()
    if _PROVIDER == "swisseph":
        swe = _swe()
        nid = swe.TRUE_NODE if nt == "true" else swe.MEAN_NODE
        r, _ = swe.calc_ut(jd_ut, nid, swe.FLG_SWIEPH)
        return r[0] % 360.0
    if nt == "true":
        return _sky.true_node_tropical(jd_ut)
    return _sky.mean_node_tropical(jd_ut)


def ascendant(jd_ut: float, lat: float, lon: float, mode: str = DEFAULT_AYANAMSHA) -> float:
    if _PROVIDER == "swisseph":
        swe = _swe(mode)
        _, ascmc = swe.houses_ex(jd_ut, lat, lon, b'W', swe.FLG_SIDEREAL)
        return ascmc[0]
    return _sky.ascendant_sidereal(jd_ut, lat, lon, mode)


def ascendant_tropical(jd_ut: float, lat: float, lon: float) -> float:
    """Tropical Ascendant (apparent of-date) in degrees [0,360). Western chart."""
    if _PROVIDER == "swisseph":
        swe = _swe()
        _, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', 0)
        return float(ascmc[0]) % 360.0
    return _sky.tropical_ascendant(jd_ut, lat, lon)


def houses(jd_ut: float, lat: float, lon: float, system: str = "whole_sign",
           mode: str = DEFAULT_AYANAMSHA) -> list:
    """12 sidereal house cusps [cusp1..cusp12]. system: 'whole_sign' (default) |
    'placidus'. mode: ayanamsha (default lahiri)."""
    hsys = b'P' if system == "placidus" else b'W'
    if _PROVIDER == "swisseph":
        swe = _swe(mode)
        cusps, _ = swe.houses_ex(jd_ut, lat, lon, hsys, swe.FLG_SIDEREAL)
        return list(cusps[:12])
    if system == "placidus":
        return _sky.placidus_cusps(jd_ut, lat, lon, mode)
    return _sky.whole_sign_cusps(_sky.ascendant_sidereal(jd_ut, lat, lon, mode))


def houses_tropical(jd_ut: float, lat: float, lon: float,
                    system: str = "placidus") -> list:
    """12 tropical house cusps [cusp1..cusp12]. system: 'placidus' (default).
    For Western charts. Whole-sign is also accepted (just uses tropical Asc)."""
    if _PROVIDER == "swisseph":
        swe = _swe()
        hsys = b'P' if system == "placidus" else b'W'
        cusps, _ = swe.houses_ex(jd_ut, lat, lon, hsys, 0)
        return list(cusps[:12])
    if system == "placidus":
        return _sky.tropical_placidus_cusps(jd_ut, lat, lon)
    return _sky.whole_sign_cusps(_sky.tropical_ascendant(jd_ut, lat, lon))


# ── Calendar helpers (pure math — engine-independent) ──────────────────────

def julday(year: int, month: int, day: int, hour: float = 0.0) -> float:
    """UT Julian Day for a Gregorian date. Drop-in replacement for swe.julday."""
    return _sky.julday(year, month, day, hour)


def jd_to_utc(jd_ut: float):
    """UT Julian Day → tz-aware datetime in UTC. Inverse of julday()."""
    return _sky.jd_to_utc(jd_ut)


# ── Rise/set + eclipses (free engine; already validated vs SE to seconds / exact dates) ──

def sun_rise_set(d, lat: float, lon: float, tz_name: str):
    return _sky.sun_rise_set(d, lat, lon, tz_name)


def moon_rise_set(d, lat: float, lon: float, tz_name: str):
    return _sky.moon_rise_set(d, lat, lon, tz_name)


def next_eclipses(from_date, horizon_days: int = 400):
    return _sky.next_eclipses(from_date, horizon_days)


def next_eclipse(from_date, horizon_days: int = 30) -> dict:
    """Soonest single eclipse (solar OR lunar) on/after from_date. Returns:
    {present, type, date, days_until, sutak_hours}. See ephem_skyfield.next_eclipse."""
    return _sky.next_eclipse(from_date, horizon_days)
