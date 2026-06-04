"""
ui_streamlit/views/oracle/compare.py
====================================
Compare Profiles — rank 2-10 people across selected criteria (Wealth,
Career, Relationship, etc.) with statistical trust layer and per-rank
driver evidence.

The math heavy-lifting (band labels, cohort percentile, discrimination
index, tie groups, generational deduplication, driver supports/drains)
lives in shared.astro.scoring.calculate_and_rank_profiles — this view
just collects profiles + criteria and renders the AI narrative on top.
"""

import streamlit as st

from shared.astro.constants import COMPARISON_CRITERIA

from features.oracle._shared import (
    collapse_sidebar_on_mobile,
    generate_astrology_dossier,
    build_comparison_knowledge, build_comparison_prompt,
    generate_content_with_fallback,
    render_profile_form, resolve_profile,
    render_chat_history, render_pdf_download,
    get_default_profile, toggle_all_criteria,
)

_MISSION_KEY = "Comparison (Multiple Profiles)"


def show_compare():
    """Standalone entry-point for Compare Profiles."""
    collapse_sidebar_on_mobile()
    st.markdown(
        "<p style='color:rgba(190,185,210,.6);font-size:.88rem;margin-bottom:1.5rem'>"
        "Rank multiple people with planetary evidence.</p><hr>",
        unsafe_allow_html=True,
    )
    dp, _ = get_default_profile()

    num_slots = st.session_state.comp_slots
    st.markdown("#### Profile Selection")
    active = []
    for i in range(num_slots):
        st.markdown(f"**Profile {i+1}**")
        active.append(render_profile_form(f"orc_{_MISSION_KEY}_{i}"))

    ca, cb, _ = st.columns([1, 1, 4])
    if ca.button("＋ Add", key=f"addc_{_MISSION_KEY}"):
        if st.session_state.comp_slots < 10:
            st.session_state.comp_slots += 1; st.rerun()
    if cb.button("－ Remove", key=f"remc_{_MISSION_KEY}"):
        if st.session_state.comp_slots > 2:
            st.session_state.comp_slots -= 1; st.rerun()

    # Criterion selection — built-in list + custom user criteria
    selected_criteria = []
    st.markdown("### What to Compare")
    st.checkbox("Select All", key="select_all_cb", on_change=toggle_all_criteria)
    ca2, cb3 = st.columns(2)
    for i, crit in enumerate(COMPARISON_CRITERIA):
        with (ca2 if i % 2 == 0 else cb3):
            if st.checkbox(crit, key=f"chk_{i}"):
                selected_criteria.append(crit)

    nc_c, nc_a = st.columns([4, 1])
    nc = nc_c.text_input("Custom", label_visibility="collapsed",
                         placeholder="e.g. Most likely to be famous")
    if nc_a.button("Add"):
        if nc.strip() and nc.strip() not in st.session_state.custom_criteria:
            st.session_state.custom_criteria.append(nc.strip()); st.rerun()
    for i, c in enumerate(st.session_state.custom_criteria):
        r1, r2 = st.columns([6, 1])
        if r1.checkbox(c, key=f"cc_{i}"):
            selected_criteria.append(c)
        if r2.button("✕", key=f"delc_{i}"):
            st.session_state.custom_criteria.pop(i); st.rerun()

    if st.button("Compare Profiles ✨", type="primary", use_container_width=True,
                 key=f"gen_{_MISSION_KEY}"):
        profiles, d60s = [], []
        for item in active:
            if item["type"] == "empty_saved":
                st.error("Fill all profile slots."); return
            prof, d60 = resolve_profile(item)
            profiles.append(prof); d60s.append(d60)
        if not selected_criteria:
            st.warning("Select at least one criterion."); return
        with st.spinner("Consulting the ephemeris..."):
            _run_compare(profiles, d60s, selected_criteria)

    history = st.session_state.get(f"oracle_{_MISSION_KEY}_history", [])
    if history:
        render_chat_history(history)
        render_pdf_download(_MISSION_KEY, "Profile Comparison", "⚖", history, dp)


def _run_compare(profiles, d60s, selected_criteria):
    """Build (name, dossier, profile) 3-tuples so the ranker uses the
    direct recalc_math_from_profile path (bypasses dossier-text regex)."""
    compact = len(profiles) > 3
    pairs = [
        (p["name"], generate_astrology_dossier(p, d, compact), p)
        for p, d in zip(profiles, d60s)
    ]
    compare_ctx = build_comparison_knowledge(selected_criteria)
    final = build_comparison_prompt(pairs, selected_criteria, knowledge_context=compare_ctx)
    st.info("📖 Comparing profiles...")
    try:
        result = generate_content_with_fallback(final, knowledge_files=None, task="agent")
    except Exception as e:
        result = f"⚠️ Reading paused ({str(e)[:100]}). Please try again in ~1 minute."

    st.session_state[f"oracle_{_MISSION_KEY}_history"] = [
        {"role":"user",  "display":"⚖ Profile Comparison", "parts":[final]},
        {"role":"model", "display":result,                  "parts":[result]},
    ]
