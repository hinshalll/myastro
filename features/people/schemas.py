"""features.people.schemas — FastAPI I/O for the shared-day readings.

Profiles use the same /kundli/compute shape as the rest of the astrology stack
(`date`, `time`, `tz`, `lat`, `lon`); a missing `time` falls back to a noon
placeholder, so every endpoint works at every birth-time tier.
"""
from __future__ import annotations

from typing import Optional

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class CoupleWeekRequest(BaseModel):
    profile_a: dict                 # the user (kundli/compute shape)
    profile_b: dict                 # the saved person (kundli/compute shape)
    start_date: Optional[str] = None   # "YYYY-MM-DD"; defaults to today (profile_a's tz)
    days: int = 7                   # how many consecutive days (the "next 7 days" rail)


class Person(BaseModel):
    name: str                       # display label for the grid cell ("Mom", "Priya")
    profile: dict                   # that person's chart (kundli/compute shape)
    relation_tag: Optional[str] = None   # 'mother' | 'partner' | 'friend' | ...


class FamilyGridRequest(BaseModel):
    people: list[Person]            # the saved people to show in the grid
    viewer: Optional[dict] = None   # optional: your own chart → adds the shared tone per row
    date: Optional[str] = None      # "YYYY-MM-DD"; defaults to today
