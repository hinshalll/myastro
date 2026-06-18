"""features.memory.schemas — I/O models for THE MEMORY."""
from __future__ import annotations

from typing import Optional

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class ExtractIn(BaseModel):
    """Text to distil durable facts from (a chat the user just had, a note)."""
    text: str
    source: str = "chat"            # 'chat' | 'journal' | 'manual'


class FactEditIn(BaseModel):
    """The user editing their own remembered fact (privacy/control)."""
    fact: Optional[str] = None
    category: Optional[str] = None
    salience: Optional[float] = None
    status: Optional[str] = None    # 'active' | 'superseded'
