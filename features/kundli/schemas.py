"""features.kundli.schemas — FastAPI I/O."""

from typing import Literal

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


ChartStyle = Literal["north_indian", "south_indian", "east_indian"]
Language = Literal["en", "hi", "ta", "te", "mr", "bn", "gu"]
Tier = Literal["free", "premium"]


class KundliRequest(BaseModel):
    profile: dict
    chart_style: ChartStyle = "north_indian"


class FreeReadingRequest(BaseModel):
    profile: dict
    chart_style: ChartStyle = "north_indian"
    include_ai: bool = False


class PremiumPDFRequest(BaseModel):
    profile: dict
    theme_name: str = "classic_vedic"
    chart_style: ChartStyle = "north_indian"
    language: Language = "en"
    include_western_appendix: bool = True
    include_ai_narrative: bool = True


class PremiumPDFResponse(BaseModel):
    pdf_base64: str
    theme_name: str
    language: Language
