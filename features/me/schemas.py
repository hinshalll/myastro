"""features.me.schemas — request/response models for the core stateful ops.

Field names mirror the Supabase columns in supabase/schema.sql so the service
layer can pass dicts straight through.
"""
from __future__ import annotations

from typing import Any, Optional

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


# ── Profiles ─────────────────────────────────────────────────────────────────

class ProfileIn(BaseModel):
    name: str
    birth_date: str                       # YYYY-MM-DD
    birth_time: Optional[str] = None      # HH:MM (24h); None → unknown-time mode
    birth_time_known: bool = False
    exact_time: bool = False
    birth_place: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    tz: Optional[str] = None
    gender: Optional[str] = None
    relation_tag: Optional[str] = None    # 'self' | 'partner' | 'mother' | ...
    source: str = "self"                  # 'self' | 'friend' | 'manual'


# ── Check-ins ────────────────────────────────────────────────────────────────

class CheckinIn(BaseModel):
    date: str                             # YYYY-MM-DD
    mood: Optional[str] = None
    energy: Optional[str] = None
    clarity: Optional[str] = None
    astro_state: Optional[dict[str, Any]] = None


# ── Journal ──────────────────────────────────────────────────────────────────

class JournalIn(BaseModel):
    date: str                             # YYYY-MM-DD
    text: str
    astro_state: Optional[dict[str, Any]] = None


# ── Settings (depth-mode, language, free-form settings jsonb) ──────────────────

class SettingsIn(BaseModel):
    depth_mode: Optional[str] = None      # 'simple' | 'balanced' | 'full'
    language: Optional[str] = None        # 'en' | 'hi' | ...
    settings: Optional[dict[str, Any]] = None


# ── Push token (for closed-app notifications) ──────────────────────────────────

class PushTokenIn(BaseModel):
    token: str                            # ExponentPushToken[...] from the device
