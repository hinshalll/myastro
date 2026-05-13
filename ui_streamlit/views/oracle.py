"""
ui_streamlit/pages/oracle.py
"""

import concurrent.futures
import time as time_module
from datetime import datetime, date

import streamlit as st
import streamlit.components.v1 as components

from math_engine.constants import PLANETS, COMPARISON_CRITERIA
from math_engine.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed,
    sign_index_from_lon, get_lagna_and_cusps,
)
from math_engine.dossier_builder import generate_astrology_dossier, get_gochara_overlay
from math_engine.scoring import calculate_destiny_confirmation
from ai_engine.gemini_client import FREE_MODELS, agent_worker, generate_content_with_fallback
from ai_engine.prompts import (
    build_agent_parashari_prompt, build_agent_timing_prompt, build_agent_kp_prompt,
    build_master_synthesizer_prompt, build_transit_prompt, build_prashna_prompt,
    build_matchmaking_prompt, build_destiny_confirmation_prompt, build_comparison_prompt,
)
from ai_engine.knowledge import get_knowledge_files

from ui_streamlit.state import get_default_profile, toggle_all_criteria
from ui_streamlit.helpers import get_moon_lon_from_profile
from ui_streamlit.components import render_profile_form, resolve_profile, stream_ai_with_followup
from ui_streamlit.cache import (
    geocode_place_cached, timezone_for_latlon_cached,
    get_knowledge_files_cached, get_comparison_reference_digest_cached,
)

try:
    from math_engine.astro_calc import check_manglik_dosha, get_manglik_cancellation_verdict
    from math_engine.dossier_builder import calculate_matchmaking_synastry
except ImportError:
    pass


def show_oracle():
    components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
    st.markdown("<h1>🔮 The Oracle</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,.6)'>Mathematically locked AI prompts from Swiss Ephemeris precision.</p>", unsafe_allow_html=True)

    missions = {
        "Deep Personal Analysis":        "🔮 Full Life Reading",
        "Matchmaking / Compatibility":   "✦ Compatibility Match",
        "Destiny & Marriage Chances":    "💞 Marriage Chances Calculator",
        "Gochara / Live Transit":        "🌍 Live Transit Analysis",
        "Comparison (Multiple Profiles)":"⚖ Compare Profiles",
        "Prashna Kundli":                "🎯 Ask a Question",
    }
    descs = {
        "Deep Personal Analysis":        "Complete reading — personality, career, wealth, marriage, timing.",
        "Matchmaking / Compatibility":   "Ashta Koota + Manglik + Compatibility.",
        "Destiny & Marriage Chances":    "Advanced cross-chart confirmation matrix.",
        "Gochara / Live Transit":        "How today's planets activate your natal chart right now.",
        "Comparison (Multiple Profiles)":"Rank multiple people with planetary evidence.",
        "Prashna Kundli":                "Ask a specific question. Get Yes/No/Delayed.",
    }

    cur = st.session_state.active_mission if st.session_state.active_mission in missions else "Deep Personal Analysis"
    cur_label = missions.get(cur, "🔮 Full Life Reading")
    sel_label = st.selectbox("Select Tool", list(missions.values()),
                             index=list(missions.values()).index(cur_label),
                             label_visibility="collapsed")
    mid = [k for k, v in missions.items() if v == sel_label][0]
    st.session_state.active_mission = mid
    st.markdown(f"<p style='color:rgba(190,185,210,.6);font-size:.88rem;margin-bottom:1.5rem'>{descs[mid]}</p><hr>", unsafe_allow_html=True)
    _run_oracle(mid)


def _run_oracle(mission):
    dp, _ = get_default_profile()

    # ── Prashna ───────────────────────────────────────────────────────────────
    if mission == "Prashna Kundli":
        question = st.text_area("Your question", placeholder="e.g. Will I get the job I applied for?")
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
            if not question.strip(): st.error("Enter a question."); return
            if not pr_man:
                geo = geocode_place_cached(cur_place.strip())
                if not geo: st.error("Location not found."); return
                p_lat, p_lon, pn = geo; p_tz = timezone_for_latlon_cached(p_lat, p_lon)
            else:
                p_lat, p_lon, p_tz, pn = prl, prn, prt, "Manual"
            now  = datetime.now(__import__("zoneinfo").ZoneInfo(p_tz))
            prof = {"name":"Prashna","date":now.date().isoformat(),"time":now.strftime("%H:%M"),
                    "place":pn,"lat":p_lat,"lon":p_lon,"tz":p_tz}
            with st.spinner("Casting chart..."):
                dos = generate_astrology_dossier(prof)
            st.session_state.prashna_prompt = build_prashna_prompt(question, dos)
            st.session_state.prashna_chat   = []

        if "prashna_prompt" in st.session_state:
            stream_ai_with_followup(st.session_state.prashna_prompt, "prashna_chat", "Answering your Prashna...")
        return

    # ── Gochara ───────────────────────────────────────────────────────────────
    if mission == "Gochara / Live Transit":
        st.markdown("#### Select your natal chart")
        item = render_profile_form("gochara", show_d60=False)
        if st.button("Analyse Live Transits ✨", type="primary", use_container_width=True):
            if item["type"] == "empty_saved": st.error("Select a profile."); return
            prof, d60 = resolve_profile(item)
            with st.spinner("Overlaying transits..."):
                dos     = generate_astrology_dossier(prof, d60)
                overlay = get_gochara_overlay(prof)
            st.session_state.transit_prompt = build_transit_prompt(dos, overlay)
            st.session_state.transit_chat   = []

        if "transit_prompt" in st.session_state:
            stream_ai_with_followup(st.session_state.transit_prompt, "transit_chat", "Reading the stars...")
        return

    # ── Multi-profile missions ────────────────────────────────────────────────
    req       = 1 if mission == "Deep Personal Analysis" else 2
    num_slots = st.session_state.comp_slots if mission == "Comparison (Multiple Profiles)" else req
    st.markdown("#### Profile Selection")
    active = []

    if mission == "Comparison (Multiple Profiles)":
        for i in range(num_slots):
            st.markdown(f"**Profile {i+1}**")
            active.append(render_profile_form(f"orc_{mission}_{i}"))
        ca, cb, _ = st.columns([1, 1, 4])
        if ca.button("＋ Add", key=f"addc_{mission}"):
            if st.session_state.comp_slots < 10: st.session_state.comp_slots += 1; st.rerun()
        if cb.button("－ Remove", key=f"remc_{mission}"):
            if st.session_state.comp_slots > 2:  st.session_state.comp_slots -= 1; st.rerun()
    else:
        cols = st.columns(min(num_slots, 2))
        for i in range(num_slots):
            with cols[i % 2]:
                st.markdown(f"**{'Person '+str(i+1) if num_slots>1 else 'Your Details'}**")
                active.append(render_profile_form(f"orc_{mission}_{i}"))

    selected_criteria = []
    if mission == "Comparison (Multiple Profiles)":
        st.markdown("### What to Compare")
        st.checkbox("Select All", key="select_all_cb", on_change=toggle_all_criteria)
        ca2, cb3 = st.columns(2)
        for i, crit in enumerate(COMPARISON_CRITERIA):
            with (ca2 if i % 2 == 0 else cb3):
                if st.checkbox(crit, key=f"chk_{i}"): selected_criteria.append(crit)
        nc_c, nc_a = st.columns([4, 1])
        nc = nc_c.text_input("Custom", label_visibility="collapsed", placeholder="e.g. Most likely to be famous")
        if nc_a.button("Add"):
            if nc.strip() and nc.strip() not in st.session_state.custom_criteria:
                st.session_state.custom_criteria.append(nc.strip()); st.rerun()
        for i, c in enumerate(st.session_state.custom_criteria):
            r1, r2 = st.columns([6, 1])
            if r1.checkbox(c, key=f"cc_{i}"): selected_criteria.append(c)
            if r2.button("✕", key=f"delc_{i}"): st.session_state.custom_criteria.pop(i); st.rerun()

    btn_labels = {
        "Deep Personal Analysis":       "Generate Full Reading ✨",
        "Matchmaking / Compatibility":  "Generate Compatibility Match ✨",
        "Comparison (Multiple Profiles)":"Compare Profiles ✨",
        "Destiny & Marriage Chances":   "Generate Destiny Marriage Matrix ✨",
    }

    if st.button(btn_labels.get(mission, "Generate ✨"), type="primary", use_container_width=True, key=f"gen_{mission}"):
        profiles = []; d60s = []
        for item in active:
            if item["type"] == "empty_saved": st.error("Fill all profile slots."); return
            prof, d60 = resolve_profile(item); profiles.append(prof); d60s.append(d60)
        if len(profiles) < req: return

        compact = mission == "Comparison (Multiple Profiles)" and len(profiles) > 3
        st.session_state[f"oracle_{mission}_history"] = []
        final  = ""
        result = ""

        with st.spinner("Consulting the ephemeris..."):

            if mission == "Deep Personal Analysis":
                dossier = generate_astrology_dossier(profiles[0], d60s[0])
                st.info("🧠 Firing Parallel AI Agents (Takes ~20s)...")
                expert_rules = "<ROLE>Elite Vedic Astrologer</ROLE><MATH_LOCK>Never alter, invent or estimate any number. Use only data present in the dossier.</MATH_LOCK>"
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    f_p = executor.submit(agent_worker, build_agent_parashari_prompt(dossier), [], FREE_MODELS[0], expert_rules)
                    f_t = executor.submit(agent_worker, build_agent_timing_prompt(dossier),    [], FREE_MODELS[0], expert_rules)
                    f_k = executor.submit(agent_worker, build_agent_kp_prompt(dossier),        [], FREE_MODELS[1], expert_rules)
                    p_notes, t_notes, k_notes = f_p.result(), f_t.result(), f_k.result()
                final = build_master_synthesizer_prompt(dossier, p_notes, t_notes, k_notes)
                time_module.sleep(3)
                st.info("📖 Writing your full reading...")
                try:
                    natal_book = get_knowledge_files_cached(["htrh1.md"])
                    result     = generate_content_with_fallback(final, knowledge_files=natal_book)
                except Exception as e:
                    result = f"⚠️ Reading generation paused ({str(e)[:100]}). Your chart data was computed. Please try again in ~1 minute."
                st.session_state[f"oracle_{mission}_history"] = [
                    {"role":"user",  "display":"🔮 Full Life Reading", "parts":[final]},
                    {"role":"model", "display":result,                 "parts":[result]},
                ]

            elif mission == "Destiny & Marriage Chances":
                p_boy  = profiles[0] if profiles[0].get("gender") == "M" else profiles[1]
                p_girl = profiles[1] if p_boy == profiles[0] else profiles[0]
                if p_boy == p_girl: p_boy = profiles[0]; p_girl = profiles[1]
                pb_idx = profiles.index(p_boy); pg_idx = profiles.index(p_girl)
                st.info("Crunching Jaimini & D9 matrices...")
                _parse_date = lambda p: date.fromisoformat(p["date"]) if isinstance(p["date"], str) else p["date"]
                _parse_time = lambda p: datetime.strptime(p["time"], "%H:%M").time() if isinstance(p["time"], str) else p["time"]
                jda, _, _ = local_to_julian_day(_parse_date(p_boy),  _parse_time(p_boy),  p_boy["tz"])
                jdb, _, _ = local_to_julian_day(_parse_date(p_girl), _parse_time(p_girl), p_girl["tz"])
                dos_a = generate_astrology_dossier(p_boy,  d60s[pb_idx])
                dos_b = generate_astrology_dossier(p_girl, d60s[pg_idx])
                dest_data = calculate_destiny_confirmation(p_boy, p_girl, jda, jdb, dos_a, dos_b)
                final     = build_destiny_confirmation_prompt(p_boy, p_girl, dos_a, dos_b, dest_data)
                st.info("📖 Generating Destiny Marriage Matrix...")
                marriage_book = get_knowledge_files_cached(["htrh2.md"])
                result = generate_content_with_fallback(final, knowledge_files=marriage_book)
                if result:
                    st.session_state[f"oracle_{mission}_history"] = [
                        {"role":"user",  "display":"💞 Destiny Marriage Matrix", "parts":[final]},
                        {"role":"model", "display":result,                       "parts":[result]},
                    ]

            elif mission == "Matchmaking / Compatibility":
                p_boy  = profiles[0] if profiles[0].get("gender") == "M" else profiles[1]
                p_girl = profiles[1] if p_boy == profiles[0] else profiles[0]
                if p_boy == p_girl: p_boy = profiles[0]; p_girl = profiles[1]
                ma = get_moon_lon_from_profile(p_boy); mb = get_moon_lon_from_profile(p_girl)
                _parse_date = lambda p: date.fromisoformat(p["date"]) if isinstance(p["date"], str) else p["date"]
                _parse_time = lambda p: datetime.strptime(p["time"], "%H:%M").time() if isinstance(p["time"], str) else p["time"]
                jda, dtla, _ = local_to_julian_day(_parse_date(p_boy),  _parse_time(p_boy),  p_boy["tz"])
                jdb, dtlb, _ = local_to_julian_day(_parse_date(p_girl), _parse_time(p_girl), p_girl["tz"])
                pla   = {pn: get_planet_longitude_and_speed(jda, pid) for pn, pid in PLANETS.items()}
                plb   = {pn: get_planet_longitude_and_speed(jdb, pid) for pn, pid in PLANETS.items()}
                laga  = sign_index_from_lon(get_lagna_and_cusps(jda, p_boy["lat"],  p_boy["lon"])[0])
                lagb  = sign_index_from_lon(get_lagna_and_cusps(jdb, p_girl["lat"], p_girl["lon"])[0])
                ma_d  = check_manglik_dosha(laga, sign_index_from_lon(pla["Moon"][0]), sign_index_from_lon(pla["Mars"][0]))
                mb_d  = check_manglik_dosha(lagb, sign_index_from_lon(plb["Moon"][0]), sign_index_from_lon(plb["Mars"][0]))
                canc  = get_manglik_cancellation_verdict(ma_d, mb_d)
                dos_a = generate_astrology_dossier(p_boy,  d60s[profiles.index(p_boy)])
                dos_b = generate_astrology_dossier(p_girl, d60s[profiles.index(p_girl)])
                koota_data, marital_a, marital_b, kp_a, kp_b = calculate_matchmaking_synastry(p_boy, p_girl, ma, mb, jda, jdb, dos_a, dos_b)
                final = build_matchmaking_prompt(dos_a, dos_b, koota_data, canc, p_boy, p_girl, marital_a, marital_b, kp_a, kp_b)
                st.info("📖 Generating compatibility reading...")
                try:
                    marriage_book = get_knowledge_files_cached(["htrh2.md"])
                    result = generate_content_with_fallback(final, knowledge_files=marriage_book)
                except Exception as e:
                    result = f"⚠️ Reading paused ({str(e)[:100]}). Please try again in ~1 minute."
                st.session_state[f"oracle_{mission}_history"] = [
                    {"role":"user",  "display":"✦ Compatibility Match", "parts":[final]},
                    {"role":"model", "display":result,                   "parts":[result]},
                ]

            elif mission == "Comparison (Multiple Profiles)":
                if not selected_criteria: st.warning("Select at least one criterion."); return
                pairs = [(p["name"], generate_astrology_dossier(p, d, compact)) for p, d in zip(profiles, d60s)]
                final = build_comparison_prompt(pairs, selected_criteria)
                st.info("📖 Comparing profiles...")
                try:
                    compare_book = get_comparison_reference_digest_cached()
                    result = generate_content_with_fallback(final, knowledge_files=compare_book)
                except Exception as e:
                    result = f"⚠️ Reading paused ({str(e)[:100]}). Please try again in ~1 minute."
                st.session_state[f"oracle_{mission}_history"] = [
                    {"role":"user",  "display":"⚖ Profile Comparison", "parts":[final]},
                    {"role":"model", "display":result,                   "parts":[result]},
                ]

        if final:
            st.session_state[f"oracle_prompt_{mission}"] = final

    # ── Render results ────────────────────────────────────────────────────────
    # Pre-generated missions (Full Life Reading, Matchmaking, Destiny, Comparison)
    # have their result already in history — render it directly without re-calling
    # the AI (which would generate a second reading on every page rerender).
    # Prashna and Gochara use stream_ai_with_followup for generation.

    pre_generated = {"Deep Personal Analysis", "Matchmaking / Compatibility",
                     "Destiny & Marriage Chances", "Comparison (Multiple Profiles)"}

    if mission in pre_generated:
        history = st.session_state.get(f"oracle_{mission}_history", [])
        for msg in history:
            if not msg.get("hidden", False):
                with st.chat_message(msg["role"], avatar="🪐" if msg["role"] == "model" else "👤"):
                    display = msg.get("display") or (msg.get("parts") or [""])[0]
                    st.markdown(display)

        # PDF button for pre-generated reading
        last_model = next(
            (m.get("display") or (m.get("parts") or [""])[0]
             for m in reversed(history) if m.get("role") == "model"),
            None,
        )
        if last_model and not last_model.startswith("⚠️") and history:
            try:
                from ui_streamlit.views.astro_pdf import build_astro_pdf
                import datetime as _dt
                feature_labels = {
                    "Deep Personal Analysis":        ("Full Life Reading",       "★"),
                    "Matchmaking / Compatibility":   ("Compatibility Match",     "♥"),
                    "Destiny & Marriage Chances":    ("Destiny Marriage Matrix", "♦"),
                    "Comparison (Multiple Profiles)":("Profile Comparison",      "⚖"),
                }
                title, emoji = feature_labels.get(mission, ("Oracle Reading", "*"))
                pdf = build_astro_pdf(
                    feature_title=title, feature_emoji=emoji,
                    sections=[{"heading": "", "body": last_model}],
                    user_name=dp.get("name", "") if dp else "",
                    metadata={"Date": _dt.datetime.now().strftime("%B %d, %Y")},
                )
                st.download_button(
                    "⬇ Download PDF", data=pdf,
                    file_name=f"oracle_{mission.lower().replace(' ','_')}.pdf",
                    mime="application/pdf", key=f"oracle_pdf_{mission}",
                )
            except Exception:
                pass

    elif f"oracle_prompt_{mission}" in st.session_state:
        # Prashna and Gochara — live generation via stream_ai_with_followup
        oracle_files = None
        if mission == "Prashna Kundli":
            oracle_files = get_knowledge_files_cached(["kp6.md"])
        elif mission == "Gochara / Live Transit":
            oracle_files = get_knowledge_files_cached(["iva.md"])
        stream_ai_with_followup(
            st.session_state[f"oracle_prompt_{mission}"],
            f"oracle_{mission}_history",
            "The Master Astrologer is writing...",
            knowledge_files=oracle_files,
            hide_user_prompt=True,
        )
