"""features.me.service — stateful core ops (profiles, check-ins, journal, streaks).

Thin layer over shared.db. Every call uses the authenticated user's RLS-scoped
client (user.client) so Postgres enforces owner-only access; we also pass the
explicit user_id (belt and suspenders).
"""
from __future__ import annotations

from shared.db import supabase_client as db


# ── Standardized sky-state — computed SERVER-SIDE so every check-in / journal
#    entry carries a FIXED-shape snapshot of the day's Moon (the client can't pass
#    a garbage shape). Best-effort: never blocks or breaks the save.

def _self_astro_profile(user) -> dict | None:
    try:
        profiles = db.list_profiles(user.client, user.user_id)
    except Exception:
        return None
    self_p = None
    for p in profiles:
        if p.get("relation_tag") == "self" or p.get("source") == "self":
            self_p = p
            break
    if self_p is None and profiles:
        self_p = profiles[0]
    if not self_p or not self_p.get("birth_date"):
        return None
    return {
        "date": self_p.get("birth_date"),
        "time": self_p.get("birth_time") or "",
        "tz": self_p.get("tz") or "Asia/Kolkata",
        "lat": self_p.get("lat"),
        "lon": self_p.get("lon"),
    }


def _astro_state(user, on_date) -> dict | None:
    try:
        from shared.astro.forecast import astro_state_for
        ap = _self_astro_profile(user)
        if not ap:
            return None
        return astro_state_for(ap, on_date)
    except Exception:
        return None


# ── Profiles ─────────────────────────────────────────────────────────────────

def list_profiles(user) -> list[dict]:
    return db.list_profiles(user.client, user.user_id)


def create_profile(user, data: dict) -> dict:
    return db.create_profile(user.client, user.user_id, data)


def update_profile(user, profile_id: str, data: dict) -> dict:
    return db.update_profile(user.client, profile_id, data)


def delete_profile(user, profile_id: str) -> None:
    db.delete_profile(user.client, profile_id)


# ── Check-ins (also bumps the check-in streak) ───────────────────────────────

def save_checkin(user, data: dict) -> dict:
    astro = data.get("astro_state") or _astro_state(user, data["date"])
    return db.save_checkin(
        user.client,
        user.user_id,
        data["date"],
        data.get("mood"),
        data.get("energy"),
        data.get("clarity"),
        astro,
    )


def list_checkins(user, limit: int = 60) -> list[dict]:
    return db.list_checkins(user.client, user.user_id, limit)


# ── Journal ──────────────────────────────────────────────────────────────────

def save_journal(user, data: dict) -> dict:
    astro = data.get("astro_state") or _astro_state(user, data["date"])
    return db.save_journal(
        user.client, user.user_id, data["date"], data["text"], astro
    )


def list_journal(user, limit: int = 60) -> list[dict]:
    return db.list_journal(user.client, user.user_id, limit)


# ── Streaks ──────────────────────────────────────────────────────────────────

def get_streak(user, kind: str = "checkin") -> dict | None:
    return db.get_streak(user.client, user.user_id, kind)


def increment_streak(user, kind: str = "checkin", today: str | None = None) -> dict:
    """`today` = the USER's date (bucket D). Pass the check-in's own `date` — the client
    already sends it and it is authoritative. Without it we fall back to the server's day,
    which is UTC and silently stalls streaks across the IST/UTC boundary. See
    shared/db/supabase_client.increment_streak."""
    return db.increment_streak(user.client, user.user_id, kind, today=today)


# ── Settings (depth-mode, language, settings jsonb) ───────────────────────────

_DEPTH_VALUES = {"simple", "balanced", "full"}


def get_settings(user) -> dict:
    row = db.get_app_user(user.client, user.user_id) or {}
    return {
        "depth_mode": row.get("depth_mode") or "simple",
        "language": row.get("language") or "en",
        "settings": row.get("settings") or {},
    }


def update_settings(user, data: dict) -> dict:
    fields: dict = {}
    if data.get("depth_mode") is not None:
        if data["depth_mode"] not in _DEPTH_VALUES:
            raise ValueError("depth_mode must be one of: simple, balanced, full")
        fields["depth_mode"] = data["depth_mode"]
    if data.get("language") is not None:
        fields["language"] = data["language"]
    if data.get("settings") is not None:
        fields["settings"] = data["settings"]
    if fields:
        db.update_app_user(user.client, user.user_id, fields)
    return get_settings(user)


# ── Push token (so the server can notify a closed app) ────────────────────────

def set_push_token(user, token: str) -> dict:
    db.update_app_user(user.client, user.user_id, {"push_token": token})
    return {"ok": True}
