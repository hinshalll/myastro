"""shared.db.supabase_client — the Streamlit-free Supabase data layer.

Two kinds of client:
  • SERVICE client — service_role key, BYPASSES row-level security. SERVER ONLY.
                     Use for shared/admin writes (caches, wallet/ledger, ad rewards).
  • USER client    — anon key + the signed-in user's JWT. Queries run AS that user,
                     so Postgres RLS enforces "owner-only" access automatically.

The CRUD helpers (profiles / check-ins / journal / streaks) all take a client +
the user_id, so they work the same whether you pass a user-scoped client (RLS on)
or the service client (RLS bypassed, server-side jobs).

supabase-py is imported lazily so this module loads even before the library is
installed (the app still boots; DB calls just raise a clear error until then).
"""
from __future__ import annotations

from datetime import date as _date, timedelta
from functools import lru_cache
from typing import Any, Optional

from shared.db.secrets import (
    supabase_anon_key,
    supabase_service_role_key,
    supabase_url,
)


# ─────────────────────────────────────────────────────────────────────────────
# Clients
# ─────────────────────────────────────────────────────────────────────────────

def _create(url: Optional[str], key: Optional[str]):
    try:
        from supabase import create_client
    except ImportError as e:  # pragma: no cover - depends on install
        raise RuntimeError(
            "supabase-py is not installed. Add 'supabase' to requirements.txt "
            "and run:  pip install supabase"
        ) from e
    if not url or not key:
        raise RuntimeError(
            "Supabase credentials missing. Set SUPABASE_URL and the matching key "
            "in env or .streamlit/secrets.toml."
        )
    return create_client(url, key)


@lru_cache(maxsize=1)
def get_service_client():
    """service_role client (bypasses RLS). SERVER ONLY — never expose to the app."""
    return _create(supabase_url(), supabase_service_role_key())


@lru_cache(maxsize=1)
def _anon_client():
    """Shared anon client used only for stateless token verification."""
    return _create(supabase_url(), supabase_anon_key())


def get_user_client(access_token: str):
    """Anon client scoped to a user's JWT, so RLS applies as that user.

    A fresh client per call — we must not mutate a shared client's auth header
    across concurrent requests.
    """
    client = _create(supabase_url(), supabase_anon_key())
    client.postgrest.auth(access_token)
    return client


def get_user_id_from_token(access_token: str) -> Optional[str]:
    """Verify a Supabase JWT against the auth server; return the user_id, or None.

    Uses the auth endpoint (not local secret decoding) so it works whether the
    project signs tokens symmetrically or with asymmetric keys.
    """
    try:
        resp = _anon_client().auth.get_user(access_token)
        if resp and getattr(resp, "user", None):
            return resp.user.id
    except Exception:
        return None
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Profiles (CRUD) — the user themselves + people they save
# ─────────────────────────────────────────────────────────────────────────────

def list_profiles(client, owner_id: str) -> list[dict]:
    res = (
        client.table("profiles").select("*")
        .eq("owner", owner_id).order("created_at").execute()
    )
    return res.data or []


def get_profile(client, profile_id: str) -> Optional[dict]:
    res = client.table("profiles").select("*").eq("id", profile_id).limit(1).execute()
    rows = res.data or []
    return rows[0] if rows else None


def create_profile(client, owner_id: str, data: dict) -> dict:
    row = {**data, "owner": owner_id}
    res = client.table("profiles").insert(row).execute()
    return res.data[0]


def update_profile(client, profile_id: str, data: dict) -> dict:
    res = client.table("profiles").update(data).eq("id", profile_id).execute()
    if not res.data:
        raise LookupError("Profile not found or not owned by this user")
    return res.data[0]


def delete_profile(client, profile_id: str) -> None:
    client.table("profiles").delete().eq("id", profile_id).execute()


# ─────────────────────────────────────────────────────────────────────────────
# Check-ins — the Pattern Engine's input (one per user per day → upsert)
# ─────────────────────────────────────────────────────────────────────────────

def save_checkin(
    client,
    user_id: str,
    date_str: str,
    mood: Optional[str] = None,
    energy: Optional[str] = None,
    clarity: Optional[str] = None,
    astro_state: Optional[dict] = None,
) -> dict:
    row = {
        "user_id": user_id,
        "date": date_str,
        "mood": mood,
        "energy": energy,
        "clarity": clarity,
        "astro_state": astro_state,
    }
    res = client.table("checkins").upsert(row, on_conflict="user_id,date").execute()
    return res.data[0]


def get_checkin(client, user_id: str, date_str: str) -> Optional[dict]:
    res = (
        client.table("checkins").select("*")
        .eq("user_id", user_id).eq("date", date_str).limit(1).execute()
    )
    rows = res.data or []
    return rows[0] if rows else None


def list_checkins(client, user_id: str, limit: int = 60) -> list[dict]:
    res = (
        client.table("checkins").select("*")
        .eq("user_id", user_id).order("date", desc=True).limit(limit).execute()
    )
    return res.data or []


# ─────────────────────────────────────────────────────────────────────────────
# Journal entries — strictly private (the Mirror)
# ─────────────────────────────────────────────────────────────────────────────

def save_journal(
    client,
    user_id: str,
    date_str: str,
    text: str,
    astro_state: Optional[dict] = None,
) -> dict:
    row = {
        "user_id": user_id,
        "date": date_str,
        "text": text,
        "astro_state": astro_state,
    }
    res = client.table("journal_entries").insert(row).execute()
    return res.data[0]


def list_journal(client, user_id: str, limit: int = 60) -> list[dict]:
    res = (
        client.table("journal_entries").select("*")
        .eq("user_id", user_id).order("date", desc=True).limit(limit).execute()
    )
    return res.data or []


# ─────────────────────────────────────────────────────────────────────────────
# Streaks — get / increment (consecutive-day aware)
# ─────────────────────────────────────────────────────────────────────────────

def get_streak(client, user_id: str, kind: str = "checkin") -> Optional[dict]:
    res = (
        client.table("streaks").select("*")
        .eq("user_id", user_id).eq("kind", kind).limit(1).execute()
    )
    rows = res.data or []
    return rows[0] if rows else None


def increment_streak(client, user_id: str, kind: str = "checkin", today: Any = None) -> dict:
    """Bump a streak with calendar awareness:
      • same day again  → no change (already counted)
      • yesterday       → count + 1
      • older / first   → reset to 1
    """
    if today is None:
        today = _date.today()
    elif isinstance(today, str):
        today = _date.fromisoformat(today)

    current = get_streak(client, user_id, kind)
    if current and current.get("last_date"):
        last = current["last_date"]
        if isinstance(last, str):
            last = _date.fromisoformat(last)
        if last == today:
            return current
        new_count = current["count"] + 1 if last == today - timedelta(days=1) else 1
    else:
        new_count = 1

    row = {
        "user_id": user_id,
        "kind": kind,
        "count": new_count,
        "last_date": today.isoformat(),
    }
    res = client.table("streaks").upsert(row, on_conflict="user_id,kind").execute()
    return res.data[0]
