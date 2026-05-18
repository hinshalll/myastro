"""
ui_streamlit/views/oracle/marriage.py
=====================================
Destiny & Marriage Chances — cross-chart confirmation matrix using
Jaimini + D9 + current dasha overlap to give a single marriage-promise
score with full classical reasoning.

Logic flow:
  1. Two profiles → resolve boy/girl
  2. Compute Julian days, build dossiers
  3. Run calculate_destiny_confirmation() — heavy classical matrix
  4. Build the destiny prompt + RAG context
  5. AI narrates the matrix
"""

import streamlit as st

from ui_streamlit.views.oracle._shared import (
    collapse_sidebar_on_mobile,
    local_to_julian_day, generate_astrology_dossier,
    calculate_destiny_confirmation,
    build_topic_query, rag_context_cached, build_destiny_confirmation_prompt,
    generate_content_with_fallback,
    render_profile_form, resolve_profile,
    render_chat_history, render_pdf_download,
    get_default_profile,
    parse_date, parse_time, resolve_boy_girl,
)

_MISSION_KEY = "Destiny & Marriage Chances"


def show_marriage():
    """Standalone entry-point for the Destiny Marriage Matrix."""
    collapse_sidebar_on_mobile()
    st.markdown(
        "<p style='color:rgba(190,185,210,.6);font-size:.88rem;margin-bottom:1.5rem'>"
        "Advanced cross-chart confirmation matrix.</p><hr>",
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

    if st.button("Generate Destiny Marriage Matrix ✨", type="primary",
                 use_container_width=True, key=f"gen_{_MISSION_KEY}"):
        profiles, d60s = [], []
        for item in active:
            if item["type"] == "empty_saved":
                st.error("Fill all profile slots."); return
            prof, d60 = resolve_profile(item)
            profiles.append(prof); d60s.append(d60)
        with st.spinner("Crunching Jaimini & D9 matrices..."):
            _run_marriage_matrix(profiles, d60s)

    history = st.session_state.get(f"oracle_{_MISSION_KEY}_history", [])
    if history:
        render_chat_history(history)
        render_pdf_download(_MISSION_KEY, "Destiny Marriage Matrix", "♦", history, dp)


def _run_marriage_matrix(profiles, d60s):
    """Destiny confirmation matrix pipeline."""
    p_boy, p_girl = resolve_boy_girl(profiles)
    pb_idx = profiles.index(p_boy); pg_idx = profiles.index(p_girl)

    jda, _, _ = local_to_julian_day(parse_date(p_boy),  parse_time(p_boy),  p_boy["tz"])
    jdb, _, _ = local_to_julian_day(parse_date(p_girl), parse_time(p_girl), p_girl["tz"])

    dos_a = generate_astrology_dossier(p_boy,  d60s[pb_idx])
    dos_b = generate_astrology_dossier(p_girl, d60s[pg_idx])
    dest_data = calculate_destiny_confirmation(p_boy, p_girl, jda, jdb, dos_a, dos_b)

    # Marriage/Jaimini classical passages for the AI to cite
    match_ctx = rag_context_cached(
        build_topic_query(topic="match",
            extras={"score": str(dest_data.get("Percentage", ""))}),
        ("htrh2.md", "kp4.md"), 10,
    )
    final = build_destiny_confirmation_prompt(
        p_boy, p_girl, dos_a, dos_b, dest_data,
        knowledge_context=match_ctx,
    )
    st.info("📖 Generating Destiny Marriage Matrix...")
    result = generate_content_with_fallback(final, knowledge_files=None)
    if result:
        st.session_state[f"oracle_{_MISSION_KEY}_history"] = [
            {"role":"user",  "display":"💞 Destiny Marriage Matrix", "parts":[final]},
            {"role":"model", "display":result,                       "parts":[result]},
        ]
