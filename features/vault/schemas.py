"""features.vault.schemas — Pydantic profile model."""

from typing import Literal

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class Profile(BaseModel):
    name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM (24h)
    place: str
    lat: float
    lon: float
    tz: str
    gender: Literal["M", "F"] = "M"
    exact_time: bool = False


class ProfileList(BaseModel):
    profiles: list[Profile]
    default_idx: int | None = None
