# Palmistry

Vedic palm reading. User gives a dominant full-palm photo and may add
role-labelled detail photos when a mobile capture flow wants higher confidence:

1. EXIF-orients and quality-checks the image.
2. MediaPipe identifies palm landmarks.
3. Generates 7 rotation-invariant mount crops (Jupiter, Saturn, Sun, Mercury,
   Venus, Mars, Luna) using Euclidean geometry so tilted hands still work.
4. Computes palm tone and hand metrics as guardrails.
5. Runs an AI-first visual pipeline where Python routes, crops, validates, and
   blocks risky claims, but the AI remains the visual palmist.

## Two-Pass Visual Pipeline

To avoid "blind RAG", semantic searches happen only after visual features are
confirmed.

1. **Pass 1 - Visual Detection & Calibration:** Calls the vision model with a
   strict prompt to detect physical lines, mounts, and marks, returning Phase A
   JSON observations. Gemini vision uses JSON-response mode for this pass when
   available. The scan also receives two Supabase reference diagrams:
   - `book_image_18.jpg`: planetary mounts and Sattva/Rajas/Tamas distribution.
   - `reference_grid_3.jpg`: a 25-box line-structure grid for breaks, chains,
     splits, islands, and similar formations.
2. **Pass 2 - Free Context Gathering:** Parses valid Phase A JSON locally, then
   queries `knowledge_lookup.py` and Qdrant using only the features Phase A
   actually confirmed.
3. **Pass 3 - Text-Only Reading:** Calls a text-only AI generation pass with
   the Phase A JSON, optional Kundli dossier, targeted Qdrant passages, and
   static Vedic context. The final prose model does not receive the images
   again, which lowers image-token cost and prevents it from re-reading the
   palm differently from the verified scan. If Phase A is invalid, poor, or not
   ready, Phase B is skipped.

## Visual Self-Correction

- **Saturn middle finger exclusion:** The middle finger is normally the longest,
  so the active ruling-planet comparison uses Jupiter/index, Sun/ring, and
  Mercury/little instead of letting Saturn always win.
- **VLM correction of fragile math hints:** Phase A visually confirms
  `index_vs_ring_length` and `vitality_visual_class`, then the pipeline updates
  the hand metrics and palm-tone payload to match the visual scan.
- **UI sync:** Streamlit writes corrected Phase A metrics back into
  `st.session_state.palm_analysis` so the visible cards match the generated
  reading.

## Knowledge Sources

- `knowledge_lookup.py` - structured static JSON for dominant planet,
  nakshatra, and palm-tone/dosha context.
- `qdrant_search.py` - semantic search over `palmistry.md`.
- `shared/astro/palm_vision.py` - quality gate, landmarks, crops, tone, and
  hand-architecture guardrail signals.

## Files

| File | What it holds |
|---|---|
| `vlm_reader.py` | AI orchestration, Phase A validation, capture-role gates |
| `knowledge_lookup.py` | Static Vedic/dosha lookup |
| `data/palm_knowledge.json` | Planet, nakshatra, and dosha meanings |
| `qdrant_search.py` | Qdrant semantic search |
| `prompts.py` | Phase A JSON prompt and Phase B markdown prompt |
| `service.py` | Pure service exports |
| `view.py` | Streamlit page |
| `api.py` | FastAPI router |

## Optional Kundli Alignment

Palmistry can overlay the user's birth chart on the reading. This is optional.
If no profile is supplied, or the user leaves Kundli alignment off, the feature
runs as a visual-only palm reading. FastAPI schemas accept `profile = None`.

## Mobile / FastAPI Capture Contract

- `POST /palmistry/read` remains backward-compatible with legacy
  `image_base64` and also accepts `captures`.
- `POST /palmistry/scan` runs the one-call visual observer only. It returns
  Phase A observations, UI signals, and `capture_guidance` without paying for
  final prose. Use it as capture preflight only; `/read` already performs its
  own scan before generating prose.
- `captures` require one `dominant_full` palm photo. Optional roles are
  `dominant_line_closeup`, `mercury_edge`, `thumb_flex`, and
  `non_dominant_full`.
- Phase A returns `capture_guidance.general_reading_ready`,
  `required_for_general`, and `optional_for_detail`.

## Conservative Limits

The dominant full-palm photo stays the core reading input. Details are marked
`not_assessable` when the capture set cannot support them:

- Marriage / relationship lines live on the side edge below Mercury. The
  backend forces this field to `not_assessable` unless a `mercury_edge` capture
  is supplied.
- Thumb flexibility is an Angustha Shastra detail that requires a flexed thumb
  or user-confirmed touch check. The backend forces this field to
  `not_assessable` unless a `thumb_flex` capture is supplied.
- Mount crops help inspection, but one flat photo cannot prove 3D mount
  elevation from highlights and shadows alone.

## AI Cost

Normal completed readings use one targeted VLM image call for Phase A plus one
text-only AI call for Phase B. Scan-only capture guidance costs one image call,
and not-ready scans skip Phase B. The visual scan model is the `vision` task in
`shared/ai/config.py` and the final prose model is the cheaper/general
`default` task because it reads structured Phase A evidence rather than images.
