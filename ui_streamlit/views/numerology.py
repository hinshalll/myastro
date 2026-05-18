"""
ui_streamlit/pages/numerology.py
"""

from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from math_engine.constants import PERSONAL_YEAR_MEANINGS
from math_engine.astro_calc import (
    calculate_numerology_core, get_personal_year, get_personal_month,
    get_personal_day, get_pinnacle_cycles,
)
from math_engine.dossier_builder import generate_astrology_dossier
from ai_engine.prompts import build_numerology_prompt

from ui_streamlit.state import get_default_profile
from ui_streamlit.helpers import get_local_today
from ui_streamlit.components import render_profile_form, resolve_profile, stream_ai_with_followup
from ui_streamlit.cache import rag_context_cached


def _num_pdf(title, user_name, metadata, chat_key):
    """Build PDF from last AI message in the given chat key."""
    try:
        from ui_streamlit.views.astro_pdf import build_astro_pdf
        msgs = st.session_state.get(chat_key, [])
        reading = next((m.get("display") or (m.get("parts") or [""])[0]
                        for m in reversed(msgs) if m.get("role") == "model"), "")
        if not reading:
            return None
        return build_astro_pdf(
            feature_title=title, feature_emoji="♦",
            sections=[{"heading": "", "body": reading}],
            user_name=user_name, metadata=metadata,
        )
    except Exception:
        return None


def show_numerology():
    components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
    st.markdown("<h1>🔢 Numerology</h1>", unsafe_allow_html=True)

    dp, _ = get_default_profile()
    tab1, tab2 = st.tabs(["📊 Full Report", "⭕ Personal Cycles & Pinnacles"])

    # ── Full Report ───────────────────────────────────────────────────────────
    with tab1:
        system = st.radio("System", ["Western (Pythagorean)","Indian/Vedic (Chaldean)"],
                          horizontal=True, key="num_sys")
        if "Chaldean" in system:
            st.caption("ℹ️ Chaldean system — authentic ancient tradition. Number 9 is sacred and not assigned to letters.")

        mode     = st.radio("Mode", ["Full Report","Ask a Question"], horizontal=True, key="num_mode")
        question = ""
        if mode == "Ask a Question":
            question = st.text_area("Your question", key="num_q", placeholder="e.g. When will my career take off?")

        use_astro = st.checkbox("🌌 Cross-validate with Vedic Kundli (maximum accuracy)", key="num_use_astro")

        if use_astro:
            st.info("Name and DOB from the astrological profile will be used for numerology.")
            item = render_profile_form("num_prof", show_d60=True)
        else:
            c1, c2 = st.columns(2)
            with c1:
                num_name = st.text_input("Full Birth Name", value=dp["name"] if dp else "", key="num_name")
            with c2:
                pre_dob  = date.fromisoformat(dp["date"]) if dp else date(2000, 1, 1)
                num_dob  = st.date_input("Date of Birth", pre_dob, min_value=date(1850,1,1), max_value=date(2050,12,31), key="num_dob")

        if st.button("Generate Numerology Report ✨", type="primary", use_container_width=True):
            if use_astro:
                if item["type"] == "empty_saved": st.error("Select a saved profile."); return
                prof, d60 = resolve_profile(item)
                name = prof["name"]; dob_str = prof["date"]
            else:
                if not num_name.strip(): st.error("Enter your name."); return
                name = num_name.strip(); dob_str = num_dob.isoformat()
                prof = None; d60 = False

            with st.spinner("Computing numbers..."):
                lp, dest, soul, pers = calculate_numerology_core(name, dob_str, system)
                dossier = generate_astrology_dossier(prof, d60) if use_astro and prof else None
                # Pre-fetch RAG context for the specific numbers
                num_books = ("inum1.md",) if "Vedic" in system else ("wnum.md",)
                num_ctx = rag_context_cached(
                    f"life path {lp} destiny {dest} soul urge {soul} personality {pers} numerology meaning",
                    num_books, k=10
                )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Life Path",  f"{lp}{'★'   if lp   in [11,22,33] else ''}")
            c2.metric("Destiny",    f"{dest}{'★'  if dest in [11,22,33] else ''}")
            c3.metric("Soul Urge",  f"{soul}{'★'  if soul in [11,22,33] else ''}")
            c4.metric("Personality",f"{pers}{'★'  if pers in [11,22,33] else ''}")

            st.session_state.num_prompt = build_numerology_prompt(name, dob_str, lp, dest, soul, pers, dossier, question, system, knowledge_context=num_ctx)
            st.session_state.num_chat   = []
            st.session_state.num_lp     = lp

        if "num_prompt" in st.session_state:
            # Prompt was already built with RAG context baked in on first click
            # (see line above setting num_prompt). Do NOT re-fetch RAG here.
            stream_ai_with_followup(st.session_state.num_prompt, "num_chat",
                                    "Analysing your numbers...", knowledge_files=None,
                                    hide_user_prompt=True)
            pdf = _num_pdf(
                f"Numerology Report ({system.split('(')[0].strip()})",
                (dp["name"] if dp else ""),
                {"Life Path": str(st.session_state.get("num_lp","?")),
                 "System": system.split("(")[0].strip()},
                "num_chat",
            )
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="numerology_report.pdf", mime="application/pdf", key="num_pdf_btn")

    # ── Personal Cycles & Pinnacles ───────────────────────────────────────────
    with tab2:
        st.markdown("#### Personal Cycles & Pinnacle Challenges")
        st.caption("Understand the numerical timing of your life phases — including the obstacles built into each cycle.")
        sys3 = st.radio("System", ["Western (Pythagorean)","Indian/Vedic (Chaldean)"],
                         horizontal=True, key="cyc_sys")
        c1, c2 = st.columns(2)
        with c1:
            cyc_name = st.text_input("Full Birth Name", value=dp["name"] if dp else "", key="cyc_name")
        with c2:
            pre_dob2 = date.fromisoformat(dp["date"]) if dp else date(2000, 1, 1)
            cyc_dob  = st.date_input("Date of Birth", pre_dob2, min_value=date(1850,1,1), max_value=date(2050,12,31), key="cyc_dob")

        if st.button("Show My Cycles ✨", type="primary", use_container_width=True):
            if not cyc_name.strip(): st.error("Enter your name."); return
            lp, _, _, _ = calculate_numerology_core(cyc_name.strip(), cyc_dob.isoformat(), sys3)
            user_tz = dp["tz"] if dp else "Asia/Kolkata"
            py  = get_personal_year(cyc_dob.isoformat())
            pm  = get_personal_month(cyc_dob.isoformat(), user_tz)
            pd  = get_personal_day(cyc_dob.isoformat(), user_tz)
            r1, r2, r3, r4 = get_pinnacle_cycles(cyc_dob.isoformat())
            y       = cyc_dob.year
            cur_age = get_local_today(user_tz).year - y

            st.markdown("#### Your Timing Numbers Today")
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Personal Year {get_local_today(user_tz).year}", str(py))
            c1.caption(PERSONAL_YEAR_MEANINGS.get(py, ""))
            c2.metric("Personal Month", str(pm))
            c3.metric("Personal Day",   str(pd))

            challenge_meanings = {
                1:"Master your need for control and ego.",
                2:"Overcome fear of confrontation and indecision.",
                3:"Build self-discipline to channel your emotions.",
                4:"Learn to work within limitations patiently.",
                5:"Ground your need for constant change and freedom.",
                6:"Release perfectionism and learn to receive.",
                7:"Trust yourself without constant external validation.",
                8:"Balance material ambition with spiritual values.",
                9:"Complete cycles; resist clinging to the past.",
                0:"Own your spiritual sensitivity as a gift.",
            }

            st.markdown("#### Pinnacle Cycles & Challenges")
            for i, (s, e, n, c) in enumerate([r1, r2, r3, r4], 1):
                is_curr = s - y <= cur_age < e - y
                badge = "◀ YOU ARE HERE" if is_curr else ""
                col   = st.container(border=True)
                badge_html = f"<span style='color:#c09040'>{badge}</span>" if badge else ""
                col.markdown(f"**Pinnacle {i}** (Ages {s-y}–{e-y if e-y < 100 else '∞'}) &nbsp; {badge_html}", unsafe_allow_html=True)
                col.write(f"**Pinnacle Number: {n}** — {PERSONAL_YEAR_MEANINGS.get(n,'')}")
                col.write(f"**Challenge Number: {c}** — {challenge_meanings.get(c, 'Master this cycle.')}")

            is_vedic = "Vedic" in sys3
            prompt = f"""<instructions>
You are a Master Numerologist — {'Chaldean (Indian/Vedic)' if is_vedic else 'Pythagorean (Western)'} system.
All numbers below are PRE-COMPUTED and LOCKED. Do NOT recalculate.
</instructions>
<numerology_data>
Subject: {cyc_name.strip()} | DOB: {cyc_dob.isoformat()} | Life Path: {lp}
Personal Year: {py} — {PERSONAL_YEAR_MEANINGS.get(py,'')}
Personal Month: {pm} | Personal Day: {pd}
Pinnacle 1 (Ages {r1[0]-y}–{r1[1]-y}): Number {r1[2]} | Challenge: {r1[3]}
Pinnacle 2 (Ages {r2[0]-y}–{r2[1]-y}): Number {r2[2]} | Challenge: {r2[3]}
Pinnacle 3 (Ages {r3[0]-y}–{r3[1]-y}): Number {r3[2]} | Challenge: {r3[3]}
Pinnacle 4 (Ages {r4[0]-y}+): Number {r4[2]} | Challenge: {r4[3]}
</numerology_data>
<mission>
Explain:
1. Current Personal Year energy and what it means for the next 12 months
2. Personal Month and Day energy — what to focus on right now
3. The currently active Pinnacle Number and its life theme
4. The currently active Challenge Number — what specific obstacle is the universe asking you to master?
5. How the Pinnacle and Challenge work together as a push-pull dynamic
</mission>"""
            st.session_state.cyc_prompt   = prompt
            st.session_state.cyc_chat     = []
            st.session_state.cyc_name_val = cyc_name.strip()

        if "cyc_prompt" in st.session_state:
            cyc_sys_val = st.session_state.get("cyc_sys", "Western (Pythagorean)")
            cyc_books = ("inum1.md",) if "Vedic" in cyc_sys_val else ("wnum.md",)
            cyc_ctx = rag_context_cached(
                "personal year pinnacle challenge cycle numerology life path meaning",
                cyc_books, k=8,
            )
            cyc_prompt = st.session_state.cyc_prompt
            if cyc_ctx:
                cyc_prompt = (
                    f"<KNOWLEDGE_CONTEXT>\n{cyc_ctx}\n</KNOWLEDGE_CONTEXT>\n"
                    "<RULES>Use only the numerology passages above for cycle/pinnacle/challenge "
                    "doctrine. Do not invent meanings outside them.</RULES>\n\n"
                    + cyc_prompt
                )
            stream_ai_with_followup(
                cyc_prompt, "cyc_chat",
                "Interpreting life cycles...", knowledge_files=None,
                hide_user_prompt=True,
            )
            pdf = _num_pdf(
                "Numerology Cycles & Pinnacles",
                (dp["name"] if dp else ""),
                {"Name": st.session_state.get("cyc_name_val",""),
                 "System": sys3.split("(")[0].strip()},
                "cyc_chat",
            )
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="numerology_cycles.pdf", mime="application/pdf", key="cyc_pdf_btn")
