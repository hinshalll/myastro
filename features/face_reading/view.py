"""features.face_reading.view — Streamlit page for Vedic Face Reading.

Works for ANY face (yourself, a friend, a photo). An OPTIONAL toggle links your
own birth chart to add the face-vs-chart cross-reference. One AI call per reading.
"""

import streamlit as st

from shared.astro.face_vision import analyze_face
from features.face_reading.vlm_reader import read_face
from features.face_reading.knowledge_lookup import get_face_context
from ui_streamlit.state import get_default_profile


_ELEMENT_EMOJI = {"earth": "🪨", "water": "💧", "fire": "🔥", "air": "🌬️", "ether": "✨"}


def _signals_card(metrics):
    fs = metrics.get("face_shape", {})
    z = metrics.get("zones", {})
    elem = fs.get("element", "")
    st.markdown("**Face Shape**")
    st.markdown(f"### {fs.get('primary','—').replace('_',' ').title()}  {_ELEMENT_EMOJI.get(elem,'')}")
    st.caption(f"Element: {elem.title()} · confidence {fs.get('confidence','')}")
    st.markdown("---")
    dom = (z.get("dominant", "") or "").replace("_", " ").title()
    st.markdown("**Dominant Zone**")
    st.markdown(f"### {dom or '—'}")
    st.caption("forehead = intellect · mid-face = drive · lower = will/appetite")


def _face_pdf(phase_b, name=""):
    try:
        from shared.pdf.astro_pdf import build_astro_pdf
        if not phase_b.strip():
            return None
        return build_astro_pdf(
            feature_title="Vedic Face Reading", feature_emoji="🔮",
            sections=[{"heading": "", "body": phase_b}],
            user_name=name, metadata={},
        )
    except Exception:
        return None


def _run_reading(analysis, use_kundli, dp):
    loading = st.empty()
    loading.markdown(
        """<div style="text-align:center;padding:2rem 0;color:rgba(200,190,220,0.85)">
        <style>@keyframes _sp{from{transform:rotate(0)}to{transform:rotate(360deg)}}</style>
        <div style="font-size:2.6rem;animation:_sp 3s linear infinite">🔮</div>
        <div style="margin-top:.8rem">Reading the face… 10–20 seconds</div></div>""",
        unsafe_allow_html=True,
    )
    dossier = ""
    if use_kundli and dp:
        try:
            from shared.astro.dossier_builder import generate_astrology_dossier
            dossier = generate_astrology_dossier(dp) or ""
        except Exception:
            dossier = ""

    knowledge_ctx = ""
    try:
        knowledge_ctx = get_face_context(
            analysis["metrics"], use_kundli=use_kundli, dossier=dossier
        ).get("formatted_block", "")
    except Exception:
        knowledge_ctx = ""

    result = read_face(
        enhanced_face=analysis["enhanced_face"],
        region_crops=analysis.get("region_crops") or {},
        metrics=analysis.get("metrics") or {},
        quality_metrics=analysis.get("quality_metrics") or {},
        pose_metrics=analysis.get("pose_metrics") or {},
        knowledge_context=knowledge_ctx,
        dossier=dossier,
        use_kundli=use_kundli,
    )
    loading.empty()
    st.session_state.face_reading = result


def _render_reading(result):
    if result.get("error"):
        st.error(result["error"]); return
    phase_a = result.get("phase_a", {}) or {}
    phase_b = (result.get("phase_b", "") or "").strip()
    if phase_a.get("image_quality") == "poor" or not phase_b:
        st.error("📷 " + (phase_a.get("image_issues") or "Photo not usable — try a clear, front-facing, well-lit shot."))
        return

    agree = phase_a.get("face_chart_agreement", "")
    if agree and agree != "cannot_assess":
        note = phase_a.get("face_chart_note", "")
        {"strong": st.success, "moderate": st.info, "weak": st.warning}.get(agree, st.info)(
            f"**Face & Chart: {agree.title()} agreement** — {note}")

    st.markdown(phase_b)

    with st.expander("🔍 What the AI actually saw", expanded=False):
        st.caption("Based only on what was clearly visible. Items marked not_assessable were skipped — that's honest, not a bug.")
        st.json(phase_a)

    pdf = _face_pdf(phase_b)
    c1, c2 = st.columns(2)
    with c1:
        if pdf:
            st.download_button("⬇ Download PDF", data=pdf, file_name="face_reading.pdf",
                               mime="application/pdf", use_container_width=True)
    with c2:
        if st.button("📷 Start Fresh", use_container_width=True):
            st.session_state.face_uploader_key = st.session_state.get("face_uploader_key", 0) + 1
            for k in ("face_reading", "face_analysis", "face_cache_key"):
                st.session_state.pop(k, None)
            st.rerun()


def show_face_reading():
    st.markdown("## 🔮 Face Reading")
    st.caption("Mukha Samudrika · Vedic face reading — works for any face")

    if "face_uploader_key" not in st.session_state:
        st.session_state.face_uploader_key = 0

    uploaded = st.file_uploader(
        "Upload a clear, front-facing face photo",
        type=["jpg", "jpeg", "png"],
        help="Look straight at the camera, even light, neutral expression, hair off the forehead, no glasses.",
        key=f"face_upload_{st.session_state.face_uploader_key}",
    )
    if uploaded is None:
        with st.expander("📷 How to take a good face photo", expanded=True):
            st.markdown(
                "- **Front-facing** — look straight at the camera\n"
                "- **Even daylight**, no harsh flash or side shadow\n"
                "- **Neutral expression**, mouth relaxed\n"
                "- **Hair off the forehead**, remove glasses\n"
                "- Face **fills most of the frame**"
            )
        return

    file_bytes = uploaded.getvalue()
    cache_key = uploaded.name + str(len(file_bytes))
    if st.session_state.get("face_cache_key") != cache_key or "face_analysis" not in st.session_state:
        with st.spinner("Analysing the face..."):
            st.session_state.face_analysis = analyze_face(file_bytes)
            st.session_state.face_cache_key = cache_key
            st.session_state.pop("face_reading", None)

    analysis = st.session_state.face_analysis
    if not analysis.get("face_found"):
        st.error("Couldn't detect a face. Re-upload a clear, front-facing photo.")
        return
    for issue in analysis.get("quality_issues", []):
        st.warning(issue)
    for issue in analysis.get("pose_issues", []):
        st.warning(issue)

    col_img, col_sig = st.columns([1, 1], gap="large")
    with col_img:
        st.image(analysis.get("landmark_overlay"), caption="Detected facial geometry", use_container_width=True)
    with col_sig:
        _signals_card(analysis["metrics"])

    st.divider()

    # Optional kundli cross-reference — only when reading YOUR OWN face with a saved chart.
    dp, _ = get_default_profile()
    use_kundli = False
    if dp:
        use_kundli = st.checkbox(
            "🔗 Link my birth chart (cross-reference my face with my kundli)",
            value=False,
            help="Only for reading your OWN face. Off = a pure face reading that works for anyone.",
        )
    else:
        st.caption("Tip: set a default profile in Saved Profiles to unlock the optional face-vs-chart cross-reference.")

    if "face_reading" not in st.session_state:
        st.session_state.face_reading = None

    if st.session_state.face_reading is None:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🔮 Reveal the Reading", type="primary", use_container_width=True):
                _run_reading(analysis, use_kundli, dp)
                st.rerun()
    else:
        _render_reading(st.session_state.face_reading)
