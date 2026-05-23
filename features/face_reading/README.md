# Face Reading

Vedic face reading (**Mukha Samudrika Shastra**). Upload a front-facing photo and get a grounded reading. Works for **any** face — yourself, a friend, a photo. An **optional** toggle links your own birth chart for a face-vs-chart cross-reference.

## How it works

1. **MediaPipe Face Mesh** (478 landmarks) detects the face → `shared/astro/face_vision.py`.
2. Deterministic **geometry** is measured: face shape → Pancha Bhoota element, three-zone proportions, eye spacing/tilt, nose ratios, jaw strength, symmetry. A **2D frontal-pose gate** rejects turned/tilted faces (yaw/roll), and a mathematical **vertical pitch pose gate** limits head tilt up/down to prevent 2D foreshortening projection distortion from skewing forehead and nose proportions.
3. `knowledge_lookup.py` maps those measurements → meanings in `data/face_knowledge.json` (no API, no Qdrant).
4. **One** Gemini VLM call (`vlm_reader.py`) gets the full face + 4 region crops + the measured geometry + the knowledge block + (optionally) the kundli dossier → Phase A JSON observations + Phase B markdown reading.
5. **VLM Visual Self-Correction Override**: Phase A includes visual-pixel verification of the face shape, element, and dominant zone. If MediaPipe coordinates are shifted due to camera tilt, the VLM's high-resolution visual scan dynamically overrides them, ensuring 100% accurate structural categorization with zero user friction.
6. **High-Availability Model Fallbacks**: The VLM reader's primary model is the `vision` task in `shared/ai/config.py`; it then falls back along a robust ladder (`config vision model` -> `gemini-2.5-flash` -> `gemini-1.5-flash`) to guarantee service resilience under any API rate limits or outages.
7. **Perfect UI & API Synchronization**: The final self-corrected metrics are instantly written back to `st.session_state` (updating Streamlit cards in real-time) and returned in the FastAPI payload, eliminating any discrepancy between visual metrics and the text reading.

The measured geometry serves as a grounded baseline, while the VLM visually cross-verifies proportions and judges features that coordinates cannot (complexion, moles, expression) to compile a warm, cohesive reading.

## Two modes

- **Photo mode (default):** pure face reading, no birth chart needed. Works for anyone.
- **Kundli-linked (optional checkbox):** only when reading your *own* face with a saved default profile. Adds the chart cross-reference ("does your face match your chart") based on Patwari Dharmender Kumar Bansal's D-1 Lagna Kundali face maps.

## Accuracy & Security Choices

- **Deterministic Gating**: Limits vertical head pitch ($0.35 \le \text{pitch} \le 0.60$) to block distorted photos.
- **VLM Self-Correction**: 100% automated visual verification overrides noisy landmark coordinates.
- **Line-based reading is deliberately excluded** (forehead "rekha" lines / gait) — faint lines can't be detected reliably from one photo, the same problem as palm lines.
- `not_assessable` discipline for occluded features (hair-covered forehead, hidden ears, glasses).
- Respectful, **non-diagnostic** framing — traditional self-reflection, never medical/identity/hiring claims.

## What's in this folder

| File | What it holds |
|---|---|
| `data/face_knowledge.json` | The Mukha Samudrika knowledge base: 5 face shapes→elements, three zones, feature meanings, moles, planet appearance, and the optional kundli layer. Sources: *Saral Samudrik Shastra* + *Face Reading – Amazing Secrets* (Bansal) + classical mappings. |
| `knowledge_lookup.py` | Maps measured geometry → JSON meanings → formatted prompt block. Pure, no API. |
| `vlm_reader.py` | The single Gemini VLM call (Phase A JSON + Phase B reading). |
| `prompts.py` | The Phase A + Phase B prompt builder. |
| `service.py` | Re-exports `analyze_face` (vision) + the AI bits. |
| `schemas.py` / `api.py` | FastAPI I/O + `POST /face_reading/read` route. |
| `view.py` | The Streamlit page (upload, optional kundli toggle, overlay, reading, PDF). |

The vision pipeline lives in `shared/astro/face_vision.py` (reuses the palm engine's image prep).

## AI cost

One VLM call per reading — full face + 4 small region crops + a short prompt. **Under ₹1 per reading** on Gemini Flash Lite. No RAG / Qdrant. The model is the `vision` task in `shared/ai/config.py` (defaults to Gemini Flash Lite; provider auto-detected from the name).

## Editing tips

- Change meanings → edit `data/face_knowledge.json` (no code change).
- Tune face-shape / feature thresholds → `shared/astro/face_vision.py`.
- Adjust the reading style / sections → `prompts.py`.
