"""
fastapi_main.py
===============

The single backend entrypoint for the mobile app + new website.

What this file does
-------------------
1. Reads GEMINI_API_KEY + Qdrant creds from environment variables (or from
   .streamlit/secrets.toml if present — for dev parity with Streamlit Cloud).
2. Initialises the shared Gemini client + Swiss Ephemeris path.
3. Mounts every feature's `api.py` router under a clean URL prefix.

Run locally
-----------
    pip install fastapi uvicorn[standard]
    uvicorn fastapi_main:app --reload

Deploy on Render
----------------
    Start command: uvicorn fastapi_main:app --host 0.0.0.0 --port $PORT
    Set env vars in the Render dashboard: GEMINI_API_KEY, QDRANT_URL,
    QDRANT_API_KEY.

URL map
-------
    /                            health check
    /tarot/draw-session          POST  features/tarot/api.py  (picker step 1)
    /tarot/reveal                POST                         (picker step 2)
    /tarot/three-card            POST   (legacy auto-draw, kept for compat)
    /tarot/yes-no                POST
    /tarot/celtic-cross          POST
    /tarot/birth-card            POST
    /horoscopes/western          POST  features/horoscopes/api.py
    /horoscopes/vedic            POST
    /numerology/full-report      POST  features/numerology/api.py
    /numerology/cycles           POST
    /consultation/ask            POST  features/consultation/api.py
    /dashboard/data              POST  features/dashboard/api.py
    /dashboard/decide            POST
    /kundli/compute              POST  features/kundli/api.py
    /kundli/free-reading         POST
    /kundli/premium-pdf          POST
    /palmistry/scan              POST  features/palmistry/api.py
    /palmistry/read              POST  features/palmistry/api.py
    /face_reading/read           POST  features/face_reading/api.py
    /vault/{user_id}             GET/POST/PUT/DELETE  features/vault/api.py
    /me/profiles                 GET/POST  features/me/api.py  (Supabase; JWT required)
    /me/profiles/{id}            PUT/DELETE
    /me/checkins                 GET/POST  (POST upserts + bumps the check-in streak)
    /me/journal                  GET/POST
    /me/streaks/{kind}           GET
    /people/couple-week          POST  features/people/api.py  (2-chart 7-day weather)
    /people/family-grid          POST                          (today's grid, several people)
    /companion/micro-insight     POST  features/companion/api.py  (Day-1 mirror)
    /companion/patterns          GET                              (Pattern Engine; JWT required)
    /companion/proof             POST                             ("why did that happen?" past date)
    /reflect/purpose             POST  features/reflect/api.py  (soul/career blueprint)
    /reflect/year                POST                          (Year in Review — Cosmic Wrapped)
    /chart/interpret             POST  features/chart/api.py  (plain-English chart "front room")
    /chart/houses                POST                          (all 12 houses, warm)
    /chart/planets               POST                          (each planet in sign+house, warm)
    /docs                        Interactive Swagger UI (built into FastAPI)

Auth note
---------
The /me/* endpoints require a Supabase JWT: `Authorization: Bearer <token>`.
The mobile app gets that token from Supabase Auth (client-side sign-in); this
backend verifies it and resolves the user_id. All other routers are unchanged.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ─────────────────────────────────────────────────────────────────────────────
# Env / secrets — env var first, .streamlit/secrets.toml fallback for dev
# ─────────────────────────────────────────────────────────────────────────────

def _load_secret(key: str) -> str | None:
    """Read `key` from env first, then .streamlit/secrets.toml if present."""
    v = os.environ.get(key)
    if v:
        return v
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        try:
            import tomllib
            with open(secrets_path, "rb") as f:
                data = tomllib.load(f)
            return data.get(key)
        except Exception:
            return None
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Init shared services (Gemini, Swiss Ephemeris)
# ─────────────────────────────────────────────────────────────────────────────

def _init_backend() -> None:
    # Gemini — guarded: a missing AI library must not crash the math-only API
    # (e.g. a lean deploy that only serves /kundli, or local chart dev). The
    # AI-powered endpoints simply stay unavailable until the lib is installed.
    gemini_key = _load_secret("GEMINI_API_KEY")
    if gemini_key:
        try:
            from shared.ai.gemini_client import init_gemini
            init_gemini(gemini_key)
        except Exception as e:
            print(f"[fastapi_main] WARNING: Gemini init skipped: "
                  f"{type(e).__name__}: {e}")

    # DeepSeek — optional, only needed if a model in config.py points at it
    deepseek_key = _load_secret("DEEPSEEK_API_KEY")
    if deepseek_key:
        try:
            from shared.ai.deepseek_client import init_deepseek
            init_deepseek(deepseek_key)
        except Exception as e:
            print(f"[fastapi_main] WARNING: DeepSeek init skipped: "
                  f"{type(e).__name__}: {e}")

    # Ephemeris: handled in shared.astro.ephemeris (Skyfield default — no setup
    # required, no SE in the shipping runtime). See docs/ephemeris-decision.md.


_init_backend()


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Myastro API",
    description=(
        "Vedic-astrology + AI divination backend. Powers the mobile app + "
        "website. The Streamlit app at ui_streamlit/app.py talks to the same "
        "Python services directly (no HTTP); this API is for the mobile + "
        "web clients."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten when you know your web app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health() -> dict:
    """Health check. UptimeRobot pings this every 5 minutes."""
    return {"ok": True, "service": "myastro-api", "version": "1.0.0"}


# ─────────────────────────────────────────────────────────────────────────────
# Mount every feature's router
# ─────────────────────────────────────────────────────────────────────────────

_FEATURES = [
    ("tarot",        "features.tarot.api"),
    ("horoscopes",   "features.horoscopes.api"),
    ("numerology",   "features.numerology.api"),
    ("consultation", "features.consultation.api"),
    ("dashboard",    "features.dashboard.api"),
    ("kundli",       "features.kundli.api"),
    ("palmistry",    "features.palmistry.api"),     # /scan, /read (role-labelled palm captures)
    ("face_reading", "features.face_reading.api"),  # /read (photo; optional kundli cross-ref)
    ("vault",        "features.vault.api"),
    ("oracle",       "features.oracle.api"),   # /deep-analysis, /matchmaking, /marriage, /gochara, /compare, /prashna
    ("me",           "features.me.api"),       # authenticated user data: profiles/checkins/journal/streaks (Supabase + RLS)
    ("people",       "features.people.api"),   # /couple-week, /family-grid — shared-day readings across 2+ charts (pure math)
    ("companion",    "features.companion.api"), # /micro-insight, /patterns (JWT), /proof — the Companion's payoffs (pure math)
    ("reflect",      "features.reflect.api"),   # /purpose, /year — big-picture soul/career blueprint + Cosmic Wrapped (pure math)
    ("chart",        "features.chart.api"),     # /interpret — plain-English chart "front room" (warm cards, no AI)
    ("rituals",      "features.rituals.api"),   # /remedies — chart-derived remedies for the Rituals tab (pure math)
    ("wallet",       "features.wallet.api"),    # /prices (public) + Diya balance/spend/earn/history (JWT, server-authoritative)
    ("geo",          "features.geo.api"),       # /search — place autocomplete (label/lat/lon/tz) for onboarding (public)
    ("memory",       "features.memory.api"),    # THE MEMORY (JWT): /facts, /extract, /context — auto-remembered distilled facts
    ("talk",         "features.talk.api"),       # voice companion: POST /talk -> short warm spoken reply (+Kokoro audio if KOKORO_URL set)
    ("planner",      "features.planner.api"),    # My Day (Today→Plan, JWT): /tasks CRUD — to-dos auto-placed in the day's best windows
    ("capsule",      "features.capsule.api"),    # Time Capsule (Today→Plan, JWT): note delivered at a future moment (custom/birthday/dasha/jupiter)
    ("moon",         "features.moon.api"),       # the proactive companion, the Sage (JWT): /check, /messages — openers that glow the floating Sage (module name 'moon' is legacy)
    ("notify",       "features.notify.api"),     # closed-app push: /run-daily (cron-secret) pushes the Sage's opener + capsule arrivals; /test (JWT) pushes to your own device
]

for prefix, module_path in _FEATURES:
    try:
        module = __import__(module_path, fromlist=["router"])
        router = getattr(module, "router", None)
        if router is not None:
            app.include_router(router, prefix=f"/{prefix}", tags=[prefix])
    except Exception as e:
        # Log but don't crash — let the rest of the app come up
        print(f"[fastapi_main] WARNING: failed to mount /{prefix}: "
              f"{type(e).__name__}: {e}")
