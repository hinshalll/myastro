"""features.talk.schemas — I/O for the voice companion."""
from __future__ import annotations

from typing import Any, Optional

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class TalkIn(BaseModel):
    text: str                              # what the user said (transcribed on-device)
    lang: str = "en"                       # 'en' | 'hi'
    profile: Optional[dict[str, Any]] = None
    history: Optional[list[dict[str, Any]]] = None   # [{role, text}, ...]
    memory_context: Optional[str] = None   # from GET /memory/context


class TalkOut(BaseModel):
    reply_text: str                        # the Moon's short spoken reply (also shown on screen)
    audio_b64: Optional[str] = None        # WAV audio if a Kokoro service is wired, else None
    lang: str = "en"
