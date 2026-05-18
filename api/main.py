"""
api/main.py — FastAPI entry point for the AIS backend
=====================================================

This is the HTTP backend that the mobile app (Flutter) and the website
(Next.js) will call. It wraps the existing math_engine, ai_engine, and
pdf_engine layers — all the real logic lives there, untouched.

Run locally:
    uvicorn api.main:app --reload --port 8000

Then open:
    http://localhost:8000/docs    # interactive API documentation
    http://localhost:8000/health  # health check

Deploy on Render:
    Build command:  pip install -r requirements.txt
    Start command:  uvicorn api.main:app --host 0.0.0.0 --port $PORT

The same code runs on Render free tier, on a VPS, and on your laptop.
No Docker required, no platform-specific config.

──────────────────────────────────────────────────────────────────────
Directory layout (mirrors the mobile-app feature structure):

    api/
    ├── main.py                ← this file
    ├── schemas.py             ← Pydantic request/response models
    ├── deps.py                ← shared dependencies (Gemini init, etc.)
    └── routers/
        ├── profiles.py        ← /api/v1/profiles/*
        ├── kundli.py          ← /api/v1/kundli/*
        ├── palm.py            ← /api/v1/palm/*
        ├── tarot.py           ← /api/v1/tarot/*
        ├── numerology.py      ← /api/v1/numerology/*
        ├── horoscopes.py      ← /api/v1/horoscopes/*
        ├── consultation.py    ← /api/v1/consultation/*
        └── oracle/
            ├── deep_analysis.py    ← /api/v1/oracle/deep-analysis
            ├── matchmaking.py      ← /api/v1/oracle/matchmaking
            ├── marriage.py         ← /api/v1/oracle/marriage
            ├── gochara.py          ← /api/v1/oracle/gochara
            ├── compare.py          ← /api/v1/oracle/compare
            └── prashna.py          ← /api/v1/oracle/prashna

Each router is small (≤100 lines) and wraps the corresponding engine
function. To add a new feature: create a new router file, mount it
below. No other changes needed.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import init_app_singletons

# ── App init ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Myastro Backend",
    description="Vedic-astrology + AI divination backend. "
                "Powers the Myastro web app and the mobile app via the same endpoints.",
    version="1.0.0",
)

# ── CORS — allow mobile + web clients to call this API ────────────────────────
# In production, replace allow_origins with your real domains
# (e.g. ["https://astrosuite.com", "https://astrosuite-mobile.app"]).
# For now, "*" is fine because the API is in development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── One-time setup (Swiss Ephemeris path + Gemini init) ───────────────────────
@app.on_event("startup")
async def _startup():
    init_app_singletons()


# ── Health check (Render + UptimeRobot use this to know the service is alive) ─
# Accepts BOTH GET and HEAD because UptimeRobot's free tier only sends HEAD
# requests. The default `@app.get` decorator only accepts GET, which would
# return 405 to HEAD checks. `api_route` lets one handler serve both methods.
@app.api_route("/", methods=["GET", "HEAD"], tags=["meta"])
async def root():
    return {
        "service": "Myastro Backend",
        "status":  "ok",
        "docs":    "/docs",
        "version": "1.0.0",
    }


@app.api_route("/health", methods=["GET", "HEAD"], tags=["meta"])
async def health():
    return {"status": "ok"}


# ── Mount all feature routers under /api/v1 ───────────────────────────────────
from api.routers import (
    profiles, kundli, palm, tarot, numerology, horoscopes, consultation,
)
from api.routers.oracle import (
    deep_analysis as oracle_deep_analysis,
    matchmaking   as oracle_matchmaking,
    marriage      as oracle_marriage,
    gochara       as oracle_gochara,
    compare       as oracle_compare,
    prashna       as oracle_prashna,
)

API_PREFIX = "/api/v1"

app.include_router(profiles.router,     prefix=API_PREFIX)
app.include_router(kundli.router,       prefix=API_PREFIX)
app.include_router(palm.router,         prefix=API_PREFIX)
app.include_router(tarot.router,        prefix=API_PREFIX)
app.include_router(numerology.router,   prefix=API_PREFIX)
app.include_router(horoscopes.router,   prefix=API_PREFIX)
app.include_router(consultation.router, prefix=API_PREFIX)

app.include_router(oracle_deep_analysis.router, prefix=API_PREFIX)
app.include_router(oracle_matchmaking.router,   prefix=API_PREFIX)
app.include_router(oracle_marriage.router,      prefix=API_PREFIX)
app.include_router(oracle_gochara.router,       prefix=API_PREFIX)
app.include_router(oracle_compare.router,       prefix=API_PREFIX)
app.include_router(oracle_prashna.router,       prefix=API_PREFIX)
