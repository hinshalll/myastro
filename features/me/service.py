"""features.me.service — stateful core ops (profiles, check-ins, journal, streaks).

Thin layer over shared.db. Every call uses the authenticated user's RLS-scoped
client (user.client) so Postgres enforces owner-only access; we also pass the
explicit user_id (belt and suspenders).
"""
from __future__ import annotations

from shared.db import supabase_client as db


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
    return db.save_checkin(
        user.client,
        user.user_id,
        data["date"],
        data.get("mood"),
        data.get("energy"),
        data.get("clarity"),
        data.get("astro_state"),
    )


def list_checkins(user, limit: int = 60) -> list[dict]:
    return db.list_checkins(user.client, user.user_id, limit)


# ── Journal ──────────────────────────────────────────────────────────────────

def save_journal(user, data: dict) -> dict:
    return db.save_journal(
        user.client, user.user_id, data["date"], data["text"], data.get("astro_state")
    )


def list_journal(user, limit: int = 60) -> list[dict]:
    return db.list_journal(user.client, user.user_id, limit)


# ── Streaks ──────────────────────────────────────────────────────────────────

def get_streak(user, kind: str = "checkin") -> dict | None:
    return db.get_streak(user.client, user.user_id, kind)


def increment_streak(user, kind: str = "checkin") -> dict:
    return db.increment_streak(user.client, user.user_id, kind)
