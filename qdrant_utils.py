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

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

QDRANT_URL = "https://5353c359-9bad-4912-b23c-2a38869e4180.us-east-2-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6YjNiMmJiZTgtNjI1ZS00YzQ3LTk0MDgtMWJlNTFkNGI4MmFmIn0.cX5rpm7QPIYtEeuU8U8FJ3tnUa_PnZfBWkGdHYPCfWE"
COLLECTION_NAME = "vedic_knowledge"
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"

# ── Pure (no Streamlit) factories ─────────────────────────────────────────────
_CLIENT_SINGLETON = None
_VS_SINGLETON = None


def get_qdrant_client_pure():
    """Process-wide Qdrant client singleton. No Streamlit dependency."""
    global _CLIENT_SINGLETON
    if _CLIENT_SINGLETON is None:
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
