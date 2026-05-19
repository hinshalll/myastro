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

Hybrid retrieval (Phase 5c):
  The collection uses NAMED VECTORS — one dense (BGE) + one sparse (BM25 via
  FastEmbed). QdrantVectorStore is constructed in HYBRID mode so
  similarity_search returns Reciprocal-Rank-Fusion results across both vectors
  out of the box. Collections created before Phase 5c (single unnamed vector)
  must be dropped + re-ingested — call `recreate_collection_for_hybrid()` once.
"""

import os
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, SparseVectorParams, Modifier,
)
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
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


QDRANT_URL           = _load_secret("QDRANT_URL")
QDRANT_API_KEY       = _load_secret("QDRANT_API_KEY")
COLLECTION_NAME      = os.environ.get("QDRANT_COLLECTION", "vedic_knowledge")
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"
SPARSE_MODEL_NAME    = "Qdrant/bm25"   # fastembed BM25 alias
DENSE_VEC_NAME       = "dense"
SPARSE_VEC_NAME      = "sparse"

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


def _ensure_hybrid_collection(client):
    """Create the collection with named dense + sparse vectors if missing.

    If a collection with the same name already exists with a non-hybrid shape
    (single unnamed vector — the Phase < 5c layout), raise with instructions.
    The user must call recreate_collection_for_hybrid() to drop + recreate.
    """
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                DENSE_VEC_NAME: VectorParams(size=768, distance=Distance.COSINE),
            },
            sparse_vectors_config={
                SPARSE_VEC_NAME: SparseVectorParams(modifier=Modifier.IDF),
            },
        )
        return

    info = client.get_collection(COLLECTION_NAME)
    vectors = info.config.params.vectors
    # When vectors is a VectorParams (not a dict), the collection is single-vector
    # and incompatible with HYBRID retrieval. Raise so the caller knows to migrate.
    if not isinstance(vectors, dict) or DENSE_VEC_NAME not in vectors:
        raise RuntimeError(
            f"Collection '{COLLECTION_NAME}' uses the legacy single-vector "
            f"layout. Hybrid retrieval requires named vectors. Run "
            f"`recreate_collection_for_hybrid()` once (it drops + recreates "
            f"the collection — you'll need to re-ingest every book afterward)."
        )


def get_vector_store_pure():
    """Process-wide QdrantVectorStore singleton in HYBRID retrieval mode."""
    global _VS_SINGLETON
    if _VS_SINGLETON is None:
        client = get_qdrant_client_pure()
        _ensure_hybrid_collection(client)
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        sparse = FastEmbedSparse(model_name=SPARSE_MODEL_NAME)
        _VS_SINGLETON = QdrantVectorStore(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings,
            sparse_embedding=sparse,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name=DENSE_VEC_NAME,
            sparse_vector_name=SPARSE_VEC_NAME,
        )
    return _VS_SINGLETON


def recreate_collection_for_hybrid():
    """Drop + recreate the collection with the hybrid (dense+sparse) layout.

    DESTRUCTIVE: all chunks are deleted. Run once when migrating from the
    Phase < 5c single-vector layout, then re-ingest every book via the
    chunker tool. Resets the in-process singleton so the next call to
    get_vector_store_pure() rebuilds against the new collection.
    """
    global _VS_SINGLETON
    client = get_qdrant_client_pure()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            DENSE_VEC_NAME: VectorParams(size=768, distance=Distance.COSINE),
        },
        sparse_vectors_config={
            SPARSE_VEC_NAME: SparseVectorParams(modifier=Modifier.IDF),
        },
    )
    _VS_SINGLETON = None
    return COLLECTION_NAME


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
