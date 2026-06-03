"""shared.db.cache — app-level result caching (cost rule, blueprint §8 / §9.3).

Two layers:
  • cached_daily  — shared content generated ONCE per day per astro-state, served
                    to everyone in that state (key = date + astro_state_key).
  • cached_chart  — per-profile computed-once results. The key includes `precision`
                    so confirming a birth time later (unknown→approximate→exact)
                    recomputes once instead of serving a stale lower-precision result.

These use the SERVICE client: cached_daily is written server-side (shared content),
and cached_chart writes are server jobs. Reads are cheap and idempotent.
"""
from __future__ import annotations

from typing import Any, Optional

from shared.db.supabase_client import get_service_client


# ── Shared daily content ─────────────────────────────────────────────────────

def get_cached_daily(date_str: str, astro_state_key: str) -> Optional[Any]:
    """Return cached `content` for (date, astro_state_key), or None on a miss."""
    sb = get_service_client()
    res = (
        sb.table("cached_daily").select("content")
        .eq("date", date_str).eq("astro_state_key", astro_state_key).limit(1).execute()
    )
    rows = res.data or []
    return rows[0]["content"] if rows else None


def set_cached_daily(date_str: str, astro_state_key: str, content: Any) -> dict:
    """Store/replace shared daily content. Idempotent (upsert on the primary key)."""
    sb = get_service_client()
    row = {"date": date_str, "astro_state_key": astro_state_key, "content": content}
    res = sb.table("cached_daily").upsert(row, on_conflict="date,astro_state_key").execute()
    return res.data[0]


# ── Per-chart computed-once results ──────────────────────────────────────────

def get_cached_chart(profile_id: str, kind: str, precision: str = "unknown") -> Optional[Any]:
    """Return cached `content` for (profile, kind, precision), or None on a miss."""
    sb = get_service_client()
    res = (
        sb.table("cached_chart").select("content")
        .eq("profile_id", profile_id).eq("kind", kind).eq("precision", precision)
        .limit(1).execute()
    )
    rows = res.data or []
    return rows[0]["content"] if rows else None


def set_cached_chart(profile_id: str, kind: str, content: Any, precision: str = "unknown") -> dict:
    """Store/replace a per-chart compute. Idempotent (upsert on profile+kind+precision)."""
    sb = get_service_client()
    row = {
        "profile_id": profile_id,
        "kind": kind,
        "precision": precision,
        "content": content,
    }
    res = sb.table("cached_chart").upsert(row, on_conflict="profile_id,kind,precision").execute()
    return res.data[0]
