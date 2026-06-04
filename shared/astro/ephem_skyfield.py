"""shared.astro.ephem_skyfield — FREE ephemeris provider (Skyfield + JPL DE440s).

The future shipping engine: MIT (Skyfield) + public-domain (JPL DE440s), replacing
AGPL Swiss Ephemeris. Validated vs pyswisseph (dev-only reference) across 2000
random charts (1900-2050, all latitudes):
  planet longitudes <=3.0", ascendant <=2.7", Lahiri ayanamsa 0.00",
  mean node <=0.2"  ->  0 sign / 0 nakshatra / 0 ascendant-sign mismatches.
Nutation-in-longitude is removed (mean equinox) to match SE's Lahiri reference.

Conventions (locked, see docs/ephemeris-decision.md): Lahiri (Chitrapaksha)
ayanamsa, sidereal, Mean lunar node, whole-sign houses (Ascendant below).

Lahiri anchor A0 is FROZEN to the exact Swiss Ephemeris value at J2000 (see
`_LAHIRI_A0` below); no SE import in the shipping runtime. The whole app reaches
these helpers through the adapter seam (shared.astro.ephemeris), never directly.

Requires: skyfield, jplephem, pyerfa, numpy (+ a JPL kernel `de440s.bsp`).
"""
from __future__ import annotations

import functools
import os

import numpy as np
import erfa
from skyfield.api import load

_J2000 = 2451545.0
# Ayanamsa anchors at J2000.0 (degrees) — FROZEN to the exact values Swiss
# Ephemeris returns for each SIDM_* mode at JD 2451545.0. The runtime ayanamsa
# for any other date is anchor + IAU-2006 general precession in longitude
# (computed by pyERFA). All five are precession-based and differ ONLY by their
# J2000 anchor, so the SAME precession term serves every one — validated to
# ~0.00" vs Swiss Ephemeris across 1900-2050. The shipping engine never imports
# swisseph: these constants were derived once at dev time (see scripts) and frozen.
_AYANAMSA_ANCHORS = {
    "lahiri":        23.857092353708822,   # Chitrapaksha — Govt of India standard (default)
    "raman":         22.410791040326500,   # B.V. Raman
    "krishnamurti":  23.760240040326494,   # KP (Krishnamurti Paddhati)
    "yukteshwar":    22.478803027808170,   # Sri Yukteshwar
    "fagan_bradley": 24.740299994434963,   # Fagan/Bradley (Western sidereal)
}
_DEFAULT_AYANAMSA = "lahiri"
# Back-compat alias (some external scripts referenced the single Lahiri anchor).
_LAHIRI_A0 = _AYANAMSA_ANCHORS["lahiri"]

# DE440s names planets' barycenters for the outer/Mars bodies.
_BODY = {
    "Sun": "sun", "Moon": "moon", "Mercury": "mercury", "Venus": "venus",
    "Mars": "mars barycenter", "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    # Outer planets (Western appendix only; not classical Vedic grahas)
    "Uranus": "uranus barycenter", "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter",
}

_KERNEL = os.environ.get("JPL_KERNEL", "de440s.bsp")


def _A0(mode: str = _DEFAULT_AYANAMSA) -> float:
    """J2000 anchor for the given ayanamsha mode. Frozen to the exact Swiss
    Ephemeris value (see _AYANAMSA_ANCHORS). Unknown modes fall back to Lahiri.
    No SE import in the shipping runtime."""
    return _AYANAMSA_ANCHORS.get((mode or _DEFAULT_AYANAMSA).lower(),
                                 _AYANAMSA_ANCHORS[_DEFAULT_AYANAMSA])


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


def ayanamsa(jd_ut: float, mode: str = _DEFAULT_AYANAMSA) -> float:
    """Ayanamsa in degrees for `mode` = anchor + IAU-2006 general precession in
    longitude from J2000. Matches Swiss Ephemeris to ~0.00\" for all five
    supported modes (lahiri, raman, krishnamurti, yukteshwar, fagan_bradley).
    Default = lahiri (Chitrapaksha). Returns a plain Python float."""
    return float(_A0(mode) + np.degrees(erfa.p06e(jd_ut, 0.0)[12]))


# ── Calendar helpers (pure math — no ephemeris kernel needed) ──────────────

def julday(year: int, month: int, day: int, hour: float = 0.0) -> float:
    """UT Julian Day for a Gregorian date (Meeus, Astronomical Algorithms).
    Drop-in replacement for `swe.julday` — bit-exact match for all post-1582
    Gregorian dates. `hour` is a fractional 0-24 value (e.g. 13.5 = 13:30)."""
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return (int(365.25 * (year + 4716)) + int(30.6001 * (month + 1))
            + day + hour / 24.0 + b - 1524.5)


def jd_to_utc(jd_ut: float):
    """UT Julian Day → tz-aware datetime in UTC. Inverse of julday.
    Drop-in replacement for swe.revjul (returns a datetime instead of tuple)."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    jd = jd_ut + 0.5
    z = int(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day_f = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    day = int(day_f)
    sec_total = (day_f - day) * 86400.0
    base = datetime(year, month, day, tzinfo=ZoneInfo("UTC"))
    return base + timedelta(seconds=sec_total)


def _nutation_lon_deg(jd_ut: float) -> float:
    """Nutation in longitude (Delta-psi) in degrees. Subtracted to move from the
    true equinox of date to the MEAN equinox, which is what the Lahiri ayanamsa is
    referred to (matches Swiss Ephemeris to ~1 arcsec instead of ~17)."""
    return np.degrees(erfa.nut06a(jd_ut, 0.0)[0])


def _planet_ecliptic_latlon_of_date(jd_ut: float, planet: str):
    """Internal: apparent (true equinox of date) geocentric ecliptic (lat, lon)
    of a planet in degrees. Shared by tropical + sidereal helpers."""
    eph = _eph()
    t = _time(jd_ut)
    pos = eph["earth"].at(t).observe(eph[_BODY[planet]]).apparent().ecliptic_latlon(epoch="date")
    return float(pos[0].degrees), float(pos[1].degrees)


def planet_tropical_lon(jd_ut: float, planet: str) -> float:
    """Tropical (apparent of-date) ecliptic longitude of a planet, degrees [0,360).

    Matches Swiss Ephemeris's default `swe.calc_ut(jd, pid, FLG_SWIEPH)` (no
    sidereal flag) to ~3" — the Western/tropical chart's reference longitude."""
    return _planet_ecliptic_latlon_of_date(jd_ut, planet)[1] % 360.0


def planet_tropical_lon_speed(jd_ut: float, planet: str):
    """(tropical longitude, speed deg/day). Speed via 1-hour central difference."""
    dt = 1.0 / 24.0
    l1 = planet_tropical_lon(jd_ut - dt / 2, planet)
    l2 = planet_tropical_lon(jd_ut + dt / 2, planet)
    speed = ((l2 - l1 + 180) % 360 - 180) / dt
    return planet_tropical_lon(jd_ut, planet), speed


def planet_ecliptic_lat(jd_ut: float, planet: str) -> float:
    """Apparent geocentric ecliptic latitude in degrees [-90,90]. Same value
    for tropical and sidereal callers — latitude is unaffected by the ayanamsa
    shift along the ecliptic. Used by Graha Yuddha (planetary war winner is the
    body with the higher ecliptic latitude)."""
    return _planet_ecliptic_latlon_of_date(jd_ut, planet)[0]


def planet_sidereal_lon(jd_ut: float, planet: str, mode: str = _DEFAULT_AYANAMSA) -> float:
    """Sidereal ecliptic longitude of a planet, degrees [0,360), in ayanamsha
    `mode` (default lahiri). Returns a plain Python float."""
    trop = planet_tropical_lon(jd_ut, planet)
    return float((trop - _nutation_lon_deg(jd_ut) - ayanamsa(jd_ut, mode)) % 360.0)


def planet_sidereal_lon_speed(jd_ut: float, planet: str, mode: str = _DEFAULT_AYANAMSA):
    """(sidereal longitude, speed deg/day). Speed via 1-hour central difference.
    Speed is ayanamsha-independent, but computed consistently in `mode`.
    Both returned as plain Python floats."""
    dt = 1.0 / 24.0
    l1 = planet_sidereal_lon(jd_ut - dt / 2, planet, mode)
    l2 = planet_sidereal_lon(jd_ut + dt / 2, planet, mode)
    speed = ((l2 - l1 + 180) % 360 - 180) / dt
    return planet_sidereal_lon(jd_ut, planet, mode), float(speed)


def _mean_node_mean_of_date(jd_ut: float) -> float:
    """Internal: Mean lunar node longitude (Meeus polynomial), referred to the
    MEAN equinox of date — the frame the Lahiri ayanamsa is referred to.
    Sidereal Rahu = this - ayanamsa."""
    T = (jd_ut - _J2000) / 36525.0
    om = (125.0445479 - 1934.1362891 * T + 0.0020754 * T * T
          + T ** 3 / 467441 - T ** 4 / 60616000)
    return om % 360.0


def mean_node_tropical(jd_ut: float) -> float:
    """Apparent tropical (true equinox of date) longitude of the Mean lunar
    node (Rahu) in degrees [0,360). Matches Swiss Ephemeris's default
    `swe.calc_ut(jd, MEAN_NODE, FLG_SWIEPH)` (which includes nutation) to <1\"."""
    return float((_mean_node_mean_of_date(jd_ut) + _nutation_lon_deg(jd_ut)) % 360.0)


def mean_node_sidereal(jd_ut: float, mode: str = _DEFAULT_AYANAMSA) -> float:
    """Sidereal longitude of the Mean lunar node (Rahu) in ayanamsha `mode`.
    Ketu = +180. Computed in the mean-of-date frame the ayanamsa is referred to."""
    return float((_mean_node_mean_of_date(jd_ut) - ayanamsa(jd_ut, mode)) % 360.0)


def _true_node_apparent_of_date(jd_ut: float) -> float:
    """Osculating (TRUE) ascending node of the Moon's instantaneous orbit, as an
    apparent (true equinox of date) ecliptic longitude in degrees [0,360).

    Method: the line of nodes is where the orbital plane meets the ecliptic. The
    orbital-plane normal is h = r x (dr/dt); the ascending-node direction is
    z_hat x h, so its longitude is atan2(h_x, -h_y). We use the Moon's apparent
    geocentric ecliptic-of-date direction (distance cancels for plane geometry)
    and a 1-hour central difference for the rate. Matches Swiss Ephemeris
    TRUE_NODE to ~48 arcsec (0.013 deg) over 500 charts — the usual definitional
    spread for the osculating node between software, far below any sign/nakshatra
    boundary. The MEAN node (the default) stays exact to ~0.17". True node is an
    opt-in toggle (config.node_type()='true'), not the default."""
    dt = 1.0 / 24.0  # 1 hour, in days

    def _unit(j: float):
        beta_deg, lam_deg = _planet_ecliptic_latlon_of_date(j, "Moon")
        b = np.radians(beta_deg)
        l = np.radians(lam_deg)
        cb = np.cos(b)
        return np.array([cb * np.cos(l), cb * np.sin(l), np.sin(b)])

    r0 = _unit(jd_ut)
    vel = (_unit(jd_ut + dt / 2) - _unit(jd_ut - dt / 2)) / dt
    h = np.cross(r0, vel)
    return float(np.degrees(np.arctan2(h[0], -h[1])) % 360.0)


def true_node_tropical(jd_ut: float) -> float:
    """Apparent tropical (true equinox of date) longitude of the TRUE (osculating)
    lunar node (Rahu) in degrees [0,360). Ketu = +180."""
    return _true_node_apparent_of_date(jd_ut)


def true_node_sidereal(jd_ut: float, mode: str = _DEFAULT_AYANAMSA) -> float:
    """Sidereal longitude of the TRUE (osculating) lunar node (Rahu) in ayanamsha
    `mode`. Ketu = +180. Nutation removed to the mean equinox the ayanamsa uses,
    mirroring planet_sidereal_lon."""
    return float((_true_node_apparent_of_date(jd_ut)
                  - _nutation_lon_deg(jd_ut) - ayanamsa(jd_ut, mode)) % 360.0)


def _ascendant_rad(jd_ut: float, lat: float, lon: float) -> float:
    """Internal: Ascendant in radians, true-equinox-of-date frame (apparent).
    Shared by tropical_ascendant + ascendant_sidereal + Placidus."""
    t = _time(jd_ut)
    ramc = np.radians((t.gast * 15.0 + lon) % 360.0)
    eps = erfa.obl06(jd_ut, 0.0) + erfa.nut06a(jd_ut, 0.0)[1]   # true obliquity
    phi = np.radians(lat)
    return np.arctan2(np.cos(ramc),
                      -(np.sin(ramc) * np.cos(eps) + np.tan(phi) * np.sin(eps)))


def tropical_ascendant(jd_ut: float, lat: float, lon: float) -> float:
    """Tropical (apparent of-date) Ascendant longitude, degrees [0,360).
    Used for Western chart computations — matches Swiss Ephemeris's default
    tropical Ascendant (no SIDEREAL flag) to ~1-2 arcsec."""
    return float(np.degrees(_ascendant_rad(jd_ut, lat, lon)) % 360.0)


def ascendant_sidereal(jd_ut: float, lat: float, lon: float,
                       mode: str = _DEFAULT_AYANAMSA) -> float:
    """Sidereal Ascendant (Lagna) longitude, degrees, in ayanamsha `mode`
    (default lahiri). Whole-sign houses follow directly from the Asc's sign.

    The apparent (true-equinox-of-date) Ascendant is shifted by -nutation_lon
    (true→mean equinox) then -ayanamsa (mean tropical→sidereal); matches Swiss
    Ephemeris to ~1-2 arcsec. Returns a plain Python float."""
    return float((np.degrees(_ascendant_rad(jd_ut, lat, lon))
                  - _nutation_lon_deg(jd_ut) - ayanamsa(jd_ut, mode)) % 360.0)


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


def _placidus_intermediates_rad(jd_ut: float, lat: float, lon: float):
    """Internal: solve the four Placidus intermediate cusps + Asc + MC in the
    true-equinox-of-date frame (radians). Method: semi-arc trisection of the
    diurnal/nocturnal arcs (classical Placidus), iterated to converge.

    Returns (asc, mc, c11, c12, c2, c3) all in radians. Shared by both
    tropical_placidus_cusps and placidus_cusps.

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
    return asc, mc, c11, c12, c2, c3


def _assemble_12_placidus_cusps(asc_deg, mc_deg, c11_deg, c12_deg, c2_deg, c3_deg):
    """Internal: assemble the 12 cusps from Asc, MC, and the 4 intermediates
    (all in degrees, same reference frame). Cusps 7-12 are the +180 mirrors.
    Returns a list of plain Python floats."""
    a, m = asc_deg % 360.0, mc_deg % 360.0
    e11, e12, e2, e3 = c11_deg % 360.0, c12_deg % 360.0, c2_deg % 360.0, c3_deg % 360.0
    return [float(x) for x in
            (a, e2, e3, (m + 180) % 360, (e11 + 180) % 360, (e12 + 180) % 360,
             (a + 180) % 360, (e2 + 180) % 360, (e3 + 180) % 360, m, e11, e12)]


def tropical_placidus_cusps(jd_ut: float, lat: float, lon: float) -> list:
    """12 tropical (apparent of-date) Placidus house cusps in degrees.
    Used for Western chart computations. Matches Swiss Ephemeris's default
    tropical Placidus cusps (no SIDEREAL flag) to <1\"."""
    asc, mc, c11, c12, c2, c3 = _placidus_intermediates_rad(jd_ut, lat, lon)
    return _assemble_12_placidus_cusps(
        np.degrees(asc), np.degrees(mc), np.degrees(c11),
        np.degrees(c12), np.degrees(c2), np.degrees(c3))


def placidus_cusps(jd_ut: float, lat: float, lon: float,
                   mode: str = _DEFAULT_AYANAMSA) -> list:
    """12 sidereal Placidus house cusps [cusp1 .. cusp12] in degrees, in
    ayanamsha `mode` (default lahiri).

    Validated to 0.00" vs Swiss Ephemeris across 300 charts x 12 cusps (incl. 60N),
    with 0/3600 KP cusp sub-lord mismatches. Used only when KP is enabled (the
    default Vedic chart uses whole-sign houses).

    Same intermediate math as tropical_placidus_cusps, then each cusp is shifted
    from true-equinox-of-date by -nutation_lon (→ mean equinox) and -ayanamsa
    (mean tropical → sidereal).
    """
    asc, mc, c11, c12, c2, c3 = _placidus_intermediates_rad(jd_ut, lat, lon)
    nu, ay = _nutation_lon_deg(jd_ut), ayanamsa(jd_ut, mode)
    sid = lambda x: np.degrees(x) - nu - ay
    return _assemble_12_placidus_cusps(
        sid(asc), sid(mc), sid(c11), sid(c12), sid(c2), sid(c3))


def moon_rise_set(d, lat: float, lon: float, tz_name: str):
    """Local moonrise, moonset (next after rise) as tz-aware datetimes.
    Topocentric (includes lunar parallax + refraction), matching Swiss Ephemeris."""
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
    # radius_degrees ~0.25 = Moon's apparent semidiameter (upper-limb rise/set,
    # matching Swiss Ephemeris's convention).
    f = almanac.risings_and_settings(eph, eph["moon"], loc, radius_degrees=0.25)
    times, events = almanac.find_discrete(t0, t1, f)
    seq = [(ti.utc_datetime().astimezone(tz), int(ev)) for ti, ev in zip(times, events)]
    rises = [dt for dt, ev in seq if ev == 1]
    sets_ = [dt for dt, ev in seq if ev == 0]
    moonrise = rises[0] if rises else None
    moonset = next((s for s in sets_ if moonrise and s > moonrise), None)
    return moonrise, moonset


def next_eclipses(from_date, horizon_days: int = 400):
    """(next_solar_date, next_lunar_date) on/after from_date, searching forward.
    Lunar via Skyfield eclipselib; solar (global) via a new-moon-near-node test
    (the Moon's ecliptic latitude at conjunction within the solar eclipse limit).
    Dates are UTC — for an alert card, day-level precision is what matters."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    from skyfield import almanac, eclipselib

    eph, ts = _eph(), _ts()
    d0 = datetime(from_date.year, from_date.month, from_date.day, tzinfo=ZoneInfo("UTC"))
    t0 = ts.from_datetime(d0)
    t1 = ts.from_datetime(d0 + timedelta(days=horizon_days))

    lt, _ly, _det = eclipselib.lunar_eclipses(t0, t1, eph)
    next_lunar = lt[0].utc_datetime().date() if len(lt.tt) else None

    next_solar = None
    earth = eph["earth"]
    pt, pp = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    for i in range(len(pp)):
        if int(pp[i]) == 0:  # new moon
            ti = pt[i]
            beta = earth.at(ti).observe(eph["moon"]).apparent().ecliptic_latlon()[0].degrees
            if abs(beta) < 1.5:  # within the solar-eclipse ecliptic limit
                next_solar = ti.utc_datetime().date()
                break
    return next_solar, next_lunar


def next_eclipse(from_date, horizon_days: int = 30):
    """Soonest single eclipse (solar OR lunar) on/after `from_date` — whichever
    is sooner. Returns a dict:
        {present, type, date, days_until, sutak_hours}
    where `type` is 'Surya Grahan' (solar, sutak 12h) or 'Chandra Grahan'
    (lunar, sutak 9h). `present` is True only if the eclipse falls within
    `horizon_days`. Dates are UTC — for an alert card, day-level is enough.

    Convenience wrapper over next_eclipses() that picks the nearest event."""
    search_horizon = max(horizon_days, 400)
    next_solar, next_lunar = next_eclipses(from_date, horizon_days=search_horizon)
    candidates = []
    if next_solar is not None:
        candidates.append(("Surya Grahan", next_solar, 12))
    if next_lunar is not None:
        candidates.append(("Chandra Grahan", next_lunar, 9))
    if not candidates:
        return {"present": False, "type": None, "date": None,
                "days_until": None, "sutak_hours": None}
    etype, edate, sutak_hours = min(candidates, key=lambda x: x[1])
    days_until = (edate - from_date).days
    return {
        "present": 0 <= days_until <= horizon_days,
        "type": etype, "date": edate,
        "days_until": days_until, "sutak_hours": sutak_hours,
    }
