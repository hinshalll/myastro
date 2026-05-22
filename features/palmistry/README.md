# Palmistry

Vedic palm reading. User uploads a photo, and the system performs a high-fidelity Samudrika Shastra reading:

1. EXIF-orients + quality-checks the image.
2. MediaPipe identifies palm landmarks.
3. Generates 7 rotation-invariant mount crops (Jupiter, Saturn, Sun, Mercury, Venus, Mars, Luna) using mathematical Euclidean distance metrics to handle tilted hands perfectly.
4. Computes vitality (HSV) + hand metrics.
5. Runs a cheap, ultra-accurate **Two-Pass Visual VLM pipeline**.

## Two-Pass Visual Pipeline

To cure "Blind RAG" (where semantic searches occurred before visual features were confirmed), the pipeline is orchestrated as follows:

1. **Pass 1 (Visual Detection)**: Calls the VLM with a cheap, strict prompt to detect physical lines, mounts, and marks, outputting a clean **Phase A JSON** observations block.
2. **Pass 2 (Context Gathering - Free)**: Parses the Phase A JSON locally. Queries the local `knowledge_lookup.py` database (ruling planet, nakshatra, and skin dosha mapping from HSV vitality) and triggers a targeted Qdrant semantic search using the *actual physical features* confirmed in Pass 1.
3. **Pass 3 (Coherent Reading)**: Calls the VLM with all images + dossier + targeted Qdrant passages + static Vedic contexts to output a beautiful, grounded **Phase B Markdown Reading**.

## Knowledge sources stacked

- `knowledge_lookup.py` — structured static JSON: dominant planet + nakshatra + skin dosha mapping (no API calls).
- `qdrant_search.py` — semantic Qdrant search of `palmistry.md`.
- Math facts from `palm_vision.py` (hand metrics, vitality, line traces).

## What's in this folder

| File | What it holds |
|---|---|
| `vlm_reader.py`      | Two-Pass VLM orchestration and visual coordinator |
| `knowledge_lookup.py`| Static JSON lookup for Vedic/dosha matching |
| `data/palm_knowledge.json` | Static lookup table: planet → traits, nakshatra → meanings, dosha → traits. Loaded once and cached. ~84 KB. |
| `qdrant_search.py`   | Qdrant semantic search |
| `prompts.py`         | The Phase A strict JSON prompt + Phase B markdown reading prompts |
| `service.py`         | Re-exports vision_pipeline (`shared/astro/palm_vision.py`) + the AI bits |
| `view.py`            | Streamlit page with optional Kundli alignment checkbox |
| `api.py`             | FastAPI router |

## Optional Birth Chart (Kundli) Alignment

Palmistry can overlay the user's birth chart (Kundli) on the reading. This feature is completely optional. If a default profile is missing or if the checkbox `"Integrate Birth Chart (Kundli) for deeper alignment"` is unticked, the system performs a pure, high-fidelity visual-only palm reading. Request schemas accept `profile = None` gracefully.

## AI cost

Two highly targeted Gemini Flash Lite VLM calls per reading (Phase A observations scan + Phase B markdown reading). Extremely cost-efficient: **~Rs. 0.35 per reading** (far below the Rs. 1 target cap).
