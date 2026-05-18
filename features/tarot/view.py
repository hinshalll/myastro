"""features.tarot.view — the Streamlit page for Mystic Tarot.

Imports business logic from features.tarot.service + features.tarot.prompts.
For shared UI helpers (tarot card overlay, AI streaming, RAG cache) it still
imports from ui_streamlit.components and ui_streamlit.cache — those live
outside the feature because every feature uses them.
"""

import time as time_module
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from features.tarot.constants import FULL_TAROT_DECK, CELTIC_CROSS_POSITIONS
from features.tarot.service import (
    draw_three, draw_one, draw_celtic_cross, get_birth_card,
)
from features.tarot.prompts import (
    build_three_card_prompt, build_yes_no_prompt,
    build_celtic_cross_prompt, build_birth_card_prompt,
)
from ui_streamlit.components import (
    render_tarot_overlay, stream_ai_with_followup, tarot_reversed_help,
)
from ui_streamlit.cache import rag_context_cached


def _tarot_pdf(title, metadata, chat_key):
    try:
        from ui_streamlit.views.astro_pdf import build_astro_pdf
        msgs = st.session_state.get(chat_key, [])
        reading = next((m.get("display") or (m.get("parts") or [""])[0]
                        for m in reversed(msgs) if m.get("role") == "model"), "")
        if not reading:
            return None
        return build_astro_pdf(
            feature_title=title, feature_emoji="♠",
            sections=[{"heading": "", "body": reading}],
            user_name="", metadata=metadata,
        )
    except Exception:
        return None


def show_tarot():
    components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
    st.markdown("<h1>🃏 Mystic Tarot</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,.6)'>Ask a question and consult the cards. Cryptographically secure randomisation.</p>", unsafe_allow_html=True)

    tab_choice = st.radio(
        "Mode",
        ["✦ Three-Card Spread", "☯ Yes / No Oracle", "🔮 Celtic Cross (10 Cards)", "🌟 Birth Card"],
        horizontal=True, key="tarot_mode_radio", label_visibility="collapsed",
    )

    # Reset transient state when the user flips modes
    if st.session_state.get("_last_tarot_tab", "") != tab_choice:
        st.session_state.tarot3_drawn = False; st.session_state.tarot3_cards = []
        st.session_state.tarot3_states = []; st.session_state.tarot3_mode = "General Guidance"
        st.session_state.yn_drawn = False; st.session_state.yn_card = None; st.session_state.yn_state = None
        st.session_state.cc_drawn = False; st.session_state.cc_cards = []; st.session_state.cc_states = []
        st.session_state.bc_revealed = False; st.session_state._last_tarot_tab = tab_choice

    st.markdown("---")

    # ── Three-Card Spread ────────────────────────────────────────────────
    if "Three-Card" in tab_choice:
        def on_mode_change():
            st.session_state.tarot3_drawn = False
            st.session_state.tarot3_cards = []
            st.session_state.tarot3_states = []

        spread_mode = st.radio(
            "Spread type",
            ["General Guidance", "Love & Dynamics", "Decision / Two Paths"],
            horizontal=True, key="t3_spread", label_visibility="collapsed", on_change=on_mode_change,
        )
        placeholder = {
            "General Guidance":     "e.g. What energy is around my career this month?",
            "Love & Dynamics":      "e.g. What should I know about my connection with...",
            "Decision / Two Paths": "e.g. Path A or Path B?",
        }[spread_mode]
        q = st.text_area("Your question", placeholder=placeholder, key="t3_q")
        rev = st.checkbox("Include Reversed Cards", key="t3_rev", help=tarot_reversed_help())

        if st.button("Draw 3 Cards", type="primary", use_container_width=True, key="draw3"):
            if not q.strip(): st.error("Ask a question first."); return
            with st.spinner("Shuffling..."): time_module.sleep(1.2)
            cards, states = draw_three(include_reversed=rev)
            st.session_state.tarot3_cards = cards
            st.session_state.tarot3_states = states
            st.session_state.tarot3_drawn = True
            st.session_state.tarot3_mode = spread_mode
            st.session_state.tarot3_chat = []

        if st.session_state.tarot3_drawn and st.session_state.tarot3_cards:
            render_tarot_overlay(st.session_state.tarot3_cards, st.session_state.tarot3_states, "three")
            st.markdown(f"**Cards:** {' · '.join(f'{c} ({s})' for c, s in zip(st.session_state.tarot3_cards, st.session_state.tarot3_states))}")
            cards_str = " ".join(st.session_state.tarot3_cards)
            states_str = " ".join(st.session_state.tarot3_states)
            tarot_ctx = rag_context_cached(
                f"{q} {cards_str} {states_str} tarot meaning",
                ("tguide.md",), k=8,
            )
            prompt = build_three_card_prompt(q, st.session_state.tarot3_cards,
                                              st.session_state.tarot3_states,
                                              st.session_state.tarot3_mode,
                                              knowledge_context=tarot_ctx)
            stream_ai_with_followup(prompt, "tarot3_chat", "Interpreting the cards...",
                                    knowledge_files=None, hide_user_prompt=True)
            pdf = _tarot_pdf("Three-Card Tarot Reading",
                {"Cards": " · ".join(f"{c} ({s})" for c, s in zip(
                    st.session_state.tarot3_cards, st.session_state.tarot3_states)),
                 "Spread": st.session_state.tarot3_mode}, "tarot3_chat")
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="tarot_three_card.pdf", mime="application/pdf", key="t3_pdf")
            if st.button("🔄 New Reading", key="reset3"):
                st.session_state.tarot3_drawn = False; st.session_state.tarot3_cards = []; st.rerun()

    # ── Yes / No Oracle ──────────────────────────────────────────────────
    elif "Yes / No" in tab_choice:
        q = st.text_input("Your yes/no question",
                          placeholder="e.g. Will this situation resolve in my favour?", key="yn_q")
        rev = st.checkbox("Include Reversed Cards", key="yn_rev", help=tarot_reversed_help())

        if st.button("Draw One Card", type="primary", use_container_width=True, key="draw_yn"):
            if not q.strip(): st.error("Ask a question."); return
            card, state = draw_one(include_reversed=rev)
            st.session_state.yn_card = card
            st.session_state.yn_state = state
            st.session_state.yn_drawn = True
            st.session_state.yn_chat = []

        if st.session_state.yn_drawn and st.session_state.yn_card:
            render_tarot_overlay([st.session_state.yn_card], [st.session_state.yn_state], "one")
            st.markdown(f"**Card:** {st.session_state.yn_card} ({st.session_state.yn_state})")
            yn_ctx = rag_context_cached(
                f"{q} {st.session_state.yn_card} {st.session_state.yn_state} tarot meaning upright reversed",
                ("tguide.md",), k=6,
            )
            stream_ai_with_followup(
                build_yes_no_prompt(q, st.session_state.yn_card, st.session_state.yn_state,
                                    knowledge_context=yn_ctx),
                "yn_chat", "Sensing the answer...",
                knowledge_files=None, hide_user_prompt=True,
            )
            pdf = _tarot_pdf("Yes / No Oracle",
                {"Card": f"{st.session_state.yn_card} ({st.session_state.yn_state})"}, "yn_chat")
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="tarot_yesno.pdf", mime="application/pdf", key="yn_pdf")
            if st.button("🔄 Ask Again", key="reset_yn"):
                st.session_state.yn_drawn = False; st.session_state.yn_card = None; st.rerun()

    # ── Celtic Cross ─────────────────────────────────────────────────────
    elif "Celtic Cross" in tab_choice:
        q = st.text_area("Your question (optional)",
                         placeholder="e.g. What do I need to know about the next chapter of my life?", key="cc_q")
        rev = st.checkbox("Include Reversed Cards", key="cc_rev", help=tarot_reversed_help())

        if st.button("Draw 10 Cards", type="primary", use_container_width=True, key="draw_cc"):
            with st.spinner("Laying out the Celtic Cross..."): time_module.sleep(1.5)
            cards, states = draw_celtic_cross(include_reversed=rev)
            st.session_state.cc_cards = cards
            st.session_state.cc_states = states
            st.session_state.cc_drawn = True
            st.session_state.cc_chat = []

        if st.session_state.cc_drawn and st.session_state.cc_cards:
            render_tarot_overlay(st.session_state.cc_cards, st.session_state.cc_states, "ten")
            for i, (c, s) in enumerate(zip(st.session_state.cc_cards, st.session_state.cc_states)):
                st.markdown(f"**{CELTIC_CROSS_POSITIONS[i]}:** {c} ({s})")
            cc_cards_str = " ".join(st.session_state.cc_cards)
            cc_ctx = rag_context_cached(
                f"{q or 'general life overview'} {cc_cards_str} celtic cross tarot spread",
                ("tguide.md",), k=10,
            )
            prompt = build_celtic_cross_prompt(q or "General life overview",
                                                st.session_state.cc_cards,
                                                st.session_state.cc_states,
                                                knowledge_context=cc_ctx)
            stream_ai_with_followup(prompt, "cc_chat", "Weaving the narrative...",
                                    knowledge_files=None, hide_user_prompt=True)
            pdf = _tarot_pdf("Celtic Cross Tarot Reading",
                {"Cards": ", ".join(st.session_state.cc_cards[:3]) + "..."}, "cc_chat")
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="tarot_celtic_cross.pdf", mime="application/pdf", key="cc_pdf")
            if st.button("🔄 New Celtic Cross", key="reset_cc"):
                st.session_state.cc_drawn = False; st.session_state.cc_cards = []; st.rerun()

    # ── Birth Card ───────────────────────────────────────────────────────
    elif "Birth Card" in tab_choice:
        st.markdown("#### Your Tarot Birth Card")
        st.caption("A permanent card determined by your date of birth — it represents your soul's archetype and lifelong theme.")
        bc_dob = st.date_input("Date of Birth", date(2000, 1, 1),
                               min_value=date(1850, 1, 1), max_value=date(2050, 12, 31),
                               key="bc_dob_input")

        if st.button("Reveal My Birth Card", type="primary", use_container_width=True, key="reveal_bc"):
            st.session_state.bc_dob = bc_dob
            st.session_state.bc_revealed = True
            st.session_state.bc_chat = []

        if st.session_state.bc_revealed and st.session_state.bc_dob:
            card = get_birth_card(st.session_state.bc_dob.isoformat())
            render_tarot_overlay([card], ["Upright"], "one")
            st.markdown(f"**Your Birth Card:** {card}")
            st.caption("This card never changes — it is your permanent soul archetype.")
            bc_ctx = rag_context_cached(
                f"{card} birth card tarot soul archetype lifelong meaning",
                ("tguide.md",), k=6,
            )
            stream_ai_with_followup(
                build_birth_card_prompt(card, str(st.session_state.bc_dob), knowledge_context=bc_ctx),
                "bc_chat", "Unlocking archetype...",
                knowledge_files=None, hide_user_prompt=True,
            )
            pdf = _tarot_pdf("Tarot Birth Card Reading",
                {"Birth Card": card, "Date of Birth": str(st.session_state.bc_dob)}, "bc_chat")
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="tarot_birth_card.pdf", mime="application/pdf", key="bc_pdf")
            if st.button("🔄 Check Another Date", key="reset_bc"):
                st.session_state.bc_revealed = False; st.rerun()
