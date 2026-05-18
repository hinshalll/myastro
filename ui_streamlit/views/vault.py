"""
ui_streamlit/pages/vault.py
"""

import json
import time as time_module
from datetime import datetime, date, time

import streamlit as st
import streamlit.components.v1 as components

from ui_streamlit.state import (
    get_default_profile, set_default_profile, clear_default_profile,
    sync_db, is_duplicate_in_db, format_date_ui,
)
from ui_streamlit.cache import geocode_place_cached, timezone_for_latlon_cached


def show_vault():
    components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
    st.markdown("<h1>📖 Saved Profiles</h1>", unsafe_allow_html=True)

    dp_idx = st.session_state.default_profile_idx

    # ── Profile cards ─────────────────────────────────────────────────────────
    if not st.session_state.db:
        st.info("No saved profiles yet. Add your first one below.")
    else:
        st.markdown("### Your Profiles")
        st.caption("☆ Tap the star on any profile to set it as your default — it will auto-load across the app.")
        cols = st.columns(min(len(st.session_state.db), 3))
        for i, p in enumerate(st.session_state.db):
            is_def = (dp_idx == i)
            with cols[i % 3]:
                badge_html = '<span class="def-badge">⭐ My Profile</span><br>' if is_def else ""
                gnd = p.get("gender", "M")
                st.markdown(f"""<div class="prof-card {'prof-card-def' if is_def else 'prof-card-norm'}">
{badge_html}<p class="prof-name">{p['name']} ({gnd})</p>
<p class="prof-sub">{format_date_ui(p['date'])} · {p['time']}</p>
<p class="prof-sub">📍 {p['place'].split(',')[0]}</p>
</div>""", unsafe_allow_html=True)
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("✏️", key=f"ve_{i}", use_container_width=True, help="Edit"):
                        st.session_state.editing_idx = i; st.rerun()
                with b2:
                    if is_def:
                        if st.button("★", key=f"vd_{i}", use_container_width=True, help="Remove default"):
                            clear_default_profile(); st.rerun()
                    else:
                        if st.button("☆", key=f"vd_{i}", use_container_width=True, help="Set as my profile"):
                            set_default_profile(i); st.rerun()
                with b3:
                    if st.button("🗑️", key=f"vdel_{i}", use_container_width=True, help="Delete"):
                        st.session_state.db.pop(i)
                        sync_db()
                        if dp_idx == i:              clear_default_profile()
                        elif dp_idx is not None and dp_idx > i: set_default_profile(dp_idx - 1)
                        if st.session_state.editing_idx == i: st.session_state.editing_idx = None
                        st.rerun()

    # ── Edit form ─────────────────────────────────────────────────────────────
    if st.session_state.editing_idx is not None:
        st.markdown("---")
        ei  = st.session_state.editing_idx
        pd_ = st.session_state.db[ei]
        st.markdown(f"### ✏️ Editing: {pd_['name']}")
        e1, e2 = st.columns(2)
        with e1:
            u_name  = st.text_input("Name", pd_["name"], key="ve_n")
            u_date  = st.date_input("Date", date.fromisoformat(pd_["date"]), key="ve_d")
            pt = datetime.strptime(pd_["time"], "%H:%M").time()
            dhr = pt.hour % 12 or 12; dai = 0 if pt.hour < 12 else 1
            t1, t2, t3 = st.columns(3)
            with t1: u_hr = st.number_input("Hour", 1, 12, dhr, key="ve_hr")
            with t2: u_mi = st.number_input("Min",  0, 59, pt.minute, key="ve_mi")
            with t3: u_am = st.selectbox("AM/PM", ["AM","PM"], index=dai, key="ve_am")
            pre_gnd = pd_.get("gender", "M")
            u_gender = st.radio("Gender", ["M","F"], index=0 if pre_gnd=="M" else 1, key="ve_gnd", horizontal=True)
            u_exact  = st.checkbox("Exact Time Known", value=pd_.get("exact_time", False), key="ve_exact")
        with e2:
            is_m    = pd_["place"] == "Manual Coordinates"
            u_place = st.text_input("Birth Place", "" if is_m else pd_["place"], key="ve_p")
            manual  = st.checkbox("Manual coordinates", is_m, key="ve_man")
            det_lat = det_lon = det_tz = det_place = None
            if u_place.strip() and not manual:
                geo = geocode_place_cached(u_place.strip())
                if geo: det_lat, det_lon, det_place = geo; det_tz = timezone_for_latlon_cached(det_lat, det_lon); st.success(f"📍 {geo[2]}")
                else:   st.warning("Not found.")
            if manual:
                m1, m2, m3 = st.columns(3)
                with m1: m_lat = st.number_input("Lat", float(pd_["lat"]), format="%.4f", key="ve_lat")
                with m2: m_lon = st.number_input("Lon", float(pd_["lon"]), format="%.4f", key="ve_lon")
                with m3: m_tz  = st.text_input("TZ",   pd_["tz"],          key="ve_tz")

        b1, b2 = st.columns(2)
        if b1.button("Save Changes", type="primary"):
            h24 = (u_hr + 12 if u_am == "PM" and u_hr != 12 else 0 if u_am == "AM" and u_hr == 12 else u_hr)
            if manual:
                if not m_tz.strip(): st.error("Enter timezone."); st.stop()
                fl2, fln2, ftz2, fp2 = m_lat, m_lon, m_tz, "Manual Coordinates"
            else:
                if det_lat is None: st.error("Enter valid birth place."); st.stop()
                fl2, fln2, ftz2, fp2 = det_lat, det_lon, det_tz, det_place
                if not ftz2: st.error("Timezone failed."); st.stop()
            st.session_state.db[ei] = {
                "name": u_name, "date": u_date.isoformat(),
                "time": time(h24, u_mi).strftime("%H:%M"),
                "place": fp2, "lat": fl2, "lon": fln2, "tz": ftz2,
                "gender": u_gender, "exact_time": u_exact,
            }
            st.session_state.editing_idx = None
            sync_db()
            st.rerun()
        if b2.button("Cancel"):
            st.session_state.editing_idx = None; st.rerun()

    # ── Add new profile ───────────────────────────────────────────────────────
    st.markdown("---")
    if not st.session_state.show_add_profile:
        if st.button("➕ Add New Profile", use_container_width=True, key="toggle_add"):
            st.session_state.show_add_profile = True; st.rerun()
    else:
        st.markdown("### ➕ Add New Profile")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                v_n = st.text_input("Name", key="v_new_n")
                v_d = st.date_input("Date of Birth", date(2000,1,1), min_value=date(1850,1,1), max_value=date(2050,12,31), key="v_new_d")
                t1, t2, t3 = st.columns(3)
                with t1: v_h = st.number_input("Hour", 1, 12, 12, key="v_new_h")
                with t2: v_m = st.number_input("Min",  0, 59,  0, key="v_new_m")
                with t3: v_a = st.selectbox("AM/PM", ["AM","PM"], index=1, key="v_new_a")
                v_gender = st.radio("Gender", ["M","F"], index=0, key="v_new_gnd", horizontal=True)
                v_exact  = st.checkbox("Exact Time Known", value=False, key="v_new_exact")
            with c2:
                v_p   = st.text_input("Birth Place (City, Country)", key="v_new_p")
                v_man = st.checkbox("Manual coordinates", key="v_new_man")
                if v_man:
                    vm1, vm2, vm3 = st.columns(3)
                    with vm1: v_lat   = st.number_input("Lat", value=0.0,            format="%.4f", key="v_new_lat")
                    with vm2: v_lon_v = st.number_input("Lon", value=0.0,            format="%.4f", key="v_new_lon")
                    with vm3: v_tz    = st.text_input("TZ",    "Asia/Kolkata",                      key="v_new_tz")

            also_def = st.checkbox("Set this as my default profile", key="v_also_def")
            sa1, sa2 = st.columns(2)
            if sa1.button("Add Profile", type="primary", use_container_width=True):
                if not v_n.strip(): st.error("Name required."); st.stop()
                h24 = (v_h + 12 if v_a == "PM" and v_h != 12 else 0 if v_a == "AM" and v_h == 12 else v_h)
                if v_man:
                    if not v_tz.strip(): st.error("Timezone required."); st.stop()
                    lat, lon, tz, pn = v_lat, v_lon_v, v_tz, "Manual Coordinates"
                else:
                    if not v_p.strip(): st.error("Place required."); st.stop()
                    geo = geocode_place_cached(v_p.strip())
                    if not geo: st.error("Location not found."); st.stop()
                    lat, lon, pn = geo; tz = timezone_for_latlon_cached(lat, lon)
                new_prof = {
                    "name": v_n.strip(), "date": v_d.isoformat(),
                    "time": time(h24, v_m).strftime("%H:%M"),
                    "place": pn, "lat": lat, "lon": lon, "tz": tz,
                    "gender": v_gender, "exact_time": v_exact,
                }
                if not is_duplicate_in_db(new_prof):
                    st.session_state.db.append(new_prof)
                    sync_db()
                    if also_def: set_default_profile(len(st.session_state.db) - 1)
                    st.success("Profile added!")
                    st.session_state.show_add_profile = False
                    time_module.sleep(0.5)
                    st.rerun()
                else:
                    st.warning("Profile already exists.")
            if sa2.button("Cancel", use_container_width=True):
                st.session_state.show_add_profile = False; st.rerun()

    # ── Data backup ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💾 Data Backup")
    export_data = {"profiles": st.session_state.db, "default_idx": st.session_state.default_profile_idx}
    b1, b2 = st.columns(2)
    with b1:
        st.download_button(
            "⬇️ Export Profiles",
            data=json.dumps(export_data, indent=2),
            file_name="kundli_backup.json",
            use_container_width=True,
        )
    with b2:
        uf = st.file_uploader("Import Backup JSON", type="json", label_visibility="collapsed")
        if uf:
            try:
                imp = json.loads(uf.getvalue().decode("utf-8"))
                if isinstance(imp, dict) and "profiles" in imp:
                    st.session_state.db = imp["profiles"]
                    sync_db()
                    if imp.get("default_idx") is not None:
                        set_default_profile(imp["default_idx"])
                    st.success("Backup restored!")
                    time_module.sleep(0.5)
                    st.rerun()
                elif isinstance(imp, list):
                    st.session_state.db = imp
                    sync_db()
                    st.success("Imported.")
                    time_module.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid format.")
            except Exception as e:
                st.error(f"Invalid file: {e}")
