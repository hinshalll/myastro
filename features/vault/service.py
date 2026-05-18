"""features.vault.service — pure-Python profile helpers.

Currently a thin re-export. The real implementations live in ui_streamlit/state.py
(localStorage-coupled). When the mobile app + FastAPI are built, this file will
hold the storage-agnostic versions.
"""

from ui_streamlit.state import (
    is_duplicate_in_db, sync_db,
    get_default_profile, set_default_profile, clear_default_profile,
    format_date_ui,
)


__all__ = [
    "is_duplicate_in_db", "sync_db",
    "get_default_profile", "set_default_profile", "clear_default_profile",
    "format_date_ui",
]
