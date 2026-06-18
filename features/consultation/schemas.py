"""features.consultation.schemas — FastAPI I/O models."""

from typing import Optional

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
    # THE MEMORY: the app fetches GET /memory/context and passes its `text` here so
    # the companion remembers the user across sessions (chat itself is ephemeral).
    memory_context: Optional[str] = None


class ConsultationResponse(BaseModel):
    intent: str
    reading: str
