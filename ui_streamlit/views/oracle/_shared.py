"""
ui_streamlit/views/oracle/_shared.py
====================================
Shared imports + helpers used by every Oracle sub-view.

Why this file exists
--------------------
The Oracle has six independent features (Deep Analysis, Matchmaking,
Marriage, Gochara, Compare, Prashna). They share:
  • Common imports (math/ai/ui modules)
  • A gender-resolver (Matchmaking + Marriage both need boy/girl split)
  • A "result render + PDF download" tail that fires after generation

Putting these in one place keeps each feature file under ~100 lines.
"""

from datetime import datetime, date

import streamlit as st
import streamlit.components.v1 as components

# ── math + ai engine re-exports (so each oracle sub-file imports from here) ───
from math_engine.constants import PLANETS, SIGN_LORDS_MAP
from math_engine.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed,
    sign_index_from_lon, get_lagna_and_cusps,
)
from math_engine.dossier_builder import generate_astrology_dossier, get_gochara_overlay
from math_engine.scoring import calculate_destiny_confirmation, calculate_compatibility_index

from ai_engine.gemini_client import FREE_MODELS, agent_worker, generate_content_with_fallback
from ai_engine.prompts import (
    build_agent_parashari_prompt, build_agent_timing_prompt, build_agent_kp_prompt,
    build_master_synthesizer_prompt, build_transit_prompt, build_prashna_prompt,
    build_matchmaking_prompt, build_destiny_confirmation_prompt, build_comparison_prompt,
)
from ai_engine.knowledge import build_topic_query, build_comparison_knowledge

from ui_streamlit.state import get_default_profile, toggle_all_criteria
from ui_streamlit.helpers import get_moon_lon_from_profile
from ui_streamlit.components import render_profile_form, resolve_profile, stream_ai_with_followup
from ui_streamlit.cache import (
    geocode_place_cached, timezone_for_latlon_cached, rag_context_cached,
)

# Matchmaking-specific imports — wrapped in try because they can be absent
# during partial refactors; the matchmaking sub-view handles that gracefully.
try:
    from math_engine.astro_calc import check_manglik_dosha, get_manglik_cancellation_verdict
    from math_engine.dossier_builder import calculate_matchmaking_synastry
except ImportError:   # pragma: no cover
    check_manglik_dosha = None
    get_manglik_cancellation_verdict = None
    calculate_matchmaking_synastry = None


# ── small parse helpers used by Matchmaking + Marriage ────────────────────────

def parse_date(p):
    """Convert profile['date'] (str or date) to a date object."""
    return date.fromisoformat(p["date"]) if isinstance(p["date"], str) else p["date"]


def parse_time(p):
    """Convert profile['time'] (str or time) to a time object."""
    return datetime.strptime(p["time"], "%H:%M").time() if isinstance(p["time"], str) else p["time"]


def resolve_boy_girl(profiles):
    """Given a list of 2 profiles, return (boy_profile, girl_profile) by
    checking the `gender` field. Falls back to profile-order if both have
    the same gender (or none). Used by Matchmaking + Marriage sub-views.
    """
    p_boy  = profiles[0] if profiles[0].get("gender") == "M" else profiles[1]
    p_girl = profiles[1] if p_boy == profiles[0] else profiles[0]
    if p_boy == p_girl:
        p_boy, p_girl = profiles[0], profiles[1]
    return p_boy, p_girl


# ── collapsed-sidebar JS used by every oracle sub-view on mobile ──────────────

def collapse_sidebar_on_mobile():
    """Inject one-liner JS that auto-collapses the Streamlit sidebar on mobile
    so the oracle view gets full width. Called at the top of every sub-view."""
    components.html(
        '<script>setTimeout(function(){'
        'var b=window.parent.document.querySelector(\'button[aria-label="Collapse sidebar"]\');'
        'if(b&&window.parent.innerWidth<=768)b.click();},80);</script>',
        height=0, width=0,
    )


# ── shared PDF download tail used by Deep / Matchmaking / Marriage / Compare ──

def render_pdf_download(mission_key, feature_title, feature_emoji, history, dp):
    """Render the "Download PDF" button below a pre-generated reading.

    Args:
        mission_key   : the mission identifier (used in download filename)
        feature_title : e.g. "Full Life Reading"
        feature_emoji : e.g. "★"
        history       : the session-state history list (oracle_<mission>_history)
        dp            : default profile dict, or None
    """
    last_model = next(
        (m.get("display") or (m.get("parts") or [""])[0]
         for m in reversed(history) if m.get("role") == "model"),
        None,
    )
    if not last_model or last_model.startswith("⚠️") or not history:
        return
    try:
        from ui_streamlit.views.astro_pdf import build_astro_pdf
        import datetime as _dt
        pdf = build_astro_pdf(
            feature_title=feature_title, feature_emoji=feature_emoji,
            sections=[{"heading": "", "body": last_model}],
            user_name=dp.get("name", "") if dp else "",
            metadata={"Date": _dt.datetime.now().strftime("%B %d, %Y")},
        )
        st.download_button(
            "⬇ Download PDF", data=pdf,
            file_name=f"oracle_{mission_key.lower().replace(' ','_')}.pdf",
            mime="application/pdf", key=f"oracle_pdf_{mission_key}",
        )
    except Exception:
        pass


def render_chat_history(history):
    """Render the chat-style message history for pre-generated oracle readings."""
    for msg in history:
        if msg.get("hidden", False):
            continue
        with st.chat_message(msg["role"], avatar="🪐" if msg["role"] == "model" else "👤"):
            display = msg.get("display") or (msg.get("parts") or [""])[0]
            st.markdown(display)
