"""features.consultation.schemas — FastAPI I/O models."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class ConsultationMessage(BaseModel):
    role: str  # "user" | "model"
    text: str


class ConsultationRequest(BaseModel):
    profile: dict  # user's birth profile
    question: str
    history: list[ConsultationMessage] = []


class ConsultationResponse(BaseModel):
    intent: str
    reading: str
