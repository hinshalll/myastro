"""
ui_streamlit/views/oracle/deep_analysis.py
==========================================
Deep Personal Analysis — the flagship "Full Life Reading" that fires
three parallel AI agents (Parashari + Timing + KP), then a synthesizer.

Logic flow:
  1. Build dossier from saved profile
  2. Fetch RAG contexts for 3 agents concurrently
  3. Run 3 AI agents concurrently — each writes its own analysis notes
  4. Synthesizer agent combines all three into the final reading
  5. Render result + PDF download
"""

import concurrent.futures
import time as time_module

import streamlit as st

from features.oracle._shared import (
    collapse_sidebar_on_mobile,
    generate_astrology_dossier,
    build_topic_query, rag_context_cached,
    build_agent_parashari_prompt, build_agent_timing_prompt, build_agent_kp_prompt,
    build_master_synthesizer_prompt,
    FREE_MODELS, agent_worker, generate_content_with_fallback,
    render_profile_form, resolve_profile,
    render_chat_history, render_pdf_download,
    get_default_profile,
)

_MISSION_KEY = "Deep Personal Analysis"


def show_deep_analysis():
    """Standalone entry-point for the Full Life Reading."""
    collapse_sidebar_on_mobile()
    st.markdown(
        "<p style='color:rgba(190,185,210,.6);font-size:.88rem;margin-bottom:1.5rem'>"
        "Complete reading — personality, career, wealth, marriage, timing.</p><hr>",
        unsafe_allow_html=True,
    )
    dp, _ = get_default_profile()

    st.markdown("#### Profile Selection")
    st.markdown("**Your Details**")
    item = render_profile_form(f"orc_{_MISSION_KEY}_0")

    if st.button("Generate Full Reading ✨", type="primary", use_container_width=True,
                 key=f"gen_{_MISSION_KEY}"):
        if item["type"] == "empty_saved":
            st.error("Fill all profile slots."); return
        prof, d60 = resolve_profile(item)
        with st.spinner("Consulting the ephemeris..."):
            _run_deep_analysis(prof, d60)

    # Render results (re-rendered on every Streamlit rerun)
    history = st.session_state.get(f"oracle_{_MISSION_KEY}_history", [])
    if history:
        render_chat_history(history)
        render_pdf_download(_MISSION_KEY, "Full Life Reading", "★", history, dp)


def _run_deep_analysis(prof, d60):
    """Core engine call. Three concurrent agents → synthesizer → final result."""
    dossier = generate_astrology_dossier(prof, d60)
    st.info("🧠 Firing Parallel AI Agents (Takes ~20s)...")
    expert_rules = (
        "<ROLE>Elite Vedic Astrologer</ROLE>"
        "<MATH_LOCK>Never alter, invent or estimate any number. "
        "Use only data present in the dossier.</MATH_LOCK>"
    )

    # Fetch RAG contexts for all 3 agents concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        f_ctx_p = ex.submit(rag_context_cached,
            build_topic_query(topic="parashari", dossier=dossier),
            ("bphs1.md", "htrh1.md", "htrh2.md"), 10)
        f_ctx_t = ex.submit(rag_context_cached,
            build_topic_query(topic="timing", dossier=dossier),
            ("bphs2.md", "kp3.md"), 10)
        f_ctx_k = ex.submit(rag_context_cached,
            build_topic_query(topic="kp", dossier=dossier),
            ("bphs1.md", "kp3.md"), 8)
        ctx_p, ctx_t, ctx_k = f_ctx_p.result(), f_ctx_t.result(), f_ctx_k.result()

    # Run 3 AI agents concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f_p = executor.submit(agent_worker,
            build_agent_parashari_prompt(dossier, knowledge_context=ctx_p),
            [], FREE_MODELS[0], expert_rules)
        f_t = executor.submit(agent_worker,
            build_agent_timing_prompt(dossier, knowledge_context=ctx_t),
            [], FREE_MODELS[0], expert_rules)
        f_k = executor.submit(agent_worker,
            build_agent_kp_prompt(dossier, knowledge_context=ctx_k),
            [], FREE_MODELS[1], expert_rules)
        p_notes, t_notes, k_notes = f_p.result(), f_t.result(), f_k.result()

    final = build_master_synthesizer_prompt(dossier, p_notes, t_notes, k_notes)
    time_module.sleep(3)
    st.info("📖 Writing your full reading...")
    try:
        result = generate_content_with_fallback(final, knowledge_files=None)
    except Exception as e:
        result = (
            f"⚠️ Reading generation paused ({str(e)[:100]}). "
            "Your chart data was computed. Please try again in ~1 minute."
        )
    st.session_state[f"oracle_{_MISSION_KEY}_history"] = [
        {"role":"user",  "display":"🔮 Full Life Reading", "parts":[final]},
        {"role":"model", "display":result,                 "parts":[result]},
    ]
