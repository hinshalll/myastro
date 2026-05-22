"""features.palmistry.schemas — FastAPI I/O."""

from typing import Literal

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


PalmCaptureRole = Literal[
    "dominant_full",
    "dominant_line_closeup",
    "mercury_edge",
    "thumb_flex",
    "non_dominant_full",
]


class PalmCapture(BaseModel):
    role: PalmCaptureRole
    image_base64: str  # JPEG/PNG, base64-encoded


class PalmReadingRequest(BaseModel):
    profile: dict | None = None  # default profile (for kundli overlay)
    image_base64: str | None = None  # legacy single dominant-palm photo
    captures: list[PalmCapture] | None = None


class PalmScanRequest(BaseModel):
    image_base64: str | None = None  # legacy single dominant-palm photo
    captures: list[PalmCapture] | None = None


class PalmScanResponse(BaseModel):
    phase_a: dict
    capture_guidance: dict
    hand_metrics: dict
    palm_tone: dict
    error: str = ""


class PalmReadingResponse(BaseModel):
    phase_a: dict             # structured JSON observations
    phase_b: str              # markdown reading
    capture_guidance: dict    # optional next capture advice from the scan
    error: str = ""
