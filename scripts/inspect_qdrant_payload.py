"""
One-shot diagnostic: pull a single point from the `vedic_knowledge` collection
and print its full payload + the keys actually used, so we know exactly which
metadata field to filter on when wiring RAG.

Run from repo root:
    python scripts/inspect_qdrant_payload.py
"""
import json
import sys
import os

# Force UTF-8 stdout on Windows so payload text with Sanskrit/diacritics doesn't crash cp1252.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Make the project root importable when run as a script.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from qdrant_client import QdrantClient

# Hardcoded here (instead of importing qdrant_utils) so we don't drag in
# Streamlit's @st.cache_resource at script time.
QDRANT_URL = "https://5353c359-9bad-4912-b23c-2a38869e4180.us-east-2-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6YjNiMmJiZTgtNjI1ZS00YzQ3LTk0MDgtMWJlNTFkNGI4MmFmIn0."
    "cX5rpm7QPIYtEeuU8U8FJ3tnUa_PnZfBWkGdHYPCfWE"
)
COLLECTION_NAME = "vedic_knowledge"


def main():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    print(f"[i] Connected. Inspecting collection: {COLLECTION_NAME}\n")

    # 1) Collection-level info (vector size, point count, etc.)
    try:
        info = client.get_collection(COLLECTION_NAME)
        print("=== COLLECTION INFO ===")
        print(f"  points_count : {info.points_count}")
        print(f"  status       : {info.status}")
        try:
            vec_cfg = info.config.params.vectors
            print(f"  vector_cfg   : {vec_cfg}")
        except Exception:
            pass
        print()
    except Exception as e:
        print(f"[!] Could not fetch collection info: {e}\n")

    # 2) Scroll a few points and print payloads.
    print("=== SAMPLE POINTS (up to 3) ===")
    points, _next = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=3,
        with_payload=True,
        with_vectors=False,
    )

    if not points:
        print("[!] No points returned. Collection may be empty.")
        return

    for idx, p in enumerate(points, 1):
        print(f"\n--- Point {idx} ---")
        print(f"id    : {p.id}")
        print(f"keys  : {list((p.payload or {}).keys())}")
        # Truncate any massive text fields so the console output stays readable.
        safe_payload = {}
        for k, v in (p.payload or {}).items():
            if isinstance(v, str) and len(v) > 400:
                safe_payload[k] = v[:400] + f"... <truncated, full length={len(v)}>"
            else:
                safe_payload[k] = v
        print("payload:")
        print(json.dumps(safe_payload, indent=2, ensure_ascii=False, default=str))

    # 3) Highlight the likely "source/book" key so the user sees it instantly.
    print("\n=== LIKELY FILENAME / BOOK KEY ===")
    candidate_keys = ("source", "book", "file", "filename", "file_name", "path", "doc_id", "document")
    payload = points[0].payload or {}
    # LangChain's QdrantVectorStore wraps payload under `metadata` by default.
    nested = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else None

    hits = []
    for k in candidate_keys:
        if k in payload:
            hits.append(("payload." + k, payload[k]))
        if nested and k in nested:
            hits.append(("payload.metadata." + k, nested[k]))

    if hits:
        for path, val in hits:
            print(f"  {path} = {val!r}")
    else:
        print("  (none of the common keys matched — inspect the payload above and pick the right field)")


if __name__ == "__main__":
    main()
