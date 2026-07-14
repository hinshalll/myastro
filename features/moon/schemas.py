"""features.moon.schemas — the proactive companion (the Sage) I/O. Module named `moon` (legacy)."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class MoonCheckRequest(BaseModel):
    today: str | None = None         # "YYYY-MM-DD"; defaults to today (server)
