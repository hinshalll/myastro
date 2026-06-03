"""shared.db — the Supabase data layer (Streamlit-free).

Import the pieces you need:

    from shared.db.supabase_client import (
        get_service_client, get_user_client, get_user_id_from_token,
    )
    from shared.db import supabase_client as db   # CRUD: profiles/checkins/journal/streaks
    from shared.db import cache                    # cached_daily / cached_chart helpers

Rules (non-negotiable):
  • Nothing in this package imports streamlit (shared purity rule).
  • Secrets come from env first, then .streamlit/secrets.toml (see shared.db.secrets).
  • The service_role key is SERVER-ONLY — never shipped to the mobile app.
"""
