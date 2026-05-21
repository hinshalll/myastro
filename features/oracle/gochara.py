"""
ui_streamlit/views/oracle/gochara.py
====================================
Gochara / Live Transit — overlay today's planetary positions on the
selected natal chart, then narrate the live transit influences.

Logic: pick a saved profile → build dossier + transit overlay → RAG
pulls classical transit passages → AI weaves them with the chart.
"""

import streamlit as st

from features.oracle._shared import (
    collapse_sidebar_on_mobile,
    generate_astrology_dossier, get_gochara_overlay,
    build_topic_query, rag_context_cached,
    build_transit_prompt,
    render_profile_form, resolve_profile, stream_ai_with_followup,
)


def show_gochara():
    """Standalone entry-point for live-transit analysis."""
    collapse_sidebar_on_mobile()
    st.markdown(
        "<p style='color:rgba(190,185,210,.6);font-size:.88rem;margin-bottom:1.5rem'>"
        "How today's planets activate your natal chart right now.</p><hr>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Select your natal chart")
    item = render_profile_form("gochara", show_d60=False)

    if st.button("Analyse Live Transits ✨", type="primary", use_container_width=True):
        if item["type"] == "empty_saved":
            st.error("Select a profile."); return
        prof, d60 = resolve_profile(item)
        with st.spinner("Overlaying transits..."):
            dos     = generate_astrology_dossier(prof, d60)
            overlay = get_gochara_overlay(prof)
        gochara_ctx = rag_context_cached(
            build_topic_query(topic="gochara", dossier=dos),
            ("bphs2.md", "htrh2.md"), k=10,
        )
        transit_prompt = build_transit_prompt(dos, overlay, knowledge_context=gochara_ctx)
        st.session_state.transit_prompt = transit_prompt
        st.session_state.transit_chat   = []

    if "transit_prompt" in st.session_state:
        stream_ai_with_followup(
            st.session_state.transit_prompt, "transit_chat", "Reading the stars...",
            hide_user_prompt=True,
        )
