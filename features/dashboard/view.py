"""
ui_streamlit/pages/dashboard.py
"""

import json
import random
import streamlit as st
import swisseph as swe
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

from shared.astro.constants import PLANETS, DASHA_ORDER
from features.tarot.constants import FULL_TAROT_DECK, TAROT_BASE
from shared.astro.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed,
    sign_index_from_lon, calculate_tara_bala,
)
from shared.astro.dossier_builder import (
    generate_astrology_dossier, get_gochara_overlay, build_vimshottari_timeline,
)
from shared.ai.gemini_client import generate_content_with_fallback
from features.dashboard.prompts import build_decide_prompt

from ui_streamlit.state import get_default_profile
from ui_streamlit.helpers import get_local_today, safe_json, get_filename
from ui_streamlit.cache import (
    fetch_dashboard_data_cached,
    fetch_daily_tarot_cached,
)


def show_dashboard():
    if "dash_toggles" not in st.session_state:
        st.session_state.dash_toggles = {
            "greeting": True, "consult": True, "forecast": True,
            "decide": True,   "calendar": True, "tarot": True, "dasha_alert": True,
        }

    dp, active_idx = get_default_profile()

    if not dp:
        st.markdown("## 🧭 The Cosmic Compass")
        st.info("💡 Welcome! Go to **Saved Profiles** and tap the ⭐ next to your name to set up your personal dashboard.")
        return

    prof     = dp
    tz       = prof.get("tz", "Asia/Kolkata")
    today_str = get_local_today(tz).isoformat()

    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f"## 🧭 {prof['name'].split()[0]}'s Compass")
    with c2:
        with st.popover("⚙️"):
            for k, label in [("greeting","Daily Greeting"),("consult","Consultation Room"),
                              ("forecast","Forecast"),("decide","Astro-Decide"),
                              ("calendar","Calendar"),("tarot","Tarot"),("dasha_alert","Dasha Shift Alerts")]:
                st.session_state.dash_toggles[k] = st.checkbox(label, value=st.session_state.dash_toggles.get(k, True))

    st.markdown("---")

    # ── Quick link to consultation ────────────────────────────────────────────
    if st.session_state.dash_toggles.get("consult", True):
        memory_key = f"consult_chat_{prof['name']}"
        last_msg = "Ask any question about your life, timing, or planetary energies."
        if memory_key in st.session_state and st.session_state[memory_key]:
            for msg in reversed(st.session_state[memory_key]):
                if msg["role"] == "model":
                    last_msg = msg["parts"][0][:100] + "..."
                    break
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(144,98,222,0.15),rgba(205,140,80,0.1));border:1px solid rgba(144,98,222,0.3);border-radius:12px;padding:1.2rem;margin-bottom:1rem;'>
            <h3 style='margin:0 0 .3rem 0;font-size:1.1rem;color:#fff;'>💬 Ask the Astrologer</h3>
            <p style='margin:0 0 .8rem 0;font-size:.85rem;color:#cd8c50;'><em>"{last_msg}"</em></p>
        </div>""", unsafe_allow_html=True)
        if st.button("Enter Consultation Room →", use_container_width=True):
            st.session_state.nav_page = "Consultation Room"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Dashboard data (greeting + energy) ───────────────────────────────────
    dash_cache_key = f"dash_data_{active_idx}_{today_str}"
    prof_json = json.dumps(prof, sort_keys=True)

    if st.session_state.dash_toggles.get("greeting", True) or st.session_state.dash_toggles.get("forecast", True):
        if dash_cache_key not in st.session_state:
            with st.spinner("Aligning the stars for your daily report..."):
                try:
                    st.session_state[dash_cache_key] = fetch_dashboard_data_cached(prof_json, today_str)
                except Exception:
                    st.session_state[dash_cache_key] = {
                        "GREETING": "The stars are quiet right now (All Free Models Exhausted). Try again in a minute!",
                        "ENERGY": "Resting", "FOCUS": "Patience", "CAUTION": "Rushing",
                        "WINDOW": "Later", "SUMMARY": "Cosmic bandwidth limit reached.",
                    }

    if st.session_state.dash_toggles.get("greeting", True) and dash_cache_key in st.session_state:
        st.markdown(f"""
        <div style="padding-left:14px;border-left:4px solid #9062de;margin-bottom:1.5rem;">
            <p style="font-size:1.05rem;font-weight:500;color:#e2e0ec;margin:0;line-height:1.5;">
                {st.session_state[dash_cache_key].get('GREETING', '')}
            </p>
        </div>""", unsafe_allow_html=True)

    # ── Cosmic week calendar ──────────────────────────────────────────────────
    if st.session_state.dash_toggles.get("calendar", True):
        st.markdown("### 📅 Your Cosmic Week")
        st.caption("Your personalized weather based on your Moon sign. 🟢 Green = Go, 🔴 Red = Lay low.")
        now = datetime.now(ZoneInfo(tz))
        p_date = date.fromisoformat(prof["date"])
        p_time = datetime.strptime(prof["time"], "%H:%M").time()
        jd_natal, _, _ = local_to_julian_day(p_date, p_time, tz)
        natal_moon, _ = get_planet_longitude_and_speed(jd_natal, PLANETS["Moon"])

        html = '<div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:10px;">'
        todays_advice = ""
        for i in range(7):
            d = now + timedelta(days=i)
            utc_d = d.astimezone(ZoneInfo("UTC"))
            jd = swe.julday(utc_d.year, utc_d.month, utc_d.day, 12.0)
            moon_raw, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
            moon = float(moon_raw[0]) % 360
            tara = calculate_tara_bala(natal_moon, moon)
            is_today = (i == 0)
            if is_today:
                todays_advice = f"**Today's Focus ({tara['tara'].split(' ')[0]}):** {tara['advice']}"
            bg     = "rgba(144,98,222,0.2)" if is_today else "rgba(255,255,255,0.05)"
            border = "border:1px solid #9062de;" if is_today else "border:1px solid rgba(255,255,255,0.1);"
            theme  = tara["advice"].split(".")[0] + "."
            html += f"""<div style="min-width:150px;padding:12px;border-radius:10px;background:{bg};{border}text-align:center;flex-shrink:0;display:flex;flex-direction:column;justify-content:space-between;">
<div><div style="font-size:.75rem;color:#beb9cd;font-weight:bold;letter-spacing:.5px;">{'TODAY' if is_today else d.strftime('%a, %b %d').upper()}</div>
<div style="font-size:1.4rem;margin:6px 0;">{tara['color'].split(' ')[0]}</div>
<div style="font-size:.85rem;color:#fff;font-weight:600;">{tara['tara'].split(' ')[0]}</div></div>
<div style="font-size:.68rem;color:rgba(255,255,255,.65);margin-top:8px;line-height:1.4;">{theme}</div></div>"""
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
        st.info(todays_advice)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Today's energy tiles ──────────────────────────────────────────────────
    if st.session_state.dash_toggles.get("forecast", True) and dash_cache_key in st.session_state:
        data = st.session_state[dash_cache_key]
        st.markdown("### 📡 Today's Energy")
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:.5rem;">
            <div style="background:rgba(255,255,255,.05);padding:12px;border-radius:10px;border-left:4px solid #cd8c50;">
                <span style="font-size:.75rem;color:#beb9cd;text-transform:uppercase;">Energy</span><br>
                <span style="font-weight:600;color:#fff;">{data.get('ENERGY','N/A')}</span></div>
            <div style="background:rgba(255,255,255,.05);padding:12px;border-radius:10px;border-left:4px solid #9062de;">
                <span style="font-size:.75rem;color:#beb9cd;text-transform:uppercase;">Focus</span><br>
                <span style="font-weight:600;color:#fff;">{data.get('FOCUS','N/A')}</span></div>
            <div style="background:rgba(255,255,255,.05);padding:12px;border-radius:10px;border-left:4px solid #e74c3c;">
                <span style="font-size:.75rem;color:#beb9cd;text-transform:uppercase;">Caution</span><br>
                <span style="font-weight:600;color:#fff;">{data.get('CAUTION','N/A')}</span></div>
            <div style="background:rgba(255,255,255,.05);padding:12px;border-radius:10px;border-left:4px solid #2ecc71;">
                <span style="font-size:.75rem;color:#beb9cd;text-transform:uppercase;">Best Time</span><br>
                <span style="font-weight:600;color:#fff;">{data.get('WINDOW','N/A')}</span></div>
        </div>""", unsafe_allow_html=True)
        st.caption(data.get("SUMMARY", ""))

    # ── Astro-Decide ──────────────────────────────────────────────────────────
    if st.session_state.dash_toggles.get("decide", True):
        st.markdown("### ⚖️ Astro-Decide")

        def clear_decide_state():
            st.session_state.astro_decide_q = ""
            st.session_state.pop("astro_decide_result", None)

        q = st.text_input("What do you need to decide right now?", key="astro_decide_q", placeholder="e.g. Should I sign this contract today?")
        c1, c2 = st.columns([3, 1])
        with c1: decide_btn = st.button("Decide", type="primary", use_container_width=True)
        with c2: st.button("Clear", use_container_width=True, on_click=clear_decide_state)

        if decide_btn:
            if not q.strip():
                st.warning("Ask something first.")
            else:
                with st.spinner("Consulting the transits..."):
                    try:
                        dos      = generate_astrology_dossier(prof, False, compact=True)
                        transits = get_gochara_overlay(prof)
                        jd_nat, _, _ = local_to_julian_day(date.fromisoformat(prof["date"]), datetime.strptime(prof["time"],"%H:%M").time(), prof["tz"])
                        natal_moon, _ = get_planet_longitude_and_speed(jd_nat, PLANETS["Moon"])
                        dt_now = datetime.now(ZoneInfo("UTC"))
                        jd_now = swe.julday(dt_now.year, dt_now.month, dt_now.day, dt_now.hour + dt_now.minute / 60.0)
                        transit_moon, _ = get_planet_longitude_and_speed(jd_now, PLANETS["Moon"])
                        tara = calculate_tara_bala(natal_moon, transit_moon)
                        py_verdict = "YES" if tara["status"] == "Go" else ("WAIT" if tara["status"] == "Stop" else "PROCEED CAUTIOUSLY")
                        prompt = build_decide_prompt(dos, transits, q, py_verdict, tara["advice"])
                        res = generate_content_with_fallback(prompt)
                        st.session_state.astro_decide_result = safe_json(res, {"VERDICT": py_verdict, "WHY": "Cosmic signals processed.", "ALTERNATIVE": tara["advice"]})
                    except Exception:
                        st.session_state.astro_decide_result = {"VERDICT": "RESTING", "WHY": "Free Models Exhausted.", "ALTERNATIVE": "Try again!"}

        if "astro_decide_result" in st.session_state:
            out = st.session_state.astro_decide_result
            with st.container(border=True):
                st.markdown(f"### 🔮 Verdict: {out.get('VERDICT','WAIT')}")
                st.markdown(f"**Why:** {out.get('WHY','')}")
                st.markdown(f"*{out.get('ALTERNATIVE','')}*")

    # ── Daily Tarot ───────────────────────────────────────────────────────────
    if st.session_state.dash_toggles.get("tarot", False):
        st.markdown("### 🃏 Daily Tarot Guidance")
        rng = random.Random(f"{prof['name']}_{today_str}")
        daily_card  = rng.choice(FULL_TAROT_DECK)
        daily_state = rng.choice(["Upright","Reversed"])

        cache_key_tarot  = f"dash_tarot_{active_idx}_{today_str}"
        reveal_key_tarot = f"{cache_key_tarot}_revealed"
        is_revealed = st.session_state.get(reveal_key_tarot, False)

        t1, t2 = st.columns([1.2, 3])
        with t1:
            img_url  = f"{TAROT_BASE}{get_filename(daily_card)}"
            back_url = f"{TAROT_BASE}tarotrear.png"
            rev_class  = "reversed" if daily_state == "Reversed" else ""
            anim_class = "dash-tarot-revealed" if is_revealed else "dash-tarot-hidden"
            st.markdown(f"""<style>
.dash-tarot-scene{{width:130px;aspect-ratio:2/3;perspective:1000px;margin:0 auto}}
.dash-tarot-card{{width:100%;height:100%;position:relative;transform-style:preserve-3d}}
.dash-tarot-revealed{{animation:dashFlip .8s cubic-bezier(.34,1.56,.64,1) forwards}}
.dash-tarot-hidden{{transform:rotateY(0deg)}}
@keyframes dashFlip{{0%{{transform:rotateY(0deg)}}100%{{transform:rotateY(180deg)}}}}
.dash-tarot-face{{position:absolute;inset:0;width:100%;height:100%;backface-visibility:hidden;border-radius:6px;box-shadow:0 4px 10px rgba(0,0,0,.5);background-size:cover;background-position:center;border:2px solid rgba(205,140,80,.6)}}
.dash-tarot-front{{transform:rotateY(180deg);background-image:url('{img_url}')}}
.dash-tarot-front.reversed{{transform:rotateY(180deg) rotateZ(180deg)}}
.dash-tarot-back{{background-image:url('{back_url}')}}
</style>
<div class="dash-tarot-scene"><div class="dash-tarot-card {anim_class}">
<div class="dash-tarot-face dash-tarot-back"></div>
<div class="dash-tarot-face dash-tarot-front {rev_class}"></div>
</div></div>""", unsafe_allow_html=True)
            label_text = f"{daily_card}<br>({daily_state})" if is_revealed else "The Oracle is waiting"
            st.markdown(f"<div style='text-align:center;font-size:.75rem;color:#beb9cd;font-weight:600;margin-top:8px;'>{label_text}</div>", unsafe_allow_html=True)

        with t2:
            if not is_revealed:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Reveal & Interpret Today's Card ✨", use_container_width=True):
                    st.session_state[reveal_key_tarot] = True
                    with st.spinner("Channeling the deck..."):
                        try:
                            tarot_result = fetch_daily_tarot_cached(prof_json, today_str, daily_card, daily_state)
                        except Exception:
                            tarot_result = {"MEANING":"Trust the process.","ACTION":"Observe.","MANTRA":"I am exactly where I need to be."}
                        st.session_state[cache_key_tarot] = tarot_result
                    st.rerun()

            if st.session_state.get(reveal_key_tarot, False):
                if cache_key_tarot not in st.session_state:
                    with st.spinner("Channeling the deck..."):
                        try:
                            st.session_state[cache_key_tarot] = fetch_daily_tarot_cached(prof_json, today_str, daily_card, daily_state)
                        except Exception:
                            st.session_state[cache_key_tarot] = {"MEANING":"Trust the process.","ACTION":"Observe.","MANTRA":"I am exactly where I need to be."}
                t_data = st.session_state[cache_key_tarot]
                st.markdown(f"""
                <div style="background:rgba(255,255,255,.03);padding:15px;border-radius:10px;border:1px solid rgba(255,255,255,.08);height:100%;">
                    <p style="margin:0 0 10px;font-size:.85rem;"><b style="color:#fff;">Meaning:</b> <span style="color:#beb9cd;">{t_data.get('MEANING','')}</span></p>
                    <p style="margin:0 0 10px;font-size:.85rem;"><b style="color:#fff;">Action:</b> <span style="color:#beb9cd;">{t_data.get('ACTION','')}</span></p>
                    <p style="margin:0;font-size:.85rem;"><b style="color:#cd8c50;">Mantra:</b> <i style="color:#e0d8f0;">"{t_data.get('MANTRA','')}"</i></p>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Dasha shift alert ─────────────────────────────────────────────────────
    if st.session_state.dash_toggles.get("dasha_alert", True):
        now_dt     = datetime.now(ZoneInfo(tz))
        today_date = now_dt.date()
        p_date = date.fromisoformat(prof["date"]) if isinstance(prof["date"], str) else prof["date"]
        p_time = datetime.strptime(prof["time"], "%H:%M").time() if isinstance(prof["time"], str) else prof["time"]

        jd_nat, dt_loc, _ = local_to_julian_day(p_date, p_time, tz)
        m_lon, _ = get_planet_longitude_and_speed(jd_nat, PLANETS["Moon"])
        d_info = build_vimshottari_timeline(dt_loc, m_lon, now_dt)

        ad_days = (d_info["ad_end"].astimezone(ZoneInfo(tz)).date() - today_date).days
        pd_days = (d_info["pd_end"].astimezone(ZoneInfo(tz)).date() - today_date).days

        themes = {
            "Sun":"authority, soul-searching, and visibility","Moon":"emotional shifts and deep changes",
            "Mars":"action, drive, and potential friction","Rahu":"ambition, obsession, and sudden events",
            "Jupiter":"expansion, wisdom, and opportunities","Saturn":"discipline, structure, and hard work",
            "Mercury":"intellect, communication, and business","Ketu":"detachment, endings, and spirituality",
            "Venus":"relationships, comfort, and harmony","Unknown":"shifting cosmic energies",
        }
        try:
            nxt_ad = DASHA_ORDER[(DASHA_ORDER.index(d_info["current_ad"]) + 1) % 9]
            nxt_pd = DASHA_ORDER[(DASHA_ORDER.index(d_info["current_pd"]) + 1) % 9]
        except Exception:
            nxt_ad, nxt_pd = "Unknown", "Unknown"

        if 0 <= ad_days <= 45:
            a_title = f"⚠️ Major Chapter Shift in {ad_days} Days"
            a_text  = f"Your Antardasha is shifting from **{d_info['current_ad']}** to **{nxt_ad}**. Prepare for a major life theme shift towards {themes.get(nxt_ad,'new paths')}."
            b_color = "#e74c3c"
        elif 0 <= pd_days <= 14:
            a_title = f"⏱️ Minor Energy Shift in {pd_days} Days"
            a_text  = f"Your Pratyantar Dasha shifts from **{d_info['current_pd']}** to **{nxt_pd}**. Expect a brief pivot towards {themes.get(nxt_pd,'new paths')}."
            b_color = "#cd8c50"
        else:
            a_title = f"⏳ Current Phase: {d_info['current_ad']} Antardasha"
            a_text  = f"You are deep in your **{d_info['current_md']}** Mahadasha and **{d_info['current_ad']}** Antardasha. The next major shift is {ad_days} days away."
            b_color = "rgba(255,255,255,0.08)"

        st.markdown(f"""
        <div style="padding:14px 18px;border-radius:12px;background:rgba(0,0,0,0.2);border:1px solid {b_color};margin-bottom:1.5rem;box-shadow:0 4px 15px rgba(0,0,0,.1);">
            <p style="margin:0 0 4px;font-size:.80rem;color:{b_color if b_color!='rgba(255,255,255,0.08)' else '#beb9cd'};text-transform:uppercase;font-weight:700;letter-spacing:.5px;">{a_title}</p>
            <p style="margin:0;font-size:.95rem;color:#e2e0ec;line-height:1.5;">{a_text}</p>
        </div>""", unsafe_allow_html=True)
