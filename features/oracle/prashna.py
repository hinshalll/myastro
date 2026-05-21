"""
ui_streamlit/views/oracle/prashna.py
=====================================
Prashna Kundli (Horary) — ask a specific yes/no question, get an answer
from a chart cast at the moment of asking.

Logic: capture the user's current location → cast a fresh dossier at
"now" → run the Python KP verdict via build_prashna_prompt → stream the
AI narrative on top of that verdict.

The Python verdict is the final word; the AI prose is just narrative.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from features.oracle._shared import (
    collapse_sidebar_on_mobile,
    generate_astrology_dossier,
    build_prashna_prompt,
    geocode_place_cached, timezone_for_latlon_cached,
    rag_context_cached,
    stream_ai_with_followup,
)


def show_prashna():
    """Standalone entry-point. Future mobile/web app calls this directly."""
    collapse_sidebar_on_mobile()
    st.markdown(
        "<p style='color:rgba(190,185,210,.6);font-size:.88rem;margin-bottom:1.5rem'>"
        "Ask a specific question. Get Yes/No/Delayed.</p><hr>",
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "Your question",
        placeholder="e.g. Will I get the job I applied for?",
    )
    st.markdown("#### Your current location")
    c1, c2 = st.columns(2)
    with c1:
        cur_place = st.text_input("City, Country", key="pr_place")
        if cur_place.strip() and not st.session_state.get("pr_man", False):
            geo = geocode_place_cached(cur_place.strip())
            if geo: st.success(f"📍 {geo[2]}")
            else:   st.warning("Not found.")
    with c2:
        pr_man = st.checkbox("Manual coordinates", key="pr_man")
        if pr_man:
            prl = st.number_input("Lat", value=30.76, format="%.4f", key="prl")
            prn = st.number_input("Lon", value=76.80, format="%.4f", key="prn")
            prt = st.text_input("Timezone", "Asia/Kolkata", key="prt")

    if st.button("Generate Prashna Reading ✨", type="primary", use_container_width=True):
        if not question.strip():
            st.error("Enter a question."); return
        if not st.session_state.get("pr_man", False):
            geo = geocode_place_cached(cur_place.strip())
            if not geo:
                st.error("Location not found."); return
            p_lat, p_lon, pn = geo
            p_tz = timezone_for_latlon_cached(p_lat, p_lon)
        else:
            p_lat = st.session_state.get("prl", 30.76)
            p_lon = st.session_state.get("prn", 76.80)
            p_tz  = st.session_state.get("prt", "Asia/Kolkata")
            pn    = "Manual"
        now  = datetime.now(ZoneInfo(p_tz))
        prof = {
            "name": "Prashna",
            "date": now.date().isoformat(),
            "time": now.strftime("%H:%M"),
            "place": pn, "lat": p_lat, "lon": p_lon, "tz": p_tz,
        }
        with st.spinner("Casting chart..."):
            dos = generate_astrology_dossier(prof)
        st.session_state.prashna_question = question
        st.session_state.prashna_dos      = dos
        st.session_state.prashna_prompt   = build_prashna_prompt(question, dos)
        st.session_state.prashna_chat     = []

    if "prashna_prompt" in st.session_state:
        prashna_ctx = rag_context_cached(
            st.session_state.get("prashna_question", "prashna horary kp question"),
            ("kp6.md",), k=8,
        )
        q_stored = st.session_state.get("prashna_question", "")
        if q_stored and "prashna_dos" in st.session_state:
            prashna_prompt_with_ctx = build_prashna_prompt(
                q_stored, st.session_state["prashna_dos"], knowledge_context=prashna_ctx,
            )
            stream_ai_with_followup(prashna_prompt_with_ctx, "prashna_chat", "Answering your Prashna...", hide_user_prompt=True)
        else:
            stream_ai_with_followup(st.session_state.prashna_prompt, "prashna_chat", "Answering your Prashna...", hide_user_prompt=True)
