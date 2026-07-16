"""features.rituals.schemas — request models for the Rituals tab."""

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover - allows import without FastAPI installed
    BaseModel = object  # type: ignore


class RemediesRequest(BaseModel):
    profile: dict


class TodayRitualRequest(BaseModel):
    profile: dict
    date: str | None = None   # "YYYY-MM-DD" in the USER's current tz
    tz: str | None = None     # IANA fallback when `date` is absent; the WEEKDAY picks the
                              # remedy planet, so it must be the user's day (shared/timeloc.py)
