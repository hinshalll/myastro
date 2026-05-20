"""
shared.ai.reranker
==================
Cross-encoder reranker — a second-stage filter applied AFTER Qdrant returns
a generous top-N. Cross-encoders score (query, passage) pairs jointly and
catch relevance bi-encoder embeddings miss.

Model: `BAAI/bge-reranker-v2-m3` (568M, multilingual, CPU-friendly).
Lazy singleton load — first call is slow (~5-10 s on CPU cold start), every
subsequent call reuses the in-memory model.

Set `RERANK_DISABLE=1` to bypass entirely. The flag is read from env vars
FIRST, then falls back to .streamlit/secrets.toml (so Streamlit users can
toggle it via secrets.toml without setting OS env vars).
Streamlit-free — safe to import from FastAPI / scripts.
"""

import os
from pathlib import Path
from typing import List, Tuple


# ── Config loader — env first, secrets.toml fallback ────────────────────────
# (Mirrors the QDRANT_API_KEY / GEMINI_API_KEY pattern used elsewhere so a
# user who edits .streamlit/secrets.toml gets the expected effect.)

def _load_setting(key: str, default: str = "") -> str:
    v = os.environ.get(key)
    if v is not None and v != "":
        return v
    try:
        sp = Path(__file__).resolve().parents[2] / ".streamlit" / "secrets.toml"
        if sp.exists():
            import tomllib
            with open(sp, "rb") as f:
                data = tomllib.load(f)
            if key in data and data[key] not in (None, ""):
                return str(data[key])
    except Exception:
        pass
    return default


_RERANKER_SINGLETON = None
_RERANKER_MODEL_NAME = _load_setting("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
_DISABLED = _load_setting("RERANK_DISABLE", "0") == "1"
_LOAD_FAILED = False   # Sticky flag — set true if first load attempt blew up
                       # (e.g. OOM on Streamlit Cloud's 1 GB free tier).


def is_disabled() -> bool:
    """True if the reranker is unavailable for any reason — explicitly disabled
    OR a previous load attempt failed. Callers should fall back to vector order."""
    return _DISABLED or _LOAD_FAILED


def get_reranker_pure():
    """Process-wide CrossEncoder singleton. Returns None if disabled OR if
    model loading failed (OOM, missing wheel, network, etc.) — the caller
    will then skip the reranker stage. RAG must never break the request."""
    global _RERANKER_SINGLETON, _LOAD_FAILED
    if _DISABLED or _LOAD_FAILED:
        return None
    if _RERANKER_SINGLETON is None:
        try:
            from sentence_transformers import CrossEncoder
            _RERANKER_SINGLETON = CrossEncoder(_RERANKER_MODEL_NAME, max_length=512)
        except Exception as e:
            # Most likely Streamlit Cloud OOM (the 568 M-param model + the
            # BGE-base embedder both fitting in 1 GB is tight). Log once and
            # silently degrade to no-rerank mode for the rest of the process.
            print(f"[reranker] disabled — model load failed: "
                  f"{type(e).__name__}: {e}")
            _LOAD_FAILED = True
            return None
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
