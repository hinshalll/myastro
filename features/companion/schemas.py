"""features.companion.schemas — FastAPI I/O for the Companion payoffs.

Profiles use the /kundli/compute shape (`date`, `time`, `tz`, …); the check-in
fields use the app's own vocab (mood: calm/tender/sharp/heavy/wired; energy:
low/steady/bright/restless; clarity: rested/okay/tired/off).
"""
from __future__ import annotations

from typing import Optional

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class MicroInsightRequest(BaseModel):
    profile: dict                       # the user (kundli/compute shape)
    mood: Optional[str] = None          # calm | tender | sharp | heavy | wired
    energy: Optional[str] = None        # low | steady | bright | restless
    clarity: Optional[str] = None       # rested | okay | tired | off
    date: Optional[str] = None          # "YYYY-MM-DD"; defaults to today (profile's tz)


class ProofRequest(BaseModel):
    profile: dict                       # the user (kundli/compute shape; birth time → precise)
    date: str                           # "YYYY-MM-DD" — the PAST date to explain
    event: Optional[str] = None         # optional: the user's own words for what happened
