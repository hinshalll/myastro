"""shared.astro.ephem_skyfield — FREE ephemeris provider (Skyfield + JPL DE440s).

The future shipping engine: MIT (Skyfield) + public-domain (JPL DE440s), replacing
AGPL Swiss Ephemeris. Validated vs pyswisseph (dev-only reference):
  planet sidereal longitudes ~17", Lahiri ayanamsa 0.00", mean node 0.19",
  ascendant ~17" — all far inside any sign/nakshatra boundary.

Conventions (locked, see docs/ephemeris-decision.md): Lahiri (Chitrapaksha)
ayanamsa, sidereal, Mean lunar node, whole-sign houses (Ascendant below).

NOTE (pre-launch): the Lahiri anchor A0 is currently calibrated from pyswisseph at
import for exact parity during validation. Before public launch, FREEZE A0 to the
constant `_LAHIRI_A0_FALLBACK` and remove the swisseph import so the shipping engine
is fully Swiss-Ephemeris-free. The whole app will call these via the adapter seam
(shared/astro/ephemeris.py), never swe directly.

Requires: skyfield, jplephem, pyerfa, numpy (+ a JPL kernel `de440s.bsp`).
"""
from __future__ import annotations

import functools
import os

import numpy as np
import erfa
from skyfield.api import load

_J2000 = 2451545.0
# Lahiri / Chitrapaksha ayanamsa at J2000.0 (degrees). Calibrated to Swiss Ephemeris
# during validation; freeze this exact value before launch.
_LAHIRI_A0_FALLBACK = 23.857094445

# DE440s names planets' barycenters for the outer/Mars bodies.
_BODY = {
    "Sun": "sun", "Moon": "moon", "Mercury": "mercury", "Venus": "venus",
    "Mars": "mars barycenter", "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
}

_KERNEL = os.environ.get("JPL_KERNEL", "de440s.bsp")


@functools.lru_cache(maxsize=1)
def _A0() -> float:
    """Lahiri anchor at J2000. Calibrated from pyswisseph in dev; constant fallback."""
    try:
        import swisseph as swe
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        return float(swe.get_ayanamsa_ut(_J2000))
    except Exception:
        return _LAHIRI_A0_FALLBACK


@functools.lru_cache(maxsize=1)
def _ts():
    return load.timescale()


@functools.lru_cache(maxsize=1)
def _eph():
    return load(_KERNEL)


def _time(jd_ut: float):
    ts = _ts()
    try:
        return ts.ut1_jd(jd_ut)
    except AttributeError:
        return ts.tt_jd(jd_ut)


def ayanamsa(jd_ut: float) -> float:
    """Lahiri (Chitrapaksha) ayanamsa in degrees = anchor + IAU-2006 general
    precession in longitude from J2000. Matches Swiss Ephemeris to ~0.00\"."""
    return _A0() + np.degrees(erfa.p06e(jd_ut, 0.0)[12])


def planet_sidereal_lon(jd_ut: float, planet: str) -> float:
    """Sidereal (Lahiri) ecliptic longitude of a planet, degrees [0,360)."""
    eph = _eph()
    earth = eph["earth"]
    t = _time(jd_ut)
    trop = (earth.at(t).observe(eph[_BODY[planet]]).apparent()
            .ecliptic_latlon(epoch="date")[1].degrees)
    return (trop - ayanamsa(jd_ut)) % 360.0


def planet_sidereal_lon_speed(jd_ut: float, planet: str):
    """(sidereal longitude, speed deg/day). Speed via 1-hour central difference."""
    dt = 1.0 / 24.0
    l1 = planet_sidereal_lon(jd_ut - dt / 2, planet)
    l2 = planet_sidereal_lon(jd_ut + dt / 2, planet)
    speed = ((l2 - l1 + 180) % 360 - 180) / dt
    return planet_sidereal_lon(jd_ut, planet), speed


def mean_node_sidereal(jd_ut: float) -> float:
    """Sidereal (Lahiri) longitude of the Mean lunar node (Rahu). Ketu = +180."""
    T = (jd_ut - _J2000) / 36525.0
    om = (125.0445479 - 1934.1362891 * T + 0.0020754 * T * T
          + T ** 3 / 467441 - T ** 4 / 60616000)
    return (om - ayanamsa(jd_ut)) % 360.0


def ascendant_sidereal(jd_ut: float, lat: float, lon: float) -> float:
    """Sidereal (Lahiri) Ascendant (Lagna) longitude, degrees. Whole-sign houses
    follow directly from the Ascendant's sign."""
    t = _time(jd_ut)
    ramc = np.radians((t.gast * 15.0 + lon) % 360.0)
    eps = erfa.obl06(jd_ut, 0.0) + erfa.nut06a(jd_ut, 0.0)[1]   # true obliquity
    phi = np.radians(lat)
    asc = np.arctan2(np.cos(ramc),
                     -(np.sin(ramc) * np.cos(eps) + np.tan(phi) * np.sin(eps)))
    return (np.degrees(asc) - ayanamsa(jd_ut)) % 360.0
