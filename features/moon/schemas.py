"""features.moon.schemas — the proactive companion (the Sage) I/O. Module named `moon` (legacy)."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class MoonCheckRequest(BaseModel):
    # The client should ALWAYS send `today` (it alone knows where the user is right now).
    today: str | None = None         # "YYYY-MM-DD" in the USER's current timezone
    # Fallback when `today` is absent. Send the user's CURRENT tz, not their birth tz.
    # It used to default to the SERVER's date — and the server is UTC, so every Indian user
    # got YESTERDAY between 00:00 and 05:30 IST. See shared/timeloc.py.
    tz: str | None = None            # IANA, e.g. "Asia/Kolkata" / "America/New_York"
