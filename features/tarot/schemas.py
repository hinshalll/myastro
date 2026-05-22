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
SpreadKey = Literal["three", "yes_no", "celtic"]


# ── Interactive picker (draw-session -> reveal) ────────────────────────────────
# The React-Native-ready flow. Step 1 shuffles a hidden deck and returns a
# signed token; step 2 sends back the tapped positions and gets the reading.

class DrawSessionRequest(BaseModel):
    spread: SpreadKey
    include_reversed: bool = False


class DrawSessionResponse(BaseModel):
    token: str               # opaque signed token — pass back to /reveal
    spread: SpreadKey
    pick_count: int          # how many cards the user must tap
    deck_size: int           # 78
    card_back_url: str       # render this for every face-down card
    expires_in: int          # seconds the token stays valid


class RevealRequest(BaseModel):
    token: str
    picks: list[int]                       # tapped hidden-deck positions, in tap order
    question: str = ""
    mode: ThreeCardMode = "General Guidance"  # only used when spread == "three"


class RevealResponse(BaseModel):
    spread: SpreadKey
    cards: list[str]
    states: list[CardState]
    positions: list[str]     # human-readable position label per card
    image_urls: list[str]
    reading: str


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
