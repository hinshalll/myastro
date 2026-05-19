"""
qdrant_utils.py
================
Qdrant client + vector-store factories.

Two layers:
  * `get_qdrant_client_pure()` / `get_vector_store_pure()` — STREAMLIT-FREE.
    These are the canonical entry points used by shared.ai/, shared.astro/,
    shared.pdf/ and the future FastAPI mobile API. Process-wide singletons.
  * `get_qdrant_client()` / `get_vector_store()` — Streamlit `@st.cache_resource`
    thin wrappers. Only defined if Streamlit is importable. The UI views use
    these to share the client across Streamlit reruns.

Backend purity rule: importing this module MUST work without Streamlit installed.
"""

import os
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


# ── Secrets loader ────────────────────────────────────────────────────────────
# Reads env vars FIRST (FastAPI / Render / mobile backend), then falls back to
# .streamlit/secrets.toml (Streamlit local dev + Streamlit Cloud's secrets UI).
# Never hardcoded — keeps creds out of git.

def _load_secret(key: str) -> str | None:
    v = os.environ.get(key)
    if v:
        return v
    sp = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
    if sp.exists():
        try:
            import tomllib
            with open(sp, "rb") as f:
                return tomllib.load(f).get(key)
        except Exception:
            return None
    return None


QDRANT_URL     = _load_secret("QDRANT_URL")
QDRANT_API_KEY = _load_secret("QDRANT_API_KEY")
COLLECTION_NAME      = os.environ.get("QDRANT_COLLECTION", "vedic_knowledge")
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"

# ── Pure (no Streamlit) factories ─────────────────────────────────────────────
_CLIENT_SINGLETON = None
_VS_SINGLETON = None


def get_qdrant_client_pure():
    """Process-wide Qdrant client singleton. No Streamlit dependency."""
    global _CLIENT_SINGLETON
    if _CLIENT_SINGLETON is None:
        if not QDRANT_URL or not QDRANT_API_KEY:
            raise RuntimeError(
                "QDRANT_URL / QDRANT_API_KEY not set. "
                "Add them to .streamlit/secrets.toml for local dev, "
                "or set them as env vars on Render / Streamlit Cloud."
            )
        _CLIENT_SINGLETON = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _CLIENT_SINGLETON


def get_vector_store_pure():
    """Process-wide QdrantVectorStore singleton. No Streamlit dependency."""
    global _VS_SINGLETON
    if _VS_SINGLETON is None:
        client = get_qdrant_client_pure()
        existing = [c.name for c in client.get_collections().collections]
        if COLLECTION_NAME not in existing:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        _VS_SINGLETON = QdrantVectorStore(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings,
        )
    return _VS_SINGLETON


# ── Streamlit-cached wrappers (optional) ──────────────────────────────────────
# Only defined when Streamlit is available, so importing this module from
# shared.ai / a FastAPI host without Streamlit installed still works.
try:
    import streamlit as st

    @st.cache_resource
    def get_qdrant_client():
        return get_qdrant_client_pure()

    @st.cache_resource
    def get_vector_store():
        return get_vector_store_pure()
except ImportError:  # Headless / mobile-API host
    pass
