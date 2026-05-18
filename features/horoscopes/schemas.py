"""features.horoscopes.schemas — FastAPI I/O models."""

from typing import Literal

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


Timeframe = Literal["Daily", "Monthly", "Yearly"]


class WesternRequest(BaseModel):
    sun_sign: str  # e.g. "Leo"
    today: str     # ISO date string YYYY-MM-DD


class WesternResponse(BaseModel):
    reading: str


class VedicRequest(BaseModel):
    profile: dict  # {name, date, time, place, lat, lon, tz, ...}
    timeframe: Timeframe = "Daily"
    today: str


class VedicResponse(BaseModel):
    rashi: str
    nakshatra: str | None = None
    reading: str
