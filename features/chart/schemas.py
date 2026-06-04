"""features.chart.schemas — FastAPI I/O for the chart-interpretation layer.

Profiles use the /kundli/compute shape and need lat/lon; an exact birth time
unlocks the rising sign + houses, an unknown time falls back to the sign-only
reads + a precision note.
"""
from __future__ import annotations

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class InterpretRequest(BaseModel):
    profile: dict                       # kundli/compute shape (needs lat/lon)
