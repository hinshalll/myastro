"""
ui_streamlit/views/oracle/
==========================
The Oracle is now a package of 6 independent features, each in its own
file. Each `show_X()` is a complete entry-point that can be plugged
straight into a mobile-app screen or a website page later.

  ┌──────────────────────────┬──────────────────────────────────────┐
  │ Feature                  │ Module                               │
  ├──────────────────────────┼──────────────────────────────────────┤
  │ Full Life Reading        │ oracle.deep_analysis.show_deep_analysis │
  │ Compatibility Match      │ oracle.matchmaking.show_matchmaking  │
  │ Destiny Marriage Matrix  │ oracle.marriage.show_marriage        │
  │ Live Transit (Gochara)   │ oracle.gochara.show_gochara          │
  │ Compare Profiles         │ oracle.compare.show_compare          │
  │ Prashna (Horary)         │ oracle.prashna.show_prashna          │
  └──────────────────────────┴──────────────────────────────────────┘

The legacy entry-point `show_oracle()` keeps working for the current
Streamlit app — it presents a dropdown that dispatches to the six
sub-views. When you switch to Next.js / Flutter, each `show_X()` is
already a standalone screen.
"""

import streamlit as st

from ui_streamlit.views.oracle._shared import collapse_sidebar_on_mobile

# Re-export each show_*() so external code can import directly if it wants
# to skip the legacy dropdown (e.g. when building a separate menu).
from ui_streamlit.views.oracle.deep_analysis import show_deep_analysis
from ui_streamlit.views.oracle.matchmaking   import show_matchmaking
from ui_streamlit.views.oracle.marriage      import show_marriage
from ui_streamlit.views.oracle.gochara       import show_gochara
from ui_streamlit.views.oracle.compare       import show_compare
from ui_streamlit.views.oracle.prashna       import show_prashna


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


__all__ = [
    "show_oracle",
    "show_deep_analysis", "show_matchmaking", "show_marriage",
    "show_gochara", "show_compare", "show_prashna",
]
