"""features.moon.api — the proactive companion, the Sage (the floating button's brain).

The user-facing character is the **Sage**; the `moon` name here is legacy (module /
table / `/moon/*` endpoints). "Moon" below means the Sage.

JWT-gated (Supabase RLS). On app open the client calls POST /moon/check; if the
Sage has something to say (and isn't already waiting with an unread message), it
seals ONE opener and returns the unread list so the button can glow + dot. The
chat REPLY itself is the existing AI Ask endpoint; this only handles the
proactive openers.
"""

from datetime import date as _date

from features.moon.schemas import MoonCheckRequest
from features.moon.service import build_opener
from shared.db import supabase_client as db

try:
    from fastapi import APIRouter, Depends, HTTPException
    from features.me.auth import get_current_user, CurrentUser
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    @router.post("/check")
    def check(req: MoonCheckRequest,
              user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """Run the proactive check. Generates at most one opener/day/kind, and
        only when nothing is already unread (so the Sage never piles up). On the
        user's very first open it sends the one-time welcome/intro first."""
        today = _date.fromisoformat(req.today) if req.today else _date.today()
        unread = db.list_moon_messages(user.client, user.user_id, unread_only=True)
        if not unread:
            if not db.moon_welcomed(user.client, user.user_id):
                # First open ever → the companion introduces itself (once), before
                # any other opener. In-app only (never pushed before they've opened).
                from features.moon.service import build_welcome
                profs = db.list_profiles(user.client, user.user_id)
                name = next((p.get("name") for p in profs
                             if p.get("relation_tag") == "self"), None)
                w = build_welcome(name)
                db.insert_moon_message(user.client, user.user_id, {
                    "kind": w["kind"], "body": w["body"],
                    "meta": w.get("meta"), "for_date": today.isoformat(),
                })
            else:
                opener = build_opener(user, today)
                if opener and not db.moon_message_exists(
                    user.client, user.user_id, opener["kind"], today.isoformat()
                ):
                    db.insert_moon_message(user.client, user.user_id, {
                        "kind": opener["kind"], "body": opener["body"],
                        "meta": opener.get("meta"), "for_date": today.isoformat(),
                    })
            unread = db.list_moon_messages(user.client, user.user_id, unread_only=True)
        return {"ok": True, "count": len(unread), "messages": unread}

    @router.get("/messages")
    def messages(unread_only: bool = False,
                 user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """The Sage's message history (or just the unread ones)."""
        return {"ok": True,
                "messages": db.list_moon_messages(user.client, user.user_id,
                                                  unread_only=unread_only)}

    @router.post("/messages/{msg_id}/read")
    def mark_read(msg_id: str,
                  user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """Mark one opener read (clears the glow + dot)."""
        m = db.mark_moon_message_read(user.client, msg_id)
        if not m:
            raise HTTPException(status_code=404, detail="Message not found")
        return {"ok": True, "message": m}
