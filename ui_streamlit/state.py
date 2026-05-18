"""
ui_streamlit/state.py

Single home for every session-state helper.
Both components.py and all page files import from here.
app.py imports from here too — no more monkey patching.

Future: when you add FastAPI, these helpers simply don't exist there —
        the API layer uses a database instead of st.session_state.
"""

import streamlit as st
from shared.astro.constants import COMPARISON_CRITERIA


# ── Profile DB helpers ────────────────────────────────────────────────────────

def sync_db():
    """Flag that the vault needs to be written to LocalStorage."""
    st.session_state.needs_sync = True


def is_duplicate_in_db(p: dict) -> bool:
    return any(
        x["name"] == p["name"] and x["date"] == p["date"]
        for x in st.session_state.db
    )


def get_default_profile():
    """Returns (profile_dict, index) or (None, None)."""
    idx = st.session_state.default_profile_idx
    if idx is not None and 0 <= idx < len(st.session_state.db):
        return st.session_state.db[idx], idx
    return None, None


def set_default_profile(idx: int):
    st.session_state.default_profile_idx = idx
    st.session_state.needs_sync = True
    st.toast("⭐ Default profile locked!")


def clear_default_profile():
    st.session_state.default_profile_idx = None
    st.session_state.needs_sync = True
    st.toast("Default profile cleared.")


def sorted_profile_options():
    """Returns [(original_index, profile_dict), ...] with the default first."""
    if not st.session_state.db:
        return []
    def_idx = st.session_state.default_profile_idx
    result = list(enumerate(st.session_state.db))
    if def_idx is not None and 0 <= def_idx < len(st.session_state.db):
        result.sort(key=lambda x: 0 if x[0] == def_idx else 1)
    return result


# ── Formatting helpers ────────────────────────────────────────────────────────

def format_date_ui(s: str) -> str:
    from datetime import datetime
    return datetime.fromisoformat(s).strftime("%d %b %Y")


# get_filename moved to features/tarot/constants.py as card_image_filename
# Re-exported here for backward compatibility (components.py imports from here).
from features.tarot.constants import card_image_filename as get_filename


# ── Criteria helpers ──────────────────────────────────────────────────────────

def toggle_all_criteria():
    v = st.session_state.select_all_cb
    for i in range(len(COMPARISON_CRITERIA)):
        st.session_state[f"chk_{i}"] = v
    for i in range(len(st.session_state.custom_criteria)):
        st.session_state[f"cc_{i}"] = v


# ── Session state initialisation ─────────────────────────────────────────────

def init_session_state():
    """
    Call once at the top of app.py.
    Initialises every key so the rest of the app can read them safely.
    """
    defaults = {
        "db":                   [],
        "db_loaded":            False,
        "default_profile_idx":  None,
        "needs_sync":           False,
        "custom_criteria":      [],
        "editing_idx":          None,
        "comp_slots":           2,
        "nav_page":             "Dashboard",
        "active_mission":       "Deep Personal Analysis",
        "tarot_tab":            "three",
        "tarot3_drawn":         False,
        "tarot3_cards":         [],
        "tarot3_states":        [],
        "tarot3_mode":          "General Guidance",
        "yn_drawn":             False,
        "yn_card":              None,
        "yn_state":             None,
        "cc_drawn":             False,
        "cc_cards":             [],
        "cc_states":            [],
        "bc_revealed":          False,
        "bc_dob":               None,
        "dash_tarot_card":      None,
        "dash_tarot_state":     None,
        "dash_tarot_date":      None,
        "show_add_profile":     False,
        "select_all_cb":        False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    for i in range(len(COMPARISON_CRITERIA)):
        if f"chk_{i}" not in st.session_state:
            st.session_state[f"chk_{i}"] = False
