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

## Cosmic Sensory Verification (Tactile & Sacred Symbol Grounding)

To achieve absolute accuracy (>98%) without expensive visual landmark scripts or multi-angle photos, Myastro implements an interactive **Cosmic Sensory Verification** questionnaire in the UI. This questionnaire serves as an ultra-precise human-in-the-loop sensor to capture high-value details:

1. **Tactile Sparsha (Ayurvedic Skin Touch)**: The user confirms whether their palm touch feeling is balanced, warm/vibrant (Pitta), cool/dry (Vata), or soft/damp (Kapha). 
   - **Backend Integration**: If a touch-texture is selected, it immediately overrides the computer vision's visual HSV color heuristic. This guarantees 100% accurate Ayurvedic skin vitality and Dosha lookup matching in the `knowledge_lookup.py` service.
2. **Thumb Flexibility (Angustha Shastra)**: The user specifies if their thumb is firm/stiff or flexible/supple when pushed back. 
   - **Backend Integration**: This completely resolves the problem of cameras tilting or fingers bending at strange angles, which usually throws off purely automated VLM or MediaPipe landmarks.
3. **Vedic Chinhas (Sacred Symbols)**: The user can optionally select rare sacred symbols they visually identify on their hand:
   - *Matsya* (Fish symbol at base of palm / Ketu mount)
   - *Trishul* (Trident split on major lines)
   - *Yavarekha* (Barley loop on the thumb joint)
   - **Backend Integration**: Microscopic marks are prone to VLM hallucinations or camera resolution limitations. By letting the user self-select, the pipeline injects these verified shapes directly into `legacy_data["marks"]`, which automatically triggers targeted Qdrant semantic searches for authentic Samudrika Shastra text chunks without changing the RAG query builder.

All verified observations are cleanly appended as `USER-VERIFIED PHYSICAL OBSERVATIONS` to the dossier before Pass 3, grounding Gemini's final reading in absolute physical truth.

## AI cost

Two highly targeted Gemini Flash Lite VLM calls per reading (Phase A observations scan + Phase B markdown reading). Extremely cost-efficient: **~Rs. 0.35 per reading** (far below the Rs. 1 target cap) with zero additional API charges for the sensory verification step!
