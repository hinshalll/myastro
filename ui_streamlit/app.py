"""
ui_streamlit/app.py  (entry point — run with: streamlit run ui_streamlit/app.py)

Responsibilities:
  1. Page config + Swiss Ephemeris setup
  2. Init Gemini (ONE call, centralised in shared.ai)
  3. Load profiles from LocalStorage into session state
  4. Route nav_page to the right show_*() function
  5. Flush LocalStorage when needs_sync is True

Nothing else lives here. All helpers are in state.py.
All page logic is in pages/.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import streamlit as st
import swisseph as swe
from streamlit_local_storage import LocalStorage

# ── engine imports ────────────────────────────────────────────────────────────
from shared.astro.constants import NAV_PAGES, COMPARISON_CRITERIA
from shared.ai.gemini_client import init_gemini

# ── ui imports ────────────────────────────────────────────────────────────────
from ui_streamlit.state import (
    init_session_state,
    set_default_profile,
)
from ui_streamlit.components import inject_nebula_css, render_sidebar, render_bottom_nav
from features.dashboard.view           import show_dashboard
from features.consultation.view        import show_consultation_room
from features.oracle         import show_oracle
from features.tarot.view               import show_tarot
from features.horoscopes.view          import show_horoscopes
from features.numerology.view          import show_numerology
from features.vault.view               import show_vault
from features.palmistry.view           import show_palmistry
from features.face_reading.view         import show_face_reading
from features.kundli.view              import show_kundli

# ── page config ───────────────────────────────────────────────────────────────
APP_NAME = "ASTRO SUITE beta"
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Swiss Ephemeris ───────────────────────────────────────────────────────────
try:
    swe.set_ephe_path("ephe")
except Exception:
    pass
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ── AI keys — configured ONCE here, used everywhere via shared.ai ─────────────
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY in .streamlit/secrets.toml")
    st.stop()
init_gemini(api_key)

# DeepSeek is optional — only needed if a model in config.py points at it.
deepseek_key = st.secrets.get("DEEPSEEK_API_KEY")
if deepseek_key:
    from shared.ai.deepseek_client import init_deepseek
    init_deepseek(deepseek_key)

# ── LocalStorage ─────────────────────────────────────────────────────────────
localS = LocalStorage()

# ── Session state — one clean call ───────────────────────────────────────────
init_session_state()

# ── Handle deep-link ?p= query param ─────────────────────────────────────────
_qp = st.query_params.get("p", "")
if _qp in NAV_PAGES:
    if st.session_state.nav_page != _qp:
        st.session_state.nav_page = _qp

# ── Load profiles from LocalStorage (once per session) ───────────────────────
if not st.session_state.db_loaded:
    saved = localS.getItem("kundli_vault")
    if saved is not None:
        if isinstance(saved, str) and saved.strip():
            try:
                st.session_state.db = json.loads(saved)
            except Exception:
                pass
        elif isinstance(saved, list):
            st.session_state.db = saved

    di = localS.getItem("kundli_default")
    try:
        st.session_state.default_profile_idx = (
            int(di) if di is not None and str(di).strip().isdigit() else None
        )
    except Exception:
        st.session_state.default_profile_idx = None

    st.session_state.db_loaded = True

# ── UI shell ──────────────────────────────────────────────────────────────────
inject_nebula_css()
render_sidebar()
render_bottom_nav()

# ── Page routing ──────────────────────────────────────────────────────────────
_ROUTES = {
    "Dashboard":         show_dashboard,
    "Consultation Room": show_consultation_room,
    "The Oracle":        show_oracle,
    "Mystic Tarot":      show_tarot,
    "Horoscopes":        show_horoscopes,
    "Numerology":        show_numerology,
    "Palm Reading":      show_palmistry,
    "Face Reading":      show_face_reading,
    "Kundli":            show_kundli,
    "Saved Profiles":    show_vault,
}
_ROUTES.get(st.session_state.nav_page, show_dashboard)()

# ── Flush LocalStorage ────────────────────────────────────────────────────────
if st.session_state.get("needs_sync", False):
    localS.setItem("kundli_vault", json.dumps(st.session_state.db), key="save_vault_data")
    if st.session_state.default_profile_idx is not None:
        localS.setItem(
            "kundli_default",
            str(st.session_state.default_profile_idx),
            key="save_default_data",
        )
    else:
        localS.setItem("kundli_default", "", key="clear_default_data")
    st.session_state.needs_sync = False
