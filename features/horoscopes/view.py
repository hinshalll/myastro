"""features.horoscopes.view — Streamlit page for Western + Vedic horoscopes."""

import json
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from shared.astro.astro_calc import get_western_sign, sign_index_from_lon, sign_name, nakshatra_info
from ui_streamlit.state import get_default_profile
from ui_streamlit.helpers import get_local_today, get_moon_lon_from_profile
from ui_streamlit.components import render_profile_form, resolve_profile
from ui_streamlit.cache import (
    generate_western_forecast_cached,
    generate_vedic_forecast_cached,
)


def _horoscope_pdf(title, user_name, metadata, reading_text):
    """Build and return a PDF for a horoscope reading."""
    try:
        from shared.pdf.astro_pdf import build_astro_pdf
        import re
        sections = []
        current_heading = ""
        current_body = []
        for line in reading_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## ") or stripped.startswith("### "):
                if current_body:
                    sections.append({"heading": current_heading, "body": "\n".join(current_body).strip()})
                    current_body = []
                current_heading = re.sub(r'^#+\s*', '', stripped)
            else:
                current_body.append(line)
        if current_body:
            sections.append({"heading": current_heading, "body": "\n".join(current_body).strip()})
        return build_astro_pdf(
            feature_title = title,
            feature_emoji = "★",
            sections      = sections or [{"heading": "", "body": reading_text}],
            user_name     = user_name,
            metadata      = metadata,
        )
    except Exception:
        return None


def show_horoscopes():
    components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
    st.markdown("<h1>🌟 Horoscopes</h1>", unsafe_allow_html=True)

    dp, _ = get_default_profile()
    user_tz  = dp["tz"] if dp else "Asia/Kolkata"
    today_str = get_local_today(user_tz).isoformat()

    t1, t2 = st.tabs(["☀️ Western (Sun Sign)", "🌙 Vedic (Moon Sign)"])

    # ── Western ─────────────────────────────────────────────────────────
    with t1:
        dob = st.date_input("Date of Birth", date(2000, 1, 1),
                            min_value=date(1850, 1, 1), max_value=date(2050, 12, 31), key="h_w_dob")
        if st.button("Calculate Daily Forecast", type="primary", key="w_btn"):
            sun_sign = get_western_sign(dob.month, dob.day)
            st.success(f"Your Sun Sign: **{sun_sign}**")
            with st.spinner("Analyzing live tropical transits..."):
                reading = generate_western_forecast_cached(sun_sign, today_str)
                st.session_state["w_reading"]  = reading
                st.session_state["w_sign"]     = sun_sign
                st.session_state["w_date_str"] = today_str

        if st.session_state.get("w_reading"):
            st.markdown("### ☀️ Daily Western Forecast")
            st.markdown(st.session_state["w_reading"])
            user_name = dp["name"] if dp else ""
            pdf = _horoscope_pdf(
                "Daily Western Horoscope", user_name,
                {"Sun Sign": st.session_state.get("w_sign", ""),
                 "Date":     st.session_state.get("w_date_str", "")},
                st.session_state["w_reading"],
            )
            if pdf:
                st.download_button("⬇ Download PDF", data=pdf,
                    file_name="western_horoscope.pdf", mime="application/pdf")

    # ── Vedic ───────────────────────────────────────────────────────────
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
                    user_name = prof.get("name", dp["name"] if dp else "")
                    meta = {"Moon Sign (Rashi)": sign_n, "Nakshatra": nak, "Date": today_str}
                    pt1, pt2, pt3 = st.tabs(["Daily", "Monthly", "Yearly"])
                    with pt1:
                        daily = generate_vedic_forecast_cached(prof_json, "Daily", today_str)
                        st.write(daily)
                        pdf = _horoscope_pdf("Daily Vedic Horoscope", user_name, meta, daily)
                        if pdf:
                            st.download_button("⬇ Download PDF", data=pdf,
                                file_name="vedic_daily.pdf", mime="application/pdf", key="vpdf_d")
                    with pt2:
                        monthly = generate_vedic_forecast_cached(prof_json, "Monthly", today_str)
                        st.write(monthly)
                        pdf = _horoscope_pdf("Monthly Vedic Horoscope", user_name, meta, monthly)
                        if pdf:
                            st.download_button("⬇ Download PDF", data=pdf,
                                file_name="vedic_monthly.pdf", mime="application/pdf", key="vpdf_m")
                    with pt3:
                        yearly = generate_vedic_forecast_cached(prof_json, "Yearly", today_str)
                        st.write(yearly)
                        pdf = _horoscope_pdf("Yearly Vedic Horoscope", user_name, meta, yearly)
                        if pdf:
                            st.download_button("⬇ Download PDF", data=pdf,
                                file_name="vedic_yearly.pdf", mime="application/pdf", key="vpdf_y")
