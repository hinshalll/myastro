"""features.dashboard.schemas — FastAPI I/O."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class DashboardRequest(BaseModel):
    profile: dict
    today: str


class DashboardData(BaseModel):
    greeting: str
    energy: str
    focus: str
    caution: str
    window: str
    summary: str


class ForecastRequest(BaseModel):
    profile: dict
    date: str | None = None   # "YYYY-MM-DD"; defaults to today (profile's tz)


class WeekRequest(BaseModel):
    profile: dict
    start_date: str | None = None   # "YYYY-MM-DD"; defaults to today (profile's tz)
    days: int = 7                   # how many consecutive days (the "next 7 days" rail)


class RelationshipWeatherRequest(BaseModel):
    profile_a: dict             # the user (kundli/compute shape)
    profile_b: dict             # the saved person (kundli/compute shape)
    date: str | None = None     # "YYYY-MM-DD"; defaults to today (profile_a's tz)


class TimingRequest(BaseModel):
    date: str   # "YYYY-MM-DD"
    lat: float
    lon: float
    tz: str     # IANA tz, e.g. "Asia/Kolkata"


class MuhurtaRequest(BaseModel):
    event_type: str     # a preset category (one of 14: marriage|travel|vehicle|property|housewarming|
                        # surgery|medical|education|job|signing|naming|mundan|annaprashana|general) used
                        # as-is, OR free text read AI-first into the nearest set (keyword fallback offline)
    start_date: str     # "YYYY-MM-DD"
    end_date: str       # "YYYY-MM-DD"
    lat: float
    lon: float
    tz: str             # IANA tz, e.g. "Asia/Kolkata"
    top_n: int = 5      # how many of the best days to return


class DayAlertsRequest(BaseModel):
    date: str           # "YYYY-MM-DD"
    tz: str             # IANA tz, e.g. "Asia/Kolkata"
    lat: float | None = None   # optional (eclipse Sutak refinement)
    lon: float | None = None


class HoraRequest(BaseModel):
    lat: float                  # current location (hora + sunrise are location-based)
    lon: float
    tz: str                     # IANA tz, e.g. "Asia/Kolkata"


class CalendarCheckEvent(BaseModel):
    date: str                   # "YYYY-MM-DD"
    start: str                  # "HH:MM" (24h) local start
    end: str | None = None      # optional
    id: str | None = None       # the phone-calendar event id (echoed back; server never stores it)
    title: str | None = None    # optional, echoed for the UI (server doesn't need it)


class CalendarCheckRequest(BaseModel):
    events: list[CalendarCheckEvent]   # the app's upcoming events (read on-device via expo-calendar)
    lat: float
    lon: float
    tz: str                     # IANA tz, e.g. "Asia/Kolkata"


class PanchangRequest(BaseModel):
    profile: dict               # the user (kundli/compute shape) — for the personal day-colour
    lat: float                  # current location (sunrise + windows are location-based)
    lon: float
    tz: str                     # IANA tz, e.g. "Asia/Kolkata"
    start_date: str | None = None  # "YYYY-MM-DD"; defaults to today (tz)
    days: int = 3               # 3 = today + next 2 (strip); ~31-35 = month grid
    full: bool | None = None    # None → auto (full detail when days <= 7)


class DecideRequest(BaseModel):
    profile: dict
    question: str


class DecideResponse(BaseModel):
    verdict: str  # YES / WAIT / PROCEED CAUTIOUSLY
    why: str
    alternative: str
