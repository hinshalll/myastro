"""
Smoke test: does the full RAG pipeline run end-to-end?
- Calls rag_context with realistic queries from every feature route in the spec.
- Confirms metadata.book filter actually restricts to the requested books.
- Reports any zero-hit feature (which would mean that feature's LLM call would
  get an empty <KNOWLEDGE_CONTEXT> and silently fall back to base-LLM knowledge —
  the exact failure mode we want to catch BEFORE production.

Run from repo root:
    python scripts/smoke_test_rag.py
"""
import sys, os, time
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ai_engine.knowledge import rag_chunks, rag_context, build_topic_query, build_comparison_knowledge

CASES = [
    # (feature_label, query, books, expected_books_in_results)
    ("Oracle: Parashari agent",
        build_topic_query(topic="parashari"),
        ["bphs1.md", "htrh1.md", "htrh2.md"]),
    ("Oracle: Timing agent",
        build_topic_query(topic="timing"),
        ["bphs2.md", "kp3.md"]),
    ("Oracle: KP agent (Deep Analysis)",
        build_topic_query(topic="kp"),
        ["bphs1.md", "kp3.md"]),
    ("Oracle: Prashna (Horary)",
        "Will I get the job I applied for?",
        ["kp6.md"]),
    ("Oracle: Matchmaking",
        build_topic_query(topic="match"),
        ["htrh2.md", "kp4.md"]),
    ("Oracle: Gochara",
        build_topic_query(topic="gochara"),
        ["bphs2.md", "htrh2.md"]),
    ("Consultation default",
        "Will my marriage happen this year?",
        ["htrh1.md", "htrh2.md"]),
    ("Forecasts: Vedic",
        "gochara transit moon sign Cancer daily forecast",
        ["bphs2.md"]),
    ("Forecasts: Daily Tarot",
        "The Hermit Upright daily guidance meaning",
        ["tguide.md"]),
    ("Numerology: Western",
        "life path 7 destiny 4 soul urge 11 personality 2",
        ["wnum.md"]),
    ("Numerology: Vedic",
        "life path 9 destiny 6 chaldean numerology meaning",
        ["inum1.md"]),
    ("Tarot: any spread",
        "The Tower Reversed three card spread love",
        ["tguide.md"]),
]

def main():
    print(f"{'FEATURE':<42} {'HITS':>4}  {'BOOK FILTER OK?':<16}  TOP BOOK")
    print("-" * 100)
    failures = []
    for label, query, books in CASES:
        t0 = time.perf_counter()
        chunks = rag_chunks(query, books, k=4)
        dt_ms = int((time.perf_counter() - t0) * 1000)

        hit_books = {c[1].get("book") for c in chunks}
        unexpected = hit_books - set(books)
        ok = "OK" if not unexpected else f"LEAK: {unexpected}"

        top_book = next(iter(hit_books), "—")
        print(f"{label:<42} {len(chunks):>4}  {ok:<16}  {top_book}  ({dt_ms} ms)")

        if not chunks:
            failures.append(f"  EMPTY: {label} returned zero chunks — feature will run book-less")
        if unexpected:
            failures.append(f"  LEAK : {label} returned chunks from {unexpected} (filter not respected)")

    print()
    if failures:
        print("❌ Issues:")
        for f in failures:
            print(f)
        sys.exit(1)
    else:
        print("✅ Every route returned chunks AND every chunk respected the book filter.")

    # Also exercise the multi-query comparison helper
    print("\n--- build_comparison_knowledge sanity ---")
    ctx = build_comparison_knowledge(["Wealth", "Relationship", "Career"])
    print(f"  context length: {len(ctx)} chars")
    print(f"  starts with   : {ctx[:120]!r}")
    if not ctx or len(ctx) < 200:
        print("  ⚠️  Comparison context looks suspiciously empty.")
    else:
        print("  ✅ Comparison RAG returned a non-trivial digest.")


if __name__ == "__main__":
    main()
