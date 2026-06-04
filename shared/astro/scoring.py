import math
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from shared.astro.constants import *
from shared.astro.astro_calc import *

def calculate_ashta_koota(moon_boy, moon_girl):
    """
    Ashta Koota (36 Gunas) — Vedic compatibility matching.

    Reads Moon longitudes (degrees) for both partners and returns the 8 Kootas
    plus Stree-Deergha + Mahendra bonus markers.

    Doctrinal corrections from classical Parashari / Muhurta texts:
      - Bhakoot: distance 8 (5-9 axis from one side) is dosha, not full points.
      - Vashya: Sagittarius (0-15° Quadruped / 15-30° Human) and Capricorn
        (0-15° Aquatic / 15-30° Quadruped) are dual-category by degree-in-sign.
      - Nadi: Gandanta-junction nakshatras (Ashlesha–Magha, Jyeshtha–Mula,
        Revati–Ashwini) intensify Nadi dosha — no cancellation by rashi lord.
    """
    # Boy's and Girl's Moon Longitudes
    s1 = sign_index_from_lon(moon_boy)
    s2 = sign_index_from_lon(moon_girl)
    deg1 = moon_boy % 30        # degree-in-sign for Vashya degree-split
    deg2 = moon_girl % 30
    n1 = min(int((moon_boy % 360) // (360 / 27)), 26)
    n2 = min(int((moon_girl % 360) // (360 / 27)), 26)

    # 1. Varna (1 point)
    vm = [1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0]
    v = 1 if vm[s1] <= vm[s2] else 0

    # 2. Vashya (2 points) — classical 5 categories: 0 Quadruped, 1 Human,
    #    2 Aquatic, 3 Wild, 4 Insect/Reptile. Sagittarius and Capricorn are
    #    dual-category by degree-in-sign (Brihat Parashara, Vashya chapter).
    def vashya_index(sign, deg):
        base = [0, 0, 1, 2, 3, 1, 1, 4, 0, 2, 1, 2]
        if sign == 8:   # Sagittarius: 0-15° Quadruped, 15-30° Human
            return 0 if deg < 15 else 1
        if sign == 9:   # Capricorn: 0-15° Aquatic, 15-30° Quadruped
            return 2 if deg < 15 else 0
        return base[sign]
    va1 = vashya_index(s1, deg1)
    va2 = vashya_index(s2, deg2)
    if va1 == va2: vap = 2
    elif {va1, va2} in [{1, 3}, {1, 4}, {2, 3}]: vap = 0
    else: vap = 1

    # 3. Tara (3 points) — count from boy's star to girl's, divide by 9.
    #    Remainders 3/5/7 (1-indexed) are inauspicious → 0-indexed [2,4,6].
    t1 = ((n2 - n1) % 27) % 9  # Boy → Girl
    t2 = ((n1 - n2) % 27) % 9  # Girl → Boy
    ta = (0 if t1 in [2, 4, 6] else 1.5) + (0 if t2 in [2, 4, 6] else 1.5)

    # 4. Yoni (4 points) — 14 yonis mapped from 27 nakshatras, 7 enemy pairs.
    ym = [0, 1, 2, 3, 3, 4, 5, 2, 5, 6, 6, 7, 8, 9, 8, 9, 10, 10, 4, 11, 12, 11, 13, 0, 13, 7, 1]
    y1, y2 = ym[n1], ym[n2]
    enemies = [{0, 8}, {1, 13}, {2, 11}, {3, 12}, {4, 10}, {5, 6}, {7, 9}]
    yo = 4 if y1 == y2 else (0 if {y1, y2} in enemies else 2)

    # 5. Graha Maitri (5 points)
    lm = [0, 1, 2, 3, 4, 2, 1, 0, 5, 6, 6, 5]
    l1, l2 = lm[s1], lm[s2]
    f_map = {0: [3, 4, 5], 1: [2, 6], 2: [1, 4], 3: [2, 4], 4: [0, 3, 5], 5: [0, 3, 4], 6: [1, 2]}
    e_map = {0: [2], 1: [3, 4], 2: [3], 3: [], 4: [1, 6], 5: [1, 2], 6: [0, 3, 4]}
    def rel(a, b): return 2 if b in f_map.get(a, []) else (0 if b in e_map.get(a, []) else 1)
    ms = {(2, 2): 5, (2, 1): 4, (1, 2): 4, (1, 1): 3, (2, 0): 1, (0, 2): 1, (1, 0): .5, (0, 1): .5, (0, 0): 0}
    m = ms.get((rel(l1, l2), rel(l2, l1)), 0)

    # 6. Gana (6 points)
    gm = [0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0]
    g1, g2 = gm[n1], gm[n2]
    if g1 == g2: g = 6
    elif g1 == 0 and g2 == 1: g = 6
    elif g1 == 1 and g2 == 0: g = 5
    elif g1 == 0 and g2 == 2: g = 1
    else: g = 0

    # 7. Bhakoot (7 points) — dosha on 2-12 (dist 1,11), 5-9 (dist 4,8),
    #    6-8 (dist 5,7) axes. Non-dosha distances: {0, 2, 3, 6, 9, 10}.
    #    FIXED: distance 8 was previously included in no-dosha by mistake.
    dist = (s2 - s1) % 12
    bh = 7 if dist in [0, 2, 3, 6, 9, 10] else 0

    # 8. Nadi (8 points) — same nadi (Adi/Madhya/Antya) creates Nadi dosha.
    nb = [0, 1, 2] * 9
    nd1, nd2 = nb[n1], nb[n2]
    nn = ""
    np = 0
    # Gandanta junctions: Ashlesha(8)–Magha(9), Jyeshtha(17)–Mula(18), Revati(26)–Ashwini(0).
    # These pairs are doubly afflicted and do not enjoy classical cancellation.
    gandanta_pairs = {frozenset([8, 9]), frozenset([17, 18]), frozenset([26, 0])}
    in_gandanta = frozenset([n1, n2]) in gandanta_pairs
    if nd1 == nd2:
        if n1 == n2:
            nn = "NADI DOSHA EXCEPTION: Same Nakshatra (Dosha Cancelled)"
        elif in_gandanta:
            nn = "NADI DOSHA INTENSIFIED: Gandanta junction nakshatras (no classical cancellation)"
        elif SIGN_LORDS_MAP[s1] != SIGN_LORDS_MAP[s2]:
            nn = "NADI DOSHA PARTIAL EXCEPTION: Different Rashi lords"
    else: np = 8

    # Stree-Deergha & Mahendra check (Bonus/Mitigation)
    dist_nak = (n2 - n1) % 27
    mahendra = "Present" if dist_nak in [3, 6, 9, 12, 15, 18, 21, 24] else "Absent"
    stree_deergha = "Excellent" if dist_nak >= 15 else "Poor"

    total = v + vap + ta + yo + m + g + bh + np
    return {
        "score": total,
        "varna": v, "vashya": vap, "tara": ta, "yoni": yo,
        "maitri": m, "gana": g, "bhakoot": bh, "nadi": np,
        "nadi_note": nn, "mahendra": mahendra, "stree_deergha": stree_deergha,
        "bhakoot_distance": dist,  # exposed for downstream RAG/explanation
        "vashya_categories": (va1, va2),  # exposed for transparency
    }


def calculate_marital_analysis(jd, lat, lon):
    """
    Compute D9 7th House, Upapada Lagna (UL) and Darapada (A7).

    Classical Jaimini convention: when the lord of a house is Rahu or Ketu,
    use the node's DISPOSITOR (sign-lord of the node's current sign), not a
    hard-coded Saturn/Venus proxy. The node has no own sign, so Arudha is
    derived through the planet that actually rules where the node sits.
    """
    cusps = get_lagna_and_cusps(jd, lat, lon)
    lagna_lon = cusps[0]
    lagna_sign = sign_index_from_lon(lagna_lon)

    # Tropical planet longitudes for the 7 grahas
    p = {pn: get_planet_longitude_and_speed(jd, pid)[0] for pn, pid in PLANETS.items()}

    # Rahu / Ketu for dispositor resolution
    rahu_lon = get_rahu_longitude(jd)
    ketu_lon = (rahu_lon + 180.0) % 360.0
    rahu_sign = sign_index_from_lon(rahu_lon)
    ketu_sign = sign_index_from_lon(ketu_lon)

    def resolve_lord(lord_str):
        """Resolve a sign lord to a usable graha for Arudha calc.
        Rahu/Ketu → their dispositor (sign-lord of their current sign)."""
        if lord_str == "Rahu":
            return SIGN_LORDS_MAP[rahu_sign]
        if lord_str == "Ketu":
            return SIGN_LORDS_MAP[ketu_sign]
        return lord_str

    # Navamsha (D9) — pada-count method
    d9_lagna_sign = int((lagna_lon % 360) / (360 / 108)) % 12
    d9_7th_sign = (d9_lagna_sign + 6) % 12
    d9_7th_lord = SIGN_LORDS_MAP[d9_7th_sign]

    # Upapada Lagna (UL) — Arudha of 12th House
    h12_sign = (lagna_sign + 11) % 12
    h12_lord = resolve_lord(SIGN_LORDS_MAP[h12_sign])
    lord_lon = p[h12_lord]
    lord_sign = sign_index_from_lon(lord_lon)
    dist = (lord_sign - h12_sign) % 12
    ul_sign = (lord_sign + dist) % 12
    # Classical Jaimini exceptions: Arudha = same sign or 7th from it → +10 houses
    if ul_sign == h12_sign: ul_sign = (ul_sign + 9) % 12
    elif ul_sign == (h12_sign + 6) % 12: ul_sign = (ul_sign + 9) % 12

    # Darapada (A7) — Arudha of 7th House
    h7_sign = (lagna_sign + 6) % 12
    h7_lord = resolve_lord(SIGN_LORDS_MAP[h7_sign])
    l7_sign = sign_index_from_lon(p[h7_lord])
    d7 = (l7_sign - h7_sign) % 12
    a7_sign = (l7_sign + d7) % 12
    if a7_sign == h7_sign: a7_sign = (a7_sign + 9) % 12
    elif a7_sign == (h7_sign + 6) % 12: a7_sign = (a7_sign + 9) % 12

    return {
        "D9_7th_Sign": SIGNS[d9_7th_sign],
        "D9_7th_Lord": d9_7th_lord,
        "UL_Sign": SIGNS[ul_sign],
        "UL_Lord_Used": h12_lord,        # transparency: which lord actually drove UL calc
        "A7_Sign": SIGNS[a7_sign],
        "A7_Lord_Used": h7_lord,
        "D1_7th_Sign": SIGNS[h7_sign],
    }


def calculate_wealth_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    
    al_house = f.get("arudha_lagna", {}).get("house")
    indu_sign = f.get("indu_lagna", {}).get("sign")
    indu_bonus = 0
    if indu_sign:
        indu_occ_str = sum(5 for p in f["planets"] if f["planets"][p].get("sign") == indu_sign and p in NATURAL_BENEFICS)
        indu_occ_str -= sum(5 for p in f["planets"] if f["planets"][p].get("sign") == indu_sign and p in NATURAL_MALEFICS)
        if indu_occ_str > 0: indu_bonus = indu_occ_str + 10
        elif indu_occ_str < 0: indu_bonus = indu_occ_str - 10
        
    al11_score = 0
    if al_house:
        al11_house = ((al_house + 10 - 1) % 12) + 1
        al11_score = get_bhava_bala(al11_house, ls, planet_data, f, lagna_lon, jd_ut)
        
    # Structural houses — classical wealth axes.
    # • H2 (Dhana) and H11 (Labha) are the primary wealth-house pair → 2.4 each.
    # • H9 (Bhagya) is THE fortune house — previously underweighted at 0.9.
    #   Classical BPHS gives H9 near-equal weight with H2/H11 for lifetime
    #   wealth potential (merit-driven flow). Raised to 1.8.
    # • H5 (Purva Punya) is the past-merit wealth-carrier → 1.2 (was 0.9).
    # • H10 (Karma) is the modern source-of-earning — added at 0.6.
    # • H1 (Lagna self/manifestation capacity) stays at 0.5.
    structural = score_positive([
        (get_bhava_bala(2,  ls, planet_data, f, lagna_lon, jd_ut), 2.4),
        (get_bhava_bala(11, ls, planet_data, f, lagna_lon, jd_ut), 2.4),
        (get_bhava_bala(9,  ls, planet_data, f, lagna_lon, jd_ut), 1.8),   # Bhagya — fortune
        (get_bhava_bala(5,  ls, planet_data, f, lagna_lon, jd_ut), 1.2),   # Purva Punya — merit
        (get_bhava_bala(10, ls, planet_data, f, lagna_lon, jd_ut), 0.6),   # Karma — source of earning
        (get_bhava_bala(1,  ls, planet_data, f, lagna_lon, jd_ut), 0.5),
        (al11_score, 1.2),
        (sav_norm(f["sav"].get(2)),  1.2),
        (sav_norm(f["sav"].get(11)), 1.2),
        (sav_norm(f["sav"].get(9)),  0.8),   # Bhagya SAV — wealth-by-merit signal
    ])
    karaka = score_positive([
        (get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.5),
        (get_p_str("Venus",   planet_data, ls, f, lagna_lon, jd_ut), 1.0),
        (get_p_str("Mercury", planet_data, ls, f, lagna_lon, jd_ut), 0.8),
        (varga_sign_strength(f, "D2", "Jupiter"), 0.9),
        (varga_sign_strength(f, "D2", "Venus"),   0.7),
        (varga_sign_strength(f, "D9", "Jupiter"), 0.5),
    ])
    kp = score_positive([
        (house_promise_score(2,  placidus_cusps, planet_data, r_lon, k_lon, ls, {2, 11}, {6, 8, 12}), 1.4),
        (house_promise_score(11, placidus_cusps, planet_data, r_lon, k_lon, ls, {2, 11}, {6, 8, 12}), 1.0),
    ])

    # Yogas — expanded dict now includes the previously-undetected Akhand
    # Samrajya (9 pts, classically the great wealth-sovereignty yoga) plus the
    # newly-added Mahabhagya (8), Sankha (6), and Kahala (5).
    yoga = topic_yoga_score(f, {
        "Akhand Samrajya Yoga": 9,
        "Mahabhagya Yoga":      8,
        "Lakshmi Yoga":         8,
        "Dhana Yoga":           7,
        "Sankha Yoga":          6,
        "Chandra-Mangala Yoga": 5,
        "Kahala Yoga":          5,
        "Raja Yoga":            4,
        "Parivartana Yoga":     3,
        "Viparita Raja Yoga":   2,
    }, planet_data, ls, lagna_lon, jd_ut)
    # Lagna gating for wealth yogas uses a HIGHER floor (0.50 vs default 0.30)
    # because classical wealth yogas describe ASSET-ACCUMULATION potential, not
    # SELF-MANIFESTATION potential. A native with weak Lagna can still
    # accumulate wealth via Dhana/Akhand combos (they just may not enjoy it
    # spiritually). Capping yoga benefit at 0.30 of raw was over-penalising.
    yoga = _lagna_scaled(yoga, get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), floor=0.50)

    placement = topic_house_connection(f, ["Jupiter", "Venus", "Mercury", "Moon", "Mars"], {2, 5, 9, 11})
    
    h2_lon, h11_lon = ((ls + 1) * 30 + 15) % 360, ((ls + 10) * 30 + 15) % 360
    malefic_drishti = sum((calc_drishti(planet_data[m][0], h2_lon, m) + calc_drishti(planet_data[m][0], h11_lon, m)) * 0.05 for m in ["Saturn", "Mars", "Rahu", "Ketu", "Sun"])
    # Edit 2: coefficient reduced from 3 to 2 (Bhava Bala already encodes drishti).
    drains = affliction_count(f, houses={2, 11}) * 2 + malefic_drishti

    # Edit 6a: Rahu-in-2 with weak Jupiter keeps penalty; Rahu-in-11 is a
    # classical massive-gains signature (upachaya node) and gets a bonus instead.
    rahu_house_w = planet_house(f, "Rahu")
    jup_strength_w = get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut)
    if rahu_house_w == 2 and jup_strength_w < 55:
        drains += 5

    # Classical refinements (lifetime baseline):
    # • Argala = intervention support from 2nd/4th/5th/11th to a house. Strong
    #   Argala on H2 and H11 amplifies wealth promise; Virodha Argala drains it.
    argala_bonus = (calculate_argala(2, f) + calculate_argala(11, f)) * 0.6  # ~ ±15 total
    # • Purva-Punya wealth: 5th lord or 9th lord placed IN H2 or H11 is a
    #   classical dhana yoga (past-merit → present wealth flow).
    purva_punya = 0
    if _house_lord_in_houses(f, 5, {2, 11}): purva_punya += 6
    if _house_lord_in_houses(f, 9, {2, 11}): purva_punya += 6
    # Edit 6a (cont.): Rahu-in-11 upachaya bonus.
    if rahu_house_w == 11:
        purva_punya += 4

    # • Parivartana between 2L and 11L (mutual exchange) — exceptional dhana.
    h2_lord  = f["house_lords"].get(2,  {}).get("planet")
    h11_lord = f["house_lords"].get(11, {}).get("planet")
    if h2_lord and h11_lord:
        h2_lord_sign = sign_index_from_lon(planet_data[h2_lord][0]) if h2_lord in planet_data else None
        h11_lord_sign = sign_index_from_lon(planet_data[h11_lord][0]) if h11_lord in planet_data else None
        if h2_lord_sign is not None and h11_lord_sign is not None:
            if h2_lord_sign == (ls + 10) % 12 and h11_lord_sign == (ls + 1) % 12:
                purva_punya += 10  # Parivartana yoga between H2 and H11

    # Edit 6b: D2 (Hora) Lagna lord score.
    # D2 is the master wealth chart; its Lagna lord's strength signals whether
    # the native can accumulate (Sun/Leo hora) or nurture (Moon/Cancer hora).
    d2_lagna_score = 0
    try:
        lagna_deg = lagna_lon % 30.0
        # Traditional Hora: odd signs → first half = Leo (Sun), second = Cancer (Moon)
        #                   even signs → first half = Cancer (Moon), second = Leo (Sun)
        if ls % 2 == 0:   # 0-indexed even = traditionally odd sign (Aries, Gem, …)
            d2_lagna_sign = 4 if lagna_deg < 15 else 3   # Leo or Cancer
        else:             # 0-indexed odd = traditionally even sign (Taurus, Can, …)
            d2_lagna_sign = 3 if lagna_deg < 15 else 4   # Cancer or Leo
        d2_lagna_lord = SIGN_LORDS_MAP[d2_lagna_sign]
        d2_ll_strength = get_p_str(d2_lagna_lord, planet_data, ls, f, lagna_lon, jd_ut)
        d2_lagna_score = (d2_ll_strength - 50) * 0.15
    except Exception:
        pass

    # Edit 6c: Combustion of 2L or 11L — a combust wealth-lord cannot fully
    # deliver its house promise (Sun's rays burn its significations).
    combust_penalty = 0
    for lord_key in [h2_lord, h11_lord]:
        if lord_key and lord_key in f.get("planets", {}):
            tags = f["planets"][lord_key].get("tags", set())
            if any("Combust" in t for t in tags):
                combust_penalty += 4

    # Edit 6d: 2L–11L sambandha (conjunction or mutual 7th aspect).
    # When the two primary wealth lords are in parivartana, conjunction, or
    # mutual aspect, income and accumulation reinforce each other directly.
    sambandha_bonus = 0
    h2_lord_house  = f["house_lords"].get(2,  {}).get("house")
    h11_lord_house = f["house_lords"].get(11, {}).get("house")
    if h2_lord and h11_lord and h2_lord_house and h11_lord_house:
        if h2_lord_house == h11_lord_house:
            sambandha_bonus = 6   # conjunction
        elif (h11_lord_house - h2_lord_house) % 12 == 6 or \
             (h2_lord_house - h11_lord_house) % 12 == 6:
            sambandha_bonus = 4   # mutual 7th aspect

    # ── Pandit-tier classical refinements (added after user feedback that the
    # wealth ranking didn't match real pandit readings) ────────────────────────

    # • Bhagyadhipati (9L) explicit strength — the single most important wealth-
    #   merit indicator in classical Parashari. "Bhagya hi sab kuch hai" — when
    #   the fortune-lord is strong, wealth flows; when weak, even great H2/H11
    #   yogas yield reduced fruit. Mirrors the existing D2-lagna-lord scoring.
    h9_lord_w  = f["house_lords"].get(9, {}).get("planet")
    bhagyadhipati_score = 0
    if h9_lord_w:
        h9_ll_strength = get_p_str(h9_lord_w, planet_data, ls, f, lagna_lon, jd_ut)
        bhagyadhipati_score = (h9_ll_strength - 50) * 0.20

    # • Bhagya–Labha sambandha (9L–11L connection) — fortune flowing through
    #   gains. Classically a strong dhana indicator. Mirrors the 2L–11L logic.
    h9_lord_house = f["house_lords"].get(9, {}).get("house")
    bhagya_labha_bonus = 0
    if h9_lord_w and h11_lord and h9_lord_house and h11_lord_house:
        if h9_lord_house == h11_lord_house:
            bhagya_labha_bonus = 6   # conjunction
        elif (h11_lord_house - h9_lord_house) % 12 == 6 or \
             (h9_lord_house - h11_lord_house) % 12 == 6:
            bhagya_labha_bonus = 4   # mutual 7th aspect

    # • 5L–9L conjunction (purva-punya × dharma) — classical "trikona-lord
    #   conjunction" producing exceptional Raja-Dhana yoga. Different from
    #   generic Raja Yoga because both are trikona lords (no kendra needed).
    h5_lord_w = f["house_lords"].get(5, {}).get("planet")
    h5_lord_house = f["house_lords"].get(5, {}).get("house")
    trikona_sambandha = 0
    if h5_lord_w and h9_lord_w and h5_lord_house and h9_lord_house:
        if h5_lord_house == h9_lord_house and h5_lord_w != h9_lord_w:
            trikona_sambandha = 5   # 5L+9L conjunct

    # • Saturn in 11th house — classical "disciplined wealth accumulator"
    #   signal (BPHS, Phaladeepika). Saturn in upachaya improves with time,
    #   and 11H is one of Saturn's strongest houses for sustainable wealth.
    saturn_11_bonus = 4 if planet_house(f, "Saturn") == 11 else 0

    # ────────────────────────────────────────────────────────────────────────

    return round(clamp_val(structural * 0.40 + karaka * 0.22 + kp * 0.18
                           + yoga + placement + indu_bonus + argala_bonus + purva_punya
                           + d2_lagna_score + sambandha_bonus
                           + bhagyadhipati_score + bhagya_labha_bonus
                           + trikona_sambandha + saturn_11_bonus
                           - drains - combust_penalty), 2)


def calculate_relationship_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    dk = f["karakas"].get("Darakaraka")
    
    structural = score_positive([(get_bhava_bala(7, ls, planet_data, f, lagna_lon, jd_ut), 2.5), (get_bhava_bala(2, ls, planet_data, f, lagna_lon, jd_ut), 1.2), (get_bhava_bala(4, ls, planet_data, f, lagna_lon, jd_ut), 1.0), (get_bhava_bala(5, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (get_bhava_bala(8, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (sav_norm(f["sav"].get(7)), 1.2)])
    karaka = score_positive([(get_p_str("Venus", planet_data, ls, f, lagna_lon, jd_ut), 1.8), (get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.1), (get_p_str("Moon", planet_data, ls, f, lagna_lon, jd_ut), 1.1), (get_p_str(dk, planet_data, ls, f, lagna_lon, jd_ut), 1.0), (varga_sign_strength(f, "D9", "Venus"), 1.2), (varga_sign_strength(f, "D9", "Jupiter"), 0.8), (varga_sign_strength(f, "D9", dk), 0.9)])
    kp = house_promise_score(7, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,7,11}, {1,6,10})
    yoga = topic_yoga_score(f, {"Malavya Yoga": 7, "Gajakesari Yoga": 5, "Raja Yoga": 2}, planet_data, ls, lagna_lon, jd_ut)
    yoga = _lagna_scaled(yoga, get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut))

    h7_lon = ((ls + 6) * 30 + 15) % 360
    malefic_drishti = sum(calc_drishti(planet_data[m][0], h7_lon, m) * 0.05 for m in ["Saturn", "Mars", "Rahu", "Ketu", "Sun"])
    risk = affliction_count(f, planets={"Venus", "Jupiter", "Moon", dk} - {None}) * 3 + malefic_drishti

    # Manglik penalty — aware of F7 cancellation tiers.
    # Verdict strings can be:
    #   "NOT MANGLIK ...", "WEAK MANGLIK (cancellations: ...) ...",
    #   "MILD MANGLIK (cancellations: ...) ..." (cancelled MILD case),
    #   "MILD MANGLIK — Mars in Manglik house from ...",
    #   "HIGH MANGLIK ...", "VERY HIGH MANGLIK ...".
    # Cancellations (own/exalted Mars, Jupiter/Venus aspect, Saturn conjunct)
    # drop the penalty to ~zero.
    mg = f["manglik"]
    if "cancellations:" in mg or "WEAK MANGLIK" in mg or "NOT MANGLIK" in mg:
        pass  # cancelled / weak / absent — no penalty
    elif "VERY HIGH MANGLIK" in mg: risk += 12
    elif "HIGH MANGLIK" in mg:      risk += 8
    elif "MILD MANGLIK" in mg:      risk += 4

    if planet_house(f, "Rahu") == 7 or planet_house(f, "Ketu") == 7: risk += 7

    # Classical refinements:
    # • 7th lord placement + dignity is the single biggest missing signal —
    #   in Parashari it's *more* important than karaka Venus for marriage quality.
    seventh_lord, sl_house, sl_bucket = _seventh_lord_placement(f)
    seventh_lord_score = 0
    if seventh_lord:
        sl_strength = get_p_str(seventh_lord, planet_data, ls, f, lagna_lon, jd_ut)
        # Translate placement bucket into a 0-20 contribution.
        bucket_bonus = {
            "kendra_trikona": 18,
            "upachaya": 10,
            "neutral": 8,
            "dusthana": -10,
            "unknown": 5,
        }.get(sl_bucket, 5)
        # Blend lord strength (50-95) with placement bonus (-10 to +18).
        seventh_lord_score = (sl_strength - 50) * 0.20 + bucket_bonus

    # • Upapada Lagna durability — UL's sign-lord strength signals marital stability.
    #   Already computed in calculate_marital_analysis; here we approximate the
    #   same idea from D1 by looking at the 12th-lord's placement (UL = Arudha
    #   of 12th, so 12L well-placed → UL strong).
    ul_durability = 0
    h12_lord = f["house_lords"].get(12, {}).get("planet")
    h12_lord_house = f["house_lords"].get(12, {}).get("house")
    if h12_lord_house in {1, 4, 5, 7, 9, 10, 11}: ul_durability += 6
    elif h12_lord_house in {6, 8, 12}:            ul_durability -= 4

    # • D9 7th house lord position (durable spouse-self bond).
    d9_signs = f.get("vargas", {}).get("D9", {})
    d9_strength = varga_sign_strength(f, "D9", dk) if dk else 50

    return round(clamp_val(structural * 0.34 + karaka * 0.26 + (kp/100)*20
                           + seventh_lord_score + ul_durability + yoga
                           + (d9_strength - 50) * 0.06
                           - risk), 2)


def calculate_career_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    amk = f["karakas"].get("Amatyakaraka")
    al_house = f.get("arudha_lagna", {}).get("house")
    al10_score = 0
    if al_house:
        al10_house = ((al_house + 9 - 1) % 12) + 1
        al10_score = get_bhava_bala(al10_house, ls, planet_data, f, lagna_lon, jd_ut)
        
    h7_bala = get_bhava_bala(7, ls, planet_data, f, lagna_lon, jd_ut)
    h6_weight = 0.5 if h7_bala > get_bhava_bala(6, ls, planet_data, f, lagna_lon, jd_ut) else 1.1
    structural = score_positive([(get_bhava_bala(10, ls, planet_data, f, lagna_lon, jd_ut), 2.7), (get_bhava_bala(6, ls, planet_data, f, lagna_lon, jd_ut), h6_weight), (get_bhava_bala(11, ls, planet_data, f, lagna_lon, jd_ut), 1.4), (get_bhava_bala(2, ls, planet_data, f, lagna_lon, jd_ut), 0.8), (get_bhava_bala(9, ls, planet_data, f, lagna_lon, jd_ut), 0.8), (get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), 0.5), (al10_score, 1.5), (sav_norm(f["sav"].get(10)), 1.2), (sav_norm(f["sav"].get(6)), 0.8)])
    karaka = score_positive([(get_p_str("Sun", planet_data, ls, f, lagna_lon, jd_ut), 1.2), (get_p_str("Saturn", planet_data, ls, f, lagna_lon, jd_ut), 1.3), (get_p_str("Mercury", planet_data, ls, f, lagna_lon, jd_ut), 1.0), (get_p_str("Mars", planet_data, ls, f, lagna_lon, jd_ut), 0.8), (get_p_str(amk, planet_data, ls, f, lagna_lon, jd_ut), 1.6), (varga_sign_strength(f, "D10", amk), 1.5), (varga_sign_strength(f, "D10", "Sun"), 0.8), (varga_sign_strength(f, "D10", "Saturn"), 0.8)])
    kp = score_positive([(house_promise_score(10, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,6,10,11}, {5,8,12}), 1.7), (house_promise_score(6, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,6,10,11}, {5,8,12}), 0.8)])
    yoga = topic_yoga_score(f, {"Dharma-Karma Adhipati Yoga": 10, "Raja Yoga": 7, "Ruchaka Yoga": 6, "Shasha Yoga": 6, "Bhadra Yoga": 5, "Hamsa Yoga": 3, "Neecha Bhanga Raja Yoga": 5, "Viparita Raja Yoga": 3}, planet_data, ls, lagna_lon, jd_ut)
    yoga = _lagna_scaled(yoga, get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut))
    placement = topic_house_connection(f, ["Sun", "Saturn", "Mercury", "Mars", amk], {1, 6, 10, 11})
    risk = affliction_count(f, planets={"Sun", "Saturn", "Mercury", "Mars", amk} - {None}, houses={1, 6, 10, 11}) * 3

    # Classical refinements:
    # • 10th lord placement + dignity drives career structurally (Parashari).
    #   The lord IN a good house carries the karma-house promise wherever it sits.
    tenth_lord = f["house_lords"].get(10, {}).get("planet")
    tenth_lord_house = f["house_lords"].get(10, {}).get("house")
    tenth_lord_score = 0
    if tenth_lord:
        tl_str = get_p_str(tenth_lord, planet_data, ls, f, lagna_lon, jd_ut)
        if tenth_lord_house in {1, 4, 7, 10, 5, 9, 11}: tenth_lord_score = 14
        elif tenth_lord_house in {2, 3, 6}:             tenth_lord_score = 8
        elif tenth_lord_house in {8, 12}:               tenth_lord_score = -8
        # Blend lord intrinsic strength.
        tenth_lord_score += (tl_str - 50) * 0.15

    # • Dispositor of the 10th lord — second-order strength. If the planet that
    #   rules the sign where 10L sits is itself strong, career structure compounds.
    dispositor_score = 0
    if tenth_lord and tenth_lord in planet_data:
        tl_sign = sign_index_from_lon(planet_data[tenth_lord][0])
        dispositor = SIGN_LORDS_MAP[tl_sign]
        if dispositor in planet_data:
            disp_str = get_p_str(dispositor, planet_data, ls, f, lagna_lon, jd_ut)
            dispositor_score = (disp_str - 50) * 0.08

    # D10 Lagna lord: strong AmK with weak D10 Lagna lord = hard work, no
    # permanent authority. Classical Dashamsha read: "you can do the work but
    # can you hold the throne?"
    d10_lagna_score = 0
    try:
        lagna_deg = lagna_lon % 30.0
        pada = int(lagna_deg // 3.0)
        # Odd signs (Aries=0, Gem=2, …): D10 Lagna starts from the sign itself.
        # Even signs (Taurus=1, Can=3, …): D10 Lagna starts 9 signs ahead.
        if ls % 2 == 0:
            d10_lagna_sign = (ls + pada) % 12
        else:
            d10_lagna_sign = (ls + 8 + pada) % 12
        d10_lagna_lord = SIGN_LORDS_MAP[d10_lagna_sign]
        d10_ll_strength = get_p_str(d10_lagna_lord, planet_data, ls, f, lagna_lon, jd_ut)
        d10_lagna_score = (d10_ll_strength - 50) * 0.12
    except Exception:
        pass

    return round(clamp_val(structural * 0.36 + karaka * 0.28 + kp * 0.18
                           + yoga + placement + tenth_lord_score + dispositor_score
                           + d10_lagna_score - risk), 2)


def calculate_struggles_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data

    # Burden starts from a derived baseline: a chart with strong Lagna + H4
    # + low affliction starts low; weak ones start high. Replaces the old
    # magic `18` constant which had no doctrinal basis.
    h1_bala = get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut)
    h4_bala = get_bhava_bala(4, ls, planet_data, f, lagna_lon, jd_ut)
    burden = (100 - h1_bala) * 0.18 + (100 - h4_bala) * 0.10  # ~10-30 typical
    burden += affliction_count(f, houses={8}) * 3
    burden += get_bhava_bala(12, ls, planet_data, f, lagna_lon, jd_ut) * 0.10
    burden += max(0, get_bhava_bala(6, ls, planet_data, f, lagna_lon, jd_ut) - 62) * 0.04

    graha_yuddha_count = sum(1 for p in f["planets"].values() if p.get("war") == "LOSER")
    burden += graha_yuddha_count * 5

    malefic_drishti = 0
    for h_idx in [1, 4, 7, 8, 10, 12]:
        h_lon = ((ls + h_idx - 1) * 30 + 15) % 360
        malefic_drishti += sum(calc_drishti(planet_data[m][0], h_lon, m) * 0.03 for m in ["Saturn", "Mars", "Rahu", "Ketu"])
    burden += malefic_drishti
    burden += affliction_count(f, houses={1, 4, 7, 8, 10, 12}) * 3

    # Yoga modifiers
    if "Kemadruma Yoga (Negative)" in f["yogas"]: burden += 8
    if "Viparita Raja Yoga" in f["yogas"]:        burden -= 6
    if "Gajakesari Yoga" in f["yogas"]:           burden -= 4
    if f["neecha_bhanga"]: burden -= min(6, len(f["neecha_bhanga"]) * 3)

    # Classical refinements:
    # • Manglik severity is a real struggle indicator (Mars in violence houses).
    mg = f["manglik"]
    if "cancellations:" in mg or "WEAK MANGLIK" in mg or "NOT MANGLIK" in mg:
        pass
    elif "VERY HIGH MANGLIK" in mg: burden += 6
    elif "HIGH MANGLIK" in mg:      burden += 4
    elif "MILD MANGLIK" in mg:      burden += 2

    # • Negative yogas not in the dossier catalog
    special = _special_yoga_flags(f)
    if special["Mahapatakapa"]: burden += 7
    if special["Kala_Sarpa"]:   burden += 5
    if special["Shakat"]:       burden += 4

    return round(clamp_val(burden), 2)


def calculate_health_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    lagna_lord = f["house_lords"].get(1, {}).get("planet")
    structural = score_positive([(get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), 2.6), (get_bhava_bala(8, ls, planet_data, f, lagna_lon, jd_ut), 1.5), (get_bhava_bala(3, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (get_bhava_bala(6, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (sav_norm(f["sav"].get(1)), 1.0)])
    karaka = score_positive([(get_p_str(lagna_lord, planet_data, ls, f, lagna_lon, jd_ut), 1.8), (get_p_str("Sun", planet_data, ls, f, lagna_lon, jd_ut), 1.1), (get_p_str("Moon", planet_data, ls, f, lagna_lon, jd_ut), 1.2), (get_p_str("Saturn", planet_data, ls, f, lagna_lon, jd_ut), 1.1), (varga_sign_strength(f, "D9", lagna_lord), 0.8), (varga_sign_strength(f, "D12", lagna_lord), 0.3)])
    kp = score_positive([(house_promise_score(1, placidus_cusps, planet_data, r_lon, k_lon, ls, {1,11}, {2,7}), 1.1), (100 - house_promise_score(6, placidus_cusps, planet_data, r_lon, k_lon, ls, {1,11}, {2,7}) + 40, 0.7), (house_promise_score(8, placidus_cusps, planet_data, r_lon, k_lon, ls, {1,11}, {2,7}), 0.7)])
    _yoga_h = topic_yoga_score(f, {"Hamsa Yoga": 5, "Gajakesari Yoga": 5, "Adhi Yoga": 3}, planet_data, ls, lagna_lon, jd_ut)
    _yoga_h = _lagna_scaled(_yoga_h, get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut))
    protection = benefic_support(f, {1, 6, 8}) + _yoga_h
    risk = affliction_count(f, planets={lagna_lord, "Sun", "Moon", "Saturn"} - {None}) * 3 + len(f["weak_sav_houses"] & {1, 6, 8}) * 3

    # Classical refinements:
    # • Maraka pressure — 2L/7L placement, Lagna-lord in 8, etc. Approximates
    #   the constitutional-longevity layer of Pinda Ayurdaya without the full
    #   ayurdaya calc. Already bounded to [0, 30].
    maraka = _maraka_risk(f)
    # • Graha Yuddha — Mars/Saturn LOSER means injury/chronic illness susceptibility.
    war_health = 0
    for p in ("Mars", "Saturn", "Sun"):
        if f["planets"].get(p, {}).get("war") == "LOSER":
            war_health += 3

    return round(clamp_val(structural * 0.36 + karaka * 0.28 + kp * 0.14
                           + protection - risk - maraka * 0.4 - war_health), 2)


def calculate_happiness_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    structural = score_positive([(get_bhava_bala(4, ls, planet_data, f, lagna_lon, jd_ut), 2.4), (get_bhava_bala(5, ls, planet_data, f, lagna_lon, jd_ut), 1.3), (get_bhava_bala(9, ls, planet_data, f, lagna_lon, jd_ut), 1.0), (get_bhava_bala(11, ls, planet_data, f, lagna_lon, jd_ut), 0.8), (get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), 0.6), (sav_norm(f["sav"].get(4)), 1.0)])
    karaka = score_positive([(get_p_str("Moon", planet_data, ls, f, lagna_lon, jd_ut), 1.8), (get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.3), (get_p_str("Venus", planet_data, ls, f, lagna_lon, jd_ut), 1.0), (varga_sign_strength(f, "D9", "Moon"), 0.8)])
    yoga = topic_yoga_score(f, {"Gajakesari Yoga": 9, "Hamsa Yoga": 6, "Malavya Yoga": 5, "Adhi Yoga": 4}, planet_data, ls, lagna_lon, jd_ut)
    yoga = _lagna_scaled(yoga, get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut))
    support = benefic_support(f, {1, 4, 5, 9, 11})
    risk = affliction_count(f, planets={"Moon", "Venus", "Jupiter"}) * 3
    
    fourth_lord = f["house_lords"].get(4, {}).get("planet")
    if fourth_lord:
        fl_house = planet_house(f, fourth_lord)
        if fl_house in {1, 4, 5, 9, 10, 11}: support += 8
        elif fl_house in {6, 8, 12}: risk += 8
        
    if "Kemadruma Yoga (Negative)" in f["yogas"]: risk += 10

    # Classical refinements:
    # • Indu Lagna fold-in. The Indu Lagna sign carries the chart's overall
    #   prosperity-of-Moon signature; benefics there amplify inner contentment.
    indu_sign = f.get("indu_lagna", {}).get("sign")
    indu_score = 0
    if indu_sign:
        indu_sidx = SIGN_INDEX.get(indu_sign)
        if indu_sidx is not None:
            indu_house_for_planets = (indu_sidx - ls) % 12 + 1
            # Benefics placed in Indu sign / Indu lord well-placed
            for planet in NATURAL_BENEFICS:
                if planet_house(f, planet) == indu_house_for_planets:
                    indu_score += 4
            indu_lord = SIGN_LORDS_MAP[indu_sidx]
            indu_lord_h = f["planets"].get(indu_lord, {}).get("house", 0)
            if indu_lord_h in {1, 4, 5, 9, 10, 11}: indu_score += 6
            elif indu_lord_h in {6, 8, 12}:         indu_score -= 4

    # • Atmakaraka in a trikona = soul-aligned with dharma → deep inner happiness.
    ak = f["karakas"].get("Atmakaraka")
    ak_trikona = 0
    if ak and planet_house(f, ak) in {1, 5, 9}: ak_trikona = 8

    return round(clamp_val(structural * 0.40 + karaka * 0.28 + yoga + support
                           + indu_score + ak_trikona - risk), 2)


def calculate_luck_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    ninth_lord = f["house_lords"].get(9, {}).get("planet")
    structural = score_positive([(get_bhava_bala(9, ls, planet_data, f, lagna_lon, jd_ut), 2.6), (get_bhava_bala(5, ls, planet_data, f, lagna_lon, jd_ut), 1.7), (get_bhava_bala(11, ls, planet_data, f, lagna_lon, jd_ut), 1.0), (get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), 0.8), (sav_norm(f["sav"].get(9)), 1.2), (sav_norm(f["sav"].get(5)), 0.8)])
    karaka = score_positive([(get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.7), (get_p_str(ninth_lord, planet_data, ls, f, lagna_lon, jd_ut), 1.4), (varga_sign_strength(f, "D9", "Jupiter"), 1.0), (varga_sign_strength(f, "D9", ninth_lord), 1.0), (get_p_str("Sun", planet_data, ls, f, lagna_lon, jd_ut), 0.5)])
    kp = score_positive([(house_promise_score(9, placidus_cusps, planet_data, r_lon, k_lon, ls, {9,11}, {6,8,12}), 1.4), (house_promise_score(11, placidus_cusps, planet_data, r_lon, k_lon, ls, {9,11}, {6,8,12}), 0.8)])
    yoga = topic_yoga_score(f, {"Lakshmi Yoga": 9, "Gajakesari Yoga": 7, "Hamsa Yoga": 6, "Raja Yoga": 6, "Adhi Yoga": 4}, planet_data, ls, lagna_lon, jd_ut)
    yoga = _lagna_scaled(yoga, get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut))
    placement = topic_house_connection(f, ["Jupiter", ninth_lord, "Sun"], {1, 5, 9, 11})
    risk = affliction_count(f, planets={"Jupiter", ninth_lord} - {None}) * 3

    # Classical refinements:
    # • 5th lord = purva-punya carrier; its placement determines whether past
    #   merit manifests as luck. 5L in 1/5/9/11 = strong, in dusthana = blocked.
    fifth_lord_house = f["house_lords"].get(5, {}).get("house")
    fifth_lord_score = 0
    if fifth_lord_house in {1, 5, 9, 11}:    fifth_lord_score = 8
    elif fifth_lord_house in {2, 4, 7, 10}:  fifth_lord_score = 4
    elif fifth_lord_house in {6, 8, 12}:     fifth_lord_score = -6
    # • Sun in 9 = royal blessing (Surya in dharma sthana, classical).
    sun_in_9 = 6 if planet_house(f, "Sun") == 9 else 0
    # • Atmakaraka in 9 = soul aligned with fortune.
    ak = f["karakas"].get("Atmakaraka")
    ak_in_9 = 5 if ak and planet_house(f, ak) == 9 else 0
    # • Jupiter as 9th lord and well-placed (great Vedic teacher-fortune signature).
    jupiter_as_9l_bonus = 4 if ninth_lord == "Jupiter" and (
        f["planets"].get("Jupiter", {}).get("house", 0) in {1, 5, 9, 10, 11}
    ) else 0

    return round(clamp_val(structural * 0.38 + karaka * 0.26 + kp * 0.14
                           + yoga + placement
                           + fifth_lord_score + sun_in_9 + ak_in_9 + jupiter_as_9l_bonus
                           - risk), 2)


def calculate_spiritual_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    ak = f["karakas"].get("Atmakaraka")
    twelfth_lord = f["house_lords"].get(12, {}).get("planet")
    structural = score_positive([(get_bhava_bala(12, ls, planet_data, f, lagna_lon, jd_ut), 2.0), (get_bhava_bala(9, ls, planet_data, f, lagna_lon, jd_ut), 1.6), (get_bhava_bala(8, ls, planet_data, f, lagna_lon, jd_ut), 1.3), (get_bhava_bala(5, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (get_bhava_bala(4, ls, planet_data, f, lagna_lon, jd_ut), 0.6), (sav_norm(f["sav"].get(12)), 1.0), (sav_norm(f["sav"].get(9)), 0.8)])
    karaka = score_positive([(get_p_str("Ketu", planet_data, ls, f, lagna_lon, jd_ut), 1.6), (get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.4), (get_p_str("Saturn", planet_data, ls, f, lagna_lon, jd_ut), 0.9), (get_p_str(ak, planet_data, ls, f, lagna_lon, jd_ut), 1.2), (get_p_str(twelfth_lord, planet_data, ls, f, lagna_lon, jd_ut), 1.0), (varga_sign_strength(f, "D9", ak), 0.8), (varga_sign_strength(f, "D9", "Jupiter"), 0.8)])
    placement = 0
    for planet, points in {"Ketu": 12, "Jupiter": 8, "Saturn": 5, ak: 7, twelfth_lord: 6}.items():
        if planet and planet_house(f, planet) in {1, 4, 5, 8, 9, 12}: placement += points
    yoga = topic_yoga_score(f, {"Hamsa Yoga": 8, "Viparita Raja Yoga": 7, "Gajakesari Yoga": 3}, planet_data, ls, lagna_lon, jd_ut)
    yoga = _lagna_scaled(yoga, get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut))

    # Classical refinements:
    # • Karakamsa Lagna (AK's D9 sign) is the central Jaimini spiritual signature.
    #   Planets in the 12th from Karakamsa indicate the soul's renunciation pull.
    karakamsa_idx, planets_in_12th = _karakamsa_data(f)
    karakamsa_score = 0
    if karakamsa_idx is not None:
        # Ketu/Saturn/Jupiter in the 12th from Karakamsa are the strongest
        # classical Pravrajya (renunciation) signatures.
        if "Ketu" in planets_in_12th:    karakamsa_score += 12
        if "Saturn" in planets_in_12th:  karakamsa_score += 6
        if "Jupiter" in planets_in_12th: karakamsa_score += 6
        if "Sun" in planets_in_12th:     karakamsa_score += 3
        if "Mars" in planets_in_12th:    karakamsa_score += 2

    # • Vairagya / Pravrajya yoga — Saturn conjunct Ketu in any house = renunciation.
    special = _special_yoga_flags(f)
    vairagya_bonus = 8 if special["Vairagya"] else 0

    # • Guru Chandal penalty — Jupiter conjunct Rahu/Ketu distorts the guru
    #   principle, polluting spiritual integrity with false teachings or illusions.
    guru_chandal_penalty = 8 if special.get("Guru_Chandal") else 0

    # • 12th lord placed in 5/9/12 is a classical moksha signature.
    twelfth_lord_house = f["house_lords"].get(12, {}).get("house")
    twelfth_lord_position_bonus = 6 if twelfth_lord_house in {5, 9, 12} else 0

    return round(clamp_val(structural * 0.34 + karaka * 0.27
                           + placement + yoga
                           + karakamsa_score + vairagya_bonus + twelfth_lord_position_bonus
                           - guru_chandal_penalty), 2)


def calculate_hidden_pitfalls_score(dossier, profile=None):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    ak = f["karakas"].get("Atmakaraka")
    amk = f["karakas"].get("Amatyakaraka")
    dk = f["karakas"].get("Darakaraka")
    burden = 15
    burden += get_bhava_bala(8, ls, planet_data, f, lagna_lon, jd_ut) * 0.16 + get_bhava_bala(12, ls, planet_data, f, lagna_lon, jd_ut) * 0.14 + get_bhava_bala(6, ls, planet_data, f, lagna_lon, jd_ut) * 0.07
    
    malefic_drishti = 0
    for h_idx in [1, 2, 4, 7, 8, 10, 12]:
        h_lon = ((ls + h_idx - 1) * 30 + 15) % 360
        malefic_drishti += sum(calc_drishti(planet_data[m][0], h_lon, m) * 0.03 for m in ["Saturn", "Mars", "Rahu", "Ketu"])
    burden += malefic_drishti
    
    # Affliction count — but bound it so a single planet in a dusthana
    # doesn't get counted ~3x via overlapping planet + house sets.
    karaka_affliction = affliction_count(f, planets={ak, amk, dk, "Moon", "Venus", "Jupiter"} - {None})
    house_affliction  = affliction_count(f, houses={1, 2, 4, 7, 8, 10, 12})
    # De-duplicate the overlap: a planet that's in both groups was previously
    # adding 5 + 3 = 8. Cap the combined contribution at planet_count * 5 + 1.
    combined_aff = karaka_affliction * 4 + max(0, house_affliction - karaka_affliction) * 2
    burden += combined_aff

    for planet in {ak, amk, dk, "Moon", "Venus", "Jupiter", "Saturn"} - {None}:
        if varga_sign_strength(f, "D9", planet) <= 32: burden += 4
        if varga_sign_strength(f, "D30", planet) <= 32: burden += 5

    if house_promise_score(2, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,11}, {6,8,12}) < 40: burden += 3
    if house_promise_score(7, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,7,11}, {1,6,10}) < 40: burden += 3
    if house_promise_score(10, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,6,10,11}, {5,8,12}) < 40: burden += 3

    if planet_house(f, "Rahu") in {1, 2, 4, 7, 10}: burden += 7
    if planet_house(f, "Ketu") in {1, 2, 4, 7, 10}: burden += 5

    # Classical negative yoga detection (not in the dossier's yoga catalog):
    special = _special_yoga_flags(f)
    if special["Daridra"]:      burden += 8   # 11th lord in dusthana = poverty/want
    if special["Shakat"]:       burden += 6   # Moon in 6/8/12 from Jupiter = fortune-block
    if special["Kala_Sarpa"]:   burden += 8   # all 7 grahas hemmed by Rahu-Ketu axis
    if special["Mahapatakapa"]: burden += 8   # 3+ malefics conjunct in a dusthana

    if f["neecha_bhanga"]: burden -= min(5, len(f["neecha_bhanga"]) * 2)
    if "Gajakesari Yoga" in f["yogas"]: burden -= 3
    if special["Vairagya"]:    burden -= 4   # spiritual flag mitigates worldly pitfalls
    return round(clamp_val(burden), 2)


def custom_is_reverse_rank(criteria):
    q = str(criteria).lower()
    return any(w in q for w in [
        "least", "lowest", "fewest", "less likely", "minimum", "smallest",
        "worst", "weakest", "poorest",
    ])


def custom_is_risk_topic(criteria):
    """Whether the criterion frames as a NEGATIVE outcome (rank-by-burden)."""
    q = str(criteria).lower()
    return any(w in q for w in [
        "struggle", "pitfall", "problem", "risk", "danger", "accident", "disease",
        "illness", "debt", "loss", "failure", "divorce", "separation", "enemy",
        "litigation", "scandal", "delay", "obstacle", "suffer", "hardship",
        "early death", "die young", "premature death", "addiction", "depression",
        "bankrupt", "betray", "infidelity", "cheat",
    ])


# Topic profiles for custom-criterion routing. Each entry maps keywords to a
# specialized chart-signature recipe. Multiple profiles can match — the blender
# below combines them weighted by keyword density.
_CUSTOM_TOPIC_PROFILES = [
    # ── Wealth and money flavors ────────────────────────────────────────────
    (["rich", "wealth", "money", "finance", "income", "business", "profit", "earn"],
     "Wealth", [2, 11, 5, 9], ["Jupiter", "Venus", "Mercury"], ["D2", "D9"], [2, 11],
     {"Dhana Yoga": 7, "Lakshmi Yoga": 8, "Chandra-Mangala Yoga": 5, "Raja Yoga": 4}),
    (["inherit", "inheritance", "ancestral", "windfall", "legacy", "sudden gain", "insurance"],
     "Inheritance", [8, 2, 11], ["Saturn", "Jupiter", "Rahu"], ["D9"], [2, 8],
     {"Viparita Raja Yoga": 8, "Dhana Yoga": 4}),
    # ── Relationship / marriage flavors ─────────────────────────────────────
    (["marriage", "relationship", "love", "spouse", "partner", "romance", "wedding"],
     "Relationship", [7, 2, 4, 5, 8], ["Venus", "Jupiter", "Moon"], ["D9"], [7],
     {"Malavya Yoga": 7, "Gajakesari Yoga": 5}),
    (["foreign spouse", "marry foreigner", "foreigner", "cross-cultural", "intercaste"],
     "Foreign-marriage", [7, 9, 12], ["Venus", "Rahu", "Jupiter"], ["D9"], [7, 9, 12],
     {"Raja Yoga": 3}),
    # ── Career flavors ──────────────────────────────────────────────────────
    (["career", "job", "profession", "promotion", "status", "position", "executive"],
     "Career", [10, 6, 11, 2, 9], ["Sun", "Saturn", "Mercury", "Mars"], ["D10", "D9"], [10, 6, 11],
     {"Dharma-Karma Adhipati Yoga": 10, "Raja Yoga": 7, "Shasha Yoga": 5, "Bhadra Yoga": 5}),
    (["entrepreneur", "founder", "startup", "self-employed", "own business"],
     "Entrepreneur", [7, 10, 11, 2], ["Mars", "Sun", "Mercury", "Jupiter"], ["D10"], [7, 10, 11],
     {"Raja Yoga": 6, "Dharma-Karma Adhipati Yoga": 6, "Ruchaka Yoga": 5}),
    (["tech", "engineer", "software", "scientist", "digital", "programmer", "developer"],
     "Tech", [10, 5, 11, 3], ["Mercury", "Mars", "Rahu", "Saturn"], ["D10"], [10, 11],
     {"Bhadra Yoga": 6, "Raja Yoga": 5}),
    (["doctor", "medical", "physician", "surgeon", "healer"],
     "Medical", [6, 10, 8], ["Sun", "Mars", "Jupiter", "Ketu"], ["D9"], [6, 10],
     {"Raja Yoga": 5, "Ruchaka Yoga": 5}),
    # ── Fame / public life ──────────────────────────────────────────────────
    (["fame", "famous", "celebrity", "public", "recognition", "popular", "renown", "icon"],
     "Fame", [10, 11, 5, 9, 1], ["Sun", "Moon", "Jupiter", "Rahu"], ["D10", "D9"], [10, 11],
     {"Raja Yoga": 8, "Dharma-Karma Adhipati Yoga": 8, "Gajakesari Yoga": 5}),
    (["leader", "leadership", "politic", "authority", "power", "influence", "command", "minister"],
     "Leadership", [1, 6, 9, 10, 11], ["Sun", "Mars", "Saturn", "Jupiter"], ["D10"], [10, 11],
     {"Raja Yoga": 8, "Dharma-Karma Adhipati Yoga": 9, "Ruchaka Yoga": 5, "Shasha Yoga": 5}),
    # ── Education / intellect ───────────────────────────────────────────────
    (["intelligence", "education", "study", "academic", "exam", "learning", "wisdom", "scholar", "phd"],
     "Learning", [4, 5, 9, 10], ["Mercury", "Jupiter", "Moon"], ["D9", "D24"], [5, 9],
     {"Bhadra Yoga": 6, "Hamsa Yoga": 6, "Gajakesari Yoga": 4}),
    # ── Arts / creativity ───────────────────────────────────────────────────
    (["creative", "creativity", "art", "artist", "design"],
     "Creativity", [3, 5, 2, 10, 11], ["Venus", "Mercury", "Moon"], ["D9", "D10"], [3, 5, 10, 11],
     {"Malavya Yoga": 6, "Bhadra Yoga": 5, "Gajakesari Yoga": 4}),
    (["music", "musician", "singer", "song", "compose"],
     "Music", [3, 5, 2], ["Venus", "Mercury", "Moon"], ["D9"], [3, 5],
     {"Malavya Yoga": 7, "Gajakesari Yoga": 4}),
    (["writer", "writing", "author", "poet", "novelist", "journalist"],
     "Writing", [3, 5, 2, 10], ["Mercury", "Jupiter", "Moon"], ["D9"], [3, 5],
     {"Bhadra Yoga": 6, "Gajakesari Yoga": 4}),
    (["actor", "actress", "performer", "drama", "theatre", "film", "cinema"],
     "Performance", [3, 5, 10, 11], ["Venus", "Moon", "Sun"], ["D9", "D10"], [10, 11],
     {"Malavya Yoga": 7, "Raja Yoga": 5}),
    # ── Beauty / charm ──────────────────────────────────────────────────────
    (["beauty", "beautiful", "attractive", "charm", "style", "luxury", "glamour"],
     "Charm", [1, 2, 4, 5, 7], ["Venus", "Moon", "Jupiter"], ["D9"], [1, 7, 11],
     {"Malavya Yoga": 8, "Gajakesari Yoga": 4}),
    # ── Children ────────────────────────────────────────────────────────────
    (["child", "children", "progeny", "fertility", "kids", "son", "daughter"],
     "Children", [5, 2, 9, 11], ["Jupiter", "Moon", "Sun"], ["D9"], [5],
     {"Hamsa Yoga": 5, "Gajakesari Yoga": 4}),
    # ── Property / home ─────────────────────────────────────────────────────
    (["property", "home", "house", "land", "vehicle", "comfort", "real estate"],
     "Property", [4, 2, 11, 9], ["Moon", "Venus", "Mars"], ["D9"], [4, 11],
     {"Malavya Yoga": 5, "Gajakesari Yoga": 4}),
    # ── Foreign / travel ────────────────────────────────────────────────────
    (["foreign", "abroad", "travel", "overseas", "settlement", "visa", "immigrate", "emigrant"],
     "Foreign", [9, 12, 3, 7], ["Rahu", "Moon", "Jupiter", "Saturn"], ["D9"], [9, 12],
     {"Raja Yoga": 3}),
    # ── Spiritual ───────────────────────────────────────────────────────────
    (["spiritual", "moksha", "religion", "guru", "occult", "meditation", "yogi", "monk", "saint"],
     "Spiritual", [12, 9, 8, 5], ["Ketu", "Jupiter", "Saturn"], ["D9"], [12, 9],
     {"Hamsa Yoga": 8, "Viparita Raja Yoga": 7}),
    # ── Health-specific (inverted) ──────────────────────────────────────────
    (["healthy", "fit", "robust", "athletic", "vitality"],
     "Vitality", [1, 8, 3, 6], ["Sun", "Mars", "Jupiter"], ["D9", "D12"], [1, 11],
     {"Hamsa Yoga": 6, "Ruchaka Yoga": 5}),
]


def custom_topic_profile(criteria):
    """Return a single best-match topic profile (legacy single-topic path).
    Multi-topic blending is handled separately in calculate_custom_aspect_score."""
    q = str(criteria).lower()
    for words, name, houses, planets, vargas, kp_houses, yogas in _CUSTOM_TOPIC_PROFILES:
        if any(w in q for w in words):
            return {"name": name, "houses": houses, "planets": planets,
                    "vargas": vargas, "kp": kp_houses, "yogas": yogas}
    return {"name": "General Potential", "houses": [1, 5, 9, 10, 11],
            "planets": ["Sun", "Moon", "Jupiter", "Mercury"], "vargas": ["D9", "D10"],
            "kp": [10, 11], "yogas": {"Raja Yoga": 6, "Gajakesari Yoga": 5, "Hamsa Yoga": 4}}


def _custom_keyword_matches(criteria):
    """Return list of (profile_dict, match_count) for every profile whose keywords appear in the criterion.
    Empty list means no match. Multiple matches enable blending."""
    q = str(criteria).lower()
    matches = []
    for words, name, houses, planets, vargas, kp_houses, yogas in _CUSTOM_TOPIC_PROFILES:
        hits = sum(1 for w in words if w in q)
        if hits > 0:
            matches.append((
                {"name": name, "houses": houses, "planets": planets,
                 "vargas": vargas, "kp": kp_houses, "yogas": yogas},
                hits,
            ))
    return matches


def _custom_modifier_flags(criteria):
    """Detect modifier words that change how a topic is evaluated.
      • inverted: 'die young', 'early death', 'fail at X' → invert direction
      • early/timing: 'young', 'early' → no current effect (lifetime baseline only)
    """
    q = str(criteria).lower()
    return {
        "is_risk": custom_is_risk_topic(criteria),
        "is_inverted": custom_is_reverse_rank(criteria) or any(
            w in q for w in ["die young", "early death", "premature", "fail at"]
        ),
    }


def calculate_custom_aspect_score(dossier, criteria, profile=None):
    """
    Score a user-defined custom criterion against a chart.

    Strategy:
      1. Detect modifier flags (risk-framing, inversion).
      2. Find ALL matching keyword profiles (multi-topic blending).
      3. If a single dominant topic matches with a clean direction → route to
         the specialized scorer (e.g. "Most likely to be rich" → wealth).
      4. If multiple profiles match → blend their chart-signature recipes
         weighted by keyword density.
      5. If user wants inverted (risk) version of a positive topic → use
         struggles/hidden-pitfalls scorer.
    """
    flags = _custom_modifier_flags(criteria)
    q = str(criteria).lower()

    # ── Step 1: direct specialized-scorer routes for unambiguous topics ────
    # These cover ~70% of common custom criteria with full-accuracy scorers.
    is_risk = flags["is_risk"]
    if any(w in q for w in ["wealth", "rich", "money", "finance"]) and not is_risk:
        return calculate_wealth_score(dossier, profile=profile)
    if any(w in q for w in ["marriage", "relationship", "love", "spouse"]) and not is_risk and not any(w in q for w in ["foreign", "abroad"]):
        return calculate_relationship_score(dossier, profile=profile)
    if any(w in q for w in ["career", "profession", "job", "promotion"]) and not is_risk and not any(w in q for w in ["tech", "doctor", "entrepreneur", "actor", "musician"]):
        return calculate_career_score(dossier, profile=profile)
    if any(w in q for w in ["health", "longevity", "constitution", "healthy", "vitality"]) and not is_risk:
        return calculate_health_score(dossier, profile=profile)
    if any(w in q for w in ["happy", "happiness", "contentment", "fulfilled"]) and not is_risk:
        return calculate_happiness_score(dossier, profile=profile)
    if any(w in q for w in ["luck", "fortune", "fortunate"]) and not is_risk:
        return calculate_luck_score(dossier, profile=profile)
    if any(w in q for w in ["spiritual", "moksha", "religion", "occult", "guru", "monk"]):
        return calculate_spiritual_score(dossier, profile=profile)
    if any(w in q for w in ["hidden", "pitfall", "unexpected", "scandal", "secret"]):
        return calculate_hidden_pitfalls_score(dossier, profile=profile)
    if is_risk:
        return calculate_struggles_score(dossier, profile=profile)

    # ── Step 2: multi-topic blending via the keyword profiles ──────────────
    matches = _custom_keyword_matches(criteria)
    if not matches:
        spec = custom_topic_profile(criteria)
        matches = [(spec, 1)]

    # Merge multi-topic houses / planets / vargas / kp / yogas, weighted by hits.
    merged_houses = []
    merged_planets = []
    merged_vargas = set()
    merged_kp = []
    merged_yogas = {}
    total_hits = sum(h for _, h in matches)
    for spec, hits in matches:
        weight = hits / total_hits
        merged_houses.extend(spec["houses"] * max(1, hits))
        merged_planets.extend(spec["planets"] * max(1, hits))
        merged_vargas.update(spec["vargas"])
        merged_kp.extend(spec["kp"] * max(1, hits))
        for y, w in spec["yogas"].items():
            merged_yogas[y] = max(merged_yogas.get(y, 0), int(w * weight + 0.5))

    # De-dup while keeping order so the strongest topic's houses come first.
    def _ordered_unique(seq):
        seen = set(); out = []
        for x in seq:
            if x not in seen:
                seen.add(x); out.append(x)
        return out
    merged_houses = _ordered_unique(merged_houses)
    merged_planets = _ordered_unique(merged_planets)
    merged_kp = _ordered_unique(merged_kp)

    math_data = recalc_math(dossier, profile=profile)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data

    f = parse_chart_facts(dossier)
    structural_parts = []
    for idx, house in enumerate(merged_houses):
        structural_parts.append((house_score(f, house), max(0.5, 2.0 - idx * 0.20)))
    karaka_parts = [(planet_strength(f, p), 1.0) for p in merged_planets]
    for chart in merged_vargas:
        for p in merged_planets[:3]:
            karaka_parts.append((varga_sign_strength(f, chart, p), 0.45))
    kp_parts = [(kp_norm(extract_kp_promise(dossier, h)), 1.0) for h in merged_kp]

    yoga = topic_yoga_score(f, merged_yogas, planet_data, ls, lagna_lon, jd_ut)
    placement = topic_house_connection(f, merged_planets, set(merged_houses))
    risk = affliction_count(f, planets=set(merged_planets)) * 4

    score = (score_positive(structural_parts) * 0.42
             + score_positive(karaka_parts) * 0.28
             + score_positive(kp_parts) * 0.14
             + yoga + placement - risk)

    # ── Step 3: inversion modifier ─────────────────────────────────────────
    if flags["is_inverted"]:
        score = 100 - score   # 'die young', 'fail at X', etc.

    return round(clamp_val(score), 2)


def get_prashna_python_verdict(question, dossier_text):
    q_lower = question.lower()
    house = 1
    if any(w in q_lower for w in ["job","career","promotion","business","work","profession"]): house = 10
    elif any(w in q_lower for w in ["love","marry","marriage","relationship","partner","wedding","spouse"]): house = 7
    elif any(w in q_lower for w in ["money","wealth","finance","loan","buy","invest","rich","earn"]): house = 2
    elif any(w in q_lower for w in ["health","sick","recover","surgery","disease","hospital","cure"]): house = 6
    elif any(w in q_lower for w in ["child","kid","pregnancy","baby","conceive","son","daughter"]): house = 5
    elif any(w in q_lower for w in ["travel","visa","abroad","foreign","overseas","trip"]): house = 9
    elif any(w in q_lower for w in ["house","property","home","flat","vehicle","car","land"]): house = 4
    elif any(w in q_lower for w in ["court","legal","lawsuit","case","enemy","conflict"]): house = 6
    elif any(w in q_lower for w in ["education","study","degree","exam","course"]): house = 5
    elif any(w in q_lower for w in ["spiritual","moksha","liberation","guru","pilgrimage"]): house = 12

    kp_score = extract_kp_promise(dossier_text, house)
    if kp_score == 3: return "YES", f"KP H{house} Sub-Lord STRONGLY SIGNIFIES the required houses — event is PROMISED."
    elif kp_score == 2: return "DELAYED / PARTIAL", f"KP H{house} Sub-Lord partially signifies required houses — possible but with delay/conditions."
    elif kp_score == 0: return "NO", f"KP H{house} Sub-Lord does NOT signify required houses — event is DENIED by chart structure."

    score = extract_base_score(dossier_text, house)
    if score == 3: return "YES", f"H{house} is mathematically STRONGLY PROMISED (Base Score 3/3)."
    elif score == 2: return "DELAYED / PARTIAL", f"H{house} is WEAKLY PROMISED (Base Score 2/3) — possible with effort/delay."
    else: return "NO", f"H{house} lacks mathematical promise (Base Score 1/3) — chart structure does not support this event now."


# ─────────────────────────────────────────────────────────────────────────────
# Classical refinement helpers — used by the 9 specialized scorers below to
# push each toward 10/10 accuracy. All operate purely on lifetime-baseline
# chart facts (no transits, no current dasha).
# ─────────────────────────────────────────────────────────────────────────────

def _karakamsa_data(facts):
    """Karakamsa = the D9 sign occupied by the Atmakaraka. Classical Jaimini's
    primary signature for spiritual life. Returns:
        karakamsa_sign_idx, set_of_planets_in_12th_from_karakamsa.
    Used by the Spiritual scorer to detect Pravrajya/renunciation signatures.
    Returns (None, set()) if AK or D9 vargas missing.
    """
    ak = facts.get("karakas", {}).get("Atmakaraka")
    if not ak: return None, set()
    d9_signs = facts.get("vargas", {}).get("D9", {})
    if not d9_signs: return None, set()
    ak_d9_sign = d9_signs.get(ak)
    if not ak_d9_sign: return None, set()
    karakamsa_idx = SIGN_INDEX.get(ak_d9_sign)
    if karakamsa_idx is None: return None, set()
    twelfth_from_k = (karakamsa_idx + 11) % 12
    twelfth_sign_name = SIGNS[twelfth_from_k]
    in_12th = {p for p, s in d9_signs.items() if s == twelfth_sign_name}
    return karakamsa_idx, in_12th


def _seventh_lord_placement(facts):
    """Return (7th_lord_planet, house_of_7th_lord, dignity_bucket).
    dignity_bucket: 'kendra_trikona' / 'upachaya' / 'neutral' / 'dusthana' / 'unknown'.
    Used by Relationship scorer for the 7L placement signal (which was missing).
    """
    h7 = facts.get("house_lords", {}).get(7, {})
    lord = h7.get("planet")
    house = h7.get("house")
    if not lord or not house: return None, 0, "unknown"
    if house in {1, 4, 7, 10, 5, 9}:    bucket = "kendra_trikona"
    elif house in {3, 6, 11}:           bucket = "upachaya"
    elif house in {6, 8, 12}:           bucket = "dusthana"
    else:                               bucket = "neutral"
    return lord, house, bucket


def _maraka_risk(facts):
    """Maraka (death-giving) classical heuristic for Health/Longevity baseline.
    Higher score = more maraka pressure on the constitution.
    Bounded ~ [0, 30]. Used as a burden additive.
    """
    risk = 0
    # 2nd lord and 7th lord are natural marakas. If they sit in dusthana,
    # their maraka tendency is amplified (they break the very houses they own).
    h2_lord = facts.get("house_lords", {}).get(2, {}).get("planet")
    h2_lord_house = facts.get("house_lords", {}).get(2, {}).get("house")
    h7_lord = facts.get("house_lords", {}).get(7, {}).get("planet")
    h7_lord_house = facts.get("house_lords", {}).get(7, {}).get("house")
    if h2_lord_house in {6, 8, 12}:   risk += 6
    if h7_lord_house in {6, 8, 12}:   risk += 8
    # Lagna lord in 8th = severe constitutional stress.
    h1_lord_house = facts.get("house_lords", {}).get(1, {}).get("house")
    if h1_lord_house == 8:            risk += 8
    elif h1_lord_house in {6, 12}:    risk += 4
    # Affliction of Lagna lord
    h1_lord = facts.get("house_lords", {}).get(1, {}).get("planet")
    if h1_lord and h1_lord in facts.get("planets", {}):
        tags = facts["planets"][h1_lord].get("tags", set())
        if "Debilitated" in tags and h1_lord not in facts.get("neecha_bhanga", set()):
            risk += 5
        if any("Combust" in t for t in tags): risk += 3
    return min(30, risk)


def _special_yoga_flags(facts):
    """Classical negative yogas not currently in the dossier's yoga catalog.
    Returns dict of yoga_name → True/False. Used for Hidden Pitfalls and Struggles.
    """
    flags = {"Daridra": False, "Shakat": False, "Kala_Sarpa": False,
             "Vairagya": False, "Mahapatakapa": False, "Guru_Chandal": False}

    # Daridra Yoga: 11th lord in 6/8/12 → poverty/want
    h11_lord_house = facts.get("house_lords", {}).get(11, {}).get("house")
    if h11_lord_house in {6, 8, 12}: flags["Daridra"] = True

    # Shakat Yoga: Moon in 6/8/12 from Jupiter (relative axis of misfortune)
    jup_h = facts.get("planets", {}).get("Jupiter", {}).get("house", 0)
    moon_h = facts.get("planets", {}).get("Moon", {}).get("house", 0)
    if jup_h and moon_h:
        rel = ((moon_h - jup_h) % 12) + 1
        if rel in {6, 8, 12}: flags["Shakat"] = True

    # Kala Sarpa Yoga: all 7 grahas hemmed between Rahu and Ketu.
    rahu_h = facts.get("planets", {}).get("Rahu", {}).get("house", 0)
    ketu_h = facts.get("planets", {}).get("Ketu", {}).get("house", 0)
    if rahu_h and ketu_h:
        grahas = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        graha_houses = [facts["planets"].get(p, {}).get("house", 0) for p in grahas]
        if all(h > 0 for h in graha_houses):
            # Sweep from Rahu's house through the 6 houses ahead (clockwise on rasi).
            arc_forward = set()
            h = rahu_h
            for _ in range(7):
                arc_forward.add(h)
                h = (h % 12) + 1
                if h == ketu_h: break
            if all(h in arc_forward for h in graha_houses):
                flags["Kala_Sarpa"] = True
            else:
                arc_backward = set()
                h = ketu_h
                for _ in range(7):
                    arc_backward.add(h)
                    h = (h % 12) + 1
                    if h == rahu_h: break
                if all(h in arc_backward for h in graha_houses):
                    flags["Kala_Sarpa"] = True

    # Vairagya / Pravrajya Yoga: Saturn-Ketu conjunction → renunciation signature
    sat_h = facts.get("planets", {}).get("Saturn", {}).get("house", 0)
    if sat_h and ketu_h and sat_h == ketu_h:
        flags["Vairagya"] = True

    # Guru Chandal Yoga — Jupiter conjunct Rahu or Ketu.
    # The "false guru" trap: Jupiter's wisdom is distorted by a node's shadow,
    # causing spiritual confusion, deceptive teachers, or misguided idealism.
    jup_h_chandal = facts.get("planets", {}).get("Jupiter", {}).get("house", 0)
    if jup_h_chandal and (
        (rahu_h and jup_h_chandal == rahu_h) or
        (ketu_h and jup_h_chandal == ketu_h)
    ):
        flags["Guru_Chandal"] = True

    # Mahapatakapa: 3+ malefics conjunct in a single dusthana
    if facts.get("planets"):
        for dh in (6, 8, 12):
            mal_count = sum(1 for p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
                            if facts["planets"].get(p, {}).get("house") == dh)
            if mal_count >= 3:
                flags["Mahapatakapa"] = True
                break

    return flags


def _house_lord_in_houses(facts, source_house, target_houses):
    """True if the lord of `source_house` is currently placed in any of `target_houses`."""
    lord_house = facts.get("house_lords", {}).get(source_house, {}).get("house")
    return lord_house in set(target_houses)


def _planet_in_houses(facts, planet, target_houses):
    return facts.get("planets", {}).get(planet, {}).get("house", 0) in set(target_houses)


def _lagna_scaled(raw_bonus, h1_bala, floor=0.30):
    """Scale any yoga bonus by Lagna Bhava Bala.

    Classical doctrine: no yoga can bear full fruit if the Lagna
    (self / foundation) is weak. A floor of 0.30 prevents complete
    annihilation for borderline charts; a cap of 1.0 prevents
    accidental amplification above the raw promise.

    Args:
        raw_bonus: unadjusted yoga bonus (float).
        h1_bala  : Bhava Bala of the 1st house, expected 0-100 range.
        floor    : minimum scaling factor (default 0.30).
    Returns:
        Scaled bonus (float).
    """
    factor = max(floor, min(1.0, h1_bala / 100.0))
    return raw_bonus * factor


# ─────────────────────────────────────────────────────────────────────────────
# Trust & transparency layer for Compare Profiles
#
# These helpers expose calibrated honesty about the scoring engine:
#   • score_band         — qualitative band (Very Strong … Very Weak) so users
#                          don't anchor on decimals (Vedic is not quantitative).
#   • _cohort_stats      — mean/std/percentile per criterion. Surfaces cohort-
#                          relative position so "best in a weak cohort" doesn't
#                          masquerade as absolute strength.
#   • _discrimination    — variance-driven label. Low variance ⇒ ranks are
#                          unreliable for that criterion, so we say so.
#   • _detect_ties       — flag profiles within ±5 of each other (heuristic
#                          noise floor) so users don't over-interpret tiny gaps.
#   • _detect_generational — placements shared by ≥60% of cohort. These DO
#                          appear in every chart's scoring but they DON'T
#                          differentiate this cohort, so they should be cited
#                          differently in narrative.
#   • _chart_headline    — top 3 most-significant placements per chart, so the
#                          AI anchors on real placements (exalted/debilitated/
#                          Mahapurusha) before interpreting.
#   • _criterion_drivers — post-hoc "why did this chart score this way" — top
#                          3 supports + top 2 drains based on facts_dict.
# ─────────────────────────────────────────────────────────────────────────────

def score_band(score, is_negative=False):
    """Map a 0-100 score to a qualitative band label.

    Vedic astrology is a qualitative-analytical tradition; raw decimals create
    false precision. The bands are the doctrine-appropriate interpretation:
    the decimal is for ORDERING only.

    For negative-axis criteria (Struggles, Hidden Pitfalls) the labels invert
    — a high burden score = "Severe", not "Very Strong".
    """
    if score is None: return "—"
    if is_negative:
        if score >= 75: return "Severe"
        if score >= 60: return "High"
        if score >= 45: return "Moderate"
        if score >= 30: return "Low"
        return "Minimal"
    if score >= 80: return "Very Strong"
    if score >= 65: return "Strong"
    if score >= 50: return "Moderate"
    if score >= 35: return "Weak"
    return "Very Weak"


def _cohort_stats(scores_dict):
    """For a {name: score} dict, return mean, std, percentiles, discrimination.

    percentile = fraction of cohort STRICTLY BELOW this score, 0-100.
    discrimination = qualitative label based on std:
        std < 5  → 'low'      (cohort clusters, ranks unreliable)
        std < 10 → 'moderate' (some differentiation)
        std >=10 → 'high'     (clear differentiation)
    """
    values = list(scores_dict.values())
    n = len(values)
    if n == 0:
        return {"mean": 50.0, "std": 0.0, "percentiles": {}, "discrimination": "n/a"}
    if n == 1:
        only = list(scores_dict.keys())[0]
        return {"mean": values[0], "std": 0.0, "percentiles": {only: 50.0}, "discrimination": "single-profile"}
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(var)
    percentiles = {
        name: round(sum(1 for v in values if v < score) / max(1, n - 1) * 100, 1)
        for name, score in scores_dict.items()
    }
    if std < 5:    disc = "low"
    elif std < 10: disc = "moderate"
    else:          disc = "high"
    return {"mean": mean, "std": std, "percentiles": percentiles, "discrimination": disc}


def _detect_ties(scores_dict, tie_threshold=5.0):
    """Return a list of tied-group lists. Two scores are tied if they're
    within `tie_threshold` of each other. The threshold matches the heuristic
    noise floor of the scoring engine — below this gap, rank order is not
    statistically meaningful.

    Returns: [[name, name, ...], ...] groups of size ≥2.
    """
    ordered = sorted(scores_dict.items(), key=lambda kv: kv[1], reverse=True)
    groups, current = [], []
    for i, (name, score) in enumerate(ordered):
        if not current:
            current = [name]
            continue
        prev_score = scores_dict[current[-1]]
        if abs(prev_score - score) <= tie_threshold:
            current.append(name)
        else:
            if len(current) >= 2: groups.append(current)
            current = [name]
    if len(current) >= 2: groups.append(current)
    return groups


def _detect_generational_placements(facts_per_profile, threshold_fraction=0.60):
    """Detect placements shared by ≥`threshold_fraction` of the cohort.

    These placements DO appear in each chart's individual scoring (correctly),
    but they DON'T differentiate the cohort from each other. The AI should be
    told about them so it doesn't cite e.g. "Saturn in Aries" as a personal
    distinguisher when 7 of 9 cohort members share it.

    Returns dict like:
        {
            "Saturn_sign:Aries": 7,
            "yoga:Gajakesari Yoga": 6,
            ...
        }
    Threshold is on count, derived from fraction × cohort_size (min 2 to avoid
    spurious 2-of-3 hits in tiny cohorts).
    """
    n = len(facts_per_profile)
    if n < 3: return {}
    threshold = max(2, int(threshold_fraction * n))

    counters = {}
    for facts in facts_per_profile:
        seen = set()
        # Slow-moving planets define generational cohorts (Saturn, Jupiter,
        # Rahu, Ketu). Fast planets are personal.
        for p in ("Saturn", "Jupiter", "Rahu", "Ketu"):
            sign = facts.get("planets", {}).get(p, {}).get("sign")
            if sign:
                seen.add(f"{p}_sign:{sign}")
        # Yogas shared by most of cohort. facts["yogas"] is a dict (name → desc)
        # from extract_present_yogas; iterating gives keys, which is what we want.
        for y in (facts.get("yogas") or {}):
            seen.add(f"yoga:{y}")
        for item in seen:
            counters[item] = counters.get(item, 0) + 1
    return {item: count for item, count in counters.items() if count >= threshold}


def _chart_headline(facts):
    """Return up to 3 most-significant placements for a chart, prioritising
    classically-strong signals over engineered ones. Drives the per-profile
    headline block in the comparison output and forces the AI to anchor on
    real, named placements before interpreting.
    """
    bits = []

    # Tier 1 — Exalted/Debilitated planets (always headline)
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        tags = facts.get("planets", {}).get(p, {}).get("tags", set())
        sign = facts.get("planets", {}).get(p, {}).get("sign", "")
        house = facts.get("planets", {}).get(p, {}).get("house", 0)
        if "Exalted" in tags:
            bits.append(f"{p} EXALTED in {sign} (H{house})")
        elif "Debilitated" in tags:
            nb = facts.get("neecha_bhanga", set()) or set()
            if p in nb:
                bits.append(f"{p} debilitated in {sign} (H{house}) — Neecha Bhanga cancellation")
            else:
                bits.append(f"{p} debilitated in {sign} (H{house}) — no cancellation")

    # Tier 2 — Pancha Mahapurusha yogas (Ruchaka/Bhadra/Hamsa/Malavya/Shasha)
    mp_yogas = {"Ruchaka Yoga", "Bhadra Yoga", "Hamsa Yoga", "Malavya Yoga", "Shasha Yoga"}
    # facts["yogas"] is a dict from extract_present_yogas — convert keys for set ops.
    yogas_set = set(facts.get("yogas", {}) or {})
    found_mp = sorted(mp_yogas & yogas_set)
    for y in found_mp:
        bits.append(y)

    # Tier 3 — Atmakaraka identity (the soul-planet — always classically relevant)
    ak = facts.get("karakas", {}).get("Atmakaraka")
    if ak:
        ak_tags = facts.get("planets", {}).get(ak, {}).get("tags", set())
        ak_sign = facts.get("planets", {}).get(ak, {}).get("sign", "")
        ak_house = facts.get("planets", {}).get(ak, {}).get("house", 0)
        # Only headline AK if it's distinctive (already-exalted AK is captured above)
        if "Exalted" not in ak_tags and "Debilitated" not in ak_tags:
            bits.append(f"Atmakaraka: {ak} in {ak_sign} (H{ak_house})")

    # Tier 4 — Vargottama planets (sign matches D9 sign)
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        tags = facts.get("planets", {}).get(p, {}).get("tags", set())
        if any("VARGOTTAMA" in t.upper() for t in tags) and len(bits) < 5:
            bits.append(f"{p} Vargottama (D1 and D9 same sign)")

    # Tier 5 — Lagna lord status if not yet captured
    h1_lord = facts.get("house_lords", {}).get(1, {}).get("planet")
    h1_lord_h = facts.get("house_lords", {}).get(1, {}).get("house")
    if h1_lord and not any(h1_lord in b for b in bits):
        h1_lord_tags = facts.get("planets", {}).get(h1_lord, {}).get("tags", set())
        if "Exalted" in h1_lord_tags or "Own Sign" in h1_lord_tags or "Debilitated" in h1_lord_tags:
            # captured by Tier 1 above; skip
            pass
        elif h1_lord_h in {6, 8, 12}:
            bits.append(f"Lagna lord {h1_lord} in dusthana H{h1_lord_h}")
        elif h1_lord_h in {1, 4, 5, 7, 9, 10, 11}:
            bits.append(f"Lagna lord {h1_lord} well-placed in H{h1_lord_h}")

    return bits[:3] if bits else ["No exceptional placements — standard chart structure"]


# Per-criterion driver spec — used by _criterion_drivers() to read facts
# and surface the top supports/drains for each chart per criterion. This is
# the "show your work" layer that addresses the trust critique.
_CRITERION_DRIVER_SPEC = {
    "Wealth Potential": {
        # H9 added — Bhagya is a primary wealth axis in classical reading.
        "houses":  {2, 9, 11},
        "planets": ["Jupiter", "Venus", "Mercury"],
        "support_yogas": {
            "Akhand Samrajya Yoga", "Mahabhagya Yoga", "Lakshmi Yoga", "Dhana Yoga",
            "Sankha Yoga", "Chandra-Mangala Yoga", "Kahala Yoga",
        },
        "drain_yogas":   {"Daridra"},
    },
    "Relationship Quality": {
        "houses":  {7, 2},
        "planets": ["Venus", "Jupiter", "Moon"],
        "support_yogas": {"Malavya Yoga", "Gajakesari Yoga"},
        "drain_yogas":   set(),
    },
    "Career Success": {
        "houses":  {10, 6, 11},
        "planets": ["Sun", "Saturn", "Mercury", "Mars"],
        "support_yogas": {"Dharma-Karma Adhipati Yoga", "Raja Yoga", "Ruchaka Yoga",
                          "Shasha Yoga", "Bhadra Yoga"},
        "drain_yogas":   set(),
    },
    "Life Struggles": {
        "houses":  {6, 8, 12},
        "planets": ["Saturn", "Mars", "Rahu", "Ketu"],
        "support_yogas": {"Viparita Raja Yoga"},   # mitigations
        "drain_yogas":   {"Kemadruma Yoga (Negative)", "Daridra", "Mahapatakapa"},
    },
    "Health & Longevity": {
        "houses":  {1, 8},
        "planets": ["Sun", "Moon", "Saturn"],
        "support_yogas": {"Hamsa Yoga"},
        "drain_yogas":   set(),
    },
    "Happiness & Contentment": {
        "houses":  {4, 5},
        "planets": ["Moon", "Venus", "Jupiter"],
        "support_yogas": {"Gajakesari Yoga", "Hamsa Yoga", "Malavya Yoga", "Adhi Yoga"},
        "drain_yogas":   {"Kemadruma Yoga (Negative)", "Shakat"},
    },
    "Luck & Fortune": {
        "houses":  {9, 5},
        "planets": ["Jupiter", "Sun"],
        "support_yogas": {"Lakshmi Yoga", "Gajakesari Yoga", "Hamsa Yoga"},
        "drain_yogas":   set(),
    },
    "Spiritual Depth": {
        "houses":  {12, 9, 8},
        "planets": ["Ketu", "Jupiter", "Saturn"],
        "support_yogas": {"Hamsa Yoga", "Viparita Raja Yoga", "Vairagya"},
        "drain_yogas":   {"Guru_Chandal"},
    },
    "Hidden Pitfalls": {
        "houses":  {8, 12, 6},
        "planets": ["Rahu", "Ketu", "Saturn"],
        "support_yogas": set(),
        "drain_yogas":   {"Kala_Sarpa", "Mahapatakapa", "Shakat", "Daridra"},
    },
}


def _criterion_drivers(criterion_key_str, facts, max_supports=3, max_drains=2):
    """Return (supports, drains) — short driver strings for one criterion.

    This is post-hoc explanation: we scan the facts dict for the most
    relevant placements and report them. It does NOT recompute the score —
    it explains the dossier evidence that the scorer already weighted.

    Output is intentionally terse — each driver is a short noun phrase
    (e.g., "Venus exalted", "11L Saturn in H8 dusthana"), suitable for
    inline citation in the comparison table.
    """
    spec = _CRITERION_DRIVER_SPEC.get(criterion_key_str)
    if not spec:
        return [], []

    supports, drains = [], []
    # facts["yogas"] is a dict from extract_present_yogas — convert keys for set ops.
    yogas = set(facts.get("yogas", {}) or {})
    special_flags = _special_yoga_flags(facts)

    # 1. Dignity of relevant karakas (exalted / debilitated — biggest news).
    for p in spec["planets"]:
        tags = facts.get("planets", {}).get(p, {}).get("tags", set())
        nb = facts.get("neecha_bhanga", set()) or set()
        if "Exalted" in tags:
            supports.append(f"{p} exalted")
        elif "Own Sign" in tags:
            supports.append(f"{p} in own sign")
        elif "Debilitated" in tags and p not in nb:
            drains.append(f"{p} debilitated (no cancellation)")
        elif any("Combust" in t for t in tags):
            drains.append(f"{p} combust")

    # 2. Supporting / draining yogas (more impressive than plain lord placement).
    for y in sorted(spec["support_yogas"] & yogas):
        supports.append(f"{y} active")
    for flag_name in spec["drain_yogas"]:
        if flag_name in yogas:
            drains.append(f"{flag_name} active")
        elif special_flags.get(flag_name):
            drains.append(f"{flag_name.replace('_', ' ')} active")

    # 3. House lord placements for the criterion's primary houses.
    for h in sorted(spec["houses"]):
        lord_info = facts.get("house_lords", {}).get(h, {})
        lord = lord_info.get("planet")
        lord_h = lord_info.get("house")
        if not lord or not lord_h: continue
        if lord_h in {1, 4, 5, 7, 9, 10, 11}:
            supports.append(f"H{h} lord {lord} in supportive H{lord_h}")
        elif lord_h in {6, 8, 12}:
            drains.append(f"H{h} lord {lord} in dusthana H{lord_h}")

    # 4. Vargottama placements (deeper-than-surface strength).
    for p in spec["planets"]:
        tags = facts.get("planets", {}).get(p, {}).get("tags", set())
        if any("VARGOTTAMA" in t.upper() for t in tags):
            supports.append(f"{p} Vargottama")

    # 5. Manglik tier for relationship
    if criterion_key_str == "Relationship Quality":
        mg = facts.get("manglik", "")
        if "VERY HIGH MANGLIK" in mg: drains.append("Very High Manglik")
        elif "HIGH MANGLIK" in mg:    drains.append("High Manglik")
        elif "MILD MANGLIK" in mg and "cancellations" not in mg:
            drains.append("Mild Manglik (uncancelled)")

    # Dedupe while preserving order
    def _dedupe(lst):
        seen = set(); out = []
        for x in lst:
            if x not in seen:
                seen.add(x); out.append(x)
        return out
    return _dedupe(supports)[:max_supports], _dedupe(drains)[:max_drains]


def calculate_and_rank_profiles(profiles_dossiers, criteria):
    """
    Multi-profile parameter ranking.

    profiles_dossiers may be either:
        [(name, dossier)]            — legacy 2-tuple, regex recalc_math path
        [(name, dossier, profile)]   — preferred 3-tuple, direct recalc from BirthData
    The 3-tuple form bypasses the dossier-text regex entirely and eliminates
    the silent-50.0-fallback class of bugs.

    Composite ranking is an UNWEIGHTED MEAN across selected criteria — useful
    as a tendency summary but does not reflect per-criterion importance.
    Per-criterion rankings below it are the authoritative ones.

    ── Design notes ────────────────────────────────────────────────────────────
    • Yoga bonuses are Lagna-scaled (_lagna_scaled): classical doctrine holds
      that no yoga bears full fruit when the Lagna (self/foundation) is weak.
      A floor of 0.30 prevents complete annihilation for borderline charts.

    • KP sub-lord scores are treated as a continuous 0-100 heuristic strength
      rather than a binary gate. Full KP gating (deny-if-not-promised) is a
      defensible stricter reading but is deferred to avoid false negatives on
      charts with partial KP data.

    • Ayanamsa: Lahiri (Chitrapaksha) is the locked engine convention — set in
      shared.astro.ephemeris (default Skyfield provider). No per-call setup is
      needed. The KP offset (~5'7") is negligible at the heuristic precision
      this engine targets.

    • The Overall composite assigns equal weight to every selected criterion.
      If "Hidden Pitfalls" is included alongside "Career Success", they contribute
      the same amount. Cite per-criterion rankings for decisions that hinge on
      a single parameter.
    ────────────────────────────────────────────────────────────────────────────
    """
    import sys

    scoring_map = {
        "Wealth Potential":         (calculate_wealth_score, False),
        "Relationship Quality":     (calculate_relationship_score, False),
        "Career Success":           (calculate_career_score, False),
        "Life Struggles":           (calculate_struggles_score, True),
        "Health & Longevity":       (calculate_health_score, False),
        "Happiness & Contentment":  (calculate_happiness_score, False),
        "Luck & Fortune":           (calculate_luck_score, False),
        "Spiritual Depth":          (calculate_spiritual_score, False),
        "Hidden Pitfalls":          (calculate_hidden_pitfalls_score, True),
    }

    active = []
    for c in criteria:
        key = criterion_key(c)
        if key in scoring_map:
            active.append((c, key, scoring_map[key][0], scoring_map[key][1]))
        else:
            active.append((
                c, c.strip(),
                lambda dossier, profile=None, custom=c: calculate_custom_aspect_score(dossier, custom, profile=profile),
                custom_is_reverse_rank(c),
            ))

    # Normalize input: pad to (name, dossier, profile) 3-tuples.
    normalized = []
    for item in profiles_dossiers:
        if len(item) == 3:
            normalized.append(tuple(item))
        else:
            name, dossier = item
            normalized.append((name, dossier, None))

    # Parse each profile's facts ONCE — used for headlines, drivers, generational
    # detection. Saves work vs each scorer re-parsing.
    facts_by_name = {}
    for name, dossier, _profile in normalized:
        try:
            facts_by_name[name] = parse_chart_facts(dossier)
        except Exception:
            facts_by_name[name] = {}

    # Run scorers
    raw = {name: {} for name, _, _ in normalized}
    failures = []
    for name, dossier, profile in normalized:
        for full_label, key, func, is_inverted in active:
            try:
                score = float(func(dossier, profile=profile))
            except Exception as e:
                failures.append(f"  [{name}] {full_label}: {type(e).__name__}: {str(e)[:120]}")
                score = 50.0
            raw[name][key] = {"score": score, "inverted": is_inverted, "label": full_label}

    if failures:
        print("[calculate_and_rank_profiles] WARNING: one or more scorers raised — "
              "those profiles will show a neutral 50.0 for the affected criteria:",
              file=sys.stderr)
        for line in failures:
            print(line, file=sys.stderr)

    # Per-criterion ranks + cohort stats
    ranks = {key: {} for _, key, _, _ in active}
    stats_by_key = {}
    ties_by_key = {}
    for _, key, _, is_inverted in active:
        ordered = sorted(normalized, key=lambda item: raw[item[0]][key]["score"], reverse=not is_inverted)
        for idx, (name, *_rest) in enumerate(ordered, start=1):
            ranks[key][name] = idx
        scores_dict = {name: raw[name][key]["score"] for name, _, _ in normalized}
        stats_by_key[key] = _cohort_stats(scores_dict)
        ties_by_key[key] = _detect_ties(scores_dict)

    # Composite (unweighted mean of positive/inverted-negative scores)
    composite = {}
    for name, _, _ in normalized:
        parts = []
        for _, key, _, is_inverted in active:
            s = raw[name][key]["score"]
            parts.append(100 - s if is_inverted else s)
        composite[name] = sum(parts) / len(parts) if parts else 50.0
    composite_order = sorted(composite, key=composite.get, reverse=True)
    composite_rank = {name: idx for idx, name in enumerate(composite_order, start=1)}
    composite_stats = _cohort_stats(composite)
    composite_ties = _detect_ties(composite)

    # Generational placements (≥60% of cohort share)
    gen_placements = _detect_generational_placements(list(facts_by_name.values()))

    # ── Output assembly ────────────────────────────────────────────────────────
    out = []

    # 1. Cohort overview + trust notes (FIRST so the AI reads them before claims).
    n_profiles = len(normalized)
    out.append("### Cohort Overview")
    out.append(f"Comparing {n_profiles} profile(s) on {len(active)} criteri{'on' if len(active)==1 else 'a'}.")
    if gen_placements:
        out.append("")
        out.append("**Generational placements (shared by ≥60% of cohort — these do NOT differentiate this group):**")
        for placement, count in sorted(gen_placements.items(), key=lambda kv: -kv[1]):
            ptype, _, value = placement.partition(":")
            out.append(f"  • {ptype.replace('_', ' ')} = {value}  ({count} of {n_profiles} profiles)")
        out.append("→ AI must note these in narrative but NOT use them as personal distinguishers.")

    # 2. Chart Headlines — the single most-important section. Forces the AI to
    #    anchor on real, named placements before interpreting anything.
    out.append("")
    out.append("### Chart Headlines (anchor every interpretation in these)")
    for name, *_ in normalized:
        facts = facts_by_name.get(name, {})
        ak = facts.get("karakas", {}).get("Atmakaraka", "—")
        h1_lord = facts.get("house_lords", {}).get(1, {}).get("planet", "—")
        moon_sign = facts.get("planets", {}).get("Moon", {}).get("sign", "—")
        moon_house = facts.get("planets", {}).get("Moon", {}).get("house", "—")
        headlines = _chart_headline(facts)
        out.append(f"\n**{name}** — Lagna lord: {h1_lord} | Moon: {moon_sign} (H{moon_house}) | AmK: {ak}")
        for h in headlines:
            out.append(f"  • {h}")

    # 3. Master rankings table with bands + percentiles
    out.append("")
    out.append("### Rankings Table")
    out.append("Each cell shows: `#rank (score, band, cohort-percentile%)`. "
               "Per-criterion ranks are AUTHORITATIVE. The composite is an unweighted "
               "mean with caveats below.")
    out.append("")
    header_keys = [key for _, key, _, _ in active]
    out.append("| Profile | Overall | " + " | ".join(header_keys) + " |")
    out.append("|---|---|" + "---|" * len(header_keys))
    for name, *_ in sorted(normalized, key=lambda item: composite_rank[item[0]]):
        comp = composite[name]
        comp_band = score_band(comp, is_negative=False)
        comp_pct = composite_stats["percentiles"].get(name, 50.0)
        cells = [f"#{composite_rank[name]} ({comp:.1f}, {comp_band}, {comp_pct:.0f}%ile)"]
        for full_label, key, _, is_inverted in active:
            s = raw[name][key]["score"]
            band = score_band(s, is_negative=is_inverted)
            pct = stats_by_key[key]["percentiles"].get(name, 50.0)
            cells.append(f"#{ranks[key][name]} ({s:.1f}, {band}, {pct:.0f}%ile)")
        out.append(f"| {name} | " + " | ".join(cells) + " |")

    # 4. Discrimination index per criterion — honest about which axes are
    #    differentiating this specific cohort and which aren't.
    out.append("")
    out.append("### Discrimination per Criterion (how reliable is the rank order for this cohort?)")
    out.append("")
    disc_lines = []
    for full_label, key, _, is_inverted in active:
        s = stats_by_key[key]
        std = s["std"]; disc = s["discrimination"]
        note = {
            "low":      "⚠ LOW discrimination — cohort scores cluster, rank order is NOT statistically meaningful.",
            "moderate": "Moderate discrimination — broad rank tiers are reliable, fine ranks are not.",
            "high":     "High discrimination — rank order is reliable across the cohort.",
            "single-profile": "Single profile — no cohort comparison possible.",
            "n/a":      "n/a",
        }.get(disc, disc)
        disc_lines.append(f"  • {full_label}: std={std:.1f}, mean={s['mean']:.1f} — {note}")
    out.extend(disc_lines)

    # 5. Tie groups — flag scores within ±5 of each other so the AI doesn't
    #    over-interpret tiny gaps.
    any_ties = bool(composite_ties) or any(ties_by_key.values())
    if any_ties:
        out.append("")
        out.append("### Tie Groups (scores within ±5 should be treated as effectively equal)")
        if composite_ties:
            for grp in composite_ties:
                out.append(f"  • Overall: {' = '.join(grp)}")
        for full_label, key, _, _is_inv in active:
            for grp in ties_by_key[key]:
                out.append(f"  • {full_label}: {' = '.join(grp)}")

    # 6. Overall composite section with explicit caveat
    out.append("")
    out.append("### Overall Composite (UNWEIGHTED MEAN — diagnostic, not authoritative)")
    for idx, name in enumerate(composite_order, start=1):
        comp = composite[name]
        band = score_band(comp, is_negative=False)
        pct = composite_stats["percentiles"].get(name, 50.0)
        out.append(f"Rank {idx}: {name} — {comp:.1f}/100 ({band}, {pct:.0f}%ile in cohort)")
    out.append("⚠ Composite weights every selected criterion equally. If 'Hidden Pitfalls' "
               "is selected alongside 'Career Success', they contribute the same amount. "
               "For decisions that hinge on one parameter, cite the per-criterion ranking below, not Overall.")

    # 7. Detailed parameter rankings with driver evidence split into
    #    "Distinguishing" (rare across cohort — real personal signal) vs
    #    "Cohort-shared" (≥50% of cohort has this — should NOT be cited as
    #    a personal differentiator). This is the explicit anti-shallow-prose
    #    structure: the AI is told which drivers to use.
    out.append("")
    out.append("### Detailed Parameter Rankings (with driver evidence per chart)")

    # Compute, per criterion, the cohort frequency of every driver string.
    # A driver appearing in ≥50% of cohort is treated as cohort-shared.
    drivers_per_profile_per_key = {}
    for full_label, key, _, _is_inv in active:
        drivers_per_profile_per_key[key] = {}
        for name, *_rest in normalized:
            facts = facts_by_name.get(name, {})
            sups, drns = _criterion_drivers(key, facts, max_supports=10, max_drains=10)
            drivers_per_profile_per_key[key][name] = (sups, drns)

    cohort_n = max(1, len(normalized))
    universal_threshold = max(2, int(0.5 * cohort_n))  # ≥50% of cohort

    for full_label, key, _, is_inverted in active:
        ordered = sorted(normalized, key=lambda item: raw[item[0]][key]["score"], reverse=not is_inverted)

        # Cohort frequency of each driver string for this criterion
        sup_freq, drain_freq = {}, {}
        for nm, *_ in normalized:
            sups, drns = drivers_per_profile_per_key[key][nm]
            for s in sups:  sup_freq[s]   = sup_freq.get(s, 0) + 1
            for d in drns:  drain_freq[d] = drain_freq.get(d, 0) + 1
        universal_supports = {s for s, c in sup_freq.items() if c >= universal_threshold}
        universal_drains   = {d for d, c in drain_freq.items() if c >= universal_threshold}

        out.append(f"\n**Parameter: {full_label}**  (direction: "
                   f"{'lower burden is better' if is_inverted else 'higher promise is better'})")
        out.append(f"Cohort discrimination: {stats_by_key[key]['discrimination'].upper()} "
                   f"(std={stats_by_key[key]['std']:.1f})")
        if universal_supports:
            out.append(f"Cohort-universal supports (≥{universal_threshold}/{cohort_n} profiles "
                       f"— do NOT cite as personal distinguishers): "
                       f"{', '.join(sorted(universal_supports))}")
        if universal_drains:
            out.append(f"Cohort-universal drains (≥{universal_threshold}/{cohort_n} profiles "
                       f"— do NOT cite as personal distinguishers): "
                       f"{', '.join(sorted(universal_drains))}")

        for idx, (name, *_rest) in enumerate(ordered, start=1):
            s = raw[name][key]["score"]
            band = score_band(s, is_negative=is_inverted)
            pct = stats_by_key[key]["percentiles"].get(name, 50.0)
            out.append(f"  Rank {idx}: {name} — {s:.1f} ({band}, {pct:.0f}%ile)")

            sups, drns = drivers_per_profile_per_key[key][name]
            distinguishing_sups = [s for s in sups if s not in universal_supports][:3]
            distinguishing_drns = [d for d in drns if d not in universal_drains][:2]
            shared_sups = [s for s in sups if s in universal_supports][:2]
            shared_drns = [d for d in drns if d in universal_drains][:2]

            if distinguishing_sups:
                out.append(f"    ✓ DISTINGUISHING supports (cite these): {'; '.join(distinguishing_sups)}")
            else:
                out.append(f"    ✓ DISTINGUISHING supports: (none beyond cohort-shared)")
            if distinguishing_drns:
                out.append(f"    ✗ DISTINGUISHING drains (cite these): {'; '.join(distinguishing_drns)}")
            elif shared_drns:
                out.append(f"    ✗ DISTINGUISHING drains: (none — drains are cohort-shared)")
            if shared_sups:
                out.append(f"    · Shared with cohort (skip in narrative): {'; '.join(shared_sups)}")

    # 8. Trust notes — calibrated honesty about what the rankings mean.
    out.append("")
    out.append("### Trust Notes (how to read these rankings honestly)")
    out.append("• These scores are LIFETIME BASELINE — the chart's durable promise, not 'right now'. "
               "Current Sade Sati / transits / running Mahadasha are NOT included.")
    out.append("• Scores within ±5 of each other (see Tie Groups) are at the noise floor of the "
               "heuristic — treat as equivalent, not as a definitive ranking.")
    out.append("• Score bands (Very Strong / Strong / Moderate / Weak / Very Weak) are the "
               "qualitative reading — the decimal is for ORDERING only. Vedic astrology is not "
               "quantitative; the band is closer to the classical interpretation than the number.")
    out.append("• Cohort percentile shows position WITHIN THIS GROUP only — a 90%ile in a weak "
               "cohort is not the same as 90%ile absolutely. Always cross-check band + percentile.")
    out.append("• Generational placements (slow-moving planets — Saturn/Jupiter/Rahu/Ketu) shared "
               "across the cohort are listed above; cite them in narrative but do NOT use them as "
               "personal distinguishers.")
    out.append("• The Overall composite is an UNWEIGHTED MEAN — useful as a tendency summary, but "
               "the per-criterion ranks are the authoritative output for decisions.")
    out.append("• Yoga detections use classical conditions (BPHS / Phaladeepika). Score component "
               "weights are engineered heuristics with no classical authority on exact numbers.")
    out.append("• A chart with a Pancha Mahapurusha yoga ranking LAST overall is a paradox the AI "
               "must explain (e.g., yoga is offset by heavy dusthana cluster). Do not just state "
               "both facts.")

    return "\n".join(out)


def calculate_compatibility_index(koota, marital_a, marital_b, kp_a, kp_b,
                                  laga_lord, lagb_lord, moon_lord_a, moon_lord_b,
                                  manglik_verdict):
    """
    Combined Compatibility Index (0-100) — single percentage blending every
    matchmaking layer the LLM otherwise has to weight by hand. Token-light:
    one number for the AI to anchor on, plus the component breakdown for
    transparency.

    Weights tuned to give Ashta Koota the foundational role (45%), KP H7
    promise the manifestation gate (25%), spouse-blueprint match (D9 + UL)
    the descriptive power (20%), with Manglik as a 10% adjustment.
    """
    # 1) Ashta Koota normalized to 0-100
    koota_pct = (koota.get("score", 0) / 36.0) * 100.0

    # 2) KP H7 promise — average of both partners (each 0-3 → 0-100)
    kp_avg_pct = ((kp_a + kp_b) / 6.0) * 100.0

    # 3) Spouse blueprint match — does each partner's D9 7th lord describe
    #    the other's core (Lagna lord OR Moon-sign lord)?
    def blueprint_match(d9_lord_self, partner_core):
        if d9_lord_self in partner_core:
            return 100.0          # exact match
        # Friendly relation = partial match
        friends = {
            "Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
            "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus"],
            "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn"],
            "Saturn": ["Mercury", "Venus"],
        }
        if any(c in friends.get(d9_lord_self, []) for c in partner_core):
            return 60.0
        return 25.0

    bp_a = blueprint_match(marital_a["D9_7th_Lord"], [lagb_lord, moon_lord_b])
    bp_b = blueprint_match(marital_b["D9_7th_Lord"], [laga_lord, moon_lord_a])

    # UL alignment — UL lord matching partner's core is a durability bonus
    ul_lord_a = SIGN_LORDS_MAP[SIGNS.index(marital_a["UL_Sign"])]
    ul_lord_b = SIGN_LORDS_MAP[SIGNS.index(marital_b["UL_Sign"])]
    ul_bonus = 0
    if ul_lord_a in (lagb_lord, moon_lord_b): ul_bonus += 5
    if ul_lord_b in (laga_lord, moon_lord_a): ul_bonus += 5

    blueprint_pct = clamp_val((bp_a + bp_b) / 2.0 + ul_bonus, 0, 100)

    # 4) Manglik penalty — only applied if dosha not cancelled
    m = (manglik_verdict or "").upper()
    if "CANCELLED" in m or "BALANCED" in m or "NO MANGLIK DOSHA" in m:
        manglik_penalty = 0
    elif "HIGH MANGLIK" in m or "VERY HIGH" in m:
        manglik_penalty = 12
    elif "MILD" in m:
        manglik_penalty = 5
    else:
        manglik_penalty = 0

    # Weighted blend: 45% Koota, 25% KP H7, 20% Blueprint/UL, then Manglik adjustment
    index = (koota_pct * 0.45 + kp_avg_pct * 0.25 + blueprint_pct * 0.20) \
            * (1.0 - manglik_penalty / 100.0) \
            + (10.0 if manglik_penalty == 0 else 0.0)   # +10 bonus when no Manglik issue

    return {
        "score": round(clamp_val(index, 0, 100), 1),
        "components": {
            "Ashta_Koota_pct":   round(koota_pct, 1),
            "KP_H7_Promise_pct": round(kp_avg_pct, 1),
            "Blueprint_pct":     round(blueprint_pct, 1),
            "Manglik_penalty":   manglik_penalty,
        },
    }


def calculate_matchmaking_synastry(prof_a, prof_b, ma, mb, jda, jdb, dos_a, dos_b):
    koota_data = calculate_ashta_koota(ma, mb)
    marital_a = calculate_marital_analysis(jda, prof_a['lat'], prof_a['lon'])
    marital_b = calculate_marital_analysis(jdb, prof_b['lat'], prof_b['lon'])
    kp_a = extract_kp_promise(dos_a, 7)
    kp_b = extract_kp_promise(dos_b, 7)
    return koota_data, marital_a, marital_b, kp_a, kp_b


def _extract_h7_significators(dossier_text):
    """
    Return the set of planet names whose KP 4-Step signifies H7 for this chart.

    Reads from the structured `facts["planets"][p]["kp_sigs"]` set produced by
    parse_chart_facts(). Replaces the broken legacy extractor which split on a
    literal backslash-n and looked for a section header that doesn't exist.
    """
    facts = parse_chart_facts(dossier_text)
    return {p for p, data in facts.get("planets", {}).items()
            if 7 in (data.get("kp_sigs") or set())}


def calculate_destiny_confirmation(prof_a, prof_b, jda, jdb, dos_a, dos_b):
    """
    Five-layer Destiny Marriage Confirmation matrix (0-100%).

      1. Foundational KP H7 promise (each chart individually, max 20)
      2. Mutual blueprint match — D9 7th lord + Upapada lord + Jaimini AK/DK
         describes the actual partner (max 35)
      3. Structural synastry — Lagna-SIGN overlay (strongest), Lagna-LORD
         overlay (auxiliary), nodal obsession (max 25)
      4. Timing synchronization — shared H7 significators across charts (max 20)

    Doctrinal corrections vs prior implementation:
      - Shared H7 significators now read from parse_chart_facts() instead of
        the broken `split("\\n")` regex against a non-existent header. The
        timing score was previously always 0 — every couple lost up to 20 pts.
      - Synastry now distinguishes "A's Lagna SIGN in B's 7th house" (classical
        synastry, primary) from "A's Lagna LORD in B's 7th sign" (auxiliary
        signal, exposed but not double-counted).
    """
    pla = {pn: get_planet_longitude_and_speed(jda, pid) for pn, pid in PLANETS.items()}
    ra_a = get_rahu_longitude(jda)  # MEAN node via the ephemeris adapter
    pla["Rahu"] = (ra_a, 0); pla["Ketu"] = ((ra_a + 180) % 360, 0)
    plb = {pn: get_planet_longitude_and_speed(jdb, pid) for pn, pid in PLANETS.items()}
    ra_b = get_rahu_longitude(jdb)
    plb["Rahu"] = (ra_b, 0); plb["Ketu"] = ((ra_b + 180) % 360, 0)

    laga = sign_index_from_lon(get_lagna_and_cusps(jda, prof_a['lat'], prof_a['lon'])[0])
    lagb = sign_index_from_lon(get_lagna_and_cusps(jdb, prof_b['lat'], prof_b['lon'])[0])

    moona_sidx = sign_index_from_lon(pla["Moon"][0])
    moonb_sidx = sign_index_from_lon(plb["Moon"][0])

    laga_lord = SIGN_LORDS_MAP[laga]
    lagb_lord = SIGN_LORDS_MAP[lagb]

    def get_ak_dk(pl):
        """Jaimini Chara Karakas (7-karaka Parashari convention).
        Highest degree-in-sign = Atmakaraka; lowest = Darakaraka.
        Rahu/Ketu excluded (their motion is retrograde; some traditions use
        reverse-degree for them — the 7-karaka system is cleaner here)."""
        degs = [(p, lon % 30) for p, (lon, _) in pl.items() if p not in ["Rahu", "Ketu"]]
        degs.sort(key=lambda x: x[1], reverse=True)
        return degs[0][0], degs[-1][0]   # (Atmakaraka, Darakaraka)

    aka, dka = get_ak_dk(pla)
    akb, dkb = get_ak_dk(plb)

    marital_a = calculate_marital_analysis(jda, prof_a['lat'], prof_a['lon'])
    marital_b = calculate_marital_analysis(jdb, prof_b['lat'], prof_b['lon'])

    kp_a = extract_kp_promise(dos_a, 7)
    kp_b = extract_kp_promise(dos_b, 7)

    from datetime import datetime, date
    dt_loc_a = datetime.combine(
        date.fromisoformat(prof_a['date']) if isinstance(prof_a['date'], str) else prof_a['date'],
        datetime.strptime(prof_a['time'], "%H:%M").time() if isinstance(prof_a['time'], str) else prof_a['time'],
    )
    dt_loc_b = datetime.combine(
        date.fromisoformat(prof_b['date']) if isinstance(prof_b['date'], str) else prof_b['date'],
        datetime.strptime(prof_b['time'], "%H:%M").time() if isinstance(prof_b['time'], str) else prof_b['time'],
    )

    d_info_a = build_vimshottari_timeline(dt_loc_a, pla["Moon"][0], datetime.now())
    d_info_b = build_vimshottari_timeline(dt_loc_b, plb["Moon"][0], datetime.now())

    def is_friend(p1, p2):
        friends = {
            "Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
            "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus"],
            "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn"],
            "Saturn": ["Mercury", "Venus"],
        }
        return p2 in friends.get(p1, [])

    def score_blueprint(d9_lord, core_lords):
        if d9_lord in core_lords: return 10
        if any(is_friend(d9_lord, cl) for cl in core_lords): return 7
        return 3

    def check_nodal_obsession(rahu_lon_a, ketu_lon_a, core_lons_b):
        ra_sign = sign_index_from_lon(rahu_lon_a)
        ke_sign = sign_index_from_lon(ketu_lon_a)
        for cl in core_lons_b:
            csign = sign_index_from_lon(cl)
            if csign == ra_sign or csign == ke_sign:
                return True
        return False

    core_b_lons = [plb["Moon"][0], plb["Venus"][0], plb[lagb_lord][0]]
    core_a_lons = [pla["Moon"][0], pla["Venus"][0], pla[laga_lord][0]]

    obsession_a_to_b = check_nodal_obsession(pla["Rahu"][0], pla["Ketu"][0], core_b_lons)
    obsession_b_to_a = check_nodal_obsession(plb["Rahu"][0], plb["Ketu"][0], core_a_lons)

    # === Layer 1: KP H7 promise (max 20) ===
    score_promise = (min(kp_a, 3) / 3 * 10) + (min(kp_b, 3) / 3 * 10)

    # === Layer 2: Mutual blueprint match (max 35) ===
    score_d9_a = score_blueprint(marital_a['D9_7th_Lord'], [lagb_lord, SIGN_LORDS_MAP[moonb_sidx]])
    score_d9_b = score_blueprint(marital_b['D9_7th_Lord'], [laga_lord, SIGN_LORDS_MAP[moona_sidx]])

    ul_lord_a = SIGN_LORDS_MAP[SIGNS.index(marital_a['UL_Sign'])]
    ul_lord_b = SIGN_LORDS_MAP[SIGNS.index(marital_b['UL_Sign'])]
    score_ul_a = 5 if ul_lord_a in [lagb_lord, SIGN_LORDS_MAP[moonb_sidx]] else 0
    score_ul_b = 5 if ul_lord_b in [laga_lord, SIGN_LORDS_MAP[moona_sidx]] else 0

    score_soul = 0
    if dka in [akb, lagb_lord]: score_soul += 2.5
    if dkb in [aka, laga_lord]: score_soul += 2.5

    score_blueprint_total = score_d9_a + score_d9_b + score_ul_a + score_ul_b + score_soul

    # === Layer 3: Structural synastry (max 25) ===
    # PRIMARY: Lagna SIGN overlay — A's ascendant sign physically falls in B's 7th house.
    # This is the classical Vedic synastry signature (most powerful).
    a_lagna_in_b7 = (laga == (lagb + 6) % 12)
    b_lagna_in_a7 = (lagb == (laga + 6) % 12)

    # AUXILIARY: Lagna LORD overlay — A's Lagna lord currently sits in B's 7th sign.
    # Weaker signal; exposed in the matrix for the LLM's narrative but does not
    # double-count toward the synastry score.
    a_lord_in_b7 = (sign_index_from_lon(pla[laga_lord][0]) == (lagb + 6) % 12)
    b_lord_in_a7 = (sign_index_from_lon(plb[lagb_lord][0]) == (laga + 6) % 12)

    score_synastry = 0
    if a_lagna_in_b7: score_synastry += 7.5
    if b_lagna_in_a7: score_synastry += 7.5
    if obsession_a_to_b: score_synastry += 5
    if obsession_b_to_a: score_synastry += 5

    # === Layer 4: Timing synchronization (max 20) ===
    sigs_a = _extract_h7_significators(dos_a)
    sigs_b = _extract_h7_significators(dos_b)
    shared_sigs = sigs_a.intersection(sigs_b)

    score_timing = 0
    if len(shared_sigs) >= 2: score_timing = 20
    elif len(shared_sigs) == 1: score_timing = 10

    total_destiny_percentage = round(
        score_promise + score_blueprint_total + score_synastry + score_timing
    )

    return {
        "A": {"kp_promise": kp_a, "weak_warning": kp_a == 0, "sigs": sorted(sigs_a)},
        "B": {"kp_promise": kp_b, "weak_warning": kp_b == 0, "sigs": sorted(sigs_b)},
        "Blueprint": {
            "A_D9_7th_Lord": marital_a['D9_7th_Lord'],
            "B_Core": [lagb_lord, SIGN_LORDS_MAP[moonb_sidx]],
            "B_D9_7th_Lord": marital_b['D9_7th_Lord'],
            "A_Core": [laga_lord, SIGN_LORDS_MAP[moona_sidx]],
            "A_UL": marital_a['UL_Sign'],
            "B_UL": marital_b['UL_Sign'],
            "A_DK": dka, "A_AK": aka,
            "B_DK": dkb, "B_AK": akb,
        },
        "Synastry": {
            # Primary synastry signatures (these drive the score)
            "A_Lagna_in_B_7th": a_lagna_in_b7,
            "B_Lagna_in_A_7th": b_lagna_in_a7,
            # Auxiliary lord-overlay signatures (info only)
            "A_LagnaLord_in_B_7th": a_lord_in_b7,
            "B_LagnaLord_in_A_7th": b_lord_in_a7,
            "A_Nodal_Obsession": obsession_a_to_b,
            "B_Nodal_Obsession": obsession_b_to_a,
        },
        "Timing": {
            "A_Current_MD_AD": f"{d_info_a['current_md']} / {d_info_a['current_ad']}",
            "B_Current_MD_AD": f"{d_info_b['current_md']} / {d_info_b['current_ad']}",
            "Shared_Significators": sorted(shared_sigs),
            "A_H7_Significators": sorted(sigs_a),
            "B_H7_Significators": sorted(sigs_b),
        },
        "Percentage": total_destiny_percentage,
        "Components": {
            "Promise":   round(score_promise, 1),
            "Blueprint": round(score_blueprint_total, 1),
            "Synastry":  round(score_synastry, 1),
            "Timing":    round(score_timing, 1),
        },
    }