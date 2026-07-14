"""features.me.api — FastAPI router for the authenticated user's core data.

Mounted at /me in fastapi_main.py. EVERY endpoint requires a Supabase JWT in
the `Authorization: Bearer <token>` header (see features.me.auth).

    GET    /me/profiles
    POST   /me/profiles
    PUT    /me/profiles/{profile_id}
    DELETE /me/profiles/{profile_id}
    GET    /me/checkins?limit=60
    POST   /me/checkins              (upsert: one per day; also bumps the check-in streak)
    GET    /me/journal?limit=60
    POST   /me/journal
    GET    /me/streaks/{kind}        (kind defaults used by clients: 'checkin')
"""
from __future__ import annotations

from features.me import service
from features.me.auth import CurrentUser, get_current_user
from features.me.schemas import CheckinIn, JournalIn, ProfileIn, SettingsIn, PushTokenIn

try:
    from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


def _remember_from_journal(user_id: str, text: str) -> None:
    """Background task: distil durable facts from a new journal entry into the
    user's Memory. Best-effort — never affects the save."""
    try:
        from features.memory import service as memory_service
        memory_service.extract_and_save(user_id, text, source="journal")
    except Exception:
        pass


if router is not None:

    # ── Profiles ─────────────────────────────────────────────────────────────
    @router.get("/profiles")
    def list_profiles(user: CurrentUser = Depends(get_current_user)) -> dict:
        return {"profiles": service.list_profiles(user)}

    @router.post("/profiles")
    def create_profile(
        payload: ProfileIn, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        return service.create_profile(user, payload.model_dump(exclude_none=True))

    @router.put("/profiles/{profile_id}")
    def update_profile(
        profile_id: str,
        payload: ProfileIn,
        user: CurrentUser = Depends(get_current_user),
    ) -> dict:
        try:
            return service.update_profile(
                user, profile_id, payload.model_dump(exclude_none=True)
            )
        except LookupError:
            raise HTTPException(status_code=404, detail="Profile not found")

    @router.delete("/profiles/{profile_id}")
    def delete_profile(
        profile_id: str, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        service.delete_profile(user, profile_id)
        return {"ok": True}

    # ── Check-ins ────────────────────────────────────────────────────────────
    @router.get("/checkins")
    def list_checkins(
        limit: int = 60, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        return {"checkins": service.list_checkins(user, limit)}

    @router.post("/checkins")
    def save_checkin(
        payload: CheckinIn, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        checkin = service.save_checkin(user, payload.model_dump())
        streak = service.increment_streak(user, "checkin")
        return {"checkin": checkin, "streak": streak}

    # ── Journal ──────────────────────────────────────────────────────────────
    @router.get("/journal")
    def list_journal(
        limit: int = 60, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        return {"entries": service.list_journal(user, limit)}

    @router.post("/journal")
    def save_journal(
        payload: JournalIn,
        background_tasks: BackgroundTasks,
        user: CurrentUser = Depends(get_current_user),
    ) -> dict:
        entry = service.save_journal(user, payload.model_dump())
        # Auto-remember: distil durable facts in the background (never blocks the save).
        if payload.text and payload.text.strip():
            background_tasks.add_task(_remember_from_journal, user.user_id, payload.text)
        return entry

    # ── Streaks ──────────────────────────────────────────────────────────────
    @router.get("/streaks/{kind}")
    def get_streak(
        kind: str, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        row = service.get_streak(user, kind)
        return row or {"user_id": user.user_id, "kind": kind, "count": 0, "last_date": None}

    # ── Settings (depth-mode / language) ───────────────────────────────────────
    @router.get("/settings")
    def get_settings(user: CurrentUser = Depends(get_current_user)) -> dict:
        return service.get_settings(user)

    @router.put("/settings")
    def update_settings(
        payload: SettingsIn, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        try:
            return service.update_settings(user, payload.model_dump(exclude_none=True))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ── Push token (register the device for closed-app notifications) ───────────
    @router.put("/push-token")
    def set_push_token(
        payload: PushTokenIn, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        return service.set_push_token(user, payload.token)
