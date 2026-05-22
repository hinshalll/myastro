# Myastro

Vedic-astrology + AI divination app. Two front-ends share one backend:

- **Streamlit web app** (current) — `ui_streamlit/app.py`
- **FastAPI service** for mobile + new website (ready, not yet hosted) — `fastapi_main.py`

## For AI assistants

**Read `FEATURE_SPEC.md` first.** It is the single source of truth for what every feature does, what AI it uses, what RAG books, and what's where in the code. Each `features/<feature>/README.md` adds a plain-English page about that feature.

## Project layout

```
features/        ← User-visible features, one folder each.
                   tarot / horoscopes / numerology / consultation /
                   dashboard / kundli / palmistry / oracle / vault

shared/          ← Backend plumbing shared across features.
  astro/         ← Swiss Ephemeris + dasha + scoring + chart compute
  ai/            ← Gemini client + RAG (Qdrant) + cross-cutting prompts
  pdf/           ← WeasyPrint + 7 premium themes + PDF helpers

ui_streamlit/    ← Streamlit shell only.
                   app.py (entry) / components.py / cache.py /
                   helpers.py / state.py

fastapi_main.py  ← FastAPI entry point. Mounts every features/<feat>/api.py
                   router. Run: uvicorn fastapi_main:app

ephe/            ← Swiss Ephemeris data files (used by shared/astro/)
scripts/         ← Smoke tests
qdrant_utils.py  ← Vector-store glue
```

Each `features/<feature>/` has the same six files:

```
__init__.py / README.md / prompts.py / service.py / schemas.py / view.py / api.py
```

To edit one feature → open its folder, edit those files. To add one → copy a folder.

(A feature may add its own assets too — e.g. `features/tarot/picker/` holds the swipe-picker custom component.)

## Running locally

### Streamlit (the web app you can see)

```bash
pip install -r requirements.txt
streamlit run ui_streamlit/app.py
```

Needs `.streamlit/secrets.toml` with `GEMINI_API_KEY` (+ optional `QDRANT_URL` / `QDRANT_API_KEY`, and optional `TAROT_DRAW_SECRET` to sign tarot draw tokens in production).

### FastAPI (the backend for the mobile app + new website)

```bash
pip install -r requirements.txt
uvicorn fastapi_main:app --reload
```

Reads `GEMINI_API_KEY` from env first, falls back to `.streamlit/secrets.toml`.

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Deployment

- **Streamlit Cloud** — already deployed, auto-redeploys on `git push`
- **FastAPI** — deploy `fastapi_main.py` to Render with start command:
  ```
  uvicorn fastapi_main:app --host 0.0.0.0 --port $PORT
  ```
  See `DEPLOY.md`.
