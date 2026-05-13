"""
ui_streamlit/views/kundli.py
============================

Streamlit view for the premium Kundli PDF feature.

Flow:
    1. Profile picker (reuses existing wizard).
    2. Chart style picker (North / South / East Indian).
    3. Theme picker (Ganesha / Krishna / Shiva / Durga / Lakshmi / Saraswati
                     / Classic Vedic / Royal Gold).
    4. Language picker (en / hi / ta / te / mr / bn / gu).
    5. Optional toggles (Western appendix, BTR if exact_time=False).
    6. Generate → returns HTML (today) or PDF (after GTK3 install).

Thin shim — all heavy lifting lives in math_engine.kundli + pdf_engine.
When the mobile app ships, the equivalent layer there just imports the
same backend and calls build_kundli_pdf().
"""

import streamlit as st
import base64
from datetime import datetime

from math_engine.kundli import BirthData, compute_chart
from pdf_engine import build_kundli_pdf
from pdf_engine.builder import THEMES

from ui_streamlit.components import render_profile_form, resolve_profile


CHART_STYLES = [
    ("north_indian", "🪔 North Indian (Diamond)",
     "Lagna at the top center; signs rotate clockwise. Most common in North & Central India."),
    ("south_indian", "🛕 South Indian (Square)",
     "Fixed sign positions; planets move. Most common in Tamil Nadu, Karnataka, Andhra & Kerala."),
    ("east_indian", "🌺 East Indian (Bengali)",
     "Variation of South with corner diamonds. Common in Bengal & Odisha."),
]

LANGUAGES = [
    ("en", "English"),
    ("hi", "हिन्दी (Hindi)"),
    ("ta", "தமிழ் (Tamil)"),
    ("te", "తెలుగు (Telugu)"),
    ("mr", "मराठी (Marathi)"),
    ("bn", "বাংলা (Bengali)"),
    ("gu", "ગુજરાતી (Gujarati)"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Pretty theme cards
# ─────────────────────────────────────────────────────────────────────────────

def _theme_card(slug: str, theme: dict, selected: bool) -> str:
    border = f"3px solid {theme['accent']}" if selected else f"1px solid {theme['muted']}"
    return f"""
    <div style="
      border: {border};
      border-radius: 12px;
      padding: 14px 16px;
      background: {theme['paper']};
      color: {theme['ink']};
      margin: 4px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    ">
      <div style="font-family: 'Cinzel', serif; font-size: 1.1rem;
                  color: {theme['primary']}; letter-spacing: 0.08em;">
        {theme['name']}
      </div>
      <div style="font-style: italic; font-size: 0.85rem; color: {theme['muted']}; margin-top: 4px;">
        {theme.get('cover_subtitle', '')}
      </div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# Main view
# ─────────────────────────────────────────────────────────────────────────────

def show_kundli():
    st.markdown("""
    <div style="text-align:center; margin: 0.5rem 0 1.5rem;">
      <h1 style="font-family: 'Cinzel', serif; letter-spacing: 0.1em; margin-bottom: 0;
                 color: #D4AF37;">📜 Janma Kundli</h1>
      <p style="opacity: 0.7; margin-top: 4px;">
        Premium Vedic birth chart — 60-80 pages, beautifully themed, 100% computed,
        personalised to you.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Step 1: Profile ────────────────────────────────────────────────────
    st.markdown("### Step 1 · Whose chart?")
    pi = render_profile_form("kundli", show_d60=False)
    if pi["type"] == "empty_saved":
        st.info("Enter or select a profile above to continue.")
        return
    # resolve_profile validates and persists; safe to call only after submit
    # so we defer it to the Generate handler below.

    st.markdown("---")

    # ── Step 2: Chart style ────────────────────────────────────────────────
    st.markdown("### Step 2 · Chart style")
    cs_cols = st.columns(3)
    chart_style = st.session_state.get("kundli_chart_style", "north_indian")
    for col, (slug, label, desc) in zip(cs_cols, CHART_STYLES):
        with col:
            is_sel = chart_style == slug
            if st.button(label, key=f"cs_{slug}",
                         type="primary" if is_sel else "secondary",
                         use_container_width=True):
                st.session_state.kundli_chart_style = slug
                st.rerun()
            st.caption(desc)
    chart_style = st.session_state.get("kundli_chart_style", "north_indian")

    st.markdown("---")

    # ── Step 3: Theme ──────────────────────────────────────────────────────
    st.markdown("### Step 3 · Theme")
    st.caption("Each theme deeply integrates a Hindu deity tradition. The "
               "math is identical — the visual story changes.")
    selected_theme = st.session_state.get("kundli_theme", "classic_vedic")

    cols = st.columns(4)
    theme_slugs = list(THEMES.keys())
    for i, slug in enumerate(theme_slugs):
        with cols[i % 4]:
            theme = THEMES[slug]
            st.markdown(_theme_card(slug, theme, slug == selected_theme),
                        unsafe_allow_html=True)
            if st.button("Select" if slug != selected_theme else "✓ Selected",
                         key=f"theme_{slug}",
                         type="primary" if slug == selected_theme else "secondary",
                         use_container_width=True):
                st.session_state.kundli_theme = slug
                st.rerun()

    st.markdown("---")

    # ── Step 4: Language + options ─────────────────────────────────────────
    st.markdown("### Step 4 · Language & options")
    c1, c2 = st.columns([2, 1])
    with c1:
        lang_codes = [code for code, _label in LANGUAGES]
        lang_labels = [label for _code, label in LANGUAGES]
        lang_idx = lang_codes.index(st.session_state.get("kundli_lang", "en"))
        new_lang = st.selectbox("Generation language",
                                lang_labels, index=lang_idx,
                                help="Static interpretation text + section "
                                     "headers. Math is language-neutral.")
        st.session_state.kundli_lang = lang_codes[lang_labels.index(new_lang)]
    with c2:
        st.session_state.kundli_western = st.checkbox(
            "Include Western Appendix", value=True,
            help="A 2-3 page appendix with tropical positions, "
                 "Sun/Moon/Rising sign, and Ptolemaic aspects.")
        st.session_state.kundli_ai = st.checkbox(
            "Include AI narrative", value=True,
            help="Adds the 'Karmic Story' and decade-by-decade prediction "
                 "pages. One batched Gemini call (~₹5 budget).")

    # BTR offer note (the actual UI ships in a later pass; visible only
    # when the user marked exact_time = False in the form above).
    if pi.get("type") == "saved" and pi.get("data", {}).get("exact_time") is False:
        st.info("Birth time is marked as approximate. Birth-time rectification "
                "is available — provide 3–5 major life events and the algorithm "
                "will suggest a small adjustment that best fits your events. "
                "(Rectification UI ships in the next iteration.)")

    st.markdown("---")

    # ── Step 5: Generate ───────────────────────────────────────────────────
    st.markdown("### Step 5 · Generate")
    gen_col, info_col = st.columns([1, 2])
    with gen_col:
        do_generate = st.button("🪔 Generate Kundli",
                                type="primary", use_container_width=True)
    with info_col:
        st.caption("Free during prototyping. In the mobile app this is a "
                   "paid premium feature (~₹499).")

    if not do_generate:
        return

    # ── Compute + render ───────────────────────────────────────────────────
    with st.spinner("Computing chart & rendering 60-80 page kundli…"):
        try:
            profile, _ = resolve_profile(pi)
            bd = BirthData.from_profile(profile)
            chart = compute_chart(bd)
            data = build_kundli_pdf(
                chart,
                theme_name=st.session_state.get("kundli_theme", "classic_vedic"),
                chart_style=chart_style,
                language=st.session_state.get("kundli_lang", "en"),
                include_western_appendix=st.session_state.get("kundli_western", True),
                include_ai_narrative=st.session_state.get("kundli_ai", True),
            )
        except Exception as e:
            st.error(f"Generation failed: {type(e).__name__}: {e}")
            return

    is_pdf = data[:4] == b"%PDF"
    ext = "pdf" if is_pdf else "html"
    fname = f"{profile['name'].replace(' ','_')}_Kundli.{ext}"
    mime = "application/pdf" if is_pdf else "text/html"

    st.success(f"Kundli generated ({len(data):,} bytes).")
    if not is_pdf:
        st.warning(
            "PDF requires WeasyPrint + GTK3 runtime — on Windows install GTK3 from "
            "https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases. "
            "Until then you get the rendered HTML — open in any browser and use 'Print → "
            "Save as PDF' for an identical result."
        )
    st.download_button(
        f"⬇️ Download {ext.upper()}",
        data=data,
        file_name=fname,
        mime=mime,
        use_container_width=True,
    )

    # Inline preview for the HTML case (so the user can verify design fast)
    if not is_pdf:
        with st.expander("Preview (rendered HTML, first 2 pages-worth)", expanded=False):
            preview = data.decode("utf-8", errors="ignore")
            b64 = base64.b64encode(preview.encode("utf-8")).decode("ascii")
            st.markdown(
                f'<iframe src="data:text/html;base64,{b64}" '
                f'style="width:100%;height:720px;border:1px solid #444;border-radius:8px;"></iframe>',
                unsafe_allow_html=True,
            )
