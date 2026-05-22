"""features.face_reading.schemas — FastAPI I/O."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class FaceReadingRequest(BaseModel):
    image_base64: str            # JPEG/PNG, base64-encoded
    use_kundli: bool = False     # opt-in chart cross-reference (reading your OWN face)
    profile: dict | None = None  # required only when use_kundli is True


class FaceReadingResponse(BaseModel):
    phase_a: dict                # structured observations
    phase_b: str                 # markdown reading
    metrics: dict                # measured geometry (face shape, zones, features)
    error: str = ""
