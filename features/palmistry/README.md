# Palmistry

Vedic palm reading. User uploads a photo, the system:

1. EXIF-orients + quality-checks the image
2. MediaPipe lands palm landmarks
3. Generates 7 mount crops (Jupiter, Saturn, Sun, Mercury, Venus, Mars, Luna)
4. Computes vitality (HSV) + hand metrics
5. Calls Gemini Flash Lite ONCE with all images + kundli dossier + knowledge context

## Two-phase reading

- **Phase A** — structured JSON observations (what's visible, what's not — model is encouraged to mark `not_assessable`)
- **Phase B** — markdown reading anchored to Phase A + kundli + knowledge

## Knowledge sources stacked

- `knowledge_lookup.py` — structured JSON: dominant planet + nakshatra + dosha (no API calls)
- `qdrant_search.py` — semantic Qdrant search of `palmistry.md`
- Math facts from `vision_pipeline.py` (hand metrics, vitality, line traces)

## What's in this folder

| File | What it holds |
|---|---|
| `vlm_reader.py`      | Single Gemini VLM call (was `ai_engine/palm_vision_ai.py`) |
| `knowledge_lookup.py`| Static JSON lookup (was `ai_engine/palm_knowledge_lookup.py`) |
| `data/palm_knowledge.json` | Static lookup table: planet → traits, nakshatra → meanings, dosha → traits. Loaded once and cached. ~84 KB. |
| `qdrant_search.py`   | Qdrant semantic search (was `ai_engine/palmistry_qdrant.py`) |
| `prompts.py`         | The big Phase A + Phase B VLM prompt (was in `ai_engine/prompts.py`) |
| `service.py`         | Re-exports vision_pipeline (math_engine.palm_vision) + the AI bits |
| `view.py`            | Streamlit page |
| `api.py`             | FastAPI router |

`math_engine/palm_vision.py` (the MediaPipe pipeline) stays in the shared engine for now — moves to `shared/astro/` in Phase 3.

## Default profile required

Palmistry overlays the user's kundli on the reading, so the default profile must be set.

## AI cost

1 Gemini Flash Lite VLM call per reading (full palm + 7 mount crops + 1 reference image + prompt). ~₹2 per reading.
