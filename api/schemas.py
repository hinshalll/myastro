"""
api/schemas.py — Pydantic models for API requests + responses
==============================================================

Every endpoint accepts/returns these models. Pydantic validates the
request body automatically and FastAPI generates the /docs interactive
documentation from these.

Keep the models small + focused. One model per feature where possible.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ── BirthProfile — the universal "who" of any astrology request ──────────────

class BirthProfile(BaseModel):
    """A user's birth data. Used by almost every endpoint."""
    name:   str   = Field(..., description="Display name; can be 'Unknown' or any string")
    date:   str   = Field(..., description="ISO date 'YYYY-MM-DD'", example="1995-06-15")
    time:   str   = Field(..., description="24h 'HH:MM'",          example="06:30")
    place:  str   = Field(..., description="Place name (free text)")
    lat:    float = Field(..., ge=-90,  le=90)
    lon:    float = Field(..., ge=-180, le=180)
    tz:     str   = Field("Asia/Kolkata", description="IANA timezone")
    gender: Optional[Literal["M", "F", "O"]] = Field(None, description="M/F/O — used for matchmaking")
    exact_time: bool = Field(True, description="False = approximate time, lower confidence")


# ── Generic AI-reading response ──────────────────────────────────────────────

class ReadingResponse(BaseModel):
    """Standard wrapper for any AI-generated reading."""
    feature: str
    markdown: str
    metadata: dict = Field(default_factory=dict, description="Side info — koota score, ranks, etc.")


# ── Kundli ───────────────────────────────────────────────────────────────────

class KundliFreeResponse(BaseModel):
    """Free in-app kundli summary (returned as structured dict)."""
    feature: str = "kundli_free"
    chart_summary: dict


class KundliPremiumRequest(BaseModel):
    """Premium themed kundli PDF generation request."""
    profile: BirthProfile
    theme: Literal[
        "classic_vedic", "ganesha", "krishna", "shiva",
        "lakshmi", "saraswati", "durga",
    ] = "classic_vedic"
    chart_style: Literal["north_indian", "south_indian", "east_indian"] = "north_indian"
    language: Literal["en", "hi"] = "en"
    include_western: bool = False


# ── Palm Reading ─────────────────────────────────────────────────────────────

class PalmReadingResponse(BaseModel):
    """Output of palm analysis + AI reading."""
    feature: str = "palm_reading"
    quality_metrics: dict
    hand_metrics: dict
    vitality: dict
    phase_a: dict
    phase_b_markdown: str


# ── Oracle / Compare / Matchmaking / Marriage / Prashna / Gochara ────────────

class CompareRequest(BaseModel):
    """Compare 2-10 profiles across selected criteria."""
    profiles: List[BirthProfile] = Field(..., min_items=2, max_items=10)
    criteria: List[str] = Field(..., min_items=1,
        description="From COMPARISON_CRITERIA or custom free-text strings",
    )


class MatchmakingRequest(BaseModel):
    """Compatibility match between two profiles."""
    boy:  BirthProfile
    girl: BirthProfile


class MarriageMatrixRequest(BaseModel):
    """Destiny & marriage chances matrix between two profiles."""
    boy:  BirthProfile
    girl: BirthProfile


class GocharaRequest(BaseModel):
    """Live transit analysis for one profile."""
    profile: BirthProfile


class DeepAnalysisRequest(BaseModel):
    """Full life reading for one profile."""
    profile: BirthProfile
    include_d60: bool = False


class PrashnaRequest(BaseModel):
    """Horary question asked from a specific location at 'now'."""
    question: str = Field(..., min_length=3)
    asker_lat: float = Field(..., ge=-90,  le=90)
    asker_lon: float = Field(..., ge=-180, le=180)
    asker_tz:  str   = "Asia/Kolkata"
    asker_place: str = "Manual"


# ── Consultation Room (chat) ─────────────────────────────────────────────────

class ConsultationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConsultationRequest(BaseModel):
    """One turn of conversation with the AI astrologer."""
    profile: BirthProfile
    question: str
    history: List[ConsultationMessage] = Field(default_factory=list,
        description="Last few turns for context",
    )


# ── Tarot / Numerology / Horoscopes ──────────────────────────────────────────

class TarotDrawRequest(BaseModel):
    """Tarot draw + interpretation."""
    spread: Literal["one_card", "three_card", "celtic_cross"] = "three_card"
    question: str = ""
    profile: Optional[BirthProfile] = None


class NumerologyRequest(BaseModel):
    """Numerology profile."""
    full_name: str
    dob: str = Field(..., description="ISO date 'YYYY-MM-DD'")
    system: Literal["chaldean", "pythagorean", "vedic"] = "chaldean"


class HoroscopeRequest(BaseModel):
    """Daily / weekly / monthly horoscope."""
    profile: BirthProfile
    timeframe: Literal["day", "week", "month", "year"] = "day"
