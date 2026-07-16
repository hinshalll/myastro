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

from shared.timeloc import user_today

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


def increment_streak(client, user_id: str, kind: str = "checkin",
                     today: Any = None, tz: str | None = None) -> dict:
    """Bump a streak with calendar awareness:
      • same day again  → no change (already counted)
      • yesterday       → count + 1
      • older / first   → reset to 1

    A streak is a CALENDAR question, so it must use the USER's day (bucket D,
    LOCATION_TIME_AUDIT.md). Pass `today` (best) or `tz`.

    This used to fall back to `_date.today()` — the SERVER's day, and the server is UTC. That
    silently BROKE streaks: check in at 23:00 IST Monday (17:30 UTC Mon) then 02:00 IST Tuesday
    (20:30 UTC Mon) and both land on the same UTC day, so the second hits "same day again → no
    change". The user checked in two days running and watched their streak stall for no reason.
    """
    if today is None:
        today = user_today(tz)
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


# ─────────────────────────────────────────────────────────────────────────────
# Patterns — the Pattern Engine's unlocked personal correlations
# ─────────────────────────────────────────────────────────────────────────────

def list_patterns(client, user_id: str, limit: int = 50) -> list[dict]:
    res = (
        client.table("patterns").select("*")
        .eq("user_id", user_id).order("unlocked_at", desc=True).limit(limit).execute()
    )
    return res.data or []


def save_pattern(client, user_id: str, pattern_text: str,
                 evidence: Optional[dict] = None) -> dict:
    """Insert one newly-unlocked pattern. The caller is responsible for dedup
    (the Pattern Engine only saves a `kind` it hasn't stored before) — `evidence`
    carries the `kind` + the supporting counts as jsonb."""
    row = {"user_id": user_id, "pattern_text": pattern_text, "evidence": evidence}
    res = client.table("patterns").insert(row).execute()
    return res.data[0]


# ─────────────────────────────────────────────────────────────────────────────
# Memory facts — the distilled, auto-remembered "what the app knows about you".
# Server WRITES via the SERVICE client (like the wallet); the user READS/EDITS via
# their own RLS client. No vector DB — a user's facts are few, ranked by salience
# + recency directly.
# ─────────────────────────────────────────────────────────────────────────────

def list_memory_facts(client, user_id: str, limit: int = 200,
                      only_active: bool = True) -> list[dict]:
    q = client.table("memory_facts").select("*").eq("user_id", user_id)
    if only_active:
        q = q.eq("status", "active")
    res = (q.order("salience", desc=True)
            .order("last_seen", desc=True)
            .limit(limit).execute())
    return res.data or []


def insert_memory_fact(client, user_id: str, fact: str, category: Optional[str] = None,
                       source: str = "chat", source_ref: Optional[str] = None,
                       salience: float = 0.5) -> dict:
    row = {
        "user_id": user_id, "fact": fact, "category": category,
        "source": source, "source_ref": source_ref, "salience": salience,
    }
    res = client.table("memory_facts").insert(row).execute()
    return res.data[0]


def update_memory_fact(client, fact_id: str, fields: dict) -> Optional[dict]:
    res = client.table("memory_facts").update(fields).eq("id", fact_id).execute()
    rows = res.data or []
    return rows[0] if rows else None


def delete_memory_fact(client, fact_id: str) -> None:
    client.table("memory_facts").delete().eq("id", fact_id).execute()


# ─────────────────────────────────────────────────────────────────────────────
# My Day tasks (Today → Plan) — to-dos auto-placed into the day's best windows
# ─────────────────────────────────────────────────────────────────────────────

def list_day_tasks(client, user_id: str, date_str: Optional[str] = None,
                   limit: int = 100) -> list[dict]:
    q = client.table("day_tasks").select("*").eq("user_id", user_id)
    if date_str:
        q = q.eq("date", date_str)
    res = q.order("date").order("window_start").limit(limit).execute()
    return res.data or []


def insert_day_task(client, user_id: str, data: dict) -> dict:
    res = client.table("day_tasks").insert({**data, "user_id": user_id}).execute()
    return res.data[0]


def update_day_task(client, task_id: str, fields: dict) -> Optional[dict]:
    res = client.table("day_tasks").update(fields).eq("id", task_id).execute()
    rows = res.data or []
    return rows[0] if rows else None


def delete_day_task(client, task_id: str) -> None:
    client.table("day_tasks").delete().eq("id", task_id).execute()


# ─────────────────────────────────────────────────────────────────────────────
# Time Capsules (Today → Plan) — a note delivered at a future moment
# ─────────────────────────────────────────────────────────────────────────────

def list_time_capsules(client, user_id: str, limit: int = 200) -> list[dict]:
    res = (
        client.table("time_capsules").select("*")
        .eq("user_id", user_id).order("deliver_on").limit(limit).execute()
    )
    return res.data or []


def insert_time_capsule(client, user_id: str, data: dict) -> dict:
    res = client.table("time_capsules").insert({**data, "user_id": user_id}).execute()
    return res.data[0]


def update_time_capsule(client, capsule_id: str, fields: dict) -> Optional[dict]:
    res = client.table("time_capsules").update(fields).eq("id", capsule_id).execute()
    rows = res.data or []
    return rows[0] if rows else None


def delete_time_capsule(client, capsule_id: str) -> None:
    client.table("time_capsules").delete().eq("id", capsule_id).execute()


# ─────────────────────────────────────────────────────────────────────────────
# Moon messages (the proactive companion) — server WRITES (service client), the
# user READS / marks-read via RLS. Powers the floating Moon's glow + dot.
# ─────────────────────────────────────────────────────────────────────────────

def list_moon_messages(client, user_id: str, unread_only: bool = False,
                       limit: int = 50) -> list[dict]:
    q = client.table("moon_messages").select("*").eq("user_id", user_id)
    if unread_only:
        q = q.eq("read", False)
    res = q.order("created_at", desc=True).limit(limit).execute()
    return res.data or []


def insert_moon_message(client, user_id: str, data: dict) -> dict:
    res = client.table("moon_messages").insert({**data, "user_id": user_id}).execute()
    return res.data[0]


def mark_moon_message_read(client, msg_id: str) -> Optional[dict]:
    res = client.table("moon_messages").update({"read": True}).eq("id", msg_id).execute()
    rows = res.data or []
    return rows[0] if rows else None


def moon_message_exists(client, user_id: str, kind: str, for_date: str) -> bool:
    """Dedupe guard: has this kind of opener already been generated for this day?"""
    res = (
        client.table("moon_messages").select("id")
        .eq("user_id", user_id).eq("kind", kind).eq("for_date", for_date)
        .limit(1).execute()
    )
    return bool(res.data)


def moon_welcomed(client, user_id: str) -> bool:
    """Has the companion already sent its one-time welcome/intro message (ever)?"""
    res = (
        client.table("moon_messages").select("id")
        .eq("user_id", user_id).eq("kind", "welcome").limit(1).execute()
    )
    return bool(res.data)


# ─────────────────────────────────────────────────────────────────────────────
# Diya wallet — SERVER-AUTHORITATIVE (pass the SERVICE client, never the user's)
# ─────────────────────────────────────────────────────────────────────────────

def get_wallet(client, user_id: str) -> dict:
    """Fetch the user's wallet, auto-creating an empty one on first read."""
    res = (
        client.table("coin_wallets").select("*")
        .eq("user_id", user_id).limit(1).execute()
    )
    rows = res.data or []
    if rows:
        return rows[0]
    client.table("coin_wallets").insert({"user_id": user_id, "balance": 0}).execute()
    return {"user_id": user_id, "balance": 0, "lifetime_earned": 0, "lifetime_spent": 0}


def apply_coin_delta(
    client, user_id: str, delta: int, source: str,
    ref: Optional[str] = None, meta: Optional[dict] = None,
) -> Optional[int]:
    """Atomic wallet + ledger update via the `apply_coin_delta` SQL function
    (locks the row, rejects overdraw, writes the signed ledger row). Returns the
    new balance, or None if a debit would overdraw / on error."""
    try:
        res = client.rpc("apply_coin_delta", {
            "p_user": user_id, "p_delta": delta, "p_source": source,
            "p_ref": ref, "p_meta": meta or {},
        }).execute()
        data = res.data
        if data is None:
            return None
        return int(data[0]) if isinstance(data, list) else int(data)
    except Exception:
        return None


def earned_today(client, user_id: str) -> int:
    """Sum of Diyas earned today from routine activity (for the daily cap)."""
    from datetime import datetime, timezone
    start = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00+00:00")
    res = (
        client.table("coin_transactions").select("delta,source")
        .eq("user_id", user_id).gte("created_at", start).execute()
    )
    rows = res.data or []
    return sum(r.get("delta", 0) for r in rows
               if r.get("delta", 0) > 0 and str(r.get("source", "")).startswith("earned_"))


def list_coin_transactions(client, user_id: str, limit: int = 50) -> list[dict]:
    res = (
        client.table("coin_transactions").select("*")
        .eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    )
    return res.data or []


def is_plus_member(client, user_id: str) -> bool:
    """True if the user has an active Plus subscription."""
    try:
        res = (
            client.table("subscriptions").select("status")
            .eq("user_id", user_id).limit(1).execute()
        )
        rows = res.data or []
        return bool(rows) and rows[0].get("status") == "active"
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# App-user record — settings (depth_mode, language, settings jsonb)
# ─────────────────────────────────────────────────────────────────────────────

def get_app_user(client, user_id: str) -> Optional[dict]:
    res = (
        client.table("app_users").select("*")
        .eq("id", user_id).limit(1).execute()
    )
    rows = res.data or []
    return rows[0] if rows else None


def update_app_user(client, user_id: str, fields: dict) -> dict:
    """Upsert the app_users row (keyed by id = auth user). Used for settings
    like depth_mode / language / the settings jsonb / the push token."""
    row = {"id": user_id, **fields}
    res = client.table("app_users").upsert(row).execute()
    return res.data[0]


def list_push_users(client, limit: int = 2000) -> list[dict]:
    """Users with a saved Expo push token (for the daily proactive-push job).
    Pass the SERVICE client. Filtered in Python — fine at the current scale."""
    res = client.table("app_users").select("id,push_token").limit(limit).execute()
    return [r for r in (res.data or []) if r.get("push_token")]
