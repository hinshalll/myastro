"""
ui_streamlit/views/consultation.py — "Ask the Astrologer" open chat.

This view is the consultation room. The accuracy of every reply here depends
on three layers cooperating:

  1. shared.astro.dossier_builder.generate_astrology_dossier — produces the
     full chart dossier including the EVENT TIMING ATLAS (lifetime dasha
     sequence + per-event activation windows + karaka maturation ages).
     The Atlas is the answer-source for "at what age will I X" questions.

  2. shared.ai.prompts.build_consultation_prompt — composes the consultation
     system prompt with an intent-specific framework overlay. The base prompt
     enforces "answer first, warmth second", forbids fatalistic claims, and
     mandates that timing questions ALWAYS get an age window from the Atlas.
     The overlay tells the AI HOW to read this specific class of question.

  3. shared.ai.gemini_client.get_ai_model_by_name — picks temperature 0.5
     when the system rules contain the word "conversational" (which the new
     consultation prompt does). That's what makes the chat actually
     conversational instead of robotic-evasive.
"""

import time as time_module
import streamlit as st
import streamlit.components.v1 as components

from shared.astro.dossier_builder import generate_astrology_dossier, get_gochara_overlay
from shared.ai.gemini_client import FREE_MODELS, get_ai_model_by_name
from shared.ai import config

from features.consultation.prompts import classify_intent, build_prompt
from features.consultation.service import INTENT_RAG_BOOKS

from ui_streamlit.state import get_default_profile
from ui_streamlit.cache import rag_context_cached


def show_consultation_room():
    components.html(
        """<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""",
        height=0, width=0,
    )
    st.markdown("<h1>💬 Ask the Astrologer</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,.6)'>Have a free-flowing conversation about your chart.</p>",
        unsafe_allow_html=True,
    )

    dp, _ = get_default_profile()
    if not dp:
        st.warning(
            "Please set a ⭐ default profile in 'Saved Profiles' first so the "
            "Astrologer knows who to look at."
        )
        return

    # Chart-loading verification — show the user exactly which chart is loaded
    # so any "is it even seeing my chart" doubts get resolved before the chat
    # starts. Birth date + time + place is enough to disambiguate.
    verify_bits = [f"**{dp['name']}**"]
    if dp.get("date"): verify_bits.append(f"born {dp['date']}")
    if dp.get("time"): verify_bits.append(f"at {dp['time']}")
    if dp.get("place"): verify_bits.append(f"in {dp['place']}")
    st.success("The Astrologer is currently looking at the chart for " + ", ".join(verify_bits) + ".")

    memory_key = f"v2_chat_{dp['name']}"
    if memory_key not in st.session_state:
        st.session_state[memory_key] = []

    for msg in st.session_state[memory_key]:
        with st.chat_message("assistant" if msg["role"] == "model" else "user"):
            st.markdown(msg["display"])

    if q := st.chat_input("Ask anything..."):
        st.chat_message("user").markdown(q)
        with st.chat_message("assistant"):
            res_ph = st.empty()
            with st.spinner("Consulting books..."):
                # 1. Build the dossier (now includes EVENT TIMING ATLAS).
                dos      = generate_astrology_dossier(dp)
                transits = get_gochara_overlay(dp)

                # 2. Classify intent and compose the system prompt with overlay.
                intent          = classify_intent(q)
                system_prompt   = build_prompt(intent)

                # 3. RAG retrieval — book set picked by intent. Falls back to
                #    the broad htrh set if Qdrant has trouble.
                rag_books = INTENT_RAG_BOOKS.get(intent, INTENT_RAG_BOOKS["GENERAL"])
                try:
                    consult_ctx = rag_context_cached(q, rag_books, k=8)
                except Exception:
                    consult_ctx = ""

                # 4. Conversation history — last 4 turns kept for continuity.
                hist_text = ""
                is_first_turn = not st.session_state[memory_key]
                if st.session_state[memory_key]:
                    last_few = st.session_state[memory_key][-4:]
                    hist_text = "\n\nRECENT CONVERSATION:\n" + "\n".join(
                        f"{'User' if m['role']=='user' else 'Astrologer'}: {m['display']}"
                        for m in last_few
                    )

                # 5. Turn-style hint (first reply vs follow-up) — affects the
                #    AI's choice of opener per the STYLE_RULES in the system prompt.
                turn_hint = (
                    "TURN_TYPE: FIRST_REPLY — you MAY use a brief warm opener "
                    "naming the user once, then go to the answer."
                    if is_first_turn else
                    "TURN_TYPE: FOLLOW_UP — the user has already been greeted "
                    "in this session. Do NOT open with 'Hello [name]…'. "
                    "Start with the answer directly."
                )

                full_prompt = (
                    f"{turn_hint}\n\n"
                    f"DETECTED_INTENT: {intent}\n\n"
                    f"BIRTH CHART DOSSIER FOR {dp['name']}:\n{dos}\n\n"
                    f"TODAY'S LIVE TRANSITS:\n{transits}"
                    f"{hist_text}\n\n"
                    f"USER QUESTION: {q}"
                )

                consult_content = [consult_ctx, full_prompt] if consult_ctx else [full_prompt]

                # 6. Model call with fallback ladder.
                full_txt = ""
                success  = False
                _chat = config.model_for("chat")
                for m_id in [_chat] + [m for m in FREE_MODELS if m != _chat]:
                    if success: break
                    for attempt in range(3):
                        try:
                            model    = get_ai_model_by_name(
                                m_id, custom_system_rules=system_prompt
                            )
                            response = model.generate_content(consult_content, stream=True)
                            for chunk in response:
                                full_txt += chunk.text
                                res_ph.markdown(full_txt + "▌")
                            res_ph.markdown(full_txt)
                            success = True
                            break
                        except Exception as e:
                            err = str(e)
                            is_rate     = any(x in err for x in ["429", "quota", "RESOURCE_EXHAUSTED", "rate limit"])
                            is_overflow = any(x in err for x in ["400", "InvalidArgument", "token count exceeds", "maximum number of tokens"])
                            if is_overflow: break
                            elif is_rate and attempt < 2: time_module.sleep((2 ** attempt) * 3)
                            else: break

                if not success:
                    res_ph.warning("⏳ Models are briefly at capacity. Please try again in a moment.")
                    return

                st.session_state[memory_key].append({"role": "user",  "display": q,        "internal": q})
                st.session_state[memory_key].append({"role": "model", "display": full_txt, "internal": full_txt})

                # 7. PDF download of this response.
                try:
                    from shared.pdf.astro_pdf import build_astro_pdf
                    import datetime
                    pdf = build_astro_pdf(
                        feature_title = "Consultation Reading",
                        feature_emoji = "♋",
                        sections      = [
                            {"heading": "Your Question", "body": q},
                            {"heading": "The Astrologer's Answer", "body": full_txt},
                        ],
                        user_name     = dp.get("name", ""),
                        metadata      = {"Date": datetime.datetime.now().strftime("%B %d, %Y")},
                    )
                    st.download_button(
                        "⬇ Download this response as PDF",
                        data=pdf,
                        file_name="consultation.pdf",
                        mime="application/pdf",
                    )
                except Exception:
                    pass
