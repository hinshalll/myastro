"""features.reflect.schemas — FastAPI I/O for the reflective readings.

Profiles use the /kundli/compute shape and need lat/lon (for Lagna/houses/D10);
an unknown birth time falls back to noon with a precision note.
"""
from __future__ import annotations

from typing import Optional

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class PurposeRequest(BaseModel):
    profile: dict                       # kundli/compute shape (needs lat/lon; birth time → precise)


class YearRequest(BaseModel):
    profile: dict                       # kundli/compute shape (needs lat/lon)
    year: Optional[int] = None          # defaults to the current year (profile's tz)
