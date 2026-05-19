"""
shared.ai/knowledge.py
======================
Streamlit-free RAG primitives for the Astro Suite.

Public API:
  rag_chunks(query, books, k)            -> [(text, metadata), ...]
  rag_context(query, books, k, header)   -> formatted <KNOWLEDGE_CONTEXT> block
  build_topic_query(topic, dossier, ...) -> compact high-signal query string
  build_comparison_knowledge(criteria)   -> per-criterion multi-query digest

Every chunk is filtered by `metadata.book` so the LLM only ever sees passages
from the books that feature is allowed to cite. Replaces the old full-text
injection (`get_knowledge_files`) that shipped ~250K tokens per call.
"""

import os
import re
from typing import Iterable, List, Tuple

from qdrant_client.http import models as qmodels
from qdrant_utils import get_vector_store_pure
from shared.ai.reranker import rerank as _rerank, is_disabled as _rerank_disabled

_TOP_K_DEFAULT = 8
_MAX_CHUNK_CHARS = 1200
# Over-fetch from Qdrant so the reranker has enough candidates to re-order.
_RERANK_OVERFETCH = int(os.environ.get("RERANK_OVERFETCH", "25"))


def rag_chunks(query: str, books: Iterable[str], k: int = _TOP_K_DEFAULT) -> List[Tuple[str, dict]]:
    """Return [(text, metadata), ...] filtered to `books` (filenames like 'bphs1.md').

    Pipeline:
      1. Qdrant hybrid (dense BGE + sparse BM25, RRF-fused) → top-N
         (N = max(k, RERANK_OVERFETCH)).
      2. CrossEncoder reranker re-orders on the FULL embedded text (which
         includes the Anthropic-style context prefix when present).
      3. Trim to k.
      4. For the returned text, prefer `metadata.raw_chunk` when present
         so downstream prompts see clean chunk content without the context
         bloat. Falls back to `page_content` for legacy chunks ingested
         before Phase 5d.

    If RERANK_DISABLE=1, step 2 is skipped.
    """
    books = [b.strip() for b in books if b and b.strip()]
    if not books or not query.strip():
        return []

    # Wrap the vector-store init too: a fresh deploy may hit Qdrant before
    # the collection has been migrated to the hybrid layout. In that case
    # get_vector_store_pure() raises with a migration hint — degrade
    # gracefully so the app keeps serving (just without RAG context).
    try:
        vs = get_vector_store_pure()              # cached singleton (process-wide, no @st)
    except Exception as e:
        print(f"[rag_chunks] vector store unavailable: {e}")
        return []

    flt = qmodels.Filter(must=[
        qmodels.FieldCondition(
            key="metadata.book",
            match=qmodels.MatchAny(any=books),
        )
    ])

    fetch_k = k if _rerank_disabled() else max(k, _RERANK_OVERFETCH)

    try:
        docs = vs.similarity_search(query=query, k=fetch_k, filter=flt)
    except Exception as e:
        print(f"[rag_chunks] Error: {e}")
        return []

    # Keep the full embedded text for the reranker (it benefits from the
    # contextual prefix); swap to raw_chunk for the returned tuple.
    full_pairs: List[Tuple[str, dict]] = []
    for d in docs:
        full_text = (d.page_content or "")[:_MAX_CHUNK_CHARS]
        full_pairs.append((full_text, d.metadata or {}))

    if not _rerank_disabled() and len(full_pairs) > k:
        full_pairs = _rerank(query, full_pairs, top_k=k)
    else:
        full_pairs = full_pairs[:k]

    out: List[Tuple[str, dict]] = []
    for full_text, meta in full_pairs:
        raw = (meta.get("raw_chunk") or "").strip()
        clean_text = raw[:_MAX_CHUNK_CHARS] if raw else full_text
        out.append((clean_text, meta))
    return out

def rag_context(query: str, books: Iterable[str], k: int = _TOP_K_DEFAULT,
                header: str = "Classical passages retrieved for this question:") -> str:
    """Return a single formatted block ready to drop into a prompt."""
    chunks = rag_chunks(query, books, k=k)
    if not chunks:
        return ""
    parts = [header]
    for i, (text, meta) in enumerate(chunks, 1):
        book = meta.get("book", "unknown")
        chap = meta.get("chapter", "")
        sys_ = meta.get("system", "")
        parts.append(f"\n[{i}] ({book} | {sys_} | {chap})\n{text}")
    return "\n".join(parts)


def build_topic_query(*, topic: str, dossier: str | None = None, extras: dict | None = None) -> str:
    """Assemble a compact, high-signal query string for a fixed topic."""
    extras = extras or {}
    seeds = {
        "parashari":  "lagna lord placement nakshatra yoga atmakaraka moon sign navamsa dignity vargottama",
        "timing":     "vimshottari dasha antardasha mahadasha bhukti results lord period",
        "kp":         "cusp sub lord significator promise marriage career children 2 7 11 6 10 11",
        "horary":     "prashna horary kp ruling planet moon cusp sub lord question",
        "match":      "ashtakoot guna milan navamsa upapada lagna marriage compatibility nadi bhakoot",
        "compare":    "house strength karaka dignity yoga divisional D9 D10 D2 lifetime promise",
        "gochara":    "transit gochara saturn jupiter rahu sade sati moon natal house",
        "numerology": "life path destiny soul urge personality pinnacle challenge",
        "tarot":      "major arcana minor arcana upright reversed meaning archetype",
    }
    base = seeds.get(topic, topic)
    parts = [base]
    
    if dossier:
        # Extract high-signal facts: ascendant, moon sign/nakshatra, MD/AD, yogas, AK/DK
        signals = []
        
        lagna_match = re.search(r'Ascendant\s*\([^)]+\):\s*([\w\s]+)', dossier, re.IGNORECASE)
        if lagna_match: signals.append(f"Lagna {lagna_match.group(1).strip()}")
            
        moon_match = re.search(r'Moon\s+Sign:\s*([\w\s]+)', dossier, re.IGNORECASE)
        if moon_match: signals.append(f"Moon in {moon_match.group(1).strip()}")
        
        md_ad_match = re.search(r'Current Period:\s*(\w+\s*MD\s*/\s*\w+\s*AD)', dossier, re.IGNORECASE)
        if md_ad_match: signals.append(f"Dasha {md_ad_match.group(1).strip()}")
        
        ak_dk_match = re.search(r'(AK:\s*\w+\s*\|\s*DK:\s*\w+)', dossier, re.IGNORECASE)
        if ak_dk_match: signals.append(ak_dk_match.group(1).strip())
            
        if signals:
            parts.append(" ".join(signals))
            
    for v in extras.values():
        if v: parts.append(str(v))
    return " ".join(parts)[:512]


def build_comparison_knowledge(selected_criteria: list) -> str:
    """
    Replace get_comparison_reference_digest() with criterion-targeted RAG.
    Queries bphs1.md + kp3.md for most criteria.
    Adds htrh2.md for Relationship-type criteria.
    Deduplicates chunks and hard-caps at 24 to stay token-light.
    """
    BASE_BOOKS = ("bphs1.md", "kp3.md")
    RELATIONSHIP_BOOKS = ("bphs1.md", "kp3.md", "htrh2.md")

    seed_map = {
        "Wealth":          "house 2 11 5 9 lord jupiter venus dhana yoga D2 hora KP H2 H11",
        "Relationship":    "house 7 venus jupiter darakaraka D9 manglik navamsa upapada H7 KP promise",
        "Career":          "house 10 6 11 sun saturn mercury amatyakaraka D10 raja yoga KP H10",
        "Health":          "lagna lord house 6 8 3 sun moon saturn D9 D12 KP H1 H6 H8 maraka",
        "Happiness":       "house 4 moon 5 9 11 jupiter venus gajakesari hamsa malavya kemadruma",
        "Luck":            "house 9 5 jupiter D9 lakshmi gajakesari KP H9 H11 purva punya",
        "Spiritual":       "house 12 9 8 5 ketu jupiter saturn atmakaraka moksha hamsa viparita raja",
        "Struggles":       "lagna moon affliction dusthana sav kemadruma war combustion gandanta viparita",
        "Hidden Pitfalls": "house 8 12 6 nodes afflicted atmakaraka darakaraka gandanta combustion war dead avastha KP denial",
    }

    seen_ids = set()
    blocks = []
    for crit in selected_criteria:
        q = seed_map.get(crit, crit)
        # Use relationship books for relationship-type criteria
        is_rel = any(k in crit.lower() for k in ["relation", "marriage", "spouse", "compat"])
        books = RELATIONSHIP_BOOKS if is_rel else BASE_BOOKS
        for text, meta in rag_chunks(q, books, k=4):
            key = (meta.get("book"), meta.get("chapter"), text[:80])
            if key in seen_ids:
                continue
            seen_ids.add(key)
            blocks.append(f"[{crit} | {meta.get('book')} | {meta.get('chapter')}]\n{text}")
        if len(blocks) >= 24:
            break

    if not blocks:
        return ""
    return "Classical rulebook passages selected per criterion:\n\n" + "\n\n".join(blocks)