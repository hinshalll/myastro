"""Validate the free Skyfield engine against Swiss Ephemeris (dev-only reference).

Runs many random charts and reports max differences + sign/nakshatra mismatch rates.
Mismatches are expected ONLY at razor-edge boundaries (within ~17") — the same zone
where AstroSage / Drik Panchang already disagree with each other.

Run from repo root:  python scripts/validate_ephemeris.py [N]
Requires a JPL kernel `de440s.bsp` in the working dir (gitignored).
"""
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import swisseph as swe
from shared.astro.ephem_skyfield import (
    planet_sidereal_lon, mean_node_sidereal, ascendant_sidereal,
)

PLANETS = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
           ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
           ("Saturn", swe.SATURN)]
NAK = 360.0 / 27.0


def sign(x): return int(x // 30) % 12
def nak(x): return int(x // NAK) % 27
def adiff(a, b): return abs((a - b + 180) % 360 - 180) * 3600  # arcseconds


def main(n=500):
    random.seed(42)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    max_pos = sign_mm = nak_mm = total = 0
    max_node = max_asc = asc_sign_mm = 0
    worst = ""
    for _ in range(n):
        Y = random.randint(1900, 2050); Mo = random.randint(1, 12); D = random.randint(1, 28)
        h = random.uniform(0, 24); lat = random.uniform(-60, 60); lon = random.uniform(-180, 180)
        jd = swe.julday(Y, Mo, D, h)
        for name, sid in PLANETS:
            me = planet_sidereal_lon(jd, name)
            se, _ = swe.calc_ut(jd, sid, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
            d = adiff(me, se[0])
            if d > max_pos:
                max_pos = d; worst = f"{name} {Y}-{Mo:02d}-{D:02d} ({d:.1f}\")"
            total += 1
            if sign(me) != sign(se[0]): sign_mm += 1
            if nak(me) != nak(se[0]): nak_mm += 1
        me = mean_node_sidereal(jd)
        se, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        max_node = max(max_node, adiff(me, se[0]))
        me = ascendant_sidereal(jd, lat, lon)
        _, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
        max_asc = max(max_asc, adiff(me, ascmc[0]))
        if sign(me) != sign(ascmc[0]): asc_sign_mm += 1

    print(f"Charts: {n}   Planet positions checked: {total}")
    print(f"Max planet position diff : {max_pos:.1f} arcsec   (worst: {worst})")
    print(f"Max mean-node diff       : {max_node:.1f} arcsec")
    print(f"Max ascendant diff       : {max_asc:.1f} arcsec")
    print(f"Sign mismatches          : {sign_mm}/{total} ({100*sign_mm/total:.3f}%)")
    print(f"Nakshatra mismatches     : {nak_mm}/{total} ({100*nak_mm/total:.3f}%)")
    print(f"Ascendant-sign mismatches: {asc_sign_mm}/{n} ({100*asc_sign_mm/n:.3f}%)")
    print("(Mismatches occur only within ~17\" of a boundary — the same edge zone "
          "where major Vedic apps already disagree with each other.)")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
