# Face Reading

Vedic face reading (**Mukha Samudrika Shastra**). Upload a front-facing photo and get a grounded reading. Works for **any** face — yourself, a friend, a photo. An **optional** toggle links your own birth chart for a face-vs-chart cross-reference.

## How it works

1. **MediaPipe Face Mesh** (478 landmarks) detects the face → `shared/astro/face_vision.py`.
2. Deterministic **geometry** is measured: face shape → Pancha Bhoota element, three-zone proportions, eye spacing/tilt, nose ratios, jaw strength, symmetry. A **frontal-pose gate** rejects turned/tilted faces so the measurements are valid.
3. `knowledge_lookup.py` maps those measurements → meanings in `data/face_knowledge.json` (no API, no Qdrant).
4. **One** Gemini Flash Lite VLM call (`vlm_reader.py`) gets the full face + 4 region crops + the measured geometry + the knowledge block + (optionally) the kundli dossier → Phase A JSON observations + Phase B markdown reading.

The measured geometry is fed as **ground truth**, so the model never guesses proportions — it only judges what landmarks can't (complexion, moles, expression) and synthesises.

## Two modes

- **Photo mode (default):** pure face reading, no birth chart needed. Works for anyone.
- **Kundli-linked (optional checkbox):** only when reading your *own* face with a saved default profile. Adds the chart cross-reference ("does your face match your chart").

## Accuracy choices

- Deterministic shapes/proportions from landmarks = ground truth (not AI-guessed).
- Meanings come only from `face_knowledge.json` → grounded, no hallucination.
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

One Gemini Flash Lite VLM call per reading — full face + 4 small region crops + a short prompt. **Under ₹1 per reading.** No RAG / Qdrant.

## Editing tips

- Change meanings → edit `data/face_knowledge.json` (no code change).
- Tune face-shape / feature thresholds → `shared/astro/face_vision.py`.
- Adjust the reading style / sections → `prompts.py`.
