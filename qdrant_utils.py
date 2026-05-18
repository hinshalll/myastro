"""
qdrant_utils.py
================
Qdrant client + vector-store factories.

Keys are read from environment variables (`QDRANT_URL`, `QDRANT_API_KEY`)
with safe fallbacks to your existing cluster — so the code still runs
locally even without env vars set. In production (Render / VPS), the
env vars override the fallbacks.

This module is pure-backend: zero Streamlit dependency. Importing it
works in FastAPI, in plain Python scripts, and in any future hosting
environment.

Public API:
    get_qdrant_client_pure()   → process-wide QdrantClient singleton
    get_vector_store_pure()    → process-wide QdrantVectorStore singleton
"""

import os

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


# ── Config (env-var-first, with fallback for local dev convenience) ───────────
QDRANT_URL = os.environ.get(
    "QDRANT_URL",
    "https://5353c359-9bad-4912-b23c-2a38869e4180.us-east-2-0.aws.cloud.qdrant.io",
)
QDRANT_API_KEY = os.environ.get(
    "QDRANT_API_KEY",
    # Fallback for local dev — replace with your own if you fork this repo.
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6YjNiMmJiZTgtNjI1ZS00YzQ3LTk0MDgtMWJlNTFkNGI4MmFmIn0."
    "cX5rpm7QPIYtEeuU8U8FJ3tnUa_PnZfBWkGdHYPCfWE",
)
COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION", "vedic_knowledge")
EMBEDDING_MODEL_NAME = os.environ.get(
    "QDRANT_EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5"
)


# ── Singletons ────────────────────────────────────────────────────────────────
_CLIENT_SINGLETON = None
_VS_SINGLETON = None


def get_qdrant_client_pure():
    """Process-wide Qdrant client singleton."""
    global _CLIENT_SINGLETON
    if _CLIENT_SINGLETON is None:
        _CLIENT_SINGLETON = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _CLIENT_SINGLETON


def get_vector_store_pure():
    """Process-wide QdrantVectorStore singleton."""
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
