"""features.planner.api — My Day (Today → Plan): auto-placed to-dos.

JWT-gated (Supabase RLS). The user types a to-do; the server places it into the
day's best window (from /dashboard/timing) and stores the resolved window +
notify time so the client schedules one local notification ~15 min before.
"""

from datetime import datetime, date as _date, time as _time
from zoneinfo import ZoneInfo

from features.planner.schemas import DayTaskCreate, DayTaskUpdate
from features.planner.service import place_task
from shared.astro.astro_calc import daily_timing_windows, current_hora
from shared.db.supabase_client import (
    list_day_tasks, insert_day_task, update_day_task, delete_day_task,
)

try:
    from fastapi import APIRouter, Depends, HTTPException
    from features.me.auth import get_current_user, CurrentUser
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    @router.post("/tasks")
    def create_task(req: DayTaskCreate, user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """Add a to-do; auto-place it in the day's best window.

        The AI reads the to-do (any language / phrasing) into an importance + the
        planetary-hour (Hora) energies that suit it (shared.ai.understanding). It
        CLASSIFIES only — the engine places the task. With no API key it degrades to
        the client's importance flag and quality-only placement."""
        from shared.ai.understanding import read_day_task
        tz = req.tz
        today = datetime.now(ZoneInfo(tz)).date().isoformat()
        d = req.date or today
        d_obj = _date.fromisoformat(d)
        timing = daily_timing_windows(d_obj, req.lat, req.lon, tz)

        # Attach each daytime window's ruling Hora lord so placement can match the
        # task's nature to a suitable planetary hour (best-effort; never fatal).
        for seg in timing.get("choghadiya", []):
            if seg.get("period") != "day":
                continue
            try:
                at = datetime.combine(d_obj, _time.fromisoformat(seg["start"]), ZoneInfo(tz))
                seg["hora_lord"] = current_hora(req.lat, req.lon, tz, at=at).get("planet")
            except Exception:
                seg["hora_lord"] = None

        u = read_day_task(req.title, req.importance)

        existing = list_day_tasks(user.client, user.user_id, d)
        taken = {f'{t["window_start"]}-{t["window_end"]}'
                 for t in existing if t.get("window_start")}
        now_hm = datetime.now(ZoneInfo(tz)).strftime("%H:%M") if d == today else "00:00"
        placed = place_task(timing, now_hm, u["importance"], taken, prefer_hora=u["hora"])

        row = {
            "date": d, "title": req.title, "importance": u["importance"],
            "window_start":   placed["window_start"]   if placed else None,
            "window_end":     placed["window_end"]     if placed else None,
            "window_quality": placed["window_quality"] if placed else None,
            "notify_at":      placed["notify_at"]      if placed else None,
        }
        task = insert_day_task(user.client, user.user_id, row)
        return {"ok": True, "task": task, "placement": placed, "understood": u}

    @router.get("/tasks")
    def list_tasks(date: str | None = None,
                   user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """List the user's tasks (optionally just one date), in time order."""
        return {"ok": True, "tasks": list_day_tasks(user.client, user.user_id, date)}

    @router.patch("/tasks/{task_id}")
    def patch_task(task_id: str, req: DayTaskUpdate,
                   user: "CurrentUser" = Depends(get_current_user)) -> dict:
        """Tick off / rename / manually move a task."""
        fields = {k: v for k, v in req.dict().items() if v is not None}
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        task = update_day_task(user.client, task_id, fields)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"ok": True, "task": task}

    @router.delete("/tasks/{task_id}")
    def remove_task(task_id: str,
                    user: "CurrentUser" = Depends(get_current_user)) -> dict:
        delete_day_task(user.client, task_id)
        return {"ok": True}
