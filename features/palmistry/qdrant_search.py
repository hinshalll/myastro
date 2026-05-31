"""
shared.ai/palmistry_qdrant.py
==============================
Queries Qdrant for relevant palmistry text chunks based on detected palm features.
These chunks come from palmistry.md (ingested via the palmistry ingestor).

IMPORTANT:
- This is OPTIONAL. If the HuggingFace model can't load (RAM limit on Streamlit Cloud),
  the palmistry reading still works from palm_knowledge.json alone.
- Load is attempted once; failure is cached so it doesn't retry every reading.
- Requires palmistry.md to have been ingested first via the ingestion app.
"""

from qdrant_client.http import models as qdrant_models


# ── QUERY BUILDER ──────────────────────────────────────────────────────────────

def _build_query(palm_data: dict, elevations: dict = None) -> str:
    """
    Build a natural language query from detected palm features.
    This is what gets embedded and searched against palmistry.md chunks.
    """
    parts = []

    traced = palm_data.get("traced_lines", {})
    for line_key, feat in (traced or {}).items():
        if feat and feat.get("present"):
            label  = line_key.replace("_", " ").title()
            length = feat.get("length_pct", 0)
            depth  = feat.get("depth_label", "")
            curve  = feat.get("curvature", "")
            bu     = feat.get("branches_up", 0)
            parts.append(
                f"{label}: {depth}, length {length}%, {curve}"
                + (f", {bu} upward branches" if bu else "")
            )

    if elevations:
        top_mounts = sorted(
            [(m, ev["score"]) for m, ev in elevations.items()],
            key=lambda x: -x[1]
        )[:3]
        for mount, score in top_mounts:
            if elevations[mount].get("fullness") == "prominent" or score >= 70:
                parts.append(f"{mount} mount prominent (score {score})")

    marks = palm_data.get("marks", [])
    for m in marks:
        parts.append(f"{m.get('type','unknown')} mark at {m.get('position','')}")

    minor = palm_data.get("minor_lines", {})
    for key in minor:
        parts.append(key.replace("_", " "))

    fps = palm_data.get("fingerprints", {})
    if fps:
        fp_str = ", ".join(f"{f}={p}" for f, p in fps.items() if p != "unknown")
        if fp_str:
            parts.append(f"fingerprints: {fp_str}")

    topo = palm_data.get("topology", {})
    if topo.get("simian_line"):
        parts.append("simian line present")

    fd = palm_data.get("finger_data", {})
    if fd.get("hand_type"):
        parts.append(f"hand type {fd['hand_type']}")

    return ". ".join(parts) if parts else "Vedic palmistry palm reading"


def _build_filter(categories: list[str] = None) -> qdrant_models.Filter:
    """Build Qdrant filter: domain=palmistry, optionally also filter by category."""
    must = [
        qdrant_models.FieldCondition(
            key="metadata.domain",
            match=qdrant_models.MatchValue(value="palmistry"),
        )
    ]
    if categories:
        must.append(
            qdrant_models.FieldCondition(
                key="metadata.category",
                match=qdrant_models.MatchAny(any=categories),
            )
        )
    return qdrant_models.Filter(must=must)


# ── MAIN PUBLIC FUNCTION ───────────────────────────────────────────────────────

def query_palmistry(
    palm_data: dict,
    elevations: dict = None,
    k: int = 6,
) -> str:
    """
    Query Qdrant for palmistry text chunks relevant to this palm reading.

    Returns a formatted string ready to inject into the prompt,
    or empty string if Qdrant is unavailable.
    """
    try:
        from qdrant_utils import get_vector_store_pure
    except ImportError:
        return ""

    try:
        vector_store = get_vector_store_pure()
    except Exception as e:
        print(f"[palmistry_qdrant] ERROR: {e}")
        return ""

    try:
        query = _build_query(palm_data, elevations)

        # Determine which categories to prioritize
        categories = []
        traced = palm_data.get("traced_lines", {})
        has_lines  = any((traced.get(k) or {}).get("present") for k in traced)
        has_marks  = bool(palm_data.get("marks"))
        has_minor  = bool(palm_data.get("minor_lines"))
        has_fps    = bool(palm_data.get("fingerprints"))

        if has_lines:   categories.append("lines")
        if has_marks:   categories.append("symbols")
        if has_minor:   categories.append("lines")
        if has_fps:     categories.append("fingerprints")

        elevations = elevations or {}
        if elevations:  categories.append("mounts")

        f = _build_filter(categories if categories else None)

        results = vector_store.similarity_search(query=query, k=k, filter=f)

        if not results:
            # Retry without category filter
            f_broad = _build_filter(None)
            results = vector_store.similarity_search(query=query, k=k, filter=f_broad)

        if not results:
            return ""

        chunks = []
        for doc in results:
            content = doc.page_content
            # Strip the [BOOK:...][SYSTEM:...] header injected by ingestor
            content = content.split("\n", 2)[-1].strip() if "\n" in content else content
            if len(content) > 50:
                chunks.append(content)

        return "\n\n---\n\n".join(chunks)

    except Exception as e:
        print(f"[palmistry_qdrant] ERROR: {e}")
        return ""
