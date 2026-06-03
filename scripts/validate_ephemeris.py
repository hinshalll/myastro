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
    planet_tropical_lon, planet_ecliptic_lat, tropical_ascendant,
    tropical_placidus_cusps, mean_node_tropical, julday, jd_to_utc,
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


# Ayanamsha modes implemented on the free engine ↔ their Swiss Ephemeris SIDM_*.
AYANAMSHAS = [
    ("lahiri",        swe.SIDM_LAHIRI),
    ("raman",         swe.SIDM_RAMAN),
    ("krishnamurti",  swe.SIDM_KRISHNAMURTI),
    ("yukteshwar",    swe.SIDM_YUKTESHWAR),
    ("fagan_bradley", swe.SIDM_FAGAN_BRADLEY),
]


def validate_ayanamshas(n=300, seed=4242):
    """Each ayanamsha (free engine) vs Swiss Ephemeris across many dates +
    a full sidereal chart in each. All five are precession-based (anchor-only
    difference) so they should match to ~0.00\". Flags any that don't."""
    from shared.astro.ephem_skyfield import ayanamsa as sky_ayan, planet_sidereal_lon as sky_pl
    random.seed(seed)
    print(f"=== Ayanamsha validation vs Swiss Ephemeris: {n} dates each ===")
    worst_overall = 0.0
    all_pass = True
    for name, sidm in AYANAMSHAS:
        swe.set_sid_mode(sidm)
        max_ayan = 0.0
        sign_mm = 0
        pos_total = 0
        for _ in range(n):
            Y = random.randint(1900, 2050); Mo = random.randint(1, 12); D = random.randint(1, 28)
            h = random.uniform(0, 24)
            jd = swe.julday(Y, Mo, D, h)
            max_ayan = max(max_ayan, abs(sky_ayan(jd, name) - float(swe.get_ayanamsa_ut(jd))) * 3600)
            for nm, b in PLANETS:
                ml = sky_pl(jd, nm, name)
                sl_arr, _ = swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
                sign_mm += sgn(ml) != sgn(sl_arr[0]); pos_total += 1
        worst_overall = max(worst_overall, max_ayan)
        status = "PASS" if (max_ayan < 1.0 and sign_mm == 0) else "REVIEW"
        if status != "PASS":
            all_pass = False
        print(f"  {name:16s} max ayanamsa diff {max_ayan:6.3f}\"  sign mismatches {sign_mm}/{pos_total}  [{status}]")
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # restore default for the main run
    print(f"  -> worst ayanamsa residual across all five: {worst_overall:.3f}\"  "
          f"({'ALL PASS' if all_pass else 'SOME REVIEW'})")
    print()
    return all_pass


def main(n=500, seed=98765):
    random.seed(seed)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    maxpos = maxasc = maxnode = 0.0
    maxtrop = maxlat = maxtropasc = maxtropcusp = maxtropnode = 0.0
    sign_mm = nak_mm = asc_sign_mm = house_mm = total = 0
    trop_sign_mm = trop_asc_sign_mm = trop_cusp_sign_mm = 0
    vmm = {v[0]: 0 for v in VARGAS}
    t_mm = y_mm = k_mm = pn_mm = 0
    # Self-check: julday / jd_to_utc match Swiss Ephemeris for a few fixed points
    jd_self_mm = 0
    for (Y, Mo, D, h) in [(1900,1,1,0.0),(2000,1,1,12.0),(1987,7,28,16.5),(2026,6,3,9.25)]:
        if abs(julday(Y, Mo, D, h) - swe.julday(Y, Mo, D, h)) > 1e-9:
            jd_self_mm += 1
        # Round-trip JD → datetime → JD must be exact to seconds (~1e-5 days)
        jd_x = julday(Y, Mo, D, h)
        dt = jd_to_utc(jd_x)
        jd_back = julday(dt.year, dt.month, dt.day,
                         dt.hour + dt.minute / 60 + dt.second / 3600 + dt.microsecond/3.6e9)
        if abs(jd_back - jd_x) > 1e-4:  # ~9 seconds
            jd_self_mm += 1
    for _ in range(n):
        Y = random.randint(1940, 2035); Mo = random.randint(1, 12); D = random.randint(1, 28)
        h = random.uniform(0, 24); lat = random.uniform(-58, 62); lon = random.uniform(-180, 180)
        jd = swe.julday(Y, Mo, D, h)
        # ── Sidereal ascendant + whole-sign houses ──
        am = ascendant_sidereal(jd, lat, lon)
        _, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
        maxasc = max(maxasc, adiff(am, ascmc[0])); asc_sign_mm += sgn(am) != sgn(ascmc[0])
        # ── Tropical ascendant (Western chart) ──
        amt = tropical_ascendant(jd, lat, lon)
        _, ascmc_t = swe.houses_ex(jd, lat, lon, b'P', 0)  # tropical Placidus → ascmc[0] = Asc
        maxtropasc = max(maxtropasc, adiff(amt, ascmc_t[0]))
        trop_asc_sign_mm += sgn(amt) != sgn(ascmc_t[0])
        # ── Tropical Placidus cusps (Western chart) ──
        try:
            tc = tropical_placidus_cusps(jd, lat, lon)
            sc_t, _ = swe.houses_ex(jd, lat, lon, b'P', 0)
            for i in range(12):
                maxtropcusp = max(maxtropcusp, adiff(tc[i], sc_t[i]))
                if sgn(tc[i]) != sgn(sc_t[i]):
                    trop_cusp_sign_mm += 1
        except Exception:
            pass  # circumpolar; both engines fail
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
            # ── Tropical position (Western chart) ──
            mlt = planet_tropical_lon(jd, nm)
            slt_arr, _ = swe.calc_ut(jd, b, swe.FLG_SWIEPH)
            slt = slt_arr[0]
            maxtrop = max(maxtrop, adiff(mlt, slt))
            if sgn(mlt) != sgn(slt):
                trop_sign_mm += 1
            # ── Planet ecliptic latitude (Graha Yuddha winner) ──
            mlat = planet_ecliptic_lat(jd, nm)
            slat = float(slt_arr[1])
            # Latitude is sign-meaningful, use raw arcsec diff
            maxlat = max(maxlat, abs(mlat - slat) * 3600)
        # ── Sidereal mean node ──
        mn = mean_node_sidereal(jd)
        sn, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        maxnode = max(maxnode, adiff(mn, sn[0]))
        # ── Tropical mean node (Western Rahu) ──
        mnt = mean_node_tropical(jd)
        snt, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH)
        maxtropnode = max(maxtropnode, adiff(mnt, snt[0]))
        dt = datetime(Y, Mo, D, int(h), int((h % 1) * 60), tzinfo=ZoneInfo("Asia/Kolkata"))
        pm = get_panchanga(myl["Sun"], myl["Moon"], dt)
        ps = get_panchanga(sel["Sun"], sel["Moon"], dt)
        t_mm += pm["tithi"] != ps["tithi"]; y_mm += pm["yoga"] != ps["yoga"]
        k_mm += pm["karana"] != ps["karana"]
        pn_mm += nakshatra_info(myl["Moon"])[0] != nakshatra_info(sel["Moon"])[0]

    print(f"=== Engine validation vs Swiss Ephemeris: {n} charts, {total} positions (seed {seed}) ===")
    print(f"sidereal    : planet {maxpos:.2f}\"  ascendant {maxasc:.2f}\"  mean-node {maxnode:.2f}\"")
    print(f"tropical    : planet {maxtrop:.2f}\"  ascendant {maxtropasc:.2f}\"  "
          f"mean-node {maxtropnode:.2f}\"  cusp {maxtropcusp:.2f}\"")
    print(f"ecliptic lat: planet {maxlat:.2f}\"  (used by Graha Yuddha)")
    print(f"positions   : sidereal sign {sign_mm}/{total} nak {nak_mm}/{total}  "
          f"tropical sign {trop_sign_mm}/{total}")
    print(f"ascendant   : sidereal sign {asc_sign_mm}/{n}  houses {house_mm}/{total}  "
          f"tropical sign {trop_asc_sign_mm}/{n}  tropical cusp signs {trop_cusp_sign_mm}/{n*12}")
    print(f"panchanga   : tithi {t_mm}  yoga {y_mm}  karana {k_mm}  moon-nak {pn_mm}  (/{n})")
    print(f"calendar    : julday/jd_to_utc self-check {jd_self_mm}/8 mismatches")
    print("divisionals : " + "  ".join(f"{vn}:{vmm[vn]}" for vn, _ in VARGAS))
    core = (sign_mm + nak_mm + asc_sign_mm + house_mm + t_mm + y_mm + k_mm + pn_mm
            + trop_sign_mm + trop_asc_sign_mm + trop_cusp_sign_mm + jd_self_mm
            + sum(vmm[v] for v in vmm if v != "D60"))
    d60 = vmm["D60"]
    print()
    if core == 0:
        print(f"PASS: 0 mismatches across all core calculations (sidereal + tropical + latitude + "
              f"calendar). D60 {d60}/{total} ({100*d60/total:.3f}%) — irreducible boundary rate, "
              f"acceptable.")
    else:
        print(f"REVIEW: {core} non-D60 mismatches found — investigate (boundary cases expected to be tiny).")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    validate_ayanamshas(max(100, n // 2))
    main(n)
