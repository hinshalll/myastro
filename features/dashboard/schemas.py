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
    event_type: str     # travel|signing|naming|vehicle|housewarming|general
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


class DecideRequest(BaseModel):
    profile: dict
    question: str


class DecideResponse(BaseModel):
    verdict: str  # YES / WAIT / PROCEED CAUTIOUSLY
    why: str
    alternative: str
