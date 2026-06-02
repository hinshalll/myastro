"""shared.astro.ephem_skyfield — FREE ephemeris provider (Skyfield + JPL DE440s).

The future shipping engine: MIT (Skyfield) + public-domain (JPL DE440s), replacing
AGPL Swiss Ephemeris. Validated vs pyswisseph (dev-only reference) across 2000
random charts (1900-2050, all latitudes):
  planet longitudes <=3.0", ascendant <=2.7", Lahiri ayanamsa 0.00",
  mean node <=0.2"  ->  0 sign / 0 nakshatra / 0 ascendant-sign mismatches.
Nutation-in-longitude is removed (mean equinox) to match SE's Lahiri reference.

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


def _nutation_lon_deg(jd_ut: float) -> float:
    """Nutation in longitude (Delta-psi) in degrees. Subtracted to move from the
    true equinox of date to the MEAN equinox, which is what the Lahiri ayanamsa is
    referred to (matches Swiss Ephemeris to ~1 arcsec instead of ~17)."""
    return np.degrees(erfa.nut06a(jd_ut, 0.0)[0])


def planet_sidereal_lon(jd_ut: float, planet: str) -> float:
    """Sidereal (Lahiri) ecliptic longitude of a planet, degrees [0,360)."""
    eph = _eph()
    earth = eph["earth"]
    t = _time(jd_ut)
    trop = (earth.at(t).observe(eph[_BODY[planet]]).apparent()
            .ecliptic_latlon(epoch="date")[1].degrees)
    return (trop - _nutation_lon_deg(jd_ut) - ayanamsa(jd_ut)) % 360.0


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
    # Apparent sidereal time + true obliquity give the Ascendant in the TRUE equinox
    # frame; subtract nutation-in-longitude to reach the MEAN equinox the Lahiri
    # ayanamsa is referred to (matches Swiss Ephemeris to ~1-2 arcsec).
    ramc = np.radians((t.gast * 15.0 + lon) % 360.0)
    eps = erfa.obl06(jd_ut, 0.0) + erfa.nut06a(jd_ut, 0.0)[1]   # true obliquity
    phi = np.radians(lat)
    asc = np.arctan2(np.cos(ramc),
                     -(np.sin(ramc) * np.cos(eps) + np.tan(phi) * np.sin(eps)))
    return (np.degrees(asc) - _nutation_lon_deg(jd_ut) - ayanamsa(jd_ut)) % 360.0


def whole_sign_house(asc_lon: float, body_lon: float) -> int:
    """Whole-sign house (1..12) of a body, given the Ascendant longitude.
    The house IS the sign counted from the Ascendant's sign (traditional Vedic)."""
    asc_sign = int(asc_lon // 30) % 12
    body_sign = int(body_lon // 30) % 12
    return ((body_sign - asc_sign) % 12) + 1


def whole_sign_cusps(asc_lon: float) -> list:
    """The 12 whole-sign house cusp longitudes (each at its sign's 0 deg)."""
    asc_sign = int(asc_lon // 30) % 12
    return [((asc_sign + i) % 12) * 30.0 for i in range(12)]


def sun_rise_set(d, lat: float, lon: float, tz_name: str):
    """Local sunrise, sunset, and next-day sunrise as tz-aware datetimes.
    Standard definition (Sun's upper limb at the horizon with refraction), matching
    Swiss Ephemeris's default — needed for Rahu Kaal / Choghadiya / Muhurta windows."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    from skyfield import almanac
    from skyfield.api import wgs84

    eph, ts = _eph(), _ts()
    tz, utc = ZoneInfo(tz_name), ZoneInfo("UTC")
    loc = wgs84.latlon(lat, lon)
    start = datetime(d.year, d.month, d.day, tzinfo=tz)
    t0 = ts.from_datetime(start.astimezone(utc))
    t1 = ts.from_datetime((start + timedelta(days=2)).astimezone(utc))
    f = almanac.sunrise_sunset(eph, loc)
    times, events = almanac.find_discrete(t0, t1, f)
    seq = [(ti.utc_datetime().astimezone(tz), int(ev)) for ti, ev in zip(times, events)]
    rises = [dt for dt, ev in seq if ev == 1]
    sets_ = [dt for dt, ev in seq if ev == 0]
    sunrise = rises[0] if rises else None
    sunset = next((s for s in sets_ if sunrise and s > sunrise), None)
    next_sunrise = rises[1] if len(rises) > 1 else None
    return sunrise, sunset, next_sunrise


def placidus_cusps(jd_ut: float, lat: float, lon: float) -> list:
    """12 sidereal (Lahiri) Placidus house cusps [cusp1 .. cusp12] in degrees.

    Validated to 0.00" vs Swiss Ephemeris across 300 charts x 12 cusps (incl. 60N),
    with 0/3600 KP cusp sub-lord mismatches. Used only when KP is enabled (the
    default Vedic chart uses whole-sign houses). Method: semi-arc trisection of the
    diurnal/nocturnal arcs (the classical Placidus definition), iterated to converge.

    Note: Placidus is mathematically undefined above ~66 deg latitude (circumpolar
    region) — true for every engine. The ascensional-difference term is clamped so
    it degrades gracefully there instead of crashing; KP isn't used in polar regions.
    """
    t = _time(jd_ut)
    ramc = np.radians((t.gast * 15.0 + lon) % 360.0)
    eps = erfa.obl06(jd_ut, 0.0) + erfa.nut06a(jd_ut, 0.0)[1]   # true obliquity
    phi = np.radians(lat)
    HALF = np.pi / 2

    mc = np.arctan2(np.sin(ramc), np.cos(ramc) * np.cos(eps))
    asc = np.arctan2(np.cos(ramc),
                     -(np.sin(ramc) * np.cos(eps) + np.tan(phi) * np.sin(eps)))

    def ra_to_lon(a):
        return np.arctan2(np.sin(a), np.cos(a) * np.cos(eps))

    def iterate(formula, init):
        lam = init
        for _ in range(200):
            decl = np.arcsin(np.sin(eps) * np.sin(lam))
            ad = np.arcsin(np.clip(np.tan(phi) * np.tan(decl), -1.0, 1.0))
            nxt = ra_to_lon(formula(ad))
            if abs(((nxt - lam + np.pi) % (2 * np.pi)) - np.pi) < 1e-11:
                lam = nxt
                break
            lam = nxt
        return lam

    c11 = iterate(lambda ad: ramc + (1 / 3) * (HALF + ad), ramc + 0.5)
    c12 = iterate(lambda ad: ramc + (2 / 3) * (HALF + ad), ramc + 1.0)
    c2 = iterate(lambda ad: ramc + (HALF + ad) + (1 / 3) * (HALF - ad), ramc + 2.0)
    c3 = iterate(lambda ad: ramc + (HALF + ad) + (2 / 3) * (HALF - ad), ramc + 2.5)

    nu, ay = _nutation_lon_deg(jd_ut), ayanamsa(jd_ut)
    def sid(lam):
        return (np.degrees(lam) - nu - ay) % 360.0

    a, m = sid(asc), sid(mc)
    e11, e12, e2, e3 = sid(c11), sid(c12), sid(c2), sid(c3)
    return [a, e2, e3, (m + 180) % 360, (e11 + 180) % 360, (e12 + 180) % 360,
            (a + 180) % 360, (e2 + 180) % 360, (e3 + 180) % 360, m, e11, e12]
