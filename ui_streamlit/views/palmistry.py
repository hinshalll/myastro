"""
ui_streamlit/views/palmistry.py

Changes in this version:
  - Line Map tab dropped entirely (was producing ugly over-processed images)
  - Premium animated palm display: palm photo inside a circular frame with
    rotating concentric rings, pulsing glow, and twinkling stars — rendered
    via st.components.v1.html() to guarantee CSS animations work
  - Loading animation restored: spinning ✨ with inline @keyframes
  - Vitality now reads from raw (pre-CLAHE) image in palm_vision.py
  - User-friendly signals card (plain language, no jargon)
  - Single "Start Fresh" button clears uploader via key increment
  - Fingers & thumb included in markdown export
"""

import base64
import cv2
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import PIL.Image

from math_engine.palm_vision import analyze_palm
from math_engine.dossier_builder import generate_astrology_dossier
from ai_engine.palm_vision_ai import read_palm
from ui_streamlit.state import get_default_profile

try:
    from ai_engine.palm_knowledge_lookup import get_palm_context
except Exception:
    get_palm_context = None

try:
    from ai_engine.palmistry_qdrant import query_palmistry
except Exception:
    query_palmistry = None


# ── Planet traits (plain language) ───────────────────────────────────────────
_PLANET_TRAITS = {
    "Jupiter (index)":  ("Jupiter ♃", "Wisdom, optimism, and a natural gift for guiding others"),
    "Saturn (middle)":  ("Saturn ♄", "Depth, patience, and a strong sense of responsibility"),
    "Sun (ring)":       ("Sun ☀",    "Creativity, warmth, and a drive to shine"),
    "Mercury (little)": ("Mercury ☿", "Sharp mind, quick wit, talent for communication"),
}

_VITALITY_LABEL = {
    "Robust":   ("High Energy ⚡",    "Strong and well-energised right now"),
    "Balanced": ("Steady & Even 🌿",  "Good, consistent energy levels"),
    "Subdued":  ("Needs Rest 🌙",      "Energy is lower — prioritise sleep and calm"),
    "Cool":     ("Variable Energy 🌊", "Energy fluctuates — listen to your body"),
    "unknown":  ("—",                  ""),
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _to_pil(arr):
    if arr is None:
        return None
    if isinstance(arr, PIL.Image.Image):
        return arr
    return PIL.Image.fromarray(arr.astype(np.uint8))


def _arr_to_b64_jpeg(arr, quality=88):
    """Convert RGB numpy array to base64 JPEG string for embedding in HTML."""
    bgr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf.tobytes()).decode()


def _arr_to_b64_png(arr):
    """Convert RGB or RGBA numpy array to base64 PNG string. Preserves alpha."""
    arr = arr.astype(np.uint8)
    if arr.ndim == 3 and arr.shape[2] == 4:
        bgra = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
        _, buf = cv2.imencode('.png', bgra)
    else:
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        _, buf = cv2.imencode('.png', bgr)
    return base64.b64encode(buf.tobytes()).decode()


def _build_legacy_palm_data(analysis):
    hm  = analysis.get("hand_metrics", {})
    vit = analysis.get("vitality", {})
    return {
        "finger_data": {
            "hand_type":       hm.get("hand_type", ""),
            "hand_type_vedic": hm.get("hand_type_vedic", ""),
            "ratio_2d4d":      hm.get("ratio_2d4d", 0),
            "ratio_reading":   hm.get("ratio_reading", ""),
            "dominant_finger": hm.get("dominant_finger", ""),
        },
        "vitality_hsv": vit.get("note", ""),
        "ui_vitality":  vit.get("class", ""),
        "traced_lines": {},
        "marks":        [],
        "minor_lines":  {},
        "fingerprints": {},
    }


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════

def show_palmistry():
    _inject_styles()

    st.markdown("## 🖐 Palm Reading")
    st.caption("Samudrika Shastra · Kundli-aware reading")

    dp, _ = get_default_profile()
    if not dp:
        st.warning("Set a default profile in 'Saved Profiles' first — your kundli powers the reading.")
        return

    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded_file = st.file_uploader(
        "Upload a photo of your dominant palm",
        type=["jpg", "jpeg", "png"],
        help="Flat hand, fingers slightly apart, full palm visible, even daylight.",
        key=f"palm_upload_{st.session_state.uploader_key}",
    )

    if uploaded_file is None:
        _render_capture_tips()
        return

    file_bytes = uploaded_file.getvalue()
    cache_key  = uploaded_file.name + str(len(file_bytes))

    if (st.session_state.get("palm_cache_key") != cache_key
            or "palm_analysis" not in st.session_state):
        with st.spinner("Analysing your palm..."):
            analysis = analyze_palm(file_bytes)
            st.session_state.palm_analysis  = analysis
            st.session_state.palm_cache_key = cache_key
            st.session_state.pop("palm_reading", None)

    analysis = st.session_state.palm_analysis

    if not analysis["landmarks_found"]:
        st.error("Could not detect a hand. Re-upload a clearer photo with the full open palm visible.")
        _render_capture_tips()
        return

    for issue in analysis["quality_issues"]:
        st.warning(issue)

    # ── Premium palm display + signals ────────────────────────────────────────
    col_palm, col_signals = st.columns([1, 1.1], gap="large")

    with col_palm:
        _render_premium_palm(analysis)

    with col_signals:
        _render_signals_card(analysis)

    st.divider()

    # ── Reading ───────────────────────────────────────────────────────────────
    if "palm_reading" not in st.session_state:
        st.session_state.palm_reading = None

    if st.session_state.palm_reading is None:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("✨ Generate My Reading", type="primary", use_container_width=True):
                _run_reading(dp, analysis)
                st.rerun()
    else:
        _render_reading(st.session_state.palm_reading)


# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM ANIMATED PALM DISPLAY
# Uses st.components.v1.html() — renders in an iframe, CSS animations guaranteed
# ══════════════════════════════════════════════════════════════════════════════

def _render_premium_palm(analysis):
    isolated = analysis.get("hand_isolated")
    use_alpha = isolated is not None

    if use_alpha:
        b64 = _arr_to_b64_png(isolated)
        mime = "png"
    else:
        overlay = analysis.get("landmark_overlay")
        if overlay is None:
            overlay = analysis.get("enhanced_palm")
        if overlay is None:
            return
        b64 = _arr_to_b64_jpeg(overlay, quality=85)
        mime = "jpeg"

    palm_html = (
        '<div class="palm-float">'
        f'<img src="data:image/{mime};base64,{b64}" alt="palm" />'
        '</div>'
        if use_alpha else
        '<div class="palm-circle">'
        f'<img src="data:image/{mime};base64,{b64}" alt="palm" />'
        '</div>'
    )

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: radial-gradient(ellipse at center,
      #1a1530 0%,
      #14111e 40%,
      #0a0814 80%,
      #050309 100%);
    display: flex;
    justify-content: center;
    align-items: center;
    height: 460px;
    overflow: hidden;
    position: relative;
  }}

  /* ── Aurora nebulae — three soft blobs that drift independently ── */
  .nebula {{
    position: absolute;
    border-radius: 50%;
    filter: blur(50px);
    opacity: 0.55;
    pointer-events: none;
  }}
  .nebula-1 {{
    width: 320px; height: 320px;
    background: radial-gradient(circle, #5a3a8a 0%, transparent 65%);
    animation: drift1 18s ease-in-out infinite;
  }}
  .nebula-2 {{
    width: 280px; height: 280px;
    background: radial-gradient(circle, #c89160 0%, transparent 65%);
    animation: drift2 22s ease-in-out infinite;
    opacity: 0.35;
  }}
  .nebula-3 {{
    width: 240px; height: 240px;
    background: radial-gradient(circle, #6080b0 0%, transparent 65%);
    animation: drift3 26s ease-in-out infinite;
    opacity: 0.30;
  }}
  @keyframes drift1 {{
    0%,100% {{ transform: translate(-90px, -70px) scale(1); }}
    50%      {{ transform: translate(-50px, -110px) scale(1.1); }}
  }}
  @keyframes drift2 {{
    0%,100% {{ transform: translate(110px, 80px) scale(1.05); }}
    50%      {{ transform: translate(70px, 50px) scale(0.95); }}
  }}
  @keyframes drift3 {{
    0%,100% {{ transform: translate(80px, -100px) scale(1); }}
    50%      {{ transform: translate(120px, -70px) scale(1.08); }}
  }}

  /* ── Stage centred ── */
  .stage {{
    position: relative;
    width: 460px;
    height: 460px;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 5;
  }}

  /* ── Single delicate ring — like an aura halo ── */
  .halo-ring {{
    position: absolute;
    width: 340px;
    height: 340px;
    border-radius: 50%;
    border: 1px solid rgba(212,175,55,0.18);
    box-shadow:
      0 0 30px rgba(212,175,55,0.08) inset,
      0 0 60px rgba(140,90,220,0.06) inset;
    animation: ring-rotate 80s linear infinite;
  }}
  .halo-ring::before {{
    content: '';
    position: absolute;
    top: -2px; left: 50%;
    width: 5px; height: 5px;
    margin-left: -2.5px;
    border-radius: 50%;
    background: rgba(255,210,140,0.95);
    box-shadow: 0 0 14px rgba(255,200,130,0.9);
  }}
  @keyframes ring-rotate {{
    from {{ transform: rotate(0deg); }}
    to   {{ transform: rotate(360deg); }}
  }}

  /* ── Inner aura — pulses softly behind the hand ── */
  .aura {{
    position: absolute;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle,
      rgba(245,200,140,0.22) 0%,
      rgba(180,130,220,0.10) 45%,
      transparent 75%);
    animation: aura-pulse 5s ease-in-out infinite;
  }}
  @keyframes aura-pulse {{
    0%,100% {{ transform: scale(0.95); opacity: 0.7; }}
    50%      {{ transform: scale(1.08); opacity: 1.0; }}
  }}

  /* ── Hand ── */
  .palm-float {{
    position: relative;
    z-index: 10;
    width: 240px;
    height: 240px;
    display: flex;
    justify-content: center;
    align-items: center;
  }}
  .palm-float img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    filter:
      drop-shadow(0 0 10px rgba(255,210,150,0.35))
      drop-shadow(0 0 22px rgba(140,90,220,0.28))
      drop-shadow(0 4px 18px rgba(0,0,0,0.4));
  }}

  /* ── Fallback circular clip ── */
  .palm-circle {{
    position: relative;
    z-index: 10;
    width: 220px; height: 220px;
    border-radius: 50%;
    overflow: hidden;
    border: 1.5px solid rgba(212,175,55,0.5);
    box-shadow:
      0 0 0 4px rgba(212,175,55,0.08),
      0 0 30px rgba(212,175,55,0.25);
  }}
  .palm-circle img {{
    width: 100%; height: 100%;
    object-fit: cover;
  }}

  /* ── Drifting particles (move in slow arcs, not blink) ── */
  .particle {{
    position: absolute;
    border-radius: 50%;
    background: rgba(255,220,170,0.85);
    box-shadow: 0 0 4px rgba(255,210,160,0.7);
    pointer-events: none;
  }}

  @keyframes drift-up-1 {{
    0%   {{ transform: translate(0, 0);          opacity: 0; }}
    15%  {{ opacity: 0.85; }}
    85%  {{ opacity: 0.85; }}
    100% {{ transform: translate(20px, -130px);  opacity: 0; }}
  }}
  @keyframes drift-up-2 {{
    0%   {{ transform: translate(0, 0);          opacity: 0; }}
    20%  {{ opacity: 0.75; }}
    80%  {{ opacity: 0.75; }}
    100% {{ transform: translate(-25px, -150px); opacity: 0; }}
  }}
  @keyframes drift-side {{
    0%   {{ transform: translate(0, 0);          opacity: 0; }}
    20%  {{ opacity: 0.7; }}
    80%  {{ opacity: 0.7; }}
    100% {{ transform: translate(80px, -40px);   opacity: 0; }}
  }}

  /* ── Wisp dots that sit further out (still, faint) ── */
  .wisp {{
    position: absolute;
    width: 2px;
    height: 2px;
    border-radius: 50%;
    background: rgba(255,240,210,0.45);
    animation: wisp-fade 4s ease-in-out infinite;
  }}
  @keyframes wisp-fade {{
    0%,100% {{ opacity: 0.15; }}
    50%      {{ opacity: 0.8; }}
  }}
</style>
</head>
<body>
  <div class="nebula nebula-1"></div>
  <div class="nebula nebula-2"></div>
  <div class="nebula nebula-3"></div>

  <div class="stage">
    <div class="halo-ring"></div>
    <div class="aura"></div>
    {palm_html}
  </div>

<script>
(function() {{
  var stage = document.querySelector('.stage');

  // Drifting particles — slow rising motes, each starting at a different time
  var particles = [
    {{x: 130, y: 380, size: 3,   dur: 8,  delay: 0,   anim: 'drift-up-1'}},
    {{x: 320, y: 370, size: 2.5, dur: 9,  delay: 2.5, anim: 'drift-up-2'}},
    {{x: 100, y: 340, size: 2,   dur: 10, delay: 5,   anim: 'drift-up-1'}},
    {{x: 350, y: 320, size: 3,   dur: 7,  delay: 3,   anim: 'drift-up-2'}},
    {{x: 200, y: 410, size: 2,   dur: 11, delay: 1,   anim: 'drift-up-1'}},
    {{x: 60,  y: 230, size: 1.5, dur: 14, delay: 4,   anim: 'drift-side'}},
    {{x: 400, y: 250, size: 2,   dur: 16, delay: 2,   anim: 'drift-side'}},
  ];
  particles.forEach(function(p) {{
    var el = document.createElement('div');
    el.className = 'particle';
    el.style.width  = p.size + 'px';
    el.style.height = p.size + 'px';
    el.style.left   = p.x + 'px';
    el.style.top    = p.y + 'px';
    el.style.animation = p.anim + ' ' + p.dur + 's ease-in-out ' + p.delay + 's infinite';
    stage.appendChild(el);
  }});

  // Static faint wisps scattered far from the hand
  var wisps = [
    [50, 80, 1.0], [410, 90, 1.5], [40, 380, 1.2], [420, 380, 0.8],
    [220, 50, 1.8], [220, 430, 1.4], [85, 200, 2.2], [380, 210, 0.5],
    [150, 30, 2.6], [310, 40, 1.6], [70, 300, 3.0], [395, 300, 0.7],
  ];
  wisps.forEach(function(w) {{
    var el = document.createElement('div');
    el.className = 'wisp';
    el.style.left = w[0] + 'px';
    el.style.top  = w[1] + 'px';
    el.style.animationDelay = w[2] + 's';
    stage.appendChild(el);
  }});
}})();
</script>
</body>
</html>
"""
    components.html(html, height=470, scrolling=False)



# ══════════════════════════════════════════════════════════════════════════════
# SIGNALS CARD — plain language, no jargon
# ══════════════════════════════════════════════════════════════════════════════

def _render_signals_card(analysis):
    hm  = analysis.get("hand_metrics", {})
    vit = analysis.get("vitality", {})

    st.markdown("**Your Hand Type**")
    st.markdown(f"### {hm.get('hand_type', '—')}")
    st.caption(hm.get("hand_type_gloss", ""))
    st.markdown("---")

    dom_raw = hm.get("dominant_finger", "")
    planet_label, planet_trait = _PLANET_TRAITS.get(
        dom_raw, (dom_raw.split("(")[0].strip() if dom_raw else "—", "")
    )
    st.markdown("**Ruling Planet**")
    st.markdown(f"### {planet_label}")
    if planet_trait:
        st.caption(planet_trait)
    st.markdown("---")

    vit_class = vit.get("class", "unknown")
    vit_label, vit_caption = _VITALITY_LABEL.get(vit_class, (vit_class, vit.get("note", "")))
    st.markdown("**Life Energy Right Now**")
    st.markdown(f"### {vit_label}")
    if vit_caption:
        st.caption(vit_caption)


# ══════════════════════════════════════════════════════════════════════════════
# READING PIPELINE — with proper loading animation
# ══════════════════════════════════════════════════════════════════════════════

def _run_reading(dp, analysis):
    # Animated loading placeholder — inline @keyframes so it works without external CSS
    loading = st.empty()
    loading.markdown(
        """
        <div style="text-align:center;padding:2.5rem 0;color:rgba(200,190,220,0.8)">
          <style>
            @keyframes _spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
            @keyframes _fade { 0%,100%{opacity:.4} 50%{opacity:1} }
          </style>
          <div style="font-size:2.8rem;display:inline-block;
                      animation:_spin 3s linear infinite">✨</div>
          <div style="font-size:1.05rem;margin-top:1rem;
                      animation:_fade 2s ease-in-out infinite">
            Reading your palm…
          </div>
          <div style="font-size:0.8rem;margin-top:.4rem;
                      color:rgba(200,190,220,0.5)">
            Connecting your chart to your hand · 10–20 seconds
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    dossier     = generate_astrology_dossier(dp) or ""
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

    loading.empty()
    st.session_state.palm_reading = result


# ══════════════════════════════════════════════════════════════════════════════
# READING RENDER
# ══════════════════════════════════════════════════════════════════════════════

def _render_reading(result):
    if result.get("error"):
        st.error(result["error"])
        return

    phase_a = result.get("phase_a", {}) or {}
    phase_b = (result.get("phase_b", "") or "").strip()

    if phase_a.get("image_quality") == "poor" or not phase_b:
        msg = phase_a.get("image_issues", "") or "Image quality insufficient for a confident reading."
        st.error(f"📷 {msg}")
        if result.get("raw"):
            with st.expander("Raw response (debug)"):
                st.text(result["raw"][:3000])
        _render_start_fresh()
        return

    agreement      = phase_a.get("kundli_palm_agreement", "")
    agreement_note = phase_a.get("kundli_palm_agreement_note", "")
    if agreement and agreement != "cannot_assess":
        _render_agreement_badge(agreement, agreement_note)

    # Reading text — already markdown
    st.markdown(phase_b)

    with st.expander("🔍 What the AI actually saw in your photo", expanded=False):
        st.caption(
            "Your reading is based only on what was clearly visible. "
            "Lines marked ❓ were too unclear to include — that's honest, not a bug."
        )
        _render_phase_a(phase_a)

    st.divider()

    fc1, fc2, fc3 = st.columns([1, 1, 1])
    with fc1:
        # Build PDF on demand. Wrapped in try/except so a PDF failure
        # never blocks the user from seeing their reading.
        try:
            from ui_streamlit.views.palm_pdf import build_palm_pdf

            # Build cover image bytes from the isolated hand (or fallback)
            analysis = st.session_state.get("palm_analysis", {}) or {}
            isolated = analysis.get("hand_isolated")
            if isolated is not None:
                cover_b64 = _arr_to_b64_png(isolated)
            else:
                overlay = analysis.get("enhanced_palm")
                cover_b64 = _arr_to_b64_jpeg(overlay, quality=90) if overlay is not None else ""
            import base64 as _b64
            cover_bytes = _b64.b64decode(cover_b64) if cover_b64 else None

            # Signals for the PDF observations page
            hm  = analysis.get("hand_metrics", {}) or {}
            vit = analysis.get("vitality", {}) or {}
            dom_raw = hm.get("dominant_finger", "")
            planet_label = _PLANET_TRAITS.get(
                dom_raw, (dom_raw.split("(")[0].strip() if dom_raw else "-", "")
            )[0]
            vit_label = _VITALITY_LABEL.get(vit.get("class", "unknown"), ("-", ""))[0]
            signals = {
                "hand_type": hm.get("hand_type", "-"),
                "planet":    planet_label,
                "vitality":  vit_label,
            }

            # User name from default profile
            try:
                dp, _ = get_default_profile()
                user_name = (dp or {}).get("name", "") if dp else ""
            except Exception:
                user_name = ""

            pdf_bytes = build_palm_pdf(
                phase_b        = phase_b,
                phase_a        = phase_a,
                signals        = signals,
                palm_png_bytes = cover_bytes,
                user_name      = user_name,
            )
            st.download_button(
                "⬇ Download PDF",
                data=pdf_bytes,
                file_name="palm_reading.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            # Fallback to markdown if PDF generation fails
            st.download_button(
                "⬇ Download (.md)",
                data=_build_markdown_export(phase_b, phase_a).encode("utf-8"),
                file_name="palm_reading.md",
                mime="text/markdown",
                use_container_width=True,
                help=f"PDF generation failed: {type(e).__name__}",
            )
    with fc3:
        _render_start_fresh()


def _render_start_fresh():
    if st.button("📷 Start Fresh", use_container_width=True):
        st.session_state.uploader_key = st.session_state.get("uploader_key", 0) + 1
        for k in ("palm_reading", "palm_analysis", "palm_cache_key"):
            st.session_state.pop(k, None)
        st.rerun()


def _render_agreement_badge(level, note):
    level_l = (level or "").lower()
    friendly = {
        "strong":   "Your birth chart and your palm are saying the same thing — strong convergence.",
        "moderate": "Your chart and palm broadly agree, with some interesting differences.",
        "weak":     "Your chart and palm point in different directions — worth exploring why.",
    }
    body_note = friendly.get(level_l, note or "")
    if note and note.strip() not in body_note:
        body_note += f" {note}"
    body = f"**Chart & Palm: {level.title()} Agreement**\n\n{body_note}"
    {"strong": st.success, "moderate": st.info, "weak": st.warning}.get(level_l, st.info)(body)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE A OBSERVATIONS — plain English, no HTML tags
# ══════════════════════════════════════════════════════════════════════════════

_VIS_ICON = {
    "clear":          "✅ Clearly visible",
    "faint":          "🟡 Faintly visible",
    "fragmented":     "🟡 Present but broken",
    "not_visible":    "❌ Not present",
    "not_assessable": "❓ Couldn't read clearly",
}

_LINE_NAMES = {
    "heart": "Heart Line — emotions and relationships",
    "head":  "Head Line — thinking style and decisions",
    "life":  "Life Line — energy and life path",
    "fate":  "Fate Line — career and life direction",
    "sun":   "Sun Line — recognition and success",
}

_MOUNT_MEANING = {
    "Jupiter": "ambition & leadership",
    "Saturn":  "discipline & wisdom",
    "Sun":     "creativity & fame",
    "Mercury": "communication & intellect",
    "Venus":   "love & beauty",
    "Mars":    "courage & drive",
    "Luna":    "imagination & intuition",
}

_FULLNESS_LABEL = {
    "prominent":      "Well developed — strong influence",
    "moderate":       "Moderate — balanced influence",
    "flat":           "Underdeveloped — less prominent",
    "not_assessable": "Couldn't assess clearly",
}


def _render_phase_a(phase_a):
    if not isinstance(phase_a, dict):
        return

    lines   = phase_a.get("lines",   {}) or {}
    mounts  = phase_a.get("mounts",  {}) or {}
    fingers = phase_a.get("fingers", {}) or {}
    thumb   = phase_a.get("thumb",   {}) or {}

    if lines:
        st.markdown("**The main lines:**")
        rows = []
        for key, display in _LINE_NAMES.items():
            ld   = lines.get(key) or {}
            vis  = ld.get("visibility") or "—"
            icon = _VIS_ICON.get(vis, f"· {vis}")
            path = ld.get("path") or ""
            show_path = path and vis in ("clear", "faint", "fragmented") and path.lower() != "not_assessable"
            rows.append(f"**{display}**\n{icon}" + (f" — *{path}*" if show_path else ""))

        simian = lines.get("simian") or {}
        if simian.get("present"):
            rows.append(f"**Simian Line** (Heart + Head merged)\n✅ Detected — confidence: {simian.get('confidence','low')}")

        st.markdown("\n\n".join(rows))

    if mounts:
        st.markdown("**Planetary mounts:**")
        mount_rows = []
        for mn in ["Jupiter", "Saturn", "Sun", "Mercury", "Venus", "Mars", "Luna"]:
            md     = mounts.get(mn) or {}
            full   = md.get("fullness") or "—"
            marks  = md.get("marks") or ""
            label  = _FULLNESS_LABEL.get(full, full)
            row    = f"- **{mn}** *({_MOUNT_MEANING.get(mn,'')})* — {label}"
            if marks and "no notable" not in marks.lower() and marks != "—":
                row += f" · *{marks}*"
            mount_rows.append(row)
        st.markdown("\n".join(mount_rows))

    # ── Special marks (mystic cross, Ring of Solomon, Ring of Saturn) ─────────
    special = phase_a.get("special_marks", {}) or {}
    special_rows = []
    _SPECIAL_MEANING = {
        "mystic_cross":    ("Mystic Cross", "between heart and head lines — strong intuition and interest in the occult"),
        "ring_of_solomon": ("Ring of Solomon", "around Jupiter mount — wisdom, leadership, ability to read others"),
        "ring_of_saturn":  ("Ring of Saturn", "around Saturn mount — introspective and prone to isolation; rare and significant"),
    }
    for key, (label, meaning) in _SPECIAL_MEANING.items():
        v = special.get(key, "")
        if v == "visible":
            special_rows.append(f"- ✅ **{label}** detected — *{meaning}*")
    if special_rows:
        st.markdown("**Rare and special marks:**")
        st.markdown("\n".join(special_rows))

    if fingers or thumb:
        _tip_map = {
            "conic":     "Rounded / conic — intuitive and artistic",
            "square":    "Square — practical and methodical",
            "spatulate": "Spatulate — energetic and unconventional",
            "rounded":   "Rounded — adaptable and empathetic",
            "mixed":     "Mixed shapes — versatile personality",
        }
        _spacing_map = {
            "wide":     "Spread wide — independent and open-minded",
            "moderate": "Moderate spacing — balanced",
            "close":    "Held close — cautious and self-contained",
        }
        _flex_map = {
            "flexible": "Flexible thumb — adaptable and generous",
            "firm":     "Firm thumb — strong-willed and reliable",
            "stiff":    "Stiff thumb — very determined",
        }
        _set_map = {
            "high":   "High-set — energetic and enterprising",
            "medium": "Medium-set — balanced",
            "low":    "Low-set — calm and independent",
        }
        rows = []
        tip = fingers.get("tip_shape_dominant", "")
        if tip and tip != "not_assessable":
            rows.append(f"- **Finger tips:** {_tip_map.get(tip, tip)}")
        spacing = fingers.get("spacing", "")
        if spacing and spacing != "not_assessable":
            rows.append(f"- **Finger spacing:** {_spacing_map.get(spacing, spacing)}")
        knotted = fingers.get("knotted_joints", "")
        if knotted == "yes":
            rows.append("- **Knotted joints:** Philosophical and analytical thinker")
        elif knotted == "no":
            rows.append("- **Smooth joints:** Acts on instinct and feeling")
        t_set = thumb.get("set", "")
        if t_set and t_set != "not_assessable":
            rows.append(f"- **Thumb set:** {_set_map.get(t_set, t_set)}")
        t_flex = thumb.get("flexibility_estimate", "")
        if t_flex and t_flex != "not_assessable":
            rows.append(f"- **Thumb:** {_flex_map.get(t_flex, t_flex)}")
        if rows:
            st.markdown("**Fingers & thumb:**")
            st.markdown("\n".join(rows))


# ══════════════════════════════════════════════════════════════════════════════
# MARKDOWN EXPORT
# ══════════════════════════════════════════════════════════════════════════════

def _build_markdown_export(phase_b, phase_a):
    out = ["# My Palm Reading", "", "*Generated by Astro Suite · Samudrika Shastra*",
           "", "---", "", phase_b.strip(), ""]

    if isinstance(phase_a, dict):
        agreement = phase_a.get("kundli_palm_agreement", "")
        note      = phase_a.get("kundli_palm_agreement_note", "")
        if agreement and agreement != "cannot_assess":
            out += ["---", "", f"**Chart & Palm Agreement:** {agreement.title()}", "", note or "", ""]

        out += ["---", "", "## What the AI observed", ""]

        lines = phase_a.get("lines", {}) or {}
        if lines:
            out.append("### Lines")
            for key, display in _LINE_NAMES.items():
                ld   = lines.get(key) or {}
                vis  = ld.get("visibility", "—")
                path = ld.get("path") or ""
                row  = f"- **{display}:** {_VIS_ICON.get(vis, vis)}"
                if path and vis in ("clear", "faint", "fragmented"):
                    row += f" — {path}"
                out.append(row)
            out.append("")

        mounts = phase_a.get("mounts", {}) or {}
        if mounts:
            out.append("### Mounts")
            for m in ["Jupiter", "Saturn", "Sun", "Mercury", "Venus", "Mars", "Luna"]:
                md    = mounts.get(m) or {}
                full  = md.get("fullness", "—")
                marks = md.get("marks") or ""
                row   = f"- **{m}:** {_FULLNESS_LABEL.get(full, full)}"
                if marks and "no notable" not in marks.lower():
                    row += f" · {marks}"
                out.append(row)
            out.append("")

        fingers = phase_a.get("fingers", {}) or {}
        thumb   = phase_a.get("thumb",   {}) or {}
        if fingers or thumb:
            out.append("### Fingers & Thumb")
            for k, label in [("tip_shape_dominant", "Tip shape"), ("knotted_joints", "Knotted joints"),
                              ("spacing", "Spacing")]:
                v = fingers.get(k, "")
                if v and v != "not_assessable":
                    out.append(f"- {label}: {v}")
            for k, label in [("set", "Thumb set"), ("flexibility_estimate", "Thumb flexibility")]:
                v = thumb.get(k, "")
                if v and v != "not_assessable":
                    out.append(f"- {label}: {v}")
            out.append("")

    return "\n".join(out)


# ══════════════════════════════════════════════════════════════════════════════
# CAPTURE TIPS
# ══════════════════════════════════════════════════════════════════════════════

def _render_capture_tips():
    with st.expander("📷 How to take a good palm photo", expanded=True):
        st.markdown(
            "- Use **natural daylight** — no flash (flash washes out the lines)\n"
            "- Hold your hand **flat and open**, fingers slightly apart\n"
            "- Camera **directly above** the palm, not at an angle\n"
            "- No **shadows** across your palm\n"
            "- Use your **dominant hand** (the one you write with)\n"
            "- Let the palm **fill most of the frame**\n"
            "- **1080p minimum** resolution"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CSS — section headers gold, better reading line spacing
# ══════════════════════════════════════════════════════════════════════════════

def _inject_styles():
    st.markdown(
        """<style>
        [data-testid="stMarkdownContainer"] h2 {
            color: #d4af37 !important;
            border-bottom: 1px solid rgba(212,175,55,0.18);
            padding-bottom: 0.3rem;
            margin-top: 1.6rem;
        }
        [data-testid="stMarkdownContainer"] p { line-height: 1.78; }
        </style>""",
        unsafe_allow_html=True,
    )