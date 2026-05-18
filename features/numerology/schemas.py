"""features.numerology.schemas — FastAPI I/O models."""

from typing import Literal

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


NumerologySystem = Literal["Western (Pythagorean)", "Indian/Vedic (Chaldean)"]


class FullReportRequest(BaseModel):
    name: str
    dob: str  # YYYY-MM-DD
    system: NumerologySystem = "Western (Pythagorean)"
    question: str = ""
    profile: dict | None = None  # if provided, cross-validates with kundli
    include_d60: bool = False


class FullReportResponse(BaseModel):
    life_path: int
    destiny: int
    soul_urge: int
    personality: int
    reading: str


class CyclesRequest(BaseModel):
    name: str
    dob: str
    system: NumerologySystem = "Western (Pythagorean)"


class CyclesResponse(BaseModel):
    life_path: int
    personal_year: int
    personal_month: int
    personal_day: int
    pinnacles: list[list]  # [[start_year, end_year, number, challenge], ...]
    reading: str
