"""features.palmistry.service — re-exports + entry-point wrapper.

The vision pipeline lives in math_engine/palm_vision.py for now (moves to
shared/astro/ in Phase 3). The AI bits (vlm_reader, knowledge_lookup,
qdrant_search) live here in the feature folder.
"""

from math_engine.palm_vision import analyze_palm
from features.palmistry.vlm_reader import read_palm

try:
    from features.palmistry.knowledge_lookup import get_palm_context
except Exception:
    get_palm_context = None  # type: ignore

try:
    from features.palmistry.qdrant_search import query_palmistry
except Exception:
    query_palmistry = None  # type: ignore


__all__ = ["analyze_palm", "read_palm", "get_palm_context", "query_palmistry"]
