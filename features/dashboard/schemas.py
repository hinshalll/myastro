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


class TimingRequest(BaseModel):
    date: str   # "YYYY-MM-DD"
    lat: float
    lon: float
    tz: str     # IANA tz, e.g. "Asia/Kolkata"


class DecideRequest(BaseModel):
    profile: dict
    question: str


class DecideResponse(BaseModel):
    verdict: str  # YES / WAIT / PROCEED CAUTIOUSLY
    why: str
    alternative: str
