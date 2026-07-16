"""features.capsule.api — Time Capsule (Today → Plan): write to your future self.

JWT-gated (Supabase RLS). Create a note delivered at a future moment (a custom
date, or a computed one). The list endpoint enforces the "hint, not spoiler"
rule: a capsule's note stays hidden until its day, shows only a hint in the last
2-3 days, and reveals (and marks delivered) on/after the delivery date.
"""

from datetime import date as _date

from shared.timeloc import resolve_today
from features.capsule.schemas import CapsuleSuggestRequest, CapsuleCreate
from features.capsule.service import resolve_occasion, suggest_moments
from shared.db.supabase_client import (
    list_time_capsules, insert_time_capsule, update_time_capsule, delete_time_capsule,
)

try:
    from fastapi import APIRouter, Depends, HTTPException
    from features.me.auth import get_current_user, CurrentUser
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    @router.post("/suggest")
    def suggest(req: CapsuleSuggestRequest,
                user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """The 3 computed 'or pick a moment' options (birthday / dasha / jupiter)."""
        today = resolve_today(req.today, req.tz)   # NOT _date.today() — server is UTC
        return {"ok": True, "suggestions": suggest_moments(req.profile, today)}

    @router.post("")
    def create(req: CapsuleCreate,
               user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """Seal a capsule. Resolves the delivery date from the chosen occasion."""
        today = resolve_today(req.today, req.tz)   # NOT _date.today() — server is UTC
        try:
            deliver_on, label = resolve_occasion(req.occasion, req.profile, today, req.deliver_on)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        row = {
            "note": req.note,
            "deliver_on": deliver_on.isoformat(),
            "occasion": req.occasion,
            "occasion_label": label,
            "sealed_on": today.isoformat(),
        }
        cap = insert_time_capsule(user.client, user.user_id, row)
        return {"ok": True, "capsule": cap}

    @router.get("")
    def list_caps(today: str | None = None, tz: str | None = None,
                  user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """The user's capsules. Notes are revealed only on/after delivery; the
        last 2-3 days show a hint; earlier capsules stay fully sealed."""
        # This is the one that hurts most if the day is wrong: the whole promise is that the
        # capsule opens on ITS day. A UTC "today" opens it a day early for anyone west of
        # Greenwich and holds it a day late for India between 00:00 and 05:30 IST.
        tdy = resolve_today(today, tz)
        out = []
        for c in list_time_capsules(user.client, user.user_id):
            deliver = _date.fromisoformat(c["deliver_on"])
            days_until = (deliver - tdy).days
            base = {
                "id": c["id"],
                "deliver_on": c["deliver_on"],
                "occasion": c.get("occasion"),
                "occasion_label": c.get("occasion_label"),
                "sealed_on": c.get("sealed_on"),
                "days_until": days_until,
            }
            if days_until <= 0:
                base["status"] = "arrived"
                base["note"] = c["note"]                       # reveal
                if not c.get("delivered"):
                    update_time_capsule(user.client, c["id"], {"delivered": True})
                base["delivered"] = True
            elif days_until <= 3:
                base["status"] = "hint"                        # almost here (no content)
            else:
                base["status"] = "sealed"                      # hidden
            out.append(base)
        return {"ok": True, "capsules": out}

    @router.delete("/{capsule_id}")
    def remove(capsule_id: str,
               user: "CurrentUser" = Depends(get_current_user)) -> dict:
        delete_time_capsule(user.client, capsule_id)
        return {"ok": True}
