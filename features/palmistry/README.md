# Palmistry

Vedic palm reading. User gives a dominant full-palm photo and may add role-labelled
detail photos when a mobile capture flow wants higher confidence:

1. EXIF-orients + quality-checks the image.
2. MediaPipe identifies palm landmarks.
3. Generates 7 rotation-invariant mount crops (Jupiter, Saturn, Sun, Mercury, Venus, Mars, Luna) using mathematical Euclidean distance metrics to handle tilted hands.
4. Computes vitality (HSV) + hand metrics.
5. Runs a cheap, conservative **Two-Pass Visual VLM pipeline**.

## Two-Pass Visual Pipeline & Visual Calibration

To cure "Blind RAG" (where semantic searches occurred before visual features were confirmed), the pipeline is orchestrated as follows:

1. **Pass 1 (Visual Detection & Calibration)**: Calls the VLM with a cheap, strict prompt to detect physical lines, mounts, and marks, outputting a clean **Phase A JSON** observations block. To eliminate VLM visual limits and correctly categorize fine details (like chains, breaks, or loops), we pass two premium Supabase reference diagrams alongside the hand images:
   - **REFERENCE 1 (`book_image_18.jpg`)**: Direct mapping of planetary mounts and Sattva/Rajas/Tamas gunas.
   - **REFERENCE 2 (`reference_grid_3.jpg`)**: A 25-box template grid (A to Y) detailing physical line defects (breaks, chains, splits). Gemini cross-references clear user-hand features against this grid and records comparable line structures in the observed JSON path (e.g. "chained like box K", "split like box O").
2. **Pass 2 (Context Gathering - Free)**: Only after valid Phase A observations exist, parses that JSON locally. Queries the local `knowledge_lookup.py` database (ruling planet, nakshatra, and skin dosha mapping from HSV vitality) and triggers a targeted Qdrant semantic search using the *actual physical features* confirmed in Pass 1.
3. **Pass 3 (Coherent Reading)**: Calls the VLM with the supplied palm captures + calibration diagrams + dossier + targeted Qdrant passages + static Vedic contexts to output a grounded **Phase B Markdown Reading**. If the visual scan is invalid, not ready for a responsible general reading, or the photo is poor, Phase B is skipped so the app does not spend a second AI call on weak observations.

## VLM Visual Self-Correction & Planet Dominance Refinements

To reduce errors from physical camera angles, noisy MediaPipe coordinate calculations, or ambient lighting changes, Myastro implements a visual self-correction layer in the palmistry pipeline:

1. **Saturn Middle Finger Exclusion**: 
   In human anatomy, the middle finger (Saturn) is physically always the longest finger. Including it in comparative height checks would always make Saturn the dominant finger. In classical palmistry, active character drivers and planetary ruler attributes are determined by comparing the heights of **Jupiter (index)**, **Sun (ring)**, and **Mercury (little)** fingers. The system excludes Saturn from the dominant finger check in `shared/astro/palm_vision.py` to allow genuine personality drivers to emerge.
   
2. **Automated Visual Self-Correction Override**:
   MediaPipe landmark coordinates can be noisy due to camera tilt, and HSV color vitality heuristics can be thrown off by ambient lighting or room shadows. 
   - During **Pass 1**, the VLM is explicitly prompted to visually judge finger proportions (`"index_vs_ring_length"`: `ring_longer` / `index_longer` / `equal`) and palm color tone (`"vitality_visual_class"`: `Robust` / `Subdued` / `Balanced` / `Cool`).
   - At the end of Pass 1, the pipeline automatically overrides noisy mathematical landmark measurements with these precise VLM visual observations.
   
3. **UI Session Synchronization**:
   To avoid discrepancies where the text reading describes a "Sun dominant ring finger" or "Subdued vitality" but the UI's signals panel still displays the noisy mathematical values, `features/palmistry/view.py` dynamically writes the VLM-corrected metrics back to Streamlit's `st.session_state.palm_analysis` before the final UI rendering. This guarantees that all on-screen cards, ruling planet badges, and active signal list widgets update instantly and align perfectly.


## Knowledge sources stacked

- `knowledge_lookup.py` — structured static JSON: dominant planet + nakshatra + skin dosha mapping (no API calls).
- `qdrant_search.py` — semantic Qdrant search of `palmistry.md`.
- Guardrail signals from `palm_vision.py` (quality gate, hand metrics, palm tone, VLM crop regions).

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

## Mobile / FastAPI Capture Contract

- `POST /palmistry/read` remains backward-compatible with legacy
  `image_base64` and now also accepts `captures`.
- `POST /palmistry/scan` runs the one-call visual observer only. It returns
  Phase A observations, UI signals, and `capture_guidance` without paying for
  final reading prose. Use it as a capture preflight only; `/read` already runs
  the same scan before generating prose.
- `captures` require one `dominant_full` palm photo. Optional roles are
  `dominant_line_closeup`, `mercury_edge`, `thumb_flex`, and
  `non_dominant_full`.
- Phase A returns `capture_guidance.general_reading_ready`,
  `required_for_general`, and `optional_for_detail`. A mobile app can finish a
  normal one-photo reading smoothly, or ask for one specific extra view only
  when it unlocks a material detail.

## Conservative Limits

The dominant full-palm photo stays the core reading input. The AI marks details
as `not_assessable` when the available capture set cannot support them:

- Marriage / relationship lines live on the side edge below Mercury. A front palm
  photo should not confidently count them unless that edge is clearly visible.
- Thumb flexibility is an Angustha Shastra detail that requires a flexed thumb or
  a user-confirmed touch check. A neutral open-palm photo should not label it
  stiff or flexible.
- Mount crops help visual inspection, but one flat photo cannot prove 3D mount
  elevation from highlights and shadows alone.

## AI cost

Normal completed readings use two targeted Gemini Flash Lite VLM calls (Phase A
observations scan + Phase B markdown reading). Scan-only capture guidance costs
one call, and not-ready scans skip Phase B.
