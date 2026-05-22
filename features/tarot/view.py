"""features.tarot.view — the Streamlit page for Mystic Tarot.

Imports business logic from features.tarot.service + features.tarot.prompts.
For shared UI helpers (tarot card overlay, AI streaming, RAG cache) it still
imports from ui_streamlit.components and ui_streamlit.cache — those live
outside the feature because every feature uses them.

The three spread modes (Three-Card / Yes-No / Celtic Cross) use the interactive
picker: the backend shuffles a hidden 78-card deck, the user swipes and taps to
choose their own cards, then the reading reveals them. Birth Card is unchanged.
"""

import os
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from features.tarot.constants import CELTIC_CROSS_POSITIONS
from features.tarot.service import (
    create_draw_session, reveal_session, get_birth_card, TarotDrawError,
)
from features.tarot.prompts import (
    build_three_card_prompt, build_yes_no_prompt,
    build_celtic_cross_prompt, build_birth_card_prompt, three_card_roles,
)
from ui_streamlit.components import (
    render_tarot_overlay, stream_ai_with_followup, tarot_reversed_help,
)
from ui_streamlit.cache import rag_context_cached


# Declare the swipe-picker custom component once (serves features/tarot/picker/).
_PICKER = components.declare_component(
    "tarot_picker", path=os.path.join(os.path.dirname(__file__), "picker")
)


def tarot_picker(session: dict, nonce: int):
    """Render the face-down deck and return the user's picks (or None)."""
    return _PICKER(
        deck_size=session["deck_size"],
        pick_count=session["pick_count"],
        card_back_url=session["card_back_url"],
        session_id=str(nonce),
        key=f"picker_{session['spread']}_{nonce}",
        default=None,
    )


def _tarot_pdf(title, metadata, chat_key):
    try:
        from shared.pdf.astro_pdf import build_astro_pdf
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


def _ss(spread: str, key: str, default=None):
    """Per-spread session_state getter with a default."""
    return st.session_state.setdefault(f"{spread}_{key}", default)


def _reset_mode(spread: str):
    for k, v in (("phase", "ask"), ("session", None), ("picks", None),
                 ("cards", None), ("states", None)):
        st.session_state[f"{spread}_{k}"] = v
    st.session_state[f"{spread}_chat"] = []


def _run_picker_mode(spread: str, question: str, include_reversed: bool,
                     *, mode: str = "General Guidance", require_question: bool = True):
    """Shared shuffle → pick → reveal flow for a spread mode."""
    phase = _ss(spread, "phase", "ask")

    # ── Phase: ask — show the Shuffle button ─────────────────────────────────
    if phase == "ask":
        if st.button("🔀 Shuffle & Pick Your Cards", type="primary",
                     use_container_width=True, key=f"{spread}_shuffle"):
            if require_question and not question.strip():
                st.error("Ask a question first.")
                return
            try:
                session = create_draw_session(spread, include_reversed=include_reversed)
            except TarotDrawError as e:
                st.error(str(e)); return
            session["spread"] = spread
            st.session_state[f"{spread}_session"] = session
            st.session_state[f"{spread}_nonce"] = _ss(spread, "nonce", 0) + 1
            st.session_state[f"{spread}_q"] = question
            st.session_state[f"{spread}_mode"] = mode
            st.session_state[f"{spread}_picks"] = None
            st.session_state[f"{spread}_chat"] = []
            st.session_state[f"{spread}_phase"] = "pick"
            st.rerun()
        return

    # ── Phase: pick — show the swipeable deck ────────────────────────────────
    if phase == "pick":
        session = _ss(spread, "session")
        st.caption(f"Tap **{session['pick_count']}** card(s) from the deck below — "
                   "swipe to browse, tap to choose, then **Reveal**.")
        picks = tarot_picker(session, _ss(spread, "nonce", 0))
        if isinstance(picks, list) and len(picks) == session["pick_count"]:
            try:
                drawn = reveal_session(session["token"], picks)
            except TarotDrawError as e:
                st.error(str(e))
                if st.button("Reshuffle", key=f"{spread}_reshuf_err"):
                    _reset_mode(spread); st.rerun()
                return
            st.session_state[f"{spread}_cards"] = drawn["cards"]
            st.session_state[f"{spread}_states"] = drawn["states"]
            st.session_state[f"{spread}_picks"] = picks
            st.session_state[f"{spread}_phase"] = "reveal"
            st.rerun()
        if st.button("↩ Reshuffle", key=f"{spread}_reshuffle"):
            _reset_mode(spread); st.rerun()
        return

    # ── Phase: reveal — flip cards + stream the reading ──────────────────────
    cards = _ss(spread, "cards") or []
    states = _ss(spread, "states") or []
    q = _ss(spread, "q", "")
    return cards, states, q


# ── Public entry point ─────────────────────────────────────────────────────────

def show_tarot():
    components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
    st.markdown("<h1>🃏 Mystic Tarot</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,.6)'>Ask a question, then pick your own cards from the shuffled deck. Cryptographically secure shuffle.</p>", unsafe_allow_html=True)

    tab_choice = st.radio(
        "Mode",
        ["✦ Three-Card Spread", "☯ Yes / No Oracle", "🔮 Celtic Cross (10 Cards)", "🌟 Birth Card"],
        horizontal=True, key="tarot_mode_radio", label_visibility="collapsed",
    )

    # Reset transient state when the user flips modes
    if st.session_state.get("_last_tarot_tab", "") != tab_choice:
        for sp in ("three", "yes_no", "celtic"):
            _reset_mode(sp)
        st.session_state.bc_revealed = False
        st.session_state._last_tarot_tab = tab_choice

    st.markdown("---")

    # ── Three-Card Spread ────────────────────────────────────────────────
    if "Three-Card" in tab_choice:
        def on_mode_change():
            _reset_mode("three")

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

        result = _run_picker_mode("three", q, rev, mode=spread_mode)
        if result:
            cards, states, q_used = result
            roles = three_card_roles(_ss("three", "mode", spread_mode))
            render_tarot_overlay(cards, states, "three")
            for i, (c, s) in enumerate(zip(cards, states)):
                st.markdown(f"**{roles[i]}:** {c} ({s})")
            tarot_ctx = rag_context_cached(
                f"{q_used} {' '.join(cards)} {' '.join(states)} tarot meaning",
                ("tguide.md",), k=8,
            )
            prompt = build_three_card_prompt(q_used, cards, states,
                                             _ss("three", "mode", spread_mode),
                                             knowledge_context=tarot_ctx)
            stream_ai_with_followup(prompt, "three_chat", "Interpreting the cards...",
                                    knowledge_files=None, hide_user_prompt=True)
            pdf = _tarot_pdf("Three-Card Tarot Reading",
                {"Cards": " · ".join(f"{c} ({s})" for c, s in zip(cards, states)),
                 "Spread": _ss("three", "mode", spread_mode)}, "three_chat")
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="tarot_three_card.pdf", mime="application/pdf", key="t3_pdf")
            if st.button("🔄 New Reading", key="reset3"):
                _reset_mode("three"); st.rerun()

    # ── Yes / No Oracle ──────────────────────────────────────────────────
    elif "Yes / No" in tab_choice:
        q = st.text_input("Your yes/no question",
                          placeholder="e.g. Will this situation resolve in my favour?", key="yn_q")
        rev = st.checkbox("Include Reversed Cards", key="yn_rev", help=tarot_reversed_help())

        result = _run_picker_mode("yes_no", q, rev)
        if result:
            cards, states, q_used = result
            render_tarot_overlay(cards, states, "one")
            st.markdown(f"**Card:** {cards[0]} ({states[0]})")
            yn_ctx = rag_context_cached(
                f"{q_used} {cards[0]} {states[0]} tarot meaning upright reversed",
                ("tguide.md",), k=6,
            )
            stream_ai_with_followup(
                build_yes_no_prompt(q_used, cards[0], states[0], knowledge_context=yn_ctx),
                "yes_no_chat", "Sensing the answer...",
                knowledge_files=None, hide_user_prompt=True,
            )
            pdf = _tarot_pdf("Yes / No Oracle",
                {"Card": f"{cards[0]} ({states[0]})"}, "yes_no_chat")
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="tarot_yesno.pdf", mime="application/pdf", key="yn_pdf")
            if st.button("🔄 Ask Again", key="reset_yn"):
                _reset_mode("yes_no"); st.rerun()

    # ── Celtic Cross ─────────────────────────────────────────────────────
    elif "Celtic Cross" in tab_choice:
        q = st.text_area("Your question (optional)",
                         placeholder="e.g. What do I need to know about the next chapter of my life?", key="cc_q")
        rev = st.checkbox("Include Reversed Cards", key="cc_rev", help=tarot_reversed_help())

        result = _run_picker_mode("celtic", q, rev, require_question=False)
        if result:
            cards, states, q_used = result
            render_tarot_overlay(cards, states, "ten")
            for i, (c, s) in enumerate(zip(cards, states)):
                st.markdown(f"**{CELTIC_CROSS_POSITIONS[i]}:** {c} ({s})")
            cc_ctx = rag_context_cached(
                f"{q_used or 'general life overview'} {' '.join(cards)} celtic cross tarot spread",
                ("tguide.md",), k=10,
            )
            prompt = build_celtic_cross_prompt(q_used or "General life overview",
                                               cards, states, knowledge_context=cc_ctx)
            stream_ai_with_followup(prompt, "celtic_chat", "Weaving the narrative...",
                                    knowledge_files=None, hide_user_prompt=True)
            pdf = _tarot_pdf("Celtic Cross Tarot Reading",
                {"Cards": ", ".join(cards[:3]) + "..."}, "celtic_chat")
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="tarot_celtic_cross.pdf", mime="application/pdf", key="cc_pdf")
            if st.button("🔄 New Celtic Cross", key="reset_cc"):
                _reset_mode("celtic"); st.rerun()

    # ── Birth Card (unchanged — deterministic from DOB, Major Arcana only) ─
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

        if st.session_state.get("bc_revealed") and st.session_state.get("bc_dob"):
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
