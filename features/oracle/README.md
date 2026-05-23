# Oracle — 6 standalone sub-features

This package contains the six "tools" of the Oracle. Each sub-file is a
complete entry-point and can be wired into the mobile app or website as
its own screen.

## Sub-features

| File | Feature | Engine bits | RAG books |
|---|---|---|---|
| `deep_analysis.py` | Full Life Reading | 3 parallel agents (Parashari / Timing / KP) + synthesizer | bphs1.md, bphs2.md, kp3.md, kp4.md |
| `matchmaking.py`   | Ashta Koota + Manglik + Compatibility Index for boy/girl | `calculate_ashta_koota`, `check_manglik_dosha`, `calculate_compatibility_index` | kp4.md, htrh1.md |
| `marriage.py`      | Destiny Marriage Matrix | `calculate_destiny_confirmation` | htrh2.md, kp4.md |
| `gochara.py`       | Live Transit Analysis | `get_gochara_overlay` | bphs2.md, htrh1.md |
| `compare.py`       | Compare 2-10 profiles on user-picked criteria | scoring/percentile bands + custom criteria | htrh1.md, htrh2.md |
| `prashna.py`       | Horary chart cast at NOW + querent location | `get_prashna_python_verdict` | kp3.md, kp4.md |

## Shared bits

| File | What it holds |
|---|---|
| `__init__.py` | The legacy dropdown router (`show_oracle`) + re-exports of every `show_*` for direct use |
| `_shared.py`  | Common imports + helpers used by all six sub-views (gender resolution, sidebar collapse, PDF download tail) |

## Editing tips

- Add a 7th tool → drop a new file in this folder, add a `show_X()` function,
  add it to the `_DISPATCH` map in `__init__.py`. Done.
- Each `show_*()` is a self-contained entry point — to embed in a different
  layout, just call it directly without going through `show_oracle()`.
- The Full Life Reading's 3 parallel agents use the `agent` model from
  `shared/ai/config.py`; the other tools use the `default` model. Change either
  there (provider auto-detected from the name) — no edits needed here.
- The prompts each sub-feature uses still live in `ai_engine/prompts.py`
  for now (they're cross-cutting Parashari/Timing/KP/synthesizer/matchmaking/
  destiny/comparison/prashna/transit prompts). When the prompts are
  feature-specific (palm, tarot, etc.) they live in the feature folder.
