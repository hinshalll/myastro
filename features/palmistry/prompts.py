"""features.palmistry.prompts — VLM Phase A + Phase B prompt builder.

Two-pass prompts:
  - Phase A: visual scan to extract a strict structured JSON of lines, mounts, marks.
  - Phase B: markdown reading generation anchored to Phase A JSON + optional Kundli + classical RAG.
"""

def build_phase_a_prompt(
    hand_metrics: dict,
    vitality: dict,
    quality_metrics: dict,
    n_mount_crops: int,
    capture_roles: list[str] | None = None,
) -> str:
    hm  = hand_metrics or {}
    vit = vitality or {}
    qm  = quality_metrics or {}

    math_signals = (
        f"- Hand type: {hm.get('hand_type', 'unknown')} "
        f"({hm.get('hand_type_vedic', '')}) — {hm.get('hand_type_gloss', '')}\n"
        f"- 2D:4D ratio: {hm.get('ratio_2d4d', '?')} — {hm.get('ratio_reading', '')}\n"
        f"- Dominant finger by length: {hm.get('dominant_finger', '?')}\n"
        f"- Thumb proportion: {hm.get('thumb_proportion', '?')}\n"
        f"- Vitality bucket: {vit.get('class', '?')} — {vit.get('note', '')}\n"
        f"- Image quality: blur={qm.get('blur_score', '?')}, "
        f"exposure={qm.get('mean_v', '?')}, resolution={qm.get('resolution', '?')}\n"
    )
    supplemental_roles = [role for role in (capture_roles or []) if role != "dominant_full"]
    if supplemental_roles:
        role_list = ", ".join(supplemental_roles)
        supplemental_line = (
            f"5. OPTIONAL CAPTURE VIEWS — role-labelled extra photos: {role_list}. "
            "Use each only for features its role can reveal.\n"
        )
    else:
        supplemental_line = (
            "5. OPTIONAL CAPTURE VIEWS — none supplied. Keep side-edge and flex details "
            "not_assessable unless FULL PALM itself genuinely shows them.\n"
        )

    return f"""Be conservative. When uncertain between two readings, prefer the safer one and say so. NEVER fabricate or guess features — every claim must come from the measured geometry hints or what you observe directly in the photo.

You are an expert Vedic palmist trained in classical Samudrika Shastra. Analyze the provided hand photos to perform a highly detailed visual scan of the palm and mounts.

═══ INPUT IMAGES ═══
1. FULL PALM (labelled top-left) — the user's hand, CLAHE-enhanced for line visibility
2. {n_mount_crops} MOUNT CROPS — close-ups of Jupiter, Saturn, Sun, Mercury, Venus, Mars, Luna
3. REFERENCE 1 (mounts/gunas) — dual hand showing mounts & Sattva/Rajas/Tamas distribution
4. REFERENCE 2 (line structures) — grid of 25 boxes (A to Y) showing line shapes, chains, island loops, and break gaps
{supplemental_line}

═══ MEASURED GEOMETRY HINTS ═══
{math_signals}

═══ VISUAL IDENTIFICATION (JSON format only) ═══
Look carefully. For each line, state what you observe. Use "not_assessable" generously — if a line is unclear, mark it "not_assessable". An honest "I can't see this clearly" is more valuable than a confident wrong answer.

CRITICAL CONSERVATIVE VEDIC SCAN ORDERS:
1. FATE LINE ORIGIN: Look extremely closely at the base of the palm near the wrist crease / Ketu mount. Do not blindly default to starting in the "center" of the palm. If you see the line rise all the way from the wrist crease, mark "starts_at" as "wrist" (highly critical Ketu-origin indicating ancestral/early path strength).
2. FINGER PROPORTIONS (2D:4D): Visually compare the relative heights of the Index finger (Jupiter) and the Ring finger (Sun). Judge with high care: is the Ring finger slightly taller than the Index finger? (Slightly longer Ring finger signifies active Surya energies, passion, creative expression, and artistic drive). Evaluate this visually on the full hand. If the Ring finger is taller, set "index_vs_ring_length" to "ring_longer". If the Index finger is taller, set "index_vs_ring_length" to "index_longer". If they are virtually equal, set it to "equal".
3. COLOR & VITALITY: Evaluate the skin tone and pads of the mounts. Do not mistake ambient room shadows or camera dimness for pale/subdued vitality. Check the fullness of the Venus mount base (fleshy and pinkish indicates robust life force) and the skin's warm tone. Record your visual assessment in "vitality_visual_class" as "Robust" (warm, fleshy, pinkish), "Balanced" (healthy, even tone), "Subdued" (pale or muted tone), or "Cool" (cooler tone).
4. LINE QUALITY & STENCILS: Cross-reference the user's hand lines against REFERENCE 2's grid of formations. In the line's "path" description, explicitly note any clear structural properties or defects identified (e.g. chained like box K, island loops like box L, overlapping break like box V, split branches like box D or O, wavy like box P, etc.).
5. RELATIONSHIP LINES: Marriage/relationship lines sit on the side edge below Mercury. In a front-facing palm photo, mark them "not_assessable" unless that side edge is clearly visible and sharply focused.
6. THUMB FLEXIBILITY: A neutral open-palm photo does not prove thumb flexibility. Mark "flexibility_estimate" as "not_assessable" unless the photo clearly shows the thumb being bent backward under pressure.
7. CAPTURE GUIDANCE: Do not demand extra photos for a strong general reading if the major lines and whole-hand architecture are readable. Recommend an optional close-up or side view only when it would unlock a specific detail. Set "general_reading_ready" to false only when the supplied capture set cannot support a responsible overall reading.

For each MOUNT CROP, judge only visible fullness and clear marks (cross, star, triangle, square, island, grille, fish). A single frontal photo cannot prove 3D elevation from lighting or shadows alone, so use "not_assessable" when fullness is uncertain. Use "no notable marks" if you don't see clear marks — don't report skin texture or shadows.

IMPORTANT: Do not mistake minor skin creases or texture for major lines. Be extremely precise.

Output ONLY this JSON object. Do not wrap it in markdown fences:

{{
  "image_quality": "good|acceptable|poor",
  "image_issues": "brief note or empty string",
  "lines": {{
    "heart":  {{ "visibility": "clear|faint|fragmented|not_visible|not_assessable", "path": "brief description or 'not_assessable'", "endpoint": "Jupiter|Saturn|between_them|other|not_assessable" }},
    "head":   {{ "visibility": "...", "path": "...", "joined_to_life": "yes|no|not_assessable", "slope": "straight|gentle_downward|steep_downward|not_assessable" }},
    "life":   {{ "visibility": "...", "path": "...", "curve": "tight|moderate|wide|not_assessable" }},
    "fate":   {{ "visibility": "...", "path": "...", "starts_at": "wrist|life_line|head_line|center|absent|not_assessable" }},
    "sun":    {{ "visibility": "...", "path": "..." }},
    "marriage_lines": {{ "count_visible": "0|1|2|3+|not_assessable", "description": "brief or not_assessable" }},
    "simian": {{ "present": false, "confidence": "low|medium|high" }}
  }},
  "mounts": {{
    "Jupiter": {{ "fullness": "prominent|moderate|flat|not_assessable", "marks": "no notable marks|description" }},
    "Saturn":  {{ "fullness": "...", "marks": "..." }},
    "Sun":     {{ "fullness": "...", "marks": "..." }},
    "Mercury": {{ "fullness": "...", "marks": "..." }},
    "Venus":   {{ "fullness": "...", "marks": "..." }},
    "Mars":    {{ "fullness": "...", "marks": "..." }},
    "Luna":    {{ "fullness": "...", "marks": "..." }}
  }},
  "special_marks": {{
    "mystic_cross": "visible|not_visible|not_assessable",
    "ring_of_solomon": "visible|not_visible|not_assessable",
    "ring_of_saturn": "visible|not_visible|not_assessable"
  }},
  "fingers": {{
    "tip_shape_dominant": "conic|square|spatulate|rounded|mixed|not_assessable",
    "knotted_joints": "yes|no|not_assessable",
    "spacing": "wide|moderate|close|not_assessable",
    "index_vs_ring_length": "ring_longer|index_longer|equal|not_assessable"
  }},
  "thumb": {{
    "set": "high|medium|low|not_assessable",
    "tip_shape": "conic|square|spatulate|not_assessable",
    "flexibility_estimate": "stiff|firm|flexible|not_assessable"
  }},
  "vitality_visual_class": "Robust|Balanced|Subdued|Cool|not_assessable",
  "capture_guidance": {{
    "general_reading_ready": true,
    "required_for_general": [],
    "optional_for_detail": [
      {{ "role": "dominant_line_closeup", "reason": "brief note", "unlocks": "brief detail" }}
    ]
  }}
}}"""


def build_phase_b_prompt(
    hand_metrics: dict,
    vitality: dict,
    quality_metrics: dict,
    phase_a_json_str: str,
    dossier: str = "",
    knowledge_context: str = "",
    qdrant_context: str = "",
) -> str:
    hm  = hand_metrics or {}
    vit = vitality or {}
    qm  = quality_metrics or {}

    math_signals = (
        f"- Hand type: {hm.get('hand_type', 'unknown')} "
        f"({hm.get('hand_type_vedic', '')}) — {hm.get('hand_type_gloss', '')}\n"
        f"- 2D:4D ratio: {hm.get('ratio_2d4d', '?')} — {hm.get('ratio_reading', '')}\n"
        f"- Dominant finger by length: {hm.get('dominant_finger', '?')}\n"
        f"- Thumb proportion: {hm.get('thumb_proportion', '?')}\n"
        f"- Vitality bucket: {vit.get('class', '?')} — {vit.get('note', '')}\n"
        f"- Image quality: blur={qm.get('blur_score', '?')}, "
        f"exposure={qm.get('mean_v', '?')}, resolution={qm.get('resolution', '?')}\n"
    )

    knowledge_block = ""
    if knowledge_context and len(knowledge_context.strip()) > 50:
        knowledge_block = (
            f"\n<vedic_knowledge>\n{knowledge_context}\n</vedic_knowledge>\n"
        )

    qdrant_block = ""
    if qdrant_context and len(qdrant_context.strip()) > 50:
        qdrant_block = (
            f"\n<classical_passages>\n{qdrant_context}\n</classical_passages>\n"
            "<classical_passages_rules>\n"
            "Use only the passages above for classical doctrine. When you state a "
            "doctrine claim drawn from them, mention which book it came from using "
            "a friendly source name (e.g. 'Samudrika Shastra' or 'classical "
            "palmistry'). NEVER output literal markers like [BOOK: palmistry.md]. "
            "If a nuance isn't in the passages, omit it rather than inventing it.\n"
            "</classical_passages_rules>\n"
        )

    dossier_block = ""
    if dossier and len(dossier.strip()) > 30:
        dossier_block = (
            f"\n<kundli_dossier>\n{dossier}\n</kundli_dossier>\n"
        )

    return f"""Be conservative. When uncertain between two readings, prefer the safer one and say so. NEVER fabricate planetary positions, nakshatras, degrees, or palm features — every claim must come from either the math-derived facts, the Phase A JSON observations provided, the kundli dossier, or the classical passages.

You are an expert Vedic palmist trained in classical Samudrika Shastra. Write a highly personalized, gorgeous markdown reading for the user.

═══ CONFIRMED VISUAL OBSERVATIONS (Phase A JSON) ═══
{phase_a_json_str}

═══ MEASURED GEOMETRY SIGNALS ═══
{math_signals}{dossier_block}{knowledge_block}{qdrant_block}

═══ THE READING (Markdown Format) ═══
Write the reading using only the confirmed Phase A observations + the math facts + the kundli (if provided) + classical passages. This final prose pass is intentionally text-only: do not re-inspect or invent visual evidence beyond the Phase A JSON.

HARD RULES:
1. Never claim a feature exists if Phase A marked it "not_assessable" or "not_visible" or "absent".
2. If the Kundli dossier is provided, weave it throughout — reference specific planets, nakshatras, or ascendant. If it is NOT provided (empty/missing), DO NOT mention birth charts, planets' birth positions, nakshatras, or any chart features. Rely entirely on the physical palm architecture, mounts, and lines.
3. Flowing paragraphs. No bullet lists inside sections.
4. Tone: Extremely personal, warm, cozy, highly supportive, and comforting—like a kind, wise elder Vedic guide speaking to you over a warm cup of spiced tea in a peaceful home. Absolutely no cold, dry, or technical "AI" words or machine-learning jargon. Never say "the image shows", "pixel analysis", "VLM", "the algorithm scans", "detected by camera", or "based on the data". Talk directly to the person about their hand, their physical traits, and their spiritual energy in a loving, human way.
5. Length: 300–450 words across all sections. Keep it extremely concise, cozy, and deeply impactful to respect the user's reading experience and save generation costs.
6. Treat palm-tone vitality as a visual signal from this photo, not a health, circulation, sleep, or energy diagnosis.

ABOUT FAINT, ABSENT, AND UNCLEAR LINES:
Keep faint or absent line interpretations bounded and gentle. Treat "not_assessable" as an observation limit, not a trait. Do not convert a weak or missing visual signal into a strong personality, relationship, career, health, or spiritual claim unless the supplied Vedic knowledge or classical passages support that exact nuance.

Use exactly these section headers (markdown H2):

## First Glance
One concise, warm paragraph. The strongest, most positive features of this hand — hand type, ruling planetary energy, vitality, the most prominent line or mount. Set a cozy, personal tone. If a chart dossier was provided, add one gentle sentence on overall chart-palm harmony; otherwise, summarize the hand's core supportive theme.

## The Major Lines
One cozy, flowing paragraph. Seamlessly blend your reading of the major lines Phase A found — clear, faint, fragmented, or absent (using the positive, gentle framing above). Tell a flowing story about how their heart, head, life, and fate lines work together to shape their inner world.

## Mounts and Planetary Architecture
One cozy paragraph. Lead with the most developed mount. Describe its warm influence on their personality. Briefly note any special marks (mystic cross, Ring of Solomon, Ring of Saturn) if they were detected — explain their rare, beautiful spiritual significance.

## Hand Architecture
One warm, brief paragraph. Hand type, finger shape, and thumb. What this cozy physical combination says about their natural temperament and approach to life.

## Love and Relationships
One cozy, supportive paragraph. Venus mount, heart line, and marriage indications, woven with the 7th house energy if a chart dossier is present. Focus on their beautiful capacity for connection, warmth, and emotional harmony.

## Career and Purpose
One cozy, supportive paragraph. Fate line (or its absence), Sun line, Saturn, Mercury, and Jupiter mounts, woven with 10th house indicators if a chart dossier is present. Focus on long-term fulfillment, creative expression, and walking their own unique path.

## Spiritual Path
One cozy paragraph ONLY IF something concrete supports it (mystic cross, Ring of Solomon, water hand, strong Luna, or ascendant/Ketu indicators in the dossier). Otherwise SKIP this section entirely.

## Where the Palm Meets the Chart
One warm paragraph synthesizing specific beautiful alignments between their palm and birth chart. IF the chart dossier is NOT provided, SKIP this section entirely.

## The Path Forward
One final, comforting paragraph. 2–3 gentle, supportive suggestions for their daily life, anchored to what you observed. Practical, cozy Samudrika wisdom to guide them. End with a loving, warm closing sentence.

Now produce only the Phase B Markdown reading (do NOT output the JSON again since we already have it)."""


def build_palm_reading_prompt(
    hand_metrics: dict,
    vitality: dict,
    quality_metrics: dict,
    n_mount_crops: int,
    dossier: str = "",
    knowledge_context: str = "",
    qdrant_context: str = "",
) -> str:
    """Backward-compatible prompt wrapper."""
    return build_phase_b_prompt(
        hand_metrics=hand_metrics,
        vitality=vitality,
        quality_metrics=quality_metrics,
        phase_a_json_str="{}",
        dossier=dossier,
        knowledge_context=knowledge_context,
        qdrant_context=qdrant_context,
    )
