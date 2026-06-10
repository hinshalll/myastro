"""features.rituals.schemas — request models for the Rituals tab."""

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover - allows import without FastAPI installed
    BaseModel = object  # type: ignore


class RemediesRequest(BaseModel):
    profile: dict
