import math
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from math_engine.constants import *
from math_engine.astro_calc import *

def calculate_ashta_koota(moon_boy, moon_girl):
    # Boy's and Girl's Moon Longitudes
    s1 = sign_index_from_lon(moon_boy)
    s2 = sign_index_from_lon(moon_girl)
    n1 = min(int((moon_boy % 360) // (360 / 27)), 26)
    n2 = min(int((moon_girl % 360) // (360 / 27)), 26)
    
    # 1. Varna (1 point)
    vm = [1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0]
    v = 1 if vm[s1] <= vm[s2] else 0
    
    # 2. Vashya (2 points)
    va = [0, 0, 1, 2, 3, 1, 1, 4, 0, 2, 1, 2]
    va1, va2 = va[s1], va[s2]
    if va1 == va2: vap = 2
    elif {va1, va2} in [{1, 3}, {1, 4}, {2, 3}]: vap = 0
    else: vap = 1
    
    # 3. Tara (3 points) - Calculated from Girl to Boy and Boy to Girl
    t1 = ((n2 - n1) % 27) % 9  # Boy to Girl
    t2 = ((n1 - n2) % 27) % 9  # Girl to Boy
    ta = (0 if t1 in [2, 4, 6] else 1.5) + (0 if t2 in [2, 4, 6] else 1.5)
    
    # 4. Yoni (4 points)
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
    
    # 7. Bhakoot (7 points)
    dist = (s2 - s1) % 12
    bh = 7 if dist in [0, 2, 3, 6, 8, 9, 10] else 0
    
    # 8. Nadi (8 points)
    nb = [0, 1, 2] * 9
    nd1, nd2 = nb[n1], nb[n2]
    nn = ""
    np = 0
    if nd1 == nd2:
        if n1 == n2: nn = "NADI DOSHA EXCEPTION: Same Nakshatra (Dosha Cancelled)"
        elif SIGN_LORDS_MAP[s1] != SIGN_LORDS_MAP[s2]: nn = "NADI DOSHA PARTIAL EXCEPTION: Different Rashi lords"
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
        "nadi_note": nn, "mahendra": mahendra, "stree_deergha": stree_deergha
    }


def calculate_marital_analysis(jd, lat, lon):
    # Calculates D9 7th House, Upapada Lagna (UL) and Darapada (A7)
    cusps = get_lagna_and_cusps(jd, lat, lon)
    lagna_lon = cusps[0]
    lagna_sign = sign_index_from_lon(lagna_lon)
    
    # Planets
    p = {pn: get_planet_longitude_and_speed(jd, pid)[0] for pn, pid in PLANETS.items()}
    
    # Navamsha (D9)
    d9_lagna_sign = int((lagna_lon % 360) / (360/108)) % 12
    d9_7th_sign = (d9_lagna_sign + 6) % 12
    d9_7th_lord = SIGN_LORDS_MAP[d9_7th_sign]
    
    # Upapada Lagna (UL) - Arudha of 12th House
    h12_sign = (lagna_sign + 11) % 12
    h12_lord = SIGN_LORDS_MAP[h12_sign]
    if h12_lord == "Rahu" or h12_lord == "Ketu": h12_lord = "Saturn" # Proxy
    lord_lon = p[h12_lord]
    lord_sign = sign_index_from_lon(lord_lon)
    dist = (lord_sign - h12_sign) % 12
    ul_sign = (lord_sign + dist) % 12
    # Exceptions
    if ul_sign == h12_sign: ul_sign = (ul_sign + 9) % 12
    elif ul_sign == (h12_sign + 6) % 12: ul_sign = (ul_sign + 9) % 12
    
    # Darapada (A7)
    h7_sign = (lagna_sign + 6) % 12
    h7_lord = SIGN_LORDS_MAP[h7_sign]
    if h7_lord == "Rahu" or h7_lord == "Ketu": h7_lord = "Venus"
    l7_sign = sign_index_from_lon(p[h7_lord])
    d7 = (l7_sign - h7_sign) % 12
    a7_sign = (l7_sign + d7) % 12
    if a7_sign == h7_sign: a7_sign = (a7_sign + 9) % 12
    elif a7_sign == (h7_sign + 6) % 12: a7_sign = (a7_sign + 9) % 12
    
    return {
        "D9_7th_Sign": SIGNS[d9_7th_sign],
        "D9_7th_Lord": d9_7th_lord,
        "UL_Sign": SIGNS[ul_sign],
        "A7_Sign": SIGNS[a7_sign],
        "D1_7th_Sign": SIGNS[h7_sign]
    }


def calculate_wealth_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
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
        
    structural = score_positive([(get_bhava_bala(2, ls, planet_data, f, lagna_lon, jd_ut), 2.4), (get_bhava_bala(11, ls, planet_data, f, lagna_lon, jd_ut), 2.4), (get_bhava_bala(5, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (get_bhava_bala(9, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), 0.5), (al11_score, 1.2), (sav_norm(f["sav"].get(2)), 1.2), (sav_norm(f["sav"].get(11)), 1.2)])
    karaka = score_positive([(get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.5), (get_p_str("Venus", planet_data, ls, f, lagna_lon, jd_ut), 1.0), (get_p_str("Mercury", planet_data, ls, f, lagna_lon, jd_ut), 0.8), (varga_sign_strength(f, "D2", "Jupiter"), 0.9), (varga_sign_strength(f, "D2", "Venus"), 0.7), (varga_sign_strength(f, "D9", "Jupiter"), 0.5)])
    kp = score_positive([(get_kp_sub_lord_score(2, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,11}, {6,8,12}), 1.4), (get_kp_sub_lord_score(11, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,11}, {6,8,12}), 1.0)])
    yoga = topic_yoga_score(f, {"Dhana Yoga": 7, "Lakshmi Yoga": 8, "Chandra-Mangala Yoga": 5, "Akhand Samrajya Yoga": 9, "Raja Yoga": 4, "Parivartana Yoga": 3, "Viparita Raja Yoga": 2}, planet_data, ls, lagna_lon, jd_ut)
    placement = topic_house_connection(f, ["Jupiter", "Venus", "Mercury", "Moon", "Mars"], {2, 5, 9, 11})
    
    h2_lon, h11_lon = ((ls + 1) * 30 + 15) % 360, ((ls + 10) * 30 + 15) % 360
    malefic_drishti = sum((calc_drishti(planet_data[m][0], h2_lon, m) + calc_drishti(planet_data[m][0], h11_lon, m)) * 0.05 for m in ["Saturn", "Mars", "Rahu", "Ketu", "Sun"])
    drains = affliction_count(f, houses={2, 11}) * 3 + malefic_drishti
    if planet_house(f, "Rahu") in {2, 11} and get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut) < 55: drains += 5
    return round(clamp_val(structural * 0.40 + karaka * 0.22 + kp * 0.18 + yoga + placement + indu_bonus - drains), 2)


def calculate_relationship_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    dk = f["karakas"].get("Darakaraka")
    
    structural = score_positive([(get_bhava_bala(7, ls, planet_data, f, lagna_lon, jd_ut), 2.5), (get_bhava_bala(2, ls, planet_data, f, lagna_lon, jd_ut), 1.2), (get_bhava_bala(4, ls, planet_data, f, lagna_lon, jd_ut), 1.0), (get_bhava_bala(5, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (get_bhava_bala(8, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (sav_norm(f["sav"].get(7)), 1.2)])
    karaka = score_positive([(get_p_str("Venus", planet_data, ls, f, lagna_lon, jd_ut), 1.8), (get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.1), (get_p_str("Moon", planet_data, ls, f, lagna_lon, jd_ut), 1.1), (get_p_str(dk, planet_data, ls, f, lagna_lon, jd_ut), 1.0), (varga_sign_strength(f, "D9", "Venus"), 1.2), (varga_sign_strength(f, "D9", "Jupiter"), 0.8), (varga_sign_strength(f, "D9", dk), 0.9)])
    kp = get_kp_sub_lord_score(7, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,7,11}, {1,6,10})
    yoga = topic_yoga_score(f, {"Malavya Yoga": 7, "Gajakesari Yoga": 5, "Raja Yoga": 2}, planet_data, ls, lagna_lon, jd_ut)
    
    h7_lon = ((ls + 6) * 30 + 15) % 360
    malefic_drishti = sum(calc_drishti(planet_data[m][0], h7_lon, m) * 0.05 for m in ["Saturn", "Mars", "Rahu", "Ketu", "Sun"])
    risk = affliction_count(f, planets={"Venus", "Jupiter", "Moon", dk} - {None}) * 4 + malefic_drishti
    if "HIGH MANGLIK" in f["manglik"]: risk += 8
    elif "MILD MANGLIK" in f["manglik"]: risk += 4
    if planet_house(f, "Rahu") == 7 or planet_house(f, "Ketu") == 7: risk += 7
    return round(clamp_val(structural * 0.38 + karaka * 0.30 + (kp/100)*22 + yoga - risk), 2)


def calculate_career_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
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
    kp = score_positive([(get_kp_sub_lord_score(10, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,6,10,11}, {5,8,12}), 1.7), (get_kp_sub_lord_score(6, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,6,10,11}, {5,8,12}), 0.8)])
    yoga = topic_yoga_score(f, {"Dharma-Karma Adhipati Yoga": 10, "Raja Yoga": 7, "Ruchaka Yoga": 6, "Shasha Yoga": 6, "Bhadra Yoga": 5, "Hamsa Yoga": 3, "Neecha Bhanga Raja Yoga": 5, "Viparita Raja Yoga": 3}, planet_data, ls, lagna_lon, jd_ut)
    placement = topic_house_connection(f, ["Sun", "Saturn", "Mercury", "Mars", amk], {1, 6, 10, 11})
    risk = affliction_count(f, planets={"Sun", "Saturn", "Mercury", "Mars", amk} - {None}, houses={1, 6, 10, 11}) * 4
    return round(clamp_val(structural * 0.40 + karaka * 0.30 + kp * 0.20 + yoga + placement - risk), 2)


def calculate_struggles_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    burden = 18
    burden += (100 - get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut)) * 0.12
    burden += (100 - get_bhava_bala(4, ls, planet_data, f, lagna_lon, jd_ut)) * 0.07
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
    if "Kemadruma Yoga (Negative)" in f["yogas"]: burden += 8
    if "Viparita Raja Yoga" in f["yogas"]: burden -= 6
    if "Gajakesari Yoga" in f["yogas"]: burden -= 4
    if f["neecha_bhanga"]: burden -= min(6, len(f["neecha_bhanga"]) * 3)
    return round(clamp_val(burden), 2)


def calculate_health_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    lagna_lord = f["house_lords"].get(1, {}).get("planet")
    structural = score_positive([(get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), 2.6), (get_bhava_bala(8, ls, planet_data, f, lagna_lon, jd_ut), 1.5), (get_bhava_bala(3, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (get_bhava_bala(6, ls, planet_data, f, lagna_lon, jd_ut), 0.9), (sav_norm(f["sav"].get(1)), 1.0)])
    karaka = score_positive([(get_p_str(lagna_lord, planet_data, ls, f, lagna_lon, jd_ut), 1.8), (get_p_str("Sun", planet_data, ls, f, lagna_lon, jd_ut), 1.1), (get_p_str("Moon", planet_data, ls, f, lagna_lon, jd_ut), 1.2), (get_p_str("Saturn", planet_data, ls, f, lagna_lon, jd_ut), 1.1), (varga_sign_strength(f, "D9", lagna_lord), 0.8), (varga_sign_strength(f, "D12", lagna_lord), 0.5)])
    kp = score_positive([(get_kp_sub_lord_score(1, placidus_cusps, planet_data, r_lon, k_lon, ls, {1,11}, {2,7}), 1.1), (100 - get_kp_sub_lord_score(6, placidus_cusps, planet_data, r_lon, k_lon, ls, {1,11}, {2,7}) + 40, 0.7), (get_kp_sub_lord_score(8, placidus_cusps, planet_data, r_lon, k_lon, ls, {1,11}, {2,7}), 0.7)])
    protection = benefic_support(f, {1, 6, 8}) + topic_yoga_score(f, {"Hamsa Yoga": 5, "Gajakesari Yoga": 5, "Adhi Yoga": 3}, planet_data, ls, lagna_lon, jd_ut)
    risk = affliction_count(f, planets={lagna_lord, "Sun", "Moon", "Saturn"} - {None}) * 5 + len(f["weak_sav_houses"] & {1, 6, 8}) * 4
    return round(clamp_val(structural * 0.40 + karaka * 0.30 + kp * 0.16 + protection - risk), 2)


def calculate_happiness_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    structural = score_positive([(get_bhava_bala(4, ls, planet_data, f, lagna_lon, jd_ut), 2.4), (get_bhava_bala(5, ls, planet_data, f, lagna_lon, jd_ut), 1.3), (get_bhava_bala(9, ls, planet_data, f, lagna_lon, jd_ut), 1.0), (get_bhava_bala(11, ls, planet_data, f, lagna_lon, jd_ut), 0.8), (get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), 0.6), (sav_norm(f["sav"].get(4)), 1.0)])
    karaka = score_positive([(get_p_str("Moon", planet_data, ls, f, lagna_lon, jd_ut), 1.8), (get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.3), (get_p_str("Venus", planet_data, ls, f, lagna_lon, jd_ut), 1.0), (varga_sign_strength(f, "D9", "Moon"), 0.8)])
    yoga = topic_yoga_score(f, {"Gajakesari Yoga": 9, "Hamsa Yoga": 6, "Malavya Yoga": 5, "Adhi Yoga": 4}, planet_data, ls, lagna_lon, jd_ut)
    support = benefic_support(f, {1, 4, 5, 9, 11})
    risk = affliction_count(f, planets={"Moon", "Venus", "Jupiter"}) * 5
    
    fourth_lord = f["house_lords"].get(4, {}).get("planet")
    if fourth_lord:
        fl_house = planet_house(f, fourth_lord)
        if fl_house in {1, 4, 5, 9, 10, 11}: support += 8
        elif fl_house in {6, 8, 12}: risk += 8
        
    if "Kemadruma Yoga (Negative)" in f["yogas"]: risk += 10
    return round(clamp_val(structural * 0.43 + karaka * 0.32 + yoga + support - risk), 2)


def calculate_luck_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data
    ninth_lord = f["house_lords"].get(9, {}).get("planet")
    structural = score_positive([(get_bhava_bala(9, ls, planet_data, f, lagna_lon, jd_ut), 2.6), (get_bhava_bala(5, ls, planet_data, f, lagna_lon, jd_ut), 1.7), (get_bhava_bala(11, ls, planet_data, f, lagna_lon, jd_ut), 1.0), (get_bhava_bala(1, ls, planet_data, f, lagna_lon, jd_ut), 0.8), (sav_norm(f["sav"].get(9)), 1.2), (sav_norm(f["sav"].get(5)), 0.8)])
    karaka = score_positive([(get_p_str("Jupiter", planet_data, ls, f, lagna_lon, jd_ut), 1.7), (get_p_str(ninth_lord, planet_data, ls, f, lagna_lon, jd_ut), 1.4), (varga_sign_strength(f, "D9", "Jupiter"), 1.0), (varga_sign_strength(f, "D9", ninth_lord), 1.0), (get_p_str("Sun", planet_data, ls, f, lagna_lon, jd_ut), 0.5)])
    kp = score_positive([(get_kp_sub_lord_score(9, placidus_cusps, planet_data, r_lon, k_lon, ls, {9,11}, {6,8,12}), 1.4), (get_kp_sub_lord_score(11, placidus_cusps, planet_data, r_lon, k_lon, ls, {9,11}, {6,8,12}), 0.8)])
    yoga = topic_yoga_score(f, {"Lakshmi Yoga": 9, "Gajakesari Yoga": 7, "Hamsa Yoga": 6, "Raja Yoga": 6, "Adhi Yoga": 4}, planet_data, ls, lagna_lon, jd_ut)
    placement = topic_house_connection(f, ["Jupiter", ninth_lord, "Sun"], {1, 5, 9, 11})
    risk = affliction_count(f, planets={"Jupiter", ninth_lord} - {None}) * 5
    return round(clamp_val(structural * 0.42 + karaka * 0.30 + kp * 0.16 + yoga + placement - risk), 2)


def calculate_spiritual_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
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
    return round(clamp_val(structural * 0.38 + karaka * 0.31 + placement + yoga), 2)


def calculate_hidden_pitfalls_score(dossier):
    f = parse_chart_facts(dossier)
    math_data = recalc_math(dossier)
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
    
    burden += affliction_count(f, planets={ak, amk, dk, "Moon", "Venus", "Jupiter"} - {None}) * 5
    burden += affliction_count(f, houses={1, 2, 4, 7, 8, 10, 12}) * 3
    for planet in {ak, amk, dk, "Moon", "Venus", "Jupiter", "Saturn"} - {None}:
        if varga_sign_strength(f, "D9", planet) <= 32: burden += 4
        if varga_sign_strength(f, "D30", planet) <= 32: burden += 5
    
    if get_kp_sub_lord_score(2, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,11}, {6,8,12}) < 40: burden += 3
    if get_kp_sub_lord_score(7, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,7,11}, {1,6,10}) < 40: burden += 3
    if get_kp_sub_lord_score(10, placidus_cusps, planet_data, r_lon, k_lon, ls, {2,6,10,11}, {5,8,12}) < 40: burden += 3
    
    if planet_house(f, "Rahu") in {1, 2, 4, 7, 10}: burden += 7
    if planet_house(f, "Ketu") in {1, 2, 4, 7, 10}: burden += 5
    if f["neecha_bhanga"]: burden -= min(5, len(f["neecha_bhanga"]) * 2)
    if "Gajakesari Yoga" in f["yogas"]: burden -= 3
    return round(clamp_val(burden), 2)


def custom_is_reverse_rank(criteria):
    q = str(criteria).lower()
    return any(w in q for w in ["least", "lowest", "fewest", "less likely", "minimum", "smallest"])


def custom_is_risk_topic(criteria):
    q = str(criteria).lower()
    return any(w in q for w in [
        "struggle", "pitfall", "problem", "risk", "danger", "accident", "disease",
        "illness", "debt", "loss", "failure", "divorce", "separation", "enemy",
        "litigation", "scandal", "delay", "obstacle", "suffer", "hardship",
    ])


def custom_topic_profile(criteria):
    q = str(criteria).lower()
    profiles = [
        (["rich", "wealth", "money", "finance", "income", "business", "profit"], "Wealth", [2, 11, 5, 9], ["Jupiter", "Venus", "Mercury"], ["D2", "D9"], [2, 11], {"Dhana Yoga": 7, "Lakshmi Yoga": 8, "Chandra-Mangala Yoga": 5, "Raja Yoga": 4}),
        (["marriage", "relationship", "love", "spouse", "partner", "romance"], "Relationship", [7, 2, 4, 5, 8], ["Venus", "Jupiter", "Moon"], ["D9"], [7], {"Malavya Yoga": 7, "Gajakesari Yoga": 5}),
        (["career", "job", "profession", "promotion", "status", "position"], "Career", [10, 6, 11, 2, 9], ["Sun", "Saturn", "Mercury", "Mars"], ["D10", "D9"], [10, 6, 11], {"Dharma-Karma Adhipati Yoga": 10, "Raja Yoga": 7, "Shasha Yoga": 5, "Bhadra Yoga": 5}),
        (["fame", "famous", "celebrity", "public", "recognition", "popular", "renown"], "Fame", [10, 11, 5, 9, 1], ["Sun", "Moon", "Jupiter", "Rahu"], ["D10", "D9"], [10, 11], {"Raja Yoga": 8, "Dharma-Karma Adhipati Yoga": 8, "Gajakesari Yoga": 5}),
        (["leader", "leadership", "politic", "authority", "power", "influence", "command"], "Leadership", [1, 6, 9, 10, 11], ["Sun", "Mars", "Saturn", "Jupiter"], ["D10"], [10, 11], {"Raja Yoga": 8, "Dharma-Karma Adhipati Yoga": 9, "Ruchaka Yoga": 5, "Shasha Yoga": 5}),
        (["intelligence", "education", "study", "academic", "exam", "learning", "wisdom"], "Learning", [4, 5, 9, 10], ["Mercury", "Jupiter", "Moon"], ["D9"], [5, 9], {"Bhadra Yoga": 6, "Hamsa Yoga": 6, "Gajakesari Yoga": 4}),
        (["creative", "creativity", "art", "music", "writing", "writer", "actor", "artist"], "Creativity", [3, 5, 2, 10, 11], ["Venus", "Mercury", "Moon"], ["D9", "D10"], [3, 5, 10, 11], {"Malavya Yoga": 6, "Bhadra Yoga": 5, "Gajakesari Yoga": 4}),
        (["beauty", "beautiful", "attractive", "charm", "style", "luxury"], "Charm", [1, 2, 4, 5, 7], ["Venus", "Moon", "Jupiter"], ["D9"], [1, 7, 11], {"Malavya Yoga": 8, "Gajakesari Yoga": 4}),
        (["child", "children", "progeny", "fertility"], "Children", [5, 2, 9, 11], ["Jupiter", "Moon", "Sun"], ["D9"], [5], {"Hamsa Yoga": 5, "Gajakesari Yoga": 4}),
        (["property", "home", "house", "land", "vehicle", "comfort"], "Property", [4, 2, 11, 9], ["Moon", "Venus", "Mars"], ["D9"], [4, 11], {"Malavya Yoga": 5, "Gajakesari Yoga": 4}),
        (["foreign", "abroad", "travel", "overseas", "settlement", "visa"], "Foreign", [9, 12, 3, 7], ["Rahu", "Moon", "Jupiter", "Saturn"], ["D9"], [9, 12], {"Raja Yoga": 3}),
        (["spiritual", "moksha", "religion", "guru", "occult", "meditation"], "Spiritual", [12, 9, 8, 5], ["Ketu", "Jupiter", "Saturn"], ["D9"], [12, 9], {"Hamsa Yoga": 8, "Viparita Raja Yoga": 7}),
    ]
    for words, name, houses, planets, vargas, kp_houses, yogas in profiles:
        if any(w in q for w in words):
            return {"name": name, "houses": houses, "planets": planets, "vargas": vargas, "kp": kp_houses, "yogas": yogas}
    return {"name": "General Potential", "houses": [1, 5, 9, 10, 11], "planets": ["Sun", "Moon", "Jupiter", "Mercury"], "vargas": ["D9", "D10"], "kp": [10, 11], "yogas": {"Raja Yoga": 6, "Gajakesari Yoga": 5, "Hamsa Yoga": 4}}


def calculate_custom_aspect_score(dossier, criteria):
    q = str(criteria).lower()
    if any(w in q for w in ["wealth", "rich", "money", "finance"]) and not custom_is_risk_topic(criteria):
        return calculate_wealth_score(dossier)
    if any(w in q for w in ["marriage", "relationship", "love", "spouse"]) and not custom_is_risk_topic(criteria):
        return calculate_relationship_score(dossier)
    if any(w in q for w in ["career", "profession", "job", "promotion"]) and not custom_is_risk_topic(criteria):
        return calculate_career_score(dossier)
    if any(w in q for w in ["health", "longevity", "constitution"]) and not custom_is_risk_topic(criteria):
        return calculate_health_score(dossier)
    if any(w in q for w in ["happy", "happiness", "contentment", "fulfilled"]) and not custom_is_risk_topic(criteria):
        return calculate_happiness_score(dossier)
    if any(w in q for w in ["luck", "fortune", "fortunate"]) and not custom_is_risk_topic(criteria):
        return calculate_luck_score(dossier)
    if any(w in q for w in ["spiritual", "moksha", "religion", "occult"]):
        return calculate_spiritual_score(dossier)
    if any(w in q for w in ["hidden", "pitfall", "unexpected", "scandal", "secret"]):
        return calculate_hidden_pitfalls_score(dossier)
    if custom_is_risk_topic(criteria):
        return calculate_struggles_score(dossier)

    math_data = recalc_math(dossier)
    if not math_data: return 50.0
    ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon = math_data

    f = parse_chart_facts(dossier)
    spec = custom_topic_profile(criteria)
    structural_parts = []
    for idx, house in enumerate(spec["houses"]):
        structural_parts.append((house_score(f, house), max(0.7, 2.0 - idx * 0.25)))
    karaka_parts = [(planet_strength(f, p), 1.0) for p in spec["planets"]]
    for chart in spec["vargas"]:
        for p in spec["planets"][:3]:
            karaka_parts.append((varga_sign_strength(f, chart, p), 0.45))
    kp_parts = [(kp_norm(extract_kp_promise(dossier, h)), 1.0) for h in spec["kp"]]
    
    yoga = topic_yoga_score(f, spec["yogas"], planet_data, ls, lagna_lon, jd_ut)
    placement = topic_house_connection(f, spec["planets"], set(spec["houses"]))
    risk = affliction_count(f, planets=set(spec["planets"])) * 4
    score = score_positive(structural_parts) * 0.44 + score_positive(karaka_parts) * 0.29 + score_positive(kp_parts) * 0.15 + yoga + placement - risk
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


def calculate_and_rank_profiles(profiles_dossiers, criteria):
    scoring_map = {
        "Wealth Potential": (calculate_wealth_score, False),
        "Relationship Quality": (calculate_relationship_score, False),
        "Career Success": (calculate_career_score, False),
        "Life Struggles": (calculate_struggles_score, True),
        "Health & Longevity": (calculate_health_score, False),
        "Happiness & Contentment": (calculate_happiness_score, False),
        "Luck & Fortune": (calculate_luck_score, False),
        "Spiritual Depth": (calculate_spiritual_score, False),
        "Hidden Pitfalls": (calculate_hidden_pitfalls_score, True),
    }

    active = []
    for c in criteria:
        key = criterion_key(c)
        if key in scoring_map:
            active.append((c, key, scoring_map[key][0], scoring_map[key][1]))
        else:
            active.append((c, c.strip(), lambda dossier, custom=c: calculate_custom_aspect_score(dossier, custom), custom_is_reverse_rank(c)))

    raw = {name: {} for name, _ in profiles_dossiers}
    for name, dossier in profiles_dossiers:
        for full_label, key, func, is_inverted in active:
            try:
                score = float(func(dossier))
            except Exception:
                score = 50.0
            raw[name][key] = {"score": score, "inverted": is_inverted, "label": full_label}

    ranks = {key: {} for _, key, _, _ in active}
    for _, key, _, is_inverted in active:
        ordered = sorted(profiles_dossiers, key=lambda item: raw[item[0]][key]["score"], reverse=not is_inverted)
        for idx, (name, _) in enumerate(ordered, start=1):
            ranks[key][name] = idx

    composite = {}
    for name, _ in profiles_dossiers:
        parts = []
        for _, key, _, is_inverted in active:
            s = raw[name][key]["score"]
            parts.append(100 - s if is_inverted else s)
        composite[name] = sum(parts) / len(parts) if parts else 50.0
    composite_order = sorted(composite, key=composite.get, reverse=True)
    composite_rank = {name: idx for idx, name in enumerate(composite_order, start=1)}

    header_keys = [key for _, key, _, _ in active]
    out = []
    out.append("### Rankings Table")
    out.append("| Profile | Overall | " + " | ".join(header_keys) + " |")
    out.append("|---|---:|" + "---:|" * len(header_keys))
    for name, _ in sorted(profiles_dossiers, key=lambda item: composite_rank[item[0]]):
        cells = [f"#{composite_rank[name]} ({composite[name]:.1f})"]
        for key in header_keys:
            s = raw[name][key]["score"]
            cells.append(f"#{ranks[key][name]} ({s:.1f})")
        out.append(f"| {name} | " + " | ".join(cells) + " |")

    out.append("\n### Overall Composite Rankings")
    for idx, name in enumerate(composite_order, start=1):
        out.append(f"Rank {idx}: {name} (Composite Baseline: {composite[name]:.1f}/100)")

    out.append("\n### Detailed Parameter Rankings")
    for full_label, key, _, is_inverted in active:
        ordered = sorted(profiles_dossiers, key=lambda item: raw[item[0]][key]["score"], reverse=not is_inverted)
        out.append(f"\nParameter: {full_label}")
        out.append(f"Direction: {'lower burden is better' if is_inverted else 'higher structural promise is better'}")
        for idx, (name, _) in enumerate(ordered, start=1):
            out.append(f"Rank {idx}: {name} (Score: {raw[name][key]['score']:.1f})")
    return "\n".join(out)


def calculate_matchmaking_synastry(prof_a, prof_b, ma, mb, jda, jdb, dos_a, dos_b):
    koota_data = calculate_ashta_koota(ma, mb)
    marital_a = calculate_marital_analysis(jda, prof_a['lat'], prof_a['lon'])
    marital_b = calculate_marital_analysis(jdb, prof_b['lat'], prof_b['lon'])
    kp_a = extract_kp_promise(dos_a, 7)
    kp_b = extract_kp_promise(dos_b, 7)
    return koota_data, marital_a, marital_b, kp_a, kp_b


def calculate_destiny_confirmation(prof_a, prof_b, jda, jdb, dos_a, dos_b):
    pla = {pn: get_planet_longitude_and_speed(jda, pid) for pn, pid in PLANETS.items()}
    ra_a, _ = get_planet_longitude_and_speed(jda, swe.MEAN_NODE); pla["Rahu"] = (ra_a, 0); pla["Ketu"] = ((ra_a + 180) % 360, 0)
    plb = {pn: get_planet_longitude_and_speed(jdb, pid) for pn, pid in PLANETS.items()}
    ra_b, _ = get_planet_longitude_and_speed(jdb, swe.MEAN_NODE); plb["Rahu"] = (ra_b, 0); plb["Ketu"] = ((ra_b + 180) % 360, 0)
    
    laga = sign_index_from_lon(get_lagna_and_cusps(jda, prof_a['lat'], prof_a['lon'])[0])
    lagb = sign_index_from_lon(get_lagna_and_cusps(jdb, prof_b['lat'], prof_b['lon'])[0])
    
    moona_sidx = sign_index_from_lon(pla["Moon"][0])
    moonb_sidx = sign_index_from_lon(plb["Moon"][0])
    
    laga_lord = SIGN_LORDS_MAP[laga]
    lagb_lord = SIGN_LORDS_MAP[lagb]
    
    def get_dk_ak(pl):
        degs = [(p, lon % 30) for p, (lon, _) in pl.items() if p not in ["Rahu", "Ketu"]]
        degs.sort(key=lambda x: x[1], reverse=True)
        return degs[0][0], degs[-1][0] 
        
    aka, dka = get_dk_ak(pla)
    akb, dkb = get_dk_ak(plb)
    
    marital_a = calculate_marital_analysis(jda, prof_a['lat'], prof_a['lon'])
    marital_b = calculate_marital_analysis(jdb, prof_b['lat'], prof_b['lon'])
    
    kp_a = extract_kp_promise(dos_a, 7)
    kp_b = extract_kp_promise(dos_b, 7)
    
    from datetime import datetime, date
    dt_loc_a = datetime.combine(date.fromisoformat(prof_a['date']) if isinstance(prof_a['date'], str) else prof_a['date'], datetime.strptime(prof_a['time'], "%H:%M").time() if isinstance(prof_a['time'], str) else prof_a['time'])
    dt_loc_b = datetime.combine(date.fromisoformat(prof_b['date']) if isinstance(prof_b['date'], str) else prof_b['date'], datetime.strptime(prof_b['time'], "%H:%M").time() if isinstance(prof_b['time'], str) else prof_b['time'])
    
    d_info_a = build_vimshottari_timeline(dt_loc_a, pla["Moon"][0], datetime.now())
    d_info_b = build_vimshottari_timeline(dt_loc_b, plb["Moon"][0], datetime.now())
    
    def is_friend(p1, p2):
        friends = {
            "Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
            "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus"],
            "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn"],
            "Saturn": ["Mercury", "Venus"]
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
            if csign == ra_sign or csign == ke_sign: return True
        return False

    core_b_lons = [plb["Moon"][0], plb["Venus"][0], plb[lagb_lord][0]]
    core_a_lons = [pla["Moon"][0], pla["Venus"][0], pla[laga_lord][0]]
    
    obsession_a_to_b = check_nodal_obsession(pla["Rahu"][0], pla["Ketu"][0], core_b_lons)
    obsession_b_to_a = check_nodal_obsession(plb["Rahu"][0], plb["Ketu"][0], core_a_lons)

    score_promise = (min(kp_a, 3)/3 * 10) + (min(kp_b, 3)/3 * 10)
    
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
    
    def check_insertion(lord_a, sign_a, lag_b):
        b_h7_sign = (lag_b + 6) % 12
        if sign_a == b_h7_sign: return True
        return False
        
    a_in_b7 = check_insertion(laga_lord, sign_index_from_lon(pla[laga_lord][0]), lagb)
    b_in_a7 = check_insertion(lagb_lord, sign_index_from_lon(plb[lagb_lord][0]), laga)
    
    score_synastry = 0
    if a_in_b7: score_synastry += 7.5
    if b_in_a7: score_synastry += 7.5
    if obsession_a_to_b: score_synastry += 5
    if obsession_b_to_a: score_synastry += 5

    def extract_h7_sig(dossier):
        sigs = set()
        if "KP PLANETARY SIGNIFICATORS" in dossier:
            try:
                lines = dossier.split("KP PLANETARY SIGNIFICATORS")[1].split("=")[0].split("\\n")
                for line in lines:
                    if "7" in line:
                        p = line.split(":")[0].strip()
                        if p in PLANETS: sigs.add(p)
            except: pass
        return sigs

    sigs_a = extract_h7_sig(dos_a)
    sigs_b = extract_h7_sig(dos_b)
    shared_sigs = sigs_a.intersection(sigs_b)
    
    score_timing = 0
    if len(shared_sigs) >= 2: score_timing = 20
    elif len(shared_sigs) == 1: score_timing = 10

    total_destiny_percentage = round(score_promise + score_blueprint_total + score_synastry + score_timing)

    return {
        "A": {"kp_promise": kp_a, "weak_warning": kp_a == 0, "sigs": list(sigs_a)},
        "B": {"kp_promise": kp_b, "weak_warning": kp_b == 0, "sigs": list(sigs_b)},
        "Blueprint": {
            "A_D9_7th_Lord": marital_a['D9_7th_Lord'],
            "B_Core": [lagb_lord, SIGN_LORDS_MAP[moonb_sidx]],
            "B_D9_7th_Lord": marital_b['D9_7th_Lord'],
            "A_Core": [laga_lord, SIGN_LORDS_MAP[moona_sidx]],
            "A_UL": marital_a['UL_Sign'],
            "B_UL": marital_b['UL_Sign'],
            "A_DK": dka, "A_AK": aka,
            "B_DK": dkb, "B_AK": akb
        },
        "Synastry": {
            "A_Lagna_in_B_7th": a_in_b7,
            "B_Lagna_in_A_7th": b_in_a7,
            "A_Nodal_Obsession": obsession_a_to_b,
            "B_Nodal_Obsession": obsession_b_to_a
        },
        "Timing": {
            "A_Current_MD_AD": f"{d_info_a['current_md']} / {d_info_a['current_ad']}",
            "B_Current_MD_AD": f"{d_info_b['current_md']} / {d_info_b['current_ad']}",
            "Shared_Significators": list(shared_sigs)
        },
        "Percentage": total_destiny_percentage
    }