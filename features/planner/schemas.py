"""features.planner.schemas — My Day (Today → Plan) I/O."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class DayTaskCreate(BaseModel):
    lat: float                       # current location (the day's windows are location-based)
    lon: float
    tz: str                          # IANA tz, e.g. "Asia/Kolkata"
    title: str                       # the to-do, in the user's words ("send the pitch")
    date: str | None = None          # "YYYY-MM-DD"; defaults to today (tz)
    importance: str = "normal"       # 'normal' | 'important' (important avoids weak windows)


class DayTaskUpdate(BaseModel):
    done: bool | None = None
    title: str | None = None
    window_start: str | None = None  # manual reschedule ("HH:MM")
    window_end: str | None = None
    window_quality: str | None = None
    notify_at: str | None = None
