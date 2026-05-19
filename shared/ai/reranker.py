"""
shared.ai.reranker
==================
Cross-encoder reranker — a second-stage filter applied AFTER Qdrant returns
a generous top-N. Cross-encoders score (query, passage) pairs jointly and
catch relevance bi-encoder embeddings miss.

Model: `BAAI/bge-reranker-v2-m3` (568M, multilingual, CPU-friendly).
Lazy singleton load — first call is slow (~5-10 s on CPU cold start), every
subsequent call reuses the in-memory model.

Set `RERANK_DISABLE=1` to bypass entirely (debug / Streamlit-Cloud cold-boot).
Streamlit-free — safe to import from FastAPI / scripts.
"""

import os
from typing import List, Tuple

_RERANKER_SINGLETON = None
_RERANKER_MODEL_NAME = os.environ.get("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
_DISABLED = os.environ.get("RERANK_DISABLE", "0") == "1"


def is_disabled() -> bool:
    return _DISABLED


def get_reranker_pure():
    """Process-wide CrossEncoder singleton. Returns None if disabled."""
    global _RERANKER_SINGLETON
    if _DISABLED:
        return None
    if _RERANKER_SINGLETON is None:
        from sentence_transformers import CrossEncoder
        _RERANKER_SINGLETON = CrossEncoder(_RERANKER_MODEL_NAME, max_length=512)
    return _RERANKER_SINGLETON


def rerank(query: str, docs: List[Tuple[str, dict]], top_k: int) -> List[Tuple[str, dict]]:
    """
    Re-order (text, meta) pairs by cross-encoder relevance to `query`.
    Returns the top_k highest-scoring pairs in descending order.

    Falls back to the original ordering (truncated to top_k) if the reranker
    is disabled or fails — RAG must never break the request.
    """
    if not docs:
        return []
    if top_k >= len(docs) and _DISABLED:
        return docs[:top_k]

    model = get_reranker_pure()
    if model is None:
        return docs[:top_k]

    try:
        pairs = [(query, text) for text, _ in docs]
        scores = model.predict(pairs, batch_size=8, show_progress_bar=False)
        ranked = sorted(zip(scores, docs), key=lambda x: float(x[0]), reverse=True)
        return [pair for _, pair in ranked[:top_k]]
    except Exception as e:
        print(f"[reranker] failed, falling back to vector order: {e}")
        return docs[:top_k]
