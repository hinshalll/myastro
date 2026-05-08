"""
ui_streamlit/pages/horoscopes.py
"""

import json
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from math_engine.astro_calc import get_western_sign, sign_index_from_lon, sign_name, nakshatra_info
from ui_streamlit.state import get_default_profile
from ui_streamlit.helpers import get_local_today, get_moon_lon_from_profile
from ui_streamlit.components import render_profile_form, resolve_profile
from ui_streamlit.cache import (
    generate_western_forecast_cached,
    generate_vedic_forecast_cached,
)


def show_horoscopes():
    components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
    st.markdown("<h1>🌟 Horoscopes</h1>", unsafe_allow_html=True)

    dp, _ = get_default_profile()
    user_tz  = dp["tz"] if dp else "Asia/Kolkata"
    today_str = get_local_today(user_tz).isoformat()

    t1, t2 = st.tabs(["☀️ Western (Sun Sign)", "🌙 Vedic (Moon Sign)"])

    # ── Western ───────────────────────────────────────────────────────────────
    with t1:
        dob = st.date_input("Date of Birth", date(2000, 1, 1),
                            min_value=date(1850, 1, 1), max_value=date(2050, 12, 31), key="h_w_dob")
        if st.button("Calculate Daily Forecast", type="primary", key="w_btn"):
            sun_sign = get_western_sign(dob.month, dob.day)
            st.success(f"Your Sun Sign: **{sun_sign}**")
            with st.spinner("Analyzing live tropical transits..."):
                western_reading = generate_western_forecast_cached(sun_sign, today_str)
                st.markdown("### ☀️ Daily Western Forecast")
                st.markdown(western_reading)

    # ── Vedic ─────────────────────────────────────────────────────────────────
    with t2:
        item = render_profile_form("vedic_horo", show_d60=False)
        if st.button("Calculate Vedic Forecasts", type="primary", key="v_btn"):
            if item["type"] == "empty_saved":
                st.error("Select or enter a profile.")
            else:
                prof, _ = resolve_profile(item)
                moon_lon = get_moon_lon_from_profile(prof)
                moon_sidx = sign_index_from_lon(moon_lon)
                sign_n = sign_name(moon_sidx)
                nak, _, _ = nakshatra_info(moon_lon)

                st.success(f"Your Rashi (Moon Sign): **{sign_n}** | Birth Star: **{nak}**")

                with st.spinner("Calculating exact future planetary positions..."):
                    prof_json = json.dumps(prof, sort_keys=True)
                    pt1, pt2, pt3 = st.tabs(["Daily", "Monthly", "Yearly"])
                    with pt1:
                        st.write(generate_vedic_forecast_cached(prof_json, "Daily",   today_str))
                    with pt2:
                        st.write(generate_vedic_forecast_cached(prof_json, "Monthly", today_str))
                    with pt3:
                        st.write(generate_vedic_forecast_cached(prof_json, "Yearly",  today_str))
