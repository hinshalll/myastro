"""shared.db.secrets — read Supabase credentials safely.

Resolution order for every key:
    1. environment variable  (how Render / production sets it)
    2. .streamlit/secrets.toml  (dev parity with the Streamlit app)

NEVER imports streamlit (shared purity rule). NEVER hardcodes a key.
"""
from __future__ import annotations

import os
from pathlib import Path

# repo root = shared/db/secrets.py → parents[2]
_SECRETS_TOML = Path(__file__).resolve().parents[2] / ".streamlit" / "secrets.toml"


def get_secret(key: str, default: str | None = None) -> str | None:
    """Return `key` from env first, then .streamlit/secrets.toml, else `default`."""
    val = os.environ.get(key)
    if val:
        return val
    if _SECRETS_TOML.exists():
        try:
            import tomllib  # py3.11+
            with open(_SECRETS_TOML, "rb") as f:
                data = tomllib.load(f)
            toml_val = data.get(key)
            if toml_val:
                return str(toml_val)
        except Exception:
            pass
    return default


def supabase_url() -> str | None:
    return get_secret("SUPABASE_URL")


def supabase_anon_key() -> str | None:
    """Safe to ship in the app (RLS protects the data)."""
    return get_secret("SUPABASE_ANON_KEY")


def supabase_service_role_key() -> str | None:
    """SERVER-ONLY. Bypasses RLS — never expose to the mobile app."""
    return get_secret("SUPABASE_SERVICE_ROLE_KEY")
