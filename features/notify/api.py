"""features.notify.api — trigger the daily proactive-push job.

  POST /notify/run-daily   — the cron entry point. Protected by a shared secret
                             (env CRON_SECRET) in the `X-Cron-Secret` header, so
                             only your scheduler can fire it. Loops every user
                             with a push token.
  POST /notify/test        — JWT; run the job for the calling user only (so you
                             can feel a real push land on your own device).

The daily trigger itself is an OWNER step: point any free cron (Render Cron,
cron-job.org, a GitHub Action) at /notify/run-daily once a day with the secret
header. Expo push tokens come from a real device build.
"""
from __future__ import annotations

import os

from features.notify import service as notify_service
from shared.db import supabase_client as db

try:
    from fastapi import APIRouter, Header, HTTPException, Depends
    from features.me.auth import get_current_user, CurrentUser
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    @router.post("/run-daily")
    def run_daily(x_cron_secret: str = Header(default=None)) -> dict:
        expected = os.environ.get("CRON_SECRET")
        if not expected or x_cron_secret != expected:
            raise HTTPException(status_code=401, detail="bad or missing cron secret")
        return notify_service.run_daily()

    @router.post("/test")
    def test_self(user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """Run the proactive job for just the caller, pushing to their own saved
        token — a way to verify the whole loop on your own phone."""
        au = db.get_app_user(user.client, user.user_id) or {}
        return notify_service.run_for_user(user.user_id, token=au.get("push_token"))
