"""features.face_reading.service — re-exports + entry points.

The vision pipeline lives in shared/astro/face_vision.py. The AI bits
(vlm_reader, knowledge_lookup) live here in the feature folder.
"""

from shared.astro.face_vision import analyze_face
from features.face_reading.vlm_reader import read_face

try:
    from features.face_reading.knowledge_lookup import get_face_context
except Exception:
    get_face_context = None  # type: ignore


__all__ = ["analyze_face", "read_face", "get_face_context"]
