"""
shared.ai.reranker
==================
Cross-encoder reranker — a second-stage filter applied AFTER Qdrant returns
a generous top-N. Cross-encoders score (query, passage) pairs jointly and
catch relevance the bi-encoder embeddings miss.

Engine: FastEmbed's `TextCrossEncoder` (ONNX runtime — fast on CPU, and the
`fastembed` library is already a dependency for the BM25 sparse vectors, so
this adds nothing new).

Default model: `Xenova/ms-marco-MiniLM-L-12-v2` (~33M params, ~0.12 GB,
Apache-2.0). Re-orders 25 candidates in well under a second on CPU. Override
with the `RERANKER_MODEL` setting (e.g. `BAAI/bge-reranker-v2-m3` on a GPU host
for top-tier multilingual accuracy).

Config (`RERANK_DISABLE`, `RERANKER_MODEL`) is read from env vars FIRST, then
falls back to `.streamlit/secrets.toml` so Streamlit users can toggle it
without setting OS env vars. Streamlit-free — safe to import from FastAPI.
"""

import os
from pathlib import Path
from typing import List, Tuple


# ── Config loader — env first, secrets.toml fallback ────────────────────────

def _load_setting(key: str, default: str = "") -> str:
    v = os.environ.get(key)
    if v:
        return v
    try:
        sp = Path(__file__).resolve().parents[2] / ".streamlit" / "secrets.toml"
        if sp.exists():
            import tomllib
            with open(sp, "rb") as f:
                data = tomllib.load(f)
            if data.get(key):
                return str(data[key])
    except Exception:
        pass
    return default


_RERANKER_SINGLETON = None
_RERANKER_MODEL_NAME = _load_setting("RERANKER_MODEL", "Xenova/ms-marco-MiniLM-L-12-v2")
_DISABLED = _load_setting("RERANK_DISABLE", "0") == "1"
_LOAD_FAILED = False   # Sticky — set true if the first load attempt fails so
                       # we don't retry a doomed load on every request.


def is_disabled() -> bool:
    """True if the reranker is unavailable — explicitly disabled OR a previous
    load attempt failed. Callers fall back to the vector-search order."""
    return _DISABLED or _LOAD_FAILED


def get_reranker_pure():
    """Process-wide TextCrossEncoder singleton. Returns None if disabled or if
    the model fails to load — the caller then skips reranking. RAG must never
    break the request."""
    global _RERANKER_SINGLETON, _LOAD_FAILED
    if _DISABLED or _LOAD_FAILED:
        return None
    if _RERANKER_SINGLETON is None:
        try:
            from fastembed.rerank.cross_encoder import TextCrossEncoder
            _RERANKER_SINGLETON = TextCrossEncoder(model_name=_RERANKER_MODEL_NAME)
        except Exception as e:
            print(f"[reranker] disabled — model load failed: "
                  f"{type(e).__name__}: {e}")
            _LOAD_FAILED = True
            return None
    return _RERANKER_SINGLETON


def rerank(query: str, docs: List[Tuple[str, dict]], top_k: int) -> List[Tuple[str, dict]]:
    """Re-order (text, meta) pairs by cross-encoder relevance to `query` and
    return the top_k. Falls back to the original order (truncated) if the
    reranker is disabled or errors — RAG must never break the request."""
    if not docs:
        return []

    model = get_reranker_pure()
    if model is None:
        return docs[:top_k]

    try:
        scores = list(model.rerank(query, [text for text, _ in docs]))
        ranked = sorted(zip(scores, docs), key=lambda x: float(x[0]), reverse=True)
        return [pair for _, pair in ranked[:top_k]]
    except Exception as e:
        print(f"[reranker] failed, falling back to vector order: {e}")
        return docs[:top_k]
