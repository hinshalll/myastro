# features/me — the authenticated user's stateful core

This is the **data-layer foundation**: the first feature that reads/writes the
live Supabase database. It unlocks every stateful feature (Companion, Pattern
Engine, the Mirror journal, streaks, social, coins).

## What it does
Per-user CRUD for the core tables, keyed off the **Supabase-authenticated user**:

| Endpoint | Method | Purpose |
|---|---|---|
| `/me/profiles` | GET | List the user's saved profiles (self + people). |
| `/me/profiles` | POST | Create a profile. |
| `/me/profiles/{id}` | PUT | Update a profile. |
| `/me/profiles/{id}` | DELETE | Delete a profile. |
| `/me/checkins` | GET | List recent check-ins (Pattern Engine input). |
| `/me/checkins` | POST | Upsert today's check-in **and bump the check-in streak**. |
| `/me/journal` | GET | List Mirror journal entries (private). |
| `/me/journal` | POST | Save a journal entry. |
| `/me/streaks/{kind}` | GET | Get a streak (e.g. `checkin`). |

## Auth (how the user is resolved)
Every endpoint requires a Supabase JWT:

```
Authorization: Bearer <access_token>
```

The mobile app signs the user in **client-side** with Supabase Auth and sends
that token. `features/me/auth.py` verifies it against Supabase and builds a
**user-scoped** Supabase client. All queries run as that user, so **Postgres
Row-Level Security enforces owner-only access** — even if app code had a bug,
the database refuses cross-user reads/writes.

`get_current_user` is reusable: any future feature router that needs a logged-in
user can import it.

## Files (per-feature pattern)
- `schemas.py` — Pydantic request models (`ProfileIn`, `CheckinIn`, `JournalIn`).
- `service.py` — thin layer over `shared.db.supabase_client`, scoped to the user.
- `api.py` — the FastAPI router (mounted at `/me` in `fastapi_main.py`).
- `auth.py` — JWT verification + the `CurrentUser` dependency.

## The data layer underneath (`shared/db/`)
- `secrets.py` — env-first, then `.streamlit/secrets.toml`; never hardcodes.
- `supabase_client.py` — service client (server-only, bypasses RLS) + user client
  (RLS-scoped) + token verification + CRUD for profiles/checkins/journal/streaks.
- `cache.py` — `cached_daily` (shared, keyed by date + astro_state) and
  `cached_chart` (per-profile, keyed including birth-time precision) — the cost rule.

> `shared/*` never imports Streamlit, and the **service_role key is server-only**.

## Setup
1. Create a Supabase project and run `supabase/schema.sql` in its SQL editor.
2. Put `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` in `.env`
   (see `.env.example`) or `.streamlit/secrets.toml`.
3. `pip install supabase` (already in `requirements.txt`).
