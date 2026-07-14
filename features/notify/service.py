"""features.notify.service — the daily "reach out while the app is closed" job.

Run once a day by an external trigger (a free cron hitting POST /notify/run-daily).
For each user with a saved push token it:
  • asks the proactive Sage if it has an opener today (same rules as /moon/check),
    stores it, and PUSHES it — this is how the Sage "messages you on its own"
    even when the app is shut;
  • alerts on a Time Capsule that has just arrived.

Known-time events (eclipse, a My Day task, a capsule's exact date) are better
handled by LOCAL notifications the app schedules on-device, so they are not
re-pushed here.

Uses the SERVICE client (bypasses RLS) but every query is scoped by user_id, so
a run only ever touches that one user's rows.
"""
from __future__ import annotations

from datetime import date as _date

from shared.db import supabase_client as db
from shared.notify.expo_push import send_push
from shared.companion import COMPANION_NAME


class _ServiceUser:
    """A trusted server-side stand-in for a CurrentUser, so the proactive-Sage
    code (`build_opener`, `personalize_today`) runs unchanged inside a cron job.
    `.client` is the service client; `.user_id` scopes every query."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client = db.get_service_client()


def run_for_user(user_id: str, token: str | None = None, today=None) -> dict:
    """Generate + (optionally) push the day's proactive items for one user.
    Returns {user_id, generated, sent}. Never raises."""
    today = today or _date.today()
    su = _ServiceUser(user_id)
    pushes: list[tuple[str, str, dict]] = []

    # 1) The proactive Sage opener (same gate as /moon/check: only if nothing unread).
    try:
        from features.moon.service import build_opener
        unread = db.list_moon_messages(su.client, user_id, unread_only=True)
        if not unread:
            opener = build_opener(su, today)
            if opener and not db.moon_message_exists(
                su.client, user_id, opener["kind"], today.isoformat()
            ):
                db.insert_moon_message(su.client, user_id, {
                    "kind": opener["kind"], "body": opener["body"],
                    "meta": opener.get("meta"), "for_date": today.isoformat(),
                })
                pushes.append((COMPANION_NAME, opener["body"],
                               {"type": "moon_opener", "kind": opener["kind"]}))
    except Exception:
        pass

    # 2) A Time Capsule that has arrived (the GET reveal flips `delivered` when opened).
    try:
        for c in db.list_time_capsules(su.client, user_id):
            if c.get("delivered"):
                continue
            if _date.fromisoformat(c["deliver_on"]) <= today:
                pushes.append(("A note from your past self",
                               "Your time capsule has arrived. Tap to open it.",
                               {"type": "capsule_arrived", "id": c["id"]}))
                break                                    # one arrival nudge per run is enough
    except Exception:
        pass

    sent = 0
    if token:
        for title, body, data in pushes:
            if send_push(token, title, body, data=data).get("ok"):
                sent += 1
    return {"user_id": user_id, "generated": len(pushes), "sent": sent}


def run_daily(today=None) -> dict:
    """Run the proactive job for every user who has a push token. Returns a summary."""
    try:
        svc = db.get_service_client()
        users = db.list_push_users(svc)
    except Exception as e:
        return {"ok": False, "error": str(e), "users": 0, "sent": 0}

    users_done = sent_total = 0
    for u in users:
        res = run_for_user(u["id"], token=u.get("push_token"), today=today)
        users_done += 1
        sent_total += res.get("sent", 0)
    return {"ok": True, "users": users_done, "sent": sent_total}
