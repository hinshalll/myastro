"""features.palmistry.schemas — FastAPI I/O."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class PalmReadingRequest(BaseModel):
    profile: dict           # default profile (for kundli overlay)
    image_base64: str       # JPEG/PNG, base64-encoded


class PalmReadingResponse(BaseModel):
    phase_a: dict           # structured JSON observations
    phase_b: str            # markdown reading
    error: str = ""
