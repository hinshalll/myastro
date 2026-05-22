"""features.face_reading.prompts — single-call VLM prompt (Phase A + Phase B).

Phase A — JSON observations the model confirms/refines from the photo (with
          generous not_assessable for anything occluded or unclear).
Phase B — warm, grounded Markdown reading anchored to Phase A + the measured
          geometry + the JSON knowledge block + (optionally) the kundli.

Design: ONE call. The measured facial geometry is treated as ground truth so
the model never guesses proportions; it only judges what landmarks can't see
(complexion, moles, expression) and synthesises. Respectful, non-diagnostic.
"""


def _metrics_block(m: dict) -> str:
    fs = m.get("face_shape", {}); z = m.get("zones", {}); e = m.get("eyes", {})
    n = m.get("nose", {}); lc = m.get("lips_chin", {}); sym = m.get("symmetry", {})
    return (
        f"- Face shape (measured): {fs.get('primary','?')} → element {fs.get('element','?')} "
        f"(confidence {fs.get('confidence','?')}; aspect {fs.get('aspect_ratio','?')}, "
        f"forehead/cheek {fs.get('forehead_to_cheek','?')}, jaw/cheek {fs.get('jaw_to_cheek','?')})\n"
        f"- Three zones: upper {z.get('upper','?')} / mid {z.get('mid','?')} / lower {z.get('lower','?')} "
        f"→ dominant {z.get('dominant','?')} (note: {z.get('note','')})\n"
        f"- Eyes: {e.get('size','?')}, {e.get('spacing','?')} (ratio {e.get('spacing_ratio','?')}), {e.get('tilt','?')}\n"
        f"- Nose: {n.get('length','?')} length, {n.get('width','?')} width\n"
        f"- Lips/jaw: lips {lc.get('lip_fullness','?')}, mouth {lc.get('mouth_width','?')}, jaw {lc.get('jaw','?')}\n"
        f"- Symmetry: {sym.get('label','?')} (score {sym.get('score','?')})\n"
    )


def build_face_reading_prompt(metrics: dict, quality_metrics: dict, pose_metrics: dict,
                              n_crops: int, knowledge_context: str = "",
                              dossier: str = "", use_kundli: bool = False) -> str:
    qm = quality_metrics or {}
    measured = _metrics_block(metrics or {})

    knowledge_block = ""
    if knowledge_context and len(knowledge_context.strip()) > 40:
        knowledge_block = f"\n<vedic_knowledge>\n{knowledge_context}\n</vedic_knowledge>\n"

    kundli_block = ""
    kundli_phase_a = ""
    kundli_section = ""
    if use_kundli and dossier and len(dossier.strip()) > 30:
        kundli_block = (
            f"\n<kundli_dossier>\n{dossier}\n</kundli_dossier>\n"
            "The person linked their OWN birth chart. Cross-reference the face with it — "
            "connect measured features to the ascendant, ascendant lord, and 1st-house "
            "planets using the face→Nakshatra map and ascendant-lord signatures in the "
            "knowledge block. Never invent chart facts not in the dossier.\n"
        )
        kundli_phase_a = ',\n  "face_chart_agreement": "strong|moderate|weak|cannot_assess",\n  "face_chart_note": "one sentence"'
        kundli_section = ("\n## Where Your Face Meets Your Chart\n"
                          "One paragraph. Concrete convergences AND tensions between the face and the "
                          "birth chart (e.g. a strong jaw mirroring a Mars-ruled ascendant). This is the "
                          "unique differentiator — make it specific, mention the agreement rating naturally.\n")

    return f"""Be conservative and kind. When uncertain, prefer the gentler reading and say you're uncertain. NEVER fabricate a feature, a mole, or a chart fact. Every claim must come from the measured geometry, the Phase A JSON you produce, the knowledge block, or the dossier.

You are an expert in Vedic face reading (Mukha Samudrika Shastra), reading a real photograph for a real person. This is traditional self-reflection — warm, insightful, respectful. It is NOT medical, psychological, or identity judgement, and you must never frame it as fact about who someone "is". Speak in terms of tendencies and traditional symbolism.

═══ INPUT IMAGES ═══
1. FACE (labelled) — the person's face, enhanced for clarity
2. {n_crops} REGION CROPS — close-ups (forehead, eyes, nose, mouth/chin) to judge detail

═══ MEASURED GEOMETRY (treat as ground truth — do NOT contradict the numbers) ═══
{measured}- Image quality: blur={qm.get('blur_score','?')}, exposure={qm.get('mean_v','?')}, resolution={qm.get('resolution','?')}
{knowledge_block}{kundli_block}
═══ PHASE A — VISUAL OBSERVATION (JSON first, in ```json``` fences) ═══

Confirm or gently refine the measured face shape and zone proportions from the actual image. Noisy MediaPipe landmark detections can shift based on head nod/tilt or camera angle, so you MUST visually verify the true primary face shape, element, and dominant horizontal zone (upper forehead vs mid nose vs lower mouth) using your high-resolution vision. If they differ from the measured values, correct them. Judge what geometry cannot: complexion/glow, moles or distinctive marks (give position + colour), eyebrow thickness, and expression. Use "not_assessable" generously — hair-covered forehead, hidden ears, glasses, etc. Report moles ONLY if clearly visible; otherwise "none_clearly_visible".

```json
{{
  "image_quality": "good|acceptable|poor",
  "image_issues": "brief note or empty string",
  "face_shape": {{ "observed": "square|round|oval|tapering|inverted_pot", "element": "earth|water|fire|air|ether", "agrees_with_measured": "yes|partly|no" }},
  "dominant_zone": "upper_forehead|mid_nose|lower_mouth|not_assessable",
  "forehead": {{ "observation": "...", "not_assessable": false }},
  "eyebrows": {{ "thickness": "thick|medium|thin|not_assessable", "shape": "arched|straight|curved|not_assessable" }},
  "eyes": {{ "observation": "...", "not_assessable": false }},
  "nose": {{ "observation": "...", "not_assessable": false }},
  "lips": {{ "observation": "...", "not_assessable": false }},
  "chin_jaw": {{ "observation": "...", "not_assessable": false }},
  "cheeks": {{ "observation": "...", "not_assessable": false }},
  "ears": {{ "observation": "...", "not_assessable": true }},
  "complexion": {{ "tone": "...", "glow": "radiant|even|dull|not_assessable" }},
  "moles": "none_clearly_visible | [list each: position + colour]",
  "expression": "brief note"{kundli_phase_a}
}}
```

═══ PHASE B — THE READING (Markdown after the JSON) ═══

Use ONLY confirmed Phase A observations + the measured geometry + the knowledge block{(" + the kundli" if use_kundli else "")}. Flowing paragraphs, warm and specific. 600–900 words. Never state a feature Phase A marked not_assessable. Frame everything as traditional tendency, never fixed fate or medical/character verdict.

Use these markdown H2 section headers:

## First Impression
One paragraph. The face shape, its element, the dominant zone, and the overall impression they create.

## Element & Temperament
One paragraph. What the dominant element (and any element balance) says about their nature, using the knowledge block's traits.

## Feature by Feature
2–4 paragraphs covering the clearly-visible features (forehead, eyes & brows, nose, lips, chin/jaw). Tie each to its traditional meaning from the knowledge block. Skip anything not_assessable.

## Distinctive Marks
ONLY if a mole or distinctive mark was clearly visible — give its traditional meaning gently. Otherwise SKIP this section entirely.
{kundli_section}
## Strengths & Growth Edges
One paragraph. 2–3 genuine strengths and 1–2 gentle growth edges (use the "shadow" notes), framed kindly and constructively.

## A Closing Thought
One warm, grounding sentence.

═══ CONSTRAINTS ═══
• If image_quality is "poor", write a short Phase B asking for a clearer, front-facing, well-lit photo. Don't fabricate.
• Never give medical, psychiatric, hiring, or identity conclusions. No physiognomy-as-fact.
• No filler or generic horoscope phrasing — every sentence specific to this face.
• Don't write a section whose observations are all not_assessable.

Now produce the response: JSON first (Phase A in fences), then Phase B markdown."""
