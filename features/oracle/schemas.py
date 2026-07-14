"""features.oracle.schemas — FastAPI I/O for all 6 oracle sub-features."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class DeepAnalysisRequest(BaseModel):
    profile: dict
    include_d60: bool = False


class DeepAnalysisResponse(BaseModel):
    reading: str
    notes: dict          # {"parashari": "...", "timing": "...", "kp": "..."}


class MatchmakingRequest(BaseModel):
    profile_a: dict
    profile_b: dict


class MatchmakingResponse(BaseModel):
    koota_score: float           # out of 36 (Ashta Koota)
    manglik_verdict: str
    compatibility_index: float   # 0-100
    reading: str


class MarriageRequest(BaseModel):
    profile_a: dict              # required (the native)
    profile_b: dict | None = None  # optional partner profile


class MarriageResponse(BaseModel):
    promise_score: float         # 0-100
    timing_windows: list[dict]
    reading: str


class GocharaRequest(BaseModel):
    profile: dict
    include_d60: bool = False


class GocharaResponse(BaseModel):
    reading: str


class CompareRequest(BaseModel):
    profiles: list[dict]
    criteria: list[str]


class CompareResponse(BaseModel):
    rankings: list[dict]         # [{"name": ..., "score": ..., "rank": ...}, ...]
    reading: str


class PrashnaRequest(BaseModel):
    question: str
    place: str = ""              # querent's location, OR provide lat/lon/tz
    lat: float | None = None
    lon: float | None = None
    tz: str | None = None
    narrate: bool = True         # False = free deterministic verdict only (no AI);
                                 # True = verdict + warm AI+RAG reading (costs Diyas)


class PrashnaResponse(BaseModel):
    verdict: str                 # YES / NO / DELAYED / UNCLEAR
    reason: str = ""             # the plain KP reason (always present, no AI)
    reading: str = ""            # the warm narrative (only when narrate=True)
    topic: str = ""              # what the question was read as being about
    interpreted: str = ""        # the question restated (positive event phrasing)
