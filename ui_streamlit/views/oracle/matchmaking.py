"""
ui_streamlit/views/oracle/matchmaking.py
========================================
Matchmaking / Compatibility — Ashta Koota (36 Gunas) + Manglik with
cancellation logic + KP H7 promise + D9 synastry + Compatibility Index.

Logic flow:
  1. Two saved profiles → resolve boy/girl by gender
  2. Compute Moon longitudes + Ashta Koota
  3. Compute Manglik tier WITH classical cancellations
  4. Compute the unified Compatibility Index (0-100)
  5. Pass everything to the matchmaking AI prompt
  6. Render result + PDF download
"""

import streamlit as st

from ui_streamlit.views.oracle._shared import (
    collapse_sidebar_on_mobile,
    PLANETS, SIGN_LORDS_MAP,
    local_to_julian_day, get_planet_longitude_and_speed,
    sign_index_from_lon, get_lagna_and_cusps,
    generate_astrology_dossier,
    calculate_matchmaking_synastry, calculate_compatibility_index,
    check_manglik_dosha, get_manglik_cancellation_verdict,
    build_topic_query, rag_context_cached, build_matchmaking_prompt,
    generate_content_with_fallback,
    render_profile_form, resolve_profile,
    render_chat_history, render_pdf_download,
    get_moon_lon_from_profile, get_default_profile,
    parse_date, parse_time, resolve_boy_girl,
)

_MISSION_KEY = "Matchmaking / Compatibility"


def show_matchmaking():
    """Standalone entry-point for the Compatibility Match feature."""
    collapse_sidebar_on_mobile()
    st.markdown(
        "<p style='color:rgba(190,185,210,.6);font-size:.88rem;margin-bottom:1.5rem'>"
        "Ashta Koota + Manglik + Compatibility.</p><hr>",
        unsafe_allow_html=True,
    )
    dp, _ = get_default_profile()

    st.markdown("#### Profile Selection")
    cols = st.columns(2)
    active = []
    for i in range(2):
        with cols[i]:
            st.markdown(f"**Person {i+1}**")
            active.append(render_profile_form(f"orc_{_MISSION_KEY}_{i}"))

    if st.button("Generate Compatibility Match ✨", type="primary", use_container_width=True,
                 key=f"gen_{_MISSION_KEY}"):
        profiles, d60s = [], []
        for item in active:
            if item["type"] == "empty_saved":
                st.error("Fill all profile slots."); return
            prof, d60 = resolve_profile(item)
            profiles.append(prof); d60s.append(d60)
        with st.spinner("Consulting the ephemeris..."):
            _run_matchmaking(profiles, d60s)

    history = st.session_state.get(f"oracle_{_MISSION_KEY}_history", [])
    if history:
        render_chat_history(history)
        render_pdf_download(_MISSION_KEY, "Compatibility Match", "♥", history, dp)


def _run_matchmaking(profiles, d60s):
    """Full Ashta Koota + Manglik + Index pipeline. See module docstring."""
    p_boy, p_girl = resolve_boy_girl(profiles)
    ma = get_moon_lon_from_profile(p_boy)
    mb = get_moon_lon_from_profile(p_girl)

    jda, _, _ = local_to_julian_day(parse_date(p_boy),  parse_time(p_boy),  p_boy["tz"])
    jdb, _, _ = local_to_julian_day(parse_date(p_girl), parse_time(p_girl), p_girl["tz"])

    pla   = {pn: get_planet_longitude_and_speed(jda, pid) for pn, pid in PLANETS.items()}
    plb   = {pn: get_planet_longitude_and_speed(jdb, pid) for pn, pid in PLANETS.items()}
    laga  = sign_index_from_lon(get_lagna_and_cusps(jda, p_boy["lat"],  p_boy["lon"])[0])
    lagb  = sign_index_from_lon(get_lagna_and_cusps(jdb, p_girl["lat"], p_girl["lon"])[0])

    # Classical Manglik with cancellation logic (own sign / exalted / aspected
    # by Jupiter or Venus / Saturn conjunction) — pass full planet_data so the
    # detector can apply all classical cancellations.
    ma_d = check_manglik_dosha(
        laga, sign_index_from_lon(pla["Moon"][0]),
        sign_index_from_lon(pla["Mars"][0]),
        mars_lon=pla["Mars"][0], planet_data=pla,
    )
    mb_d = check_manglik_dosha(
        lagb, sign_index_from_lon(plb["Moon"][0]),
        sign_index_from_lon(plb["Mars"][0]),
        mars_lon=plb["Mars"][0], planet_data=plb,
    )
    canc = get_manglik_cancellation_verdict(ma_d, mb_d)

    dos_a = generate_astrology_dossier(p_boy,  d60s[profiles.index(p_boy)])
    dos_b = generate_astrology_dossier(p_girl, d60s[profiles.index(p_girl)])
    koota_data, marital_a, marital_b, kp_a, kp_b = calculate_matchmaking_synastry(
        p_boy, p_girl, ma, mb, jda, jdb, dos_a, dos_b,
    )

    # Unified Compatibility Index (0-100) blending Koota + KP H7 + D9 + UL + Manglik.
    compat_index = calculate_compatibility_index(
        koota_data, marital_a, marital_b, kp_a, kp_b,
        laga_lord=SIGN_LORDS_MAP[laga],
        lagb_lord=SIGN_LORDS_MAP[lagb],
        moon_lord_a=SIGN_LORDS_MAP[sign_index_from_lon(pla["Moon"][0])],
        moon_lord_b=SIGN_LORDS_MAP[sign_index_from_lon(plb["Moon"][0])],
        manglik_verdict=canc,
    )

    match_ctx = rag_context_cached(
        build_topic_query(topic="match", extras={"score": str(koota_data.get("score", ""))}),
        ("htrh2.md", "kp4.md"), 10,
    )
    final = build_matchmaking_prompt(
        dos_a, dos_b, koota_data, canc, p_boy, p_girl,
        marital_a, marital_b, kp_a, kp_b,
        knowledge_context=match_ctx,
        compatibility_index=compat_index,
    )
    st.info("📖 Generating compatibility reading...")
    try:
        result = generate_content_with_fallback(final, knowledge_files=None)
    except Exception as e:
        result = f"⚠️ Reading paused ({str(e)[:100]}). Please try again in ~1 minute."

    st.session_state[f"oracle_{_MISSION_KEY}_history"] = [
        {"role":"user",  "display":"✦ Compatibility Match", "parts":[final]},
        {"role":"model", "display":result,                   "parts":[result]},
    ]
