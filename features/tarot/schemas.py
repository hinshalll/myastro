"""features.tarot.schemas — request/response shapes for the FastAPI router.

Pydantic models. The Streamlit view doesn't use these — it talks to
service.py directly. The mobile app + website use these via api.py.
"""

from typing import Literal

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Pydantic isn't a hard dependency for the Streamlit-only path.
    BaseModel = object  # type: ignore
    Field = lambda *a, **kw: None  # type: ignore


ThreeCardMode = Literal["General Guidance", "Love & Dynamics", "Decision / Two Paths"]
CardState = Literal["Upright", "Reversed"]


class ThreeCardRequest(BaseModel):
    question: str
    mode: ThreeCardMode = "General Guidance"
    include_reversed: bool = False


class ThreeCardResponse(BaseModel):
    cards: list[str]
    states: list[CardState]
    reading: str


class YesNoRequest(BaseModel):
    question: str
    include_reversed: bool = False


class YesNoResponse(BaseModel):
    card: str
    state: CardState
    reading: str


class CelticCrossRequest(BaseModel):
    question: str = ""
    include_reversed: bool = False


class CelticCrossResponse(BaseModel):
    cards: list[str]
    states: list[CardState]
    reading: str


class BirthCardRequest(BaseModel):
    dob: str  # ISO date string YYYY-MM-DD


class BirthCardResponse(BaseModel):
    card: str
    reading: str
