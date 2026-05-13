"""
ui_streamlit/pages/consultation.py
"""

import time as time_module
import streamlit as st
import streamlit.components.v1 as components

from math_engine.dossier_builder import generate_astrology_dossier, get_gochara_overlay
from ai_engine.gemini_client import FREE_MODELS, get_ai_model_by_name
from ai_engine.knowledge import get_knowledge_files

from ui_streamlit.state import get_default_profile
from ui_streamlit.cache import get_knowledge_files_cached


def show_consultation_room():
    components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
    st.markdown("<h1>💬 Ask the Astrologer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,.6)'>Have a free-flowing conversation about your chart.</p>", unsafe_allow_html=True)

    dp, _ = get_default_profile()
    if not dp:
        st.warning("Please set a ⭐ default profile in 'Saved Profiles' first so the Astrologer knows who to look at.")
        return

    st.success(f"The Astrologer is currently looking at the chart for: **{dp['name']}**")

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
                dos      = generate_astrology_dossier(dp)
                transits = get_gochara_overlay(dp)

                guardrails = """<CONSULTATION_GUARDRAILS>
You are a warm, highly empathetic Vedic Astrologer. Speak conversationally, directly to the user.

RULES:
1. MATH LOCK: Never invent or alter any number. Use only data from the dossier.
2. MISSING CONTEXT: If you need the user's current life situation to answer well, ask them warmly.
3. OTHERS (NO DATA): "I'd love to help! Could you share their birth details, full name, or at minimum a first name?"
4. OTHERS (FIRST NAME ONLY): Use Vedic Name Astrology (Nama Nakshatra). Disclaimer: "I'm using name-based Vedic energy — a birth chart gives true precision."
5. OTHERS (FULL NAME): Use Chaldean Numerology + Name Astrology. Disclaimer: "Name-based reading only — birth chart needed for full accuracy."
6. OTHERS (FULL BIRTH DETAILS): General reading from their placements. Note: "For dual-chart math, use the Matchmaking tab."
7. MATCHMAKING: Only redirect to Matchmaking tab if user EXPLICITLY asks for compatibility/rishta check.
8. FUTURE TIMING: Use ONLY the Vimshottari Dasha timeline from the dossier. Never guess future transits.
9. TAROT: Redirect to Mystic Tarot tab warmly.
</CONSULTATION_GUARDRAILS>"""

                hist_text = ""
                if st.session_state[memory_key]:
                    last_few = st.session_state[memory_key][-4:]
                    hist_text = "\n\nRECENT CONVERSATION:\n" + "\n".join(
                        f"{'User' if m['role']=='user' else 'Astrologer'}: {m['display']}"
                        for m in last_few
                    )

                full_prompt = (
                    f"{guardrails}\n\n"
                    f"BIRTH CHART DOSSIER FOR {dp['name']}:\n{dos}\n\n"
                    f"TODAY'S LIVE TRANSITS:\n{transits}"
                    f"{hist_text}\n\n"
                    f"USER QUESTION: {q}"
                )

                try:
                    consult_book    = get_knowledge_files_cached(["htrh1.md"])
                    consult_content = consult_book + [full_prompt]
                except Exception:
                    consult_content = [full_prompt]

                full_txt = ""
                success  = False
                for m_id in FREE_MODELS:
                    if success: break
                    for attempt in range(3):
                        try:
                            model    = get_ai_model_by_name(m_id, custom_system_rules=guardrails)
                            response = model.generate_content(consult_content, stream=True)
                            for chunk in response:
                                full_txt += chunk.text
                                res_ph.markdown(full_txt + "▌")
                            res_ph.markdown(full_txt)
                            success = True
                            break
                        except Exception as e:
                            err = str(e)
                            is_rate     = any(x in err for x in ["429","quota","RESOURCE_EXHAUSTED","rate limit"])
                            is_overflow = any(x in err for x in ["400","InvalidArgument","token count exceeds","maximum number of tokens"])
                            if is_overflow: break
                            elif is_rate and attempt < 2: time_module.sleep((2**attempt)*3)
                            else: break

                if not success:
                    res_ph.warning("⏳ Models are briefly at capacity. Please try again in a moment.")
                    return

                st.session_state[memory_key].append({"role":"user",  "display":q,        "internal":q})
                st.session_state[memory_key].append({"role":"model", "display":full_txt,  "internal":full_txt})

                # PDF download of this response
                try:
                    from ui_streamlit.views.astro_pdf import build_astro_pdf
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
