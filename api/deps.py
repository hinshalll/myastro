"""
api/deps.py — Shared initialisation + dependencies
==================================================

Anything that needs to be set up ONCE at app start lives here:
  • Swiss Ephemeris path
  • Swiss Ephemeris sidereal mode (Lahiri)
  • Gemini API client
  • (later) Supabase client, Qdrant client

Called from api/main.py on startup.
"""

import os
import swisseph as swe
from ai_engine.gemini_client import init_gemini


def init_app_singletons():
    """Run at FastAPI startup. Idempotent — safe to call multiple times."""
    # Swiss Ephemeris
    try:
        # Search for ephe/ relative to repo root regardless of where uvicorn is run
        here = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(here)
        ephe_path = os.path.join(repo_root, "ephe")
        if os.path.isdir(ephe_path):
            swe.set_ephe_path(ephe_path)
        else:
            swe.set_ephe_path("ephe")   # fallback to cwd
    except Exception:
        pass
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Gemini API — reads key from env var GEMINI_API_KEY (set in Render
    # dashboard / .env locally / hosting provider secret manager).
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        init_gemini(api_key)
    else:
        # Don't crash on startup if key is missing — endpoints that need
        # Gemini will return a clear error. This lets you boot the API
        # in environments where you only want to test non-AI endpoints.
        print("⚠️  GEMINI_API_KEY env var not set — AI endpoints will fail.")
