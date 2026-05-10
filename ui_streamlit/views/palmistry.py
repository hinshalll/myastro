"""
ui_streamlit/views/palmistry.py
================================
Clean, accuracy-first palmistry UI.

Design principles:
  - One photo upload, one reading.
  - Show only what's reliably knowable, in detail.
  - The reading is the main content, beautifully formatted.
  - "What I actually observed" disclosure builds trust without cluttering.
  - Kundli-palm agreement badge is the unique differentiator.

What's gone vs the old UI:
  - Frangi Ridge Map (lied via the X-ray)
  - Mount Diagnostic grid + xray crops
  - "What the AI actually reads" expander with stitched canvas
  - Mount Prominence bars (measured lighting, not elevation)
  - Classical Marks panel with emojis (was noise classification)
  - Minor Lines panel (was presence-thresholding skin texture)
  - Dermatoglyphic Profile (impossible from non-macro photos)
  - Frangi Line Analysis with score/length/depth metrics (wrong components)

What's kept:
  - The user's actual palm (CLAHE-enhanced + landmark overlay)
  - Hand type, 2D:4D, dominant finger, vitality (deterministic, accurate)
  - The reading itself
  - Quality warnings (actionable for the user)
"""

import io
import base64
import streamlit as st
import PIL.Image
import numpy as np

from math_engine.palm_vision import analyze_palm
from math_engine.dossier_builder import generate_astrology_dossier
from ai_engine.palm_vision_ai import read_palm
from ui_streamlit.state import get_default_profile

# Optional integrations — graceful fallback if missing
try:
    from ai_engine.palm_knowledge_lookup import get_palm_context
except Exception:
    get_palm_context = None

try:
    from ai_engine.palmistry_qdrant import query_palmistry
except Exception:
    query_palmistry = None


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _to_pil(arr):
    if arr is None:
        return None
    if isinstance(arr, PIL.Image.Image):
        return arr
    return PIL.Image.fromarray(arr.astype(np.uint8))


def _build_legacy_palm_data(analysis):
    """
    Adapter for palm_knowledge_lookup.get_palm_context which expects the OLD
    palm_data schema. We construct a minimal compatible shape from the new
    analysis dict.
    """
    hm = analysis.get("hand_metrics", {})
    vit = analysis.get("vitality", {})
    return {
        "finger_data": {
            "hand_type":         hm.get("hand_type", ""),
            "hand_type_vedic":   hm.get("hand_type_vedic", ""),
            "ratio_2d4d":        hm.get("ratio_2d4d", 0),
            "ratio_reading":     hm.get("ratio_reading", ""),
            "dominant_finger":   hm.get("dominant_finger", ""),
        },
        "vitality_hsv":      vit.get("note", ""),
        "ui_vitality":       vit.get("class", ""),
        # Empty — VLM produces these now, so they're not pre-known
        "traced_lines":      {},
        "marks":             [],
        "minor_lines":       {},
        "fingerprints":      {},
    }


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════

def show_palmistry():
    _inject_styles()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """<div class='palm-header'>
            <h1>Palmistry</h1>
            <p>Samudrika Shastra · Kundli-aware reading</p>
        </div>""",
        unsafe_allow_html=True,
    )

    dp, _ = get_default_profile()
    if not dp:
        st.warning("Set a default profile in 'Saved Profiles' first — your kundli powers the reading.")
        return

    # ── Upload ────────────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload a photo of your dominant palm",
        type=["jpg", "jpeg", "png"],
        help="Flat hand, fingers slightly apart, full palm visible, even daylight.",
    )

    if uploaded_file is None:
        _render_capture_tips()
        return

    file_bytes = uploaded_file.getvalue()
    cache_key  = uploaded_file.name + str(len(file_bytes))

    # ── Run math (cached per upload) ──────────────────────────────────────────
    if (st.session_state.get("palm_cache_key") != cache_key
            or "palm_analysis" not in st.session_state):
        with st.spinner("Analyzing palm geometry..."):
            analysis = analyze_palm(file_bytes)
            st.session_state.palm_analysis = analysis
            st.session_state.palm_cache_key = cache_key
            st.session_state.pop("palm_reading", None)

    analysis = st.session_state.palm_analysis

    # ── Hard fail: no hand detected ───────────────────────────────────────────
    if not analysis["landmarks_found"]:
        st.error(
            "Could not detect a hand in this photo. Re-upload a clearer photo "
            "of an open palm with all fingers visible."
        )
        _render_capture_tips()
        return

    # ── Quality warnings (soft — user can still proceed) ──────────────────────
    for issue in analysis["quality_issues"]:
        st.warning(issue)

    # ── Palm + signals row ────────────────────────────────────────────────────
    col_palm, col_signals = st.columns([1, 1.15], gap="large")

    with col_palm:
        st.image(
            _to_pil(analysis["landmark_overlay"]),
            caption="Your palm (geometry mapped)",
            use_container_width=True,
        )

    with col_signals:
        _render_signals_card(analysis)

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    # ── Reading section ───────────────────────────────────────────────────────
    if "palm_reading" not in st.session_state:
        st.session_state.palm_reading = None

    if st.session_state.palm_reading is None:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("✨ Generate Full Reading", type="primary", use_container_width=True):
                _run_reading(dp, analysis)
                st.rerun()
    else:
        _render_reading(st.session_state.palm_reading)


# ══════════════════════════════════════════════════════════════════════════════
# SIGNALS CARD
# ══════════════════════════════════════════════════════════════════════════════

def _render_signals_card(analysis):
    """Compact card. Only math-reliable signals. No false precision."""
    hm = analysis.get("hand_metrics", {})
    vit = analysis.get("vitality", {})

    st.markdown(
        f"""<div class='signals-card'>

            <div class='sig-label'>Hand Type</div>
            <div class='sig-value-lg'>{hm.get('hand_type', '—')}</div>
            <div class='sig-sub'>{hm.get('hand_type_vedic', '')} · {hm.get('hand_type_gloss', '')}</div>

            <div class='sig-divider'></div>

            <div class='sig-grid'>
                <div>
                    <div class='sig-label'>2D:4D Ratio</div>
                    <div class='sig-value'>{hm.get('ratio_2d4d', '—')}</div>
                    <div class='sig-sub-sm'>{hm.get('ratio_reading', '')}</div>
                </div>
                <div>
                    <div class='sig-label'>Vitality</div>
                    <div class='sig-value'>{vit.get('class', '—')}</div>
                    <div class='sig-sub-sm'>{vit.get('note', '')}</div>
                </div>
            </div>

            <div class='sig-divider'></div>

            <div class='sig-grid'>
                <div>
                    <div class='sig-label'>Dominant Finger</div>
                    <div class='sig-value-sm'>{hm.get('dominant_finger', '—')}</div>
                </div>
                <div>
                    <div class='sig-label'>Thumb Proportion</div>
                    <div class='sig-value-sm'>{hm.get('thumb_proportion', '—')}</div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# READING PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def _run_reading(dp, analysis):
    """Single VLM call, parse, store in session state. Synchronous."""
    placeholder = st.empty()
    placeholder.markdown(
        """<div class='loading-block'>
            <div class='loading-spinner'>✨</div>
            <div class='loading-text'>Reading your palm...</div>
            <div class='loading-sub'>This usually takes 5–15 seconds.</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Build context ─────────────────────────────────────────────────────────
    dossier = generate_astrology_dossier(dp) or ""
    legacy_data = _build_legacy_palm_data(analysis)

    knowledge_context = ""
    if get_palm_context:
        try:
            ctx = get_palm_context(legacy_data, {}, dossier)
            if ctx and isinstance(ctx, dict):
                knowledge_context = ctx.get("formatted_block", "") or ""
        except Exception:
            knowledge_context = ""

    qdrant_context = ""
    if query_palmistry:
        try:
            qdrant_context = query_palmistry(legacy_data, {}) or ""
        except Exception:
            qdrant_context = ""

    # ── Single VLM call ───────────────────────────────────────────────────────
    result = read_palm(
        enhanced_palm     = analysis["enhanced_palm"],
        mount_crops       = analysis["mount_crops"],
        hand_metrics      = analysis["hand_metrics"],
        vitality          = analysis["vitality"],
        quality_metrics   = analysis["quality_metrics"],
        dossier           = dossier,
        knowledge_context = knowledge_context,
        qdrant_context    = qdrant_context,
    )

    placeholder.empty()
    st.session_state.palm_reading = result


# ══════════════════════════════════════════════════════════════════════════════
# READING RENDER
# ══════════════════════════════════════════════════════════════════════════════

def _render_reading(result):
    """Render parsed VLM output. Phase B is the main reading; Phase A is collapsible."""
    if result.get("error"):
        st.error(result["error"])
        return

    phase_a = result.get("phase_a", {}) or {}
    phase_b = (result.get("phase_b", "") or "").strip()

    # Image quality block
    img_quality = phase_a.get("image_quality", "")
    if img_quality == "poor" or not phase_b:
        msg = phase_a.get("image_issues", "") or "The image quality isn't sufficient."
        st.error(f"📷 {msg}")
        with st.expander("Show raw response (debug)"):
            st.text((result.get("raw") or "")[:3000])
        return

    # Kundli-palm agreement badge (the differentiator)
    agreement = phase_a.get("kundli_palm_agreement", "")
    agreement_note = phase_a.get("kundli_palm_agreement_note", "")
    if agreement and agreement != "cannot_assess":
        _render_agreement_badge(agreement, agreement_note)

    # Main reading card
    st.markdown(
        f"""<div class='reading-card'>
            {_format_markdown_for_display(phase_b)}
        </div>""",
        unsafe_allow_html=True,
    )

    # Disclosure expander — what the AI actually saw
    with st.expander("🔍 What I actually observed in your photo", expanded=False):
        st.caption(
            "This is what the AI could and could not see. The reading above only "
            "interprets confirmed observations. Anything marked 'not_assessable' "
            "or 'not_visible' was deliberately left out of the reading."
        )
        _render_phase_a(phase_a)

    # Footer actions
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([1, 1, 1])

    with fc1:
        # Download as markdown
        md_bytes = _build_markdown_export(phase_b, phase_a).encode("utf-8")
        st.download_button(
            "⬇  Download (.md)",
            data=md_bytes,
            file_name="palm_reading.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with fc2:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.palm_reading = None
            st.rerun()

    with fc3:
        if st.button("📷 New Photo", use_container_width=True):
            for k in ("palm_reading", "palm_analysis", "palm_cache_key"):
                st.session_state.pop(k, None)
            st.rerun()


def _render_agreement_badge(level, note):
    color_map = {
        "strong":   ("#6adb8e", "#1e3d28"),
        "moderate": ("#d4a84b", "#3d2f1a"),
        "weak":     ("#c87a8c", "#3d1e26"),
    }
    fg, bg = color_map.get(level, ("#a0a0a0", "#2a2a2a"))
    st.markdown(
        f"""<div class='agreement-badge' style='border-color:{fg}66;background:{bg}33'>
            <div class='agreement-row'>
                <div class='agreement-label'>Kundli ↔ Palm Agreement</div>
                <div class='agreement-value' style='color:{fg}'>{level.title()}</div>
            </div>
            {f'<div class="agreement-note">{note}</div>' if note else ''}
        </div>""",
        unsafe_allow_html=True,
    )


def _render_phase_a(phase_a):
    """Render structured observations honestly."""
    if not isinstance(phase_a, dict):
        return

    lines = phase_a.get("lines", {}) or {}
    mounts = phase_a.get("mounts", {}) or {}

    # Lines
    if lines:
        st.markdown("**Major lines visible:**")
        line_order = [
            ("heart", "Heart Line"),
            ("head",  "Head Line"),
            ("life",  "Life Line"),
            ("fate",  "Fate Line"),
            ("sun",   "Sun Line"),
        ]
        emoji_map = {
            "clear":          ("✓", "#6adb8e"),
            "faint":          ("~", "#d4a84b"),
            "fragmented":     ("·", "#d4a84b"),
            "not_visible":    ("✗", "#9a6ab5"),
            "not_assessable": ("?", "#888"),
        }
        for key, display in line_order:
            ld = lines.get(key, {}) or {}
            vis = ld.get("visibility", "—")
            path = ld.get("path", "") or ""
            emoji, color = emoji_map.get(vis, ("·", "#888"))
            path_html = ""
            if path and vis not in ("not_assessable", "not_visible"):
                path_html = (
                    f"<div class='obs-path'>{path}</div>"
                )
            st.markdown(
                f"""<div class='obs-row'>
                    <span class='obs-icon' style='color:{color}'>{emoji}</span>
                    <span class='obs-name'>{display}</span>
                    <span class='obs-vis'>{vis}</span>
                    {path_html}
                </div>""",
                unsafe_allow_html=True,
            )

        simian = lines.get("simian", {}) or {}
        if simian.get("present"):
            st.markdown(
                f"<div class='obs-row'><span class='obs-icon' style='color:#d4a84b'>⚡</span> "
                f"<b>Simian pattern detected</b> "
                f"<span class='obs-vis'>(confidence: {simian.get('confidence', 'low')})</span></div>",
                unsafe_allow_html=True,
            )

    # Mounts
    if mounts:
        st.markdown("<br>**Mount observations:**", unsafe_allow_html=True)
        for mount_name in ["Jupiter", "Saturn", "Sun", "Mercury", "Venus", "Mars", "Luna"]:
            md = mounts.get(mount_name, {}) or {}
            full = md.get("fullness", "—")
            marks = md.get("marks", "") or ""
            marks_html = ""
            if marks and "no notable" not in marks.lower() and marks != "—":
                marks_html = f" · <span style='color:#d4af37'>{marks}</span>"
            st.markdown(
                f"<div class='obs-row'><b>{mount_name}</b>: "
                f"<span class='obs-vis'>{full}</span>{marks_html}</div>",
                unsafe_allow_html=True,
            )

    # Fingers + thumb
    fingers = phase_a.get("fingers", {}) or {}
    thumb = phase_a.get("thumb", {}) or {}
    if fingers or thumb:
        st.markdown("<br>**Finger and thumb observations:**", unsafe_allow_html=True)
        rows = []
        if fingers.get("tip_shape_dominant"):
            rows.append(f"Dominant tip shape: <b>{fingers['tip_shape_dominant']}</b>")
        if fingers.get("knotted_joints"):
            rows.append(f"Knotted joints: <b>{fingers['knotted_joints']}</b>")
        if fingers.get("spacing"):
            rows.append(f"Spacing: <b>{fingers['spacing']}</b>")
        if thumb.get("set"):
            rows.append(f"Thumb set: <b>{thumb['set']}</b>")
        if thumb.get("flexibility_estimate"):
            rows.append(f"Thumb flexibility: <b>{thumb['flexibility_estimate']}</b>")
        for r in rows:
            st.markdown(f"<div class='obs-row'>{r}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MARKDOWN FORMATTING + EXPORT
# ══════════════════════════════════════════════════════════════════════════════

def _format_markdown_for_display(md):
    """Convert minimal markdown to styled HTML for the reading card."""
    import re
    md = md.replace("\r\n", "\n")
    # H2 → styled header
    md = re.sub(
        r'^##\s+(.+)$',
        r'<h2 class="reading-h2">\1</h2>',
        md, flags=re.MULTILINE,
    )
    # Bold
    md = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', md)
    # Italic
    md = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', md)
    # Paragraphs
    md = re.sub(r'\n\n+', '</p><p class="reading-p">', md)
    md = '<p class="reading-p">' + md + '</p>'
    md = re.sub(r'<p[^>]*>\s*(<h2[^>]*>)', r'\1', md)
    md = re.sub(r'(</h2>)\s*</p>', r'\1', md)
    md = re.sub(r'<p[^>]*>\s*</p>', '', md)
    return md


def _build_markdown_export(phase_b, phase_a):
    """Build a clean markdown file for download."""
    out = ["# Palm Reading", "", "*Samudrika Shastra · Astro Suite*", "", "---", "", phase_b.strip(), ""]

    agreement = phase_a.get("kundli_palm_agreement", "") if isinstance(phase_a, dict) else ""
    if agreement and agreement != "cannot_assess":
        note = phase_a.get("kundli_palm_agreement_note", "") if isinstance(phase_a, dict) else ""
        out.extend(["---", "", f"**Kundli–Palm Agreement:** {agreement.title()}", "", note, ""])

    out.extend(["---", "", "## What was actually observed", ""])

    lines = (phase_a or {}).get("lines", {}) or {}
    if lines:
        out.append("### Lines")
        for key in ["heart", "head", "life", "fate", "sun"]:
            ld = lines.get(key, {}) or {}
            vis = ld.get("visibility", "—")
            path = ld.get("path", "") or ""
            out.append(f"- **{key.title()} line:** {vis}" + (f" — {path}" if path and vis not in ("not_assessable", "not_visible") else ""))
        out.append("")

    mounts = (phase_a or {}).get("mounts", {}) or {}
    if mounts:
        out.append("### Mounts")
        for m in ["Jupiter", "Saturn", "Sun", "Mercury", "Venus", "Mars", "Luna"]:
            md = mounts.get(m, {}) or {}
            full = md.get("fullness", "—")
            marks = md.get("marks", "") or ""
            extra = f" · {marks}" if marks and "no notable" not in marks.lower() else ""
            out.append(f"- **{m}:** {full}{extra}")
        out.append("")

    return "\n".join(out)


# ══════════════════════════════════════════════════════════════════════════════
# CAPTURE TIPS
# ══════════════════════════════════════════════════════════════════════════════

def _render_capture_tips():
    st.markdown(
        """<div class='tips-card'>
            <div class='sig-label'>For the most accurate reading</div>
            <div class='tips-list'>
                <div>• <b>Natural daylight</b> — no flash, no harsh overhead light</div>
                <div>• <b>Hand flat and fully open</b>, fingers slightly apart</div>
                <div>• <b>Camera directly above</b>, not at an angle</div>
                <div>• <b>No shadows</b> falling across the palm</div>
                <div>• Use your <b>dominant hand</b></div>
                <div>• <b>Crop tightly</b> — palm should fill most of the frame</div>
                <div>• Minimum resolution <b>1080p</b></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# STYLES (single block, scoped class names)
# ══════════════════════════════════════════════════════════════════════════════

def _inject_styles():
    st.markdown(
        """<style>
        /* Header */
        .palm-header { padding: 0.6rem 0 1rem; }
        .palm-header h1 {
            margin: 0; font-size: 1.95rem; font-weight: 600;
            color: #f0e9ff; letter-spacing: -0.01em;
        }
        .palm-header p {
            margin: 0.25rem 0 0; color: rgba(200,190,220,0.6);
            font-size: 0.9rem; letter-spacing: 0.4px;
        }

        /* Signals card */
        .signals-card {
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
        }
        .sig-label {
            font-size: 0.7rem; color: rgba(200,190,220,0.55);
            text-transform: uppercase; letter-spacing: 1.2px;
            margin-bottom: 0.25rem;
        }
        .sig-value-lg {
            font-size: 1.3rem; font-weight: 500; color: #f0e9ff; line-height: 1.2;
        }
        .sig-value {
            font-size: 1.05rem; font-weight: 500; color: #f0e9ff; line-height: 1.2;
        }
        .sig-value-sm {
            font-size: 0.95rem; font-weight: 500; color: #f0e9ff; line-height: 1.2;
        }
        .sig-sub {
            font-size: 0.82rem; color: rgba(200,190,220,0.7); margin-top: 0.15rem;
        }
        .sig-sub-sm {
            font-size: 0.74rem; color: rgba(200,190,220,0.65);
            line-height: 1.35; margin-top: 0.1rem;
        }
        .sig-divider {
            height: 1px; background: rgba(255,255,255,0.06); margin: 1rem 0;
        }
        .sig-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem;
        }

        /* Loading */
        .loading-block {
            text-align: center; padding: 3rem 0;
            color: rgba(200,190,220,0.75);
        }
        .loading-spinner {
            font-size: 2.4rem; margin-bottom: 1rem;
            animation: spin 2.5s linear infinite;
            display: inline-block;
        }
        .loading-text { font-size: 1rem; margin-bottom: 0.4rem; }
        .loading-sub { font-size: 0.8rem; color: rgba(200,190,220,0.5); }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to   { transform: rotate(360deg); }
        }

        /* Agreement badge */
        .agreement-badge {
            border: 1px solid;
            border-radius: 12px; padding: 0.85rem 1.1rem;
            margin: 0.4rem 0 1rem;
        }
        .agreement-row {
            display: flex; justify-content: space-between; align-items: center;
        }
        .agreement-label {
            font-size: 0.72rem; color: rgba(200,190,220,0.65);
            text-transform: uppercase; letter-spacing: 1.2px;
        }
        .agreement-value {
            font-size: 1.05rem; font-weight: 600; letter-spacing: 0.3px;
        }
        .agreement-note {
            font-size: 0.82rem; color: rgba(220,210,240,0.75);
            margin-top: 0.4rem; line-height: 1.45;
        }

        /* Reading card */
        .reading-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.01));
            border: 1px solid rgba(212,175,55,0.20);
            border-radius: 18px;
            padding: 2rem 2.3rem;
            color: #e8e2f0;
        }
        .reading-h2 {
            color: #d4af37; font-size: 1.18rem; font-weight: 600;
            margin: 1.7rem 0 0.7rem; letter-spacing: 0.5px;
            border-bottom: 1px solid rgba(212,175,55,0.15);
            padding-bottom: 0.4rem;
        }
        .reading-h2:first-child { margin-top: 0; }
        .reading-p {
            margin: 0 0 1rem; line-height: 1.78; font-size: 1rem;
        }

        /* Observations (Phase A disclosure) */
        .obs-row {
            font-size: 0.88rem; padding: 0.25rem 0;
            color: rgba(220,210,240,0.85); line-height: 1.45;
        }
        .obs-icon {
            display: inline-block; width: 1.4rem;
            font-weight: 700; text-align: center;
        }
        .obs-name { font-weight: 600; }
        .obs-vis {
            color: rgba(200,190,220,0.7); margin-left: 0.4rem;
        }
        .obs-path {
            font-size: 0.78rem; color: rgba(200,190,220,0.55);
            margin: 0.15rem 0 0.2rem 1.4rem; line-height: 1.4;
        }

        /* Tips card */
        .tips-card {
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            margin-top: 0.8rem;
        }
        .tips-list {
            color: rgba(220,210,240,0.85); font-size: 0.9rem;
            line-height: 1.95; margin-top: 0.5rem;
        }
        </style>""",
        unsafe_allow_html=True,
    )
