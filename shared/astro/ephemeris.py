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

_PROVIDER = os.environ.get("EPHEMERIS_PROVIDER", "skyfield").lower()

_SWE_IDS = {}


def provider() -> str:
    return _PROVIDER


def _swe():
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    if not _SWE_IDS:
        _SWE_IDS.update({
            "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
            "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
        })
    return swe


# ── Core numeric calculations (both providers; engine-swap matters here) ──────

def ayanamsa(jd_ut: float) -> float:
    if _PROVIDER == "swisseph":
        return float(_swe().get_ayanamsa_ut(jd_ut))
    return _sky.ayanamsa(jd_ut)


def planet_lon(jd_ut: float, planet: str) -> float:
    if _PROVIDER == "swisseph":
        swe = _swe()
        r, _ = swe.calc_ut(jd_ut, _SWE_IDS[planet], swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        return r[0] % 360.0
    return _sky.planet_sidereal_lon(jd_ut, planet)


def planet_lon_speed(jd_ut: float, planet: str):
    if _PROVIDER == "swisseph":
        swe = _swe()
        r, _ = swe.calc_ut(jd_ut, _SWE_IDS[planet],
                           swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
        return r[0] % 360.0, r[3]
    return _sky.planet_sidereal_lon_speed(jd_ut, planet)


def node_lon(jd_ut: float) -> float:
    """Mean lunar node (Rahu), sidereal. Ketu = +180. (Convention: Mean node.)"""
    if _PROVIDER == "swisseph":
        swe = _swe()
        r, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        return r[0] % 360.0
    return _sky.mean_node_sidereal(jd_ut)


def ascendant(jd_ut: float, lat: float, lon: float) -> float:
    if _PROVIDER == "swisseph":
        swe = _swe()
        _, ascmc = swe.houses_ex(jd_ut, lat, lon, b'W', swe.FLG_SIDEREAL)
        return ascmc[0]
    return _sky.ascendant_sidereal(jd_ut, lat, lon)


def houses(jd_ut: float, lat: float, lon: float, system: str = "whole_sign") -> list:
    """12 sidereal house cusps [cusp1..cusp12]. system: 'whole_sign' (default) | 'placidus'."""
    hsys = b'P' if system == "placidus" else b'W'
    if _PROVIDER == "swisseph":
        swe = _swe()
        cusps, _ = swe.houses_ex(jd_ut, lat, lon, hsys, swe.FLG_SIDEREAL)
        return list(cusps[:12])
    if system == "placidus":
        return _sky.placidus_cusps(jd_ut, lat, lon)
    return _sky.whole_sign_cusps(_sky.ascendant_sidereal(jd_ut, lat, lon))


# ── Rise/set + eclipses (free engine; already validated vs SE to seconds / exact dates) ──

def sun_rise_set(d, lat: float, lon: float, tz_name: str):
    return _sky.sun_rise_set(d, lat, lon, tz_name)


def moon_rise_set(d, lat: float, lon: float, tz_name: str):
    return _sky.moon_rise_set(d, lat, lon, tz_name)


def next_eclipses(from_date, horizon_days: int = 400):
    return _sky.next_eclipses(from_date, horizon_days)
