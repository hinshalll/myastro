"""features.oracle._dropdown — the legacy Streamlit dropdown entry-point.

This is Streamlit-only code (it imports `streamlit` and the six `show_*`
sub-views). It lives in its own module so that importing the `features.oracle`
package itself stays Streamlit-free — the FastAPI router (`features.oracle.api`)
must be importable on a server that has no Streamlit installed.

The package `__init__.py` loads `show_oracle` from here lazily (PEP 562), so
this module is only imported when the Streamlit app actually asks for it.
"""

import streamlit as st

from features.oracle._shared import collapse_sidebar_on_mobile
from features.oracle.deep_analysis import show_deep_analysis
from features.oracle.matchmaking   import show_matchmaking
from features.oracle.marriage      import show_marriage
from features.oracle.gochara       import show_gochara
from features.oracle.compare       import show_compare
from features.oracle.prashna       import show_prashna


# Legacy dropdown labels — kept as-is so st.session_state.active_mission
# values created before the refactor still resolve correctly.
_MISSIONS = {
    "Deep Personal Analysis":         "🔮 Full Life Reading",
    "Matchmaking / Compatibility":    "✦ Compatibility Match",
    "Destiny & Marriage Chances":     "💞 Marriage Chances Calculator",
    "Gochara / Live Transit":         "🌍 Live Transit Analysis",
    "Comparison (Multiple Profiles)": "⚖ Compare Profiles",
    "Prashna Kundli":                 "🎯 Ask a Question",
}

# Dispatch table — maps the mission key to its show function.
_DISPATCH = {
    "Deep Personal Analysis":         show_deep_analysis,
    "Matchmaking / Compatibility":    show_matchmaking,
    "Destiny & Marriage Chances":     show_marriage,
    "Gochara / Live Transit":         show_gochara,
    "Comparison (Multiple Profiles)": show_compare,
    "Prashna Kundli":                 show_prashna,
}


def show_oracle():
    """Legacy Oracle dropdown — kept for backward compatibility with the
    current Streamlit app. Renders the tool selector and dispatches to
    the appropriate sub-view."""
    collapse_sidebar_on_mobile()
    st.markdown("<h1>🔮 The Oracle</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,.6)'>"
        "Mathematically locked AI prompts from Swiss Ephemeris precision.</p>",
        unsafe_allow_html=True,
    )

    cur = st.session_state.active_mission if st.session_state.active_mission in _MISSIONS \
          else "Deep Personal Analysis"
    cur_label = _MISSIONS.get(cur, "🔮 Full Life Reading")
    sel_label = st.selectbox(
        "Select Tool", list(_MISSIONS.values()),
        index=list(_MISSIONS.values()).index(cur_label),
        label_visibility="collapsed",
    )
    mid = [k for k, v in _MISSIONS.items() if v == sel_label][0]
    st.session_state.active_mission = mid
    _DISPATCH[mid]()
