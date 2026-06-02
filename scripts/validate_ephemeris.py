"""Comprehensive validation of the free Skyfield engine vs Swiss Ephemeris.

Swiss Ephemeris (pyswisseph) is a DEV-ONLY reference here — never shipped.
Runs N random charts and checks every calculation the app uses:
positions, ayanamsa, mean node, ascendant, whole-sign houses, panchanga, and
all 16 divisional charts (D1-D60).

Expected result: 0 mismatches everywhere EXCEPT D60, which has an irreducible
~0.05-0.1% boundary-flip rate (its 0.5-degree slices are finer than the ~1-3"
engine residual). That is gated by birth-time precision, not the engine, and is
acceptable — see docs/ephemeris-decision.md.

Run from repo root:  python scripts/validate_ephemeris.py [N]
Requires `de440s.bsp` in the working dir (gitignored).
"""
import os
import random
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import swisseph as swe
from shared.astro.ephem_skyfield import (
    planet_sidereal_lon, ascendant_sidereal, whole_sign_house, mean_node_sidereal,
)
from shared.astro.kundli import (
    d1_si, d2_si, d3_si, d4_si, d7_si, d9_si, d10_si, d12_si,
    d16_si, d20_si, d24_si, d27_si, d30_si, d40_si, d45_si, d60_si,
)
from shared.astro.astro_calc import get_panchanga, nakshatra_info

PLANETS = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
           ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
           ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]
VARGAS = [("D1", d1_si), ("D2", d2_si), ("D3", d3_si), ("D4", d4_si), ("D7", d7_si),
          ("D9", d9_si), ("D10", d10_si), ("D12", d12_si), ("D16", d16_si),
          ("D20", d20_si), ("D24", d24_si), ("D27", d27_si), ("D30", d30_si),
          ("D40", d40_si), ("D45", d45_si), ("D60", d60_si)]
NAK = 360.0 / 27.0


def sgn(x): return int(x // 30) % 12
def nk(x): return int(x // NAK) % 27
def adiff(a, b): return abs((a - b + 180) % 360 - 180) * 3600


def main(n=500, seed=98765):
    random.seed(seed)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    maxpos = maxasc = maxnode = 0.0
    sign_mm = nak_mm = asc_sign_mm = house_mm = total = 0
    vmm = {v[0]: 0 for v in VARGAS}
    t_mm = y_mm = k_mm = pn_mm = 0
    for _ in range(n):
        Y = random.randint(1940, 2035); Mo = random.randint(1, 12); D = random.randint(1, 28)
        h = random.uniform(0, 24); lat = random.uniform(-58, 62); lon = random.uniform(-180, 180)
        jd = swe.julday(Y, Mo, D, h)
        am = ascendant_sidereal(jd, lat, lon)
        _, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
        maxasc = max(maxasc, adiff(am, ascmc[0])); asc_sign_mm += sgn(am) != sgn(ascmc[0])
        myl = {}; sel = {}
        for nm, b in PLANETS:
            ml = planet_sidereal_lon(jd, nm)
            sl, _ = swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_SIDEREAL); sl = sl[0]
            myl[nm] = ml; sel[nm] = sl; total += 1
            maxpos = max(maxpos, adiff(ml, sl))
            sign_mm += sgn(ml) != sgn(sl); nak_mm += nk(ml) != nk(sl)
            if whole_sign_house(am, ml) != ((sgn(sl) - sgn(ascmc[0])) % 12) + 1:
                house_mm += 1
            for vn, fn in VARGAS:
                if fn(ml) != fn(sl):
                    vmm[vn] += 1
        mn = mean_node_sidereal(jd)
        sn, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        maxnode = max(maxnode, adiff(mn, sn[0]))
        dt = datetime(Y, Mo, D, int(h), int((h % 1) * 60), tzinfo=ZoneInfo("Asia/Kolkata"))
        pm = get_panchanga(myl["Sun"], myl["Moon"], dt)
        ps = get_panchanga(sel["Sun"], sel["Moon"], dt)
        t_mm += pm["tithi"] != ps["tithi"]; y_mm += pm["yoga"] != ps["yoga"]
        k_mm += pm["karana"] != ps["karana"]
        pn_mm += nakshatra_info(myl["Moon"])[0] != nakshatra_info(sel["Moon"])[0]

    print(f"=== Engine validation vs Swiss Ephemeris: {n} charts, {total} positions (seed {seed}) ===")
    print(f"max diffs   : planet {maxpos:.2f}\"  ascendant {maxasc:.2f}\"  mean-node {maxnode:.2f}\"")
    print(f"positions   : sign {sign_mm}/{total}  nakshatra {nak_mm}/{total}")
    print(f"ascendant   : sign {asc_sign_mm}/{n}   houses {house_mm}/{total}")
    print(f"panchanga   : tithi {t_mm}  yoga {y_mm}  karana {k_mm}  moon-nak {pn_mm}  (/{n})")
    print("divisionals : " + "  ".join(f"{vn}:{vmm[vn]}" for vn, _ in VARGAS))
    core = sign_mm + nak_mm + asc_sign_mm + house_mm + t_mm + y_mm + k_mm + pn_mm \
        + sum(vmm[v] for v in vmm if v != "D60")
    d60 = vmm["D60"]
    print()
    if core == 0:
        print(f"PASS: 0 mismatches across all core calculations. "
              f"D60 {d60}/{total} ({100*d60/total:.3f}%) — irreducible boundary rate, acceptable.")
    else:
        print(f"REVIEW: {core} non-D60 mismatches found — investigate (boundary cases expected to be tiny).")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
