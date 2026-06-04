import json
from datetime import datetime, date
from zoneinfo import ZoneInfo
from shared.astro.constants import *
from shared.astro.astro_calc import *
from shared.astro.scoring import *
from shared.astro import ephemeris
from shared.astro import config as astro_config

def generate_astrology_dossier(profile,include_d60=False,compact=False,include_kp=None):
    # KP (Placidus cusp sub-lord) sections follow the SINGLE backend toggle
    # shared.astro.config.kp_enabled() (default OFF) unless a caller forces include_kp.
    # KP OFF => the dossier carries only its always-present classical Parashari material
    # (house rulership, Vimshottari dasha, Event Timing Atlas, D9, ashtakavarga, yogas),
    # so every reading still works via TRADITIONAL methods. KP ON => the KP cusp / promise
    # / marriage-timing sections are added on top. No feature is removed either way — the
    # method swaps. The numeric scorers swap in lockstep via astro_calc.house_promise_score
    # (Parashari bhava lord when OFF, KP cusp sub-lord when ON).
    show_kp = astro_config.kp_enabled() if include_kp is None else bool(include_kp)
    lat,lon,tz_name=profile['lat'],profile['lon'],profile['tz']
    name,place_text=profile['name'],profile['place']
    prof_date=date.fromisoformat(profile['date']) if isinstance(profile['date'],str) else profile['date']
    prof_time=(datetime.strptime(profile['time'],"%H:%M").time() if isinstance(profile['time'],str) else profile['time'])
    jd_ut,dt_local,_=local_to_julian_day(prof_date,prof_time,tz_name)
    lagna_lon,_=get_lagna_and_cusps(jd_ut,lat,lon)
    placidus_cusps=get_placidus_cusps(jd_ut,lat,lon)
    planet_data={pn:get_planet_longitude_and_speed(jd_ut,pid) for pn,pid in PLANETS.items()}
    r_lon=get_rahu_longitude(jd_ut); k_lon=(r_lon+180.0)%360
    dasha_info=build_vimshottari_timeline(dt_local,planet_data["Moon"][0],datetime.now(ZoneInfo(tz_name)))
    panchanga=get_panchanga(planet_data["Sun"][0],planet_data["Moon"][0],dt_local)
    ls=sign_index_from_lon(lagna_lon); moon_sidx=sign_index_from_lon(planet_data["Moon"][0])
    mars_sidx=sign_index_from_lon(planet_data["Mars"][0])
    ll_chain=get_lagna_lord_chain(ls,planet_data,r_lon,k_lon)
    conjunctions=get_conjunctions(ls,planet_data,r_lon,k_lon)
    mutual_asp=get_mutual_aspects(ls,planet_data,r_lon,k_lon)
    graha_yuddha=detect_graha_yuddha(jd_ut,planet_data)
    f_ben,f_mal,yogak,f_neu=get_functional_planets(ls)
    manglik=check_manglik_dosha(ls,moon_sidx,mars_sidx)
    sade_sati=calculate_sade_sati(moon_sidx)
    ak,ak_deg,amk,amk_deg,karaka_chain=get_chara_karakas(planet_data)
    yogas_present,yogas_absent=detect_yogas(ls,moon_sidx,planet_data,r_lon,k_lon)
    ad_table=get_antardasha_table(dasha_info)
    house_summary=get_house_strength_summary(ls,planet_data,r_lon,k_lon,placidus_cusps)
    lat_lbl=f"{abs(lat):.5f}{'N' if lat>=0 else 'S'}"; lon_lbl=f"{abs(lon):.5f}{'E' if lon>=0 else 'W'}"
    lines=[]
    lines.append(f"{'═'*58}\nKUNDLI DOSSIER — {name.upper()}")
    lines.append(f"System: Swiss Ephemeris | Lahiri Ayanamsa | Whole Sign + KP Placidus\n{'═'*58}")
    lines.append(f"\nBIRTH DATA:\nName: {name} | Place: {place_text}")
    lines.append(f"Time: {dt_local.strftime('%d %b %Y, %I:%M %p')} ({panchanga['weekday']})")
    lines.append(f"Coordinates: {lat_lbl}, {lon_lbl} | Timezone: {tz_name}")
    lines.append(f"Tithi: {panchanga['tithi']} | Yoga: {panchanga['yoga']} | Karana: {panchanga['karana']}")
    lines.append(f"\nLAGNA FOUNDATION:\nAscendant: {sign_name(ls)} {format_dms(lagna_lon%30)}")
    al_house, al_sidx = calculate_arudha_lagna(ls, planet_data, r_lon, k_lon)
    indu_sidx = calculate_indu_lagna(ls, moon_sidx)
    lines.append(f"Lagna Lord Chain: {ll_chain} | Manglik: {manglik}")
    lines.append(f"Arudha Lagna (AL): {sign_name(al_sidx)} (H{al_house}) | Indu Lagna (Wealth): {sign_name(indu_sidx)}")
    lines.append(f"\nFUNCTIONAL PLANETS FOR {sign_name(ls).upper()} LAGNA (DO NOT override):")
    lines.append(f"  Yogakarakas: {', '.join(yogak) if yogak else 'None'}")
    lines.append(f"  Functional Benefics: {', '.join(f_ben) if f_ben else 'None'}")
    lines.append(f"  Functional Malefics: {', '.join(f_mal) if f_mal else 'None'}")
    
    lines.append(f"\nPLANETARY POSITIONS (D1 Rasi):")
    house_occupants={i:[] for i in range(1,13)}
    
    # 🛠️ HELPER FOR PAPA-KARTARI: Track where natural malefics are placed
    malefic_houses = []
    for m_pn in ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]:
        m_lon = get_planet_lon_helper(m_pn, planet_data, r_lon, k_lon)
        malefic_houses.append(whole_sign_house(ls, sign_index_from_lon(m_lon)))

    for pname in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        plon,pspd=planet_data[pname]; sidx=sign_index_from_lon(plon); house=whole_sign_house(ls,sidx)
        nak,nak_lord,pada=nakshatra_info(plon); avastha=get_baladi_avastha(plon); sl=get_kp_sub_lord(plon)
        asp={"Mars":"H4,H8,H7","Jupiter":"H5,H9,H7","Saturn":"H3,H7,H10","Rahu":"H5,H7,H9","Ketu":"H5,H7,H9"}.get(pname,f"H{((house+6)%12)+1}")
        house_occupants[house].append(pname); tags=[]
        
        # 1. Standard Dignity & Retrograde
        if pspd<0 and pname not in ["Sun","Moon"]: tags.append("Retrograde")
        if pname in COMBUST_DEGREES:
            diff=min(abs(plon-planet_data["Sun"][0]),360-abs(plon-planet_data["Sun"][0]))
            # Mercury and Venus have different combust orbs when retrograde vs direct
            if pname == "Mercury":
                orb = 14 if pspd < 0 else 12  # Retrograde: 14°, Direct: 12°
            elif pname == "Venus":
                orb = 16 if pspd < 0 else 8   # Retrograde: 16°, Direct: 8°
            else:
                orb = COMBUST_DEGREES[pname]
            if diff <= orb: tags.append(f"Combust({orb}°orb)")
        if pname in DIGNITIES:
            if sidx==DIGNITIES[pname][0]: tags.append("Exalted")
            elif sidx==DIGNITIES[pname][1]: tags.append("Debilitated")
        if pname in OWN_SIGNS and sidx in OWN_SIGNS[pname]: tags.append("Own Sign")
            
        # 2. 🛠️ D9 NAVAMSA DIGNITIES & VARGOTTAMA
        d9_sign = d9_si(plon)
        if sidx == d9_sign: tags.append("VARGOTTAMA (Immense Inner Strength)")
        if pname in DIGNITIES:
            if d9_sign == DIGNITIES[pname][0]: tags.append("D9-Exalted (Hidden Power)")
            elif d9_sign == DIGNITIES[pname][1]: tags.append("D9-Debilitated (Hidden Weakness)")
        if pname in OWN_SIGNS and d9_sign in OWN_SIGNS[pname]: tags.append("D9-Own Sign")
            
        # 3. GANDANTA & PAPA-KARTARI
        plon_mod = plon % 120 
        if plon_mod > 116.66 or plon_mod < 3.33: tags.append("GANDANTA (Karmic Knot)")
        h_prev = 12 if house == 1 else house - 1
        h_next = 1 if house == 12 else house + 1
        if (h_prev in malefic_houses) and (h_next in malefic_houses) and pname not in ["Sun", "Mars", "Saturn"]:
            tags.append("PAPA-KARTARI (Hemmed in/Blocked)")

        # 4. 🛠️ BHAVA CHALIT CUSP SHIFT
        plac_h = get_placidus_house(plon, placidus_cusps)
        if plac_h != house: tags.append(f"Bhava Chalit Shift: Acts as H{plac_h}")

        tag_str=f" [{', '.join(tags)}]" if tags else ""
        kp_4 = get_kp_4step(pname, ls, planet_data, r_lon, k_lon)
        
        lines.append(f"  {pname}: H{house} {sign_name(sidx)} {format_dms(plon%30)}{tag_str} | Avastha:{avastha} | Nak:{nak}(NL:{nak_lord} SL:{sl} P:{pada})")
        lines.append(f"    ↳ Asp: {asp} | KP 4-Step: {kp_4}")

    # Process Nodes (Rahu/Ketu)
    for pname,plon in [("Rahu",r_lon),("Ketu",k_lon)]:
        sidx=sign_index_from_lon(plon); house=whole_sign_house(ls,sidx)
        nak,nak_lord,pada=nakshatra_info(plon); sl=get_kp_sub_lord(plon); house_occupants[house].append(pname)
        
        tags = ["Retrograde"]
        d9_sign = d9_si(plon)
        if sidx == d9_sign: tags.append("VARGOTTAMA")
        plon_mod = plon % 120
        if plon_mod > 116.66 or plon_mod < 3.33: tags.append("GANDANTA")
        plac_h = get_placidus_house(plon, placidus_cusps)
        if plac_h != house: tags.append(f"Bhava Chalit Shift: Acts as H{plac_h}")
        
        kp_4 = get_kp_4step(pname, ls, planet_data, r_lon, k_lon)
        lines.append(f"  {pname}: H{house} {sign_name(sidx)} {format_dms(plon%30)} [{', '.join(tags)}] | Nak:{nak}(NL:{nak_lord} SL:{sl} P:{pada})")
        lines.append(f"    ↳ KP 4-Step: {kp_4}")
    lines.append(f"\nPRE-COMPUTED CRITICAL FACTS (DO NOT re-derive):")
    lines.append(f"[Conjunctions]\n" + ("\n".join(f"  ✓ {c}" for c in conjunctions) if conjunctions else "  None"))
    lines.append(f"[Mutual Aspects]\n" + ("\n".join(f"  ↔ {m}" for m in mutual_asp) if mutual_asp else "  None"))
    lines.append("[Graha Yuddha — Planetary War]")
    if graha_yuddha:
        for winner,loser,deg in graha_yuddha:
            lines.append(f"  ⚔ {winner} vs {loser} (sep:{deg}°) — {winner} WINS (higher ecliptic latitude)")
            lines.append(f"    → {loser}'s significations suppressed. {winner}'s amplified.")
    else: lines.append("  No Graha Yuddha in this chart.")
    lines.append("[Neecha Bhanga]")
    nb_found=False
    for pname in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        psidx=sign_index_from_lon(planet_data[pname][0])
        if pname in DIGNITIES and psidx==DIGNITIES[pname][1]:
            nb_found=True
            conds=check_neecha_bhanga(pname,ls,moon_sidx,planet_data,r_lon,k_lon)
            if conds:
                lines.append(f"  {pname} — Debilitated in {sign_name(psidx)}. NEECHA BHANGA APPLIES → treat as Raja Yoga.")
                for c in conds: lines.append(f"    ✓ {c}")
            else:
                lines.append(f"  {pname} — Debilitated in {sign_name(psidx)}. NO NEECHA BHANGA → genuinely weakened.")
    if not nb_found: lines.append("  No debilitated planets.")
    lines.append("[Yogas — PRESENT ✓]")
    for yn,yd in yogas_present: lines.append(f"  ✓ {yn}: {yd}")
    if not yogas_present: lines.append("  None detected.")
    lines.append("[Yogas — ABSENT ✗ — do NOT mention these]")
    for ya in yogas_absent: lines.append(f"  ✗ {ya}")
    lines.append(f"[Jaimini Chara Karakas — Full Chain]")
    for kname,(kplanet,kdeg) in karaka_chain.items():
        lines.append(f"  {kname}: {kplanet} ({kdeg:.2f}°)")
    lines.append(f"\nHOUSE STRENGTH SUMMARY (pre-computed, use directly):")
    for hs in house_summary: lines.append(f"  {hs}")
    if not compact:
        # Ashtakavarga — full calculation
        bav = calculate_ashtakavarga(ls, planet_data, r_lon, k_lon)
        lines.append(f"\n{format_ashtakavarga_summary(bav, ls)}")
    lines.append(f"\nHOUSE RULERSHIP MAP:")
    for h in range(1,13):
        h_sidx=(ls+h-1)%12; h_lord=SIGN_LORDS_MAP[h_sidx]
        ll_house=get_planet_house(h_lord,ls,planet_data,r_lon,k_lon)
        occ=", ".join(house_occupants[h]) if house_occupants[h] else "Empty"
        lines.append(f"  H{h:02d}({sign_name(h_sidx)}): Lord={h_lord}(H{ll_house}) | {occ}")
    if not compact and show_kp:
        lines.append(f"\nKP PLACIDUS CUSPS (for timing/event promise only):")
        for h in range(1,13):
            clon=placidus_cusps[h-1]; csidx=sign_index_from_lon(clon)
            _,cnl,_=nakshatra_info(clon); csl=get_kp_sub_lord(clon)
            lines.append(f"  H{h:02d}: {sign_name(csidx)} {format_dms(clon%30)} | NL:{cnl} | SL:{csl}")
        
        # KP EVENT PROMISE ANALYSIS — key houses checked per kp3.md rules
        lines.append(f"\nKP EVENT PROMISE ANALYSIS (Sub-Lord of each cusp vs required houses):")
        lines.append("  [KP cusp verdicts are ONE of three timing layers. They show whether the")
        lines.append("   CUSP GATE alone promises an event. They DO NOT override Parashari Dasha.]")
        lines.append("  [AI RULE: A 'NOT PROMISED' KP verdict means the cusp gate is weak —")
        lines.append("   it does NOT mean 'the event will never happen'. Dasha-lord activation")
        lines.append("   still triggers the event, just with classical-style effort. For 'when/")
        lines.append("   what age' questions, ALWAYS use the EVENT TIMING ATLAS below as primary.]")
        for h_check in [7, 10, 6, 5, 4, 2, 9, 12]:
            try:
                promise_line = get_kp_cusp_promise(h_check, ls, planet_data, r_lon, k_lon, placidus_cusps)
                lines.append(f"  {promise_line}")
            except Exception:
                pass
        
        # KP Marriage Timing Clues
        try:
            marriage_timing = get_kp_marriage_timing_clues(ls, planet_data, r_lon, k_lon, placidus_cusps, dasha_info)
            lines.append(f"\nKP MARRIAGE TIMING CLUES:")
            lines.append(f"  {marriage_timing['h7_promise']}")
            lines.append(f"  Significators for marriage (2-7-11): {', '.join(marriage_timing['significators'][:8])}")
            lines.append(f"  Current Dasha Timing: {marriage_timing['timing_verdict']}")
        except Exception:
            pass
    lines.append(f"\nDIVISIONAL CHARTS:")
    all_pn=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
    d2,d3,d4,d7,d9,d10,d12,d30,d60=[],[],[],[],[],[],[],[],[]
    for pn in all_pn:
        pl=get_planet_lon_helper(pn,planet_data,r_lon,k_lon)
        d2.append(f"{pn}:{sign_name(d2_si(pl))}"); d3.append(f"{pn}:{sign_name(d3_si(pl))}")
        d4.append(f"{pn}:{sign_name(d4_si(pl))}"); d7.append(f"{pn}:{sign_name(d7_si(pl))}")
        d9.append(f"{pn}:{sign_name(d9_si(pl))}"); d10.append(f"{pn}:{sign_name(d10_si(pl))}")
        d12.append(f"{pn}:{sign_name(d12_si(pl))}"); d30.append(f"{pn}:{sign_name(d30_si(pl))}")
        if include_d60: d60.append(f"{pn}:{sign_name(d60_si(pl))}")
    lines.append(f"  D9 Navamsa(Marriage): {', '.join(d9)}")
    lines.append(f"  D10 Dasamsa(Career):  {', '.join(d10)}")
    lines.append(f"  D2 Hora(Wealth):      {', '.join(d2)}")
    lines.append(f"  D3 Drekkana(Courage): {', '.join(d3)}")
    lines.append(f"  D4 Chaturt(Property): {', '.join(d4)}")
    lines.append(f"  D7 Saptam(Children):  {', '.join(d7)}")
    lines.append(f"  D12 Dwadam(Parents):  {', '.join(d12)}")
    lines.append(f"  D30 Trimsamsa(Pitfalls): {', '.join(d30)}")
    if include_d60: lines.append(f"  D60 Shashtiamsa(Karma): {', '.join(d60)}")
    lines.append(f"\nVIMSHOTTARI DASHA:")
    lines.append(f"Birth Nakshatra: {dasha_info['birth_nakshatra']} | Balance: {dasha_info['balance_years']:.2f} yrs of {dasha_info['start_lord']}")
    lines.append(f"Current MD: {dasha_info['current_md']} ({dasha_info['md_start'].strftime('%b %Y')} → {dasha_info['md_end'].strftime('%b %Y')})")
    lines.append(f"Current AD: {dasha_info['current_ad']} ({dasha_info['ad_start'].strftime('%b %Y')} → {dasha_info['ad_end'].strftime('%b %Y')})")
    lines.append(f"Current PD: {dasha_info['current_pd']} ({dasha_info['pd_start'].strftime('%d %b %Y')} → {dasha_info['pd_end'].strftime('%d %b %Y')})")
    lines.append(f"\nFULL ANTARDASHA SEQUENCE IN {dasha_info['current_md'].upper()} MAHADASHA:")
    lines.append("(Use ONLY these exact dates — do NOT calculate independently)")
    for row in ad_table: lines.append(row)

    # ── EVENT TIMING ATLAS — precomputed answers for "when/what age" questions ──
    if not compact:
        try:
            atlas = build_event_timing_atlas(
                profile, dasha_info, ls, planet_data, r_lon, k_lon, placidus_cusps
            )
            lines.append("\n" + atlas)
        except Exception as e:
            # Atlas is additive — never break the dossier if it fails.
            lines.append(f"\nEVENT TIMING ATLAS: (unavailable: {type(e).__name__})")

    lines.append(f"\nCURRENT AFFLICTIONS:\nSade Sati: {sade_sati}")
    return "\n".join(lines)


def get_gochara_overlay(profile):
    """Live transit vs natal chart overlay."""
    dt_now=datetime.now(ZoneInfo("UTC"))
    jd_now=ephemeris.julday(dt_now.year,dt_now.month,dt_now.day,dt_now.hour+dt_now.minute/60.0)
    prof_date=date.fromisoformat(profile['date']) if isinstance(profile['date'],str) else profile['date']
    prof_time=(datetime.strptime(profile['time'],"%H:%M").time() if isinstance(profile['time'],str) else profile['time'])
    jd_natal,dt_local,_=local_to_julian_day(prof_date,prof_time,profile['tz'])
    lagna_lon,_=get_lagna_and_cusps(jd_natal,profile['lat'],profile['lon'])
    natal_data={pn:get_planet_longitude_and_speed(jd_natal,pid) for pn,pid in PLANETS.items()}
    natal_r=get_rahu_longitude(jd_natal)
    transit_data={pn:get_planet_longitude_and_speed(jd_now,pid) for pn,pid in PLANETS.items()}
    transit_r=get_rahu_longitude(jd_now)
    ls=sign_index_from_lon(lagna_lon)
    lines=["NATAL CHART (birth positions):"]
    for pn in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        nl=get_planet_lon_helper(pn,natal_data,natal_r,(natal_r+180)%360)
        nh=whole_sign_house(ls,sign_index_from_lon(nl))
        lines.append(f"  Natal {pn}: {sign_name(sign_index_from_lon(nl))} H{nh}")
    lines.append(f"\nLIVE TRANSIT POSITIONS ({dt_now.strftime('%d %b %Y')}):")
    for pn in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        tl=get_planet_lon_helper(pn,transit_data,transit_r,(transit_r+180)%360)
        nl=get_planet_lon_helper(pn,natal_data,natal_r,(natal_r+180)%360)
        th=whole_sign_house(ls,sign_index_from_lon(tl))
        nh=whole_sign_house(ls,sign_index_from_lon(nl))
        diff_houses=((th-nh)%12)
        lines.append(f"  Transit {pn}: {sign_name(sign_index_from_lon(tl))} H{th} (was H{nh} at birth, {diff_houses} houses moved)")
    lines.append(f"  Transit Rahu: {sign_name(sign_index_from_lon(transit_r))} H{whole_sign_house(ls,sign_index_from_lon(transit_r))}")
    return "\n".join(lines)