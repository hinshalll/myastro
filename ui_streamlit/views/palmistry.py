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
    # Prefer the isolated hand (RGBA, transparent background) for the premium float effect
    isolated = analysis.get("hand_isolated")
    use_alpha = isolated is not None

    if use_alpha:
        b64 = _arr_to_b64_png(isolated)
        mime = "png"
    else:
        # Fallback: rectangular image, will be circular-clipped
        overlay = analysis.get("landmark_overlay")
        if overlay is None:
            overlay = analysis.get("enhanced_palm")
        if overlay is None:
            return
        b64 = _arr_to_b64_jpeg(overlay, quality=85)
        mime = "jpeg"

    # ── Two display modes ────────────────────────────────────────────────────
    # ALPHA MODE: hand floats freely with drop shadow (no circular clip)
    # FALLBACK : original circular-clipped rectangular image
    palm_html_alpha = (
        '<div class="palm-float">'
        f'<img src="data:image/{mime};base64,{b64}" alt="palm" />'
        '</div>'
    )
    palm_html_fallback = (
        '<div class="palm-circle">'
        f'<img src="data:image/{mime};base64,{b64}" alt="palm" />'
        '</div>'
    )
    palm_html = palm_html_alpha if use_alpha else palm_html_fallback

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0e1117;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 430px;
    overflow: hidden;
  }}

  .cosmos {{
    position: relative;
    width: 400px;
    height: 400px;
    display: flex;
    justify-content: center;
    align-items: center;
  }}

  /* ── Floating hand (alpha mode, premium) ── */
  .palm-float {{
    position: relative;
    z-index: 10;
    width: 230px;
    height: 230px;
    display: flex;
    justify-content: center;
    align-items: center;
  }}
  .palm-float img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    filter:
      drop-shadow(0 0 8px rgba(212,175,55,0.35))
      drop-shadow(0 0 16px rgba(140,90,220,0.25));
  }}

  /* ── Fallback circular clip (when isolation fails) ── */
  .palm-circle {{
    position: relative;
    z-index: 10;
    width: 210px;
    height: 210px;
    border-radius: 50%;
    overflow: hidden;
    border: 2px solid rgba(212,175,55,0.55);
    box-shadow:
      0 0 0 4px rgba(212,175,55,0.08),
      0 0 30px rgba(212,175,55,0.25),
      0 0 60px rgba(140,90,200,0.15);
  }}
  .palm-circle img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center center;
  }}

  /* ── Pulse glow behind palm ── */
  .glow {{
    position: absolute;
    z-index: 9;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    background: radial-gradient(circle,
      rgba(140,80,220,0.22) 0%,
      rgba(212,175,55,0.08) 50%,
      transparent 75%);
    animation: pulse 4s ease-in-out infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ transform: scale(0.97); opacity: 0.7; }}
    50%       {{ transform: scale(1.05); opacity: 1.0; }}
  }}

  /* ── Rotating rings ── */
  .ring {{
    position: absolute;
    border-radius: 50%;
    top: 50%;
    left: 50%;
  }}
  .ring-1 {{
    width: 290px; height: 290px;
    margin-top: -145px; margin-left: -145px;
    border: 1.5px dashed rgba(212,175,55,0.45);
    animation: spin-cw 18s linear infinite;
  }}
  .ring-2 {{
    width: 338px; height: 338px;
    margin-top: -169px; margin-left: -169px;
    border: 1px solid rgba(170,130,230,0.22);
    animation: spin-ccw 32s linear infinite;
  }}
  .ring-3 {{
    width: 390px; height: 390px;
    margin-top: -195px; margin-left: -195px;
    border: 1px solid rgba(212,175,55,0.10);
    animation: spin-cw 60s linear infinite;
  }}
  @keyframes spin-cw  {{ from {{ transform: rotate(0deg);   }} to {{ transform: rotate(360deg);  }} }}
  @keyframes spin-ccw {{ from {{ transform: rotate(0deg);   }} to {{ transform: rotate(-360deg); }} }}

  /* ── Dot markers ── */
  .rdot {{
    position: absolute;
    border-radius: 50%;
    background: rgba(212,175,55,0.75);
  }}
  .rdot-sm {{ width: 5px; height: 5px; }}
  .rdot-md {{ width: 7px; height: 7px; }}
  .rdot-lg {{
    width: 9px; height: 9px;
    box-shadow: 0 0 6px rgba(212,175,55,0.9);
    background: rgba(212,175,55,0.9);
  }}

  /* ── Twinkling stars ── */
  .star {{ position: absolute; border-radius: 50%; background: white; }}
  @keyframes twinkle {{
    0%, 100% {{ opacity: 0.05; transform: scale(0.8); }}
    50%       {{ opacity: 0.75; transform: scale(1.2); }}
  }}
</style>
</head>
<body>
<div class="cosmos">
  <div class="glow"></div>
  <div class="ring ring-3" id="ring3"></div>
  <div class="ring ring-2" id="ring2"></div>
  <div class="ring ring-1" id="ring1"></div>
  {palm_html}
</div>

<script>
(function() {{
  // Ring 1: 12 dots on r=145, center at (145,145) of 290x290 div
  var r1 = document.getElementById('ring1');
  for (var i = 0; i < 12; i++) {{
    var a = (i * 30 - 90) * Math.PI / 180;
    var isCardinal = (i % 3 === 0);
    var sz = isCardinal ? 7 : 5;
    var dot = document.createElement('div');
    dot.className = 'rdot ' + (isCardinal ? 'rdot-md' : 'rdot-sm');
    dot.style.left = (145 + 145 * Math.cos(a) - sz/2) + 'px';
    dot.style.top  = (145 + 145 * Math.sin(a) - sz/2) + 'px';
    r1.appendChild(dot);
  }}

  // Ring 2: 8 dots on r=169, center at (169,169) of 338x338 div
  var r2 = document.getElementById('ring2');
  [0, 45, 90, 135, 180, 225, 270, 315].forEach(function(deg) {{
    var a2 = (deg - 90) * Math.PI / 180;
    var isMain = (deg % 90 === 0);
    var sz2 = isMain ? 9 : 5;
    var dot2 = document.createElement('div');
    dot2.className = 'rdot ' + (isMain ? 'rdot-lg' : 'rdot-sm');
    dot2.style.left = (169 + 169 * Math.cos(a2) - sz2/2) + 'px';
    dot2.style.top  = (169 + 169 * Math.sin(a2) - sz2/2) + 'px';
    dot2.style.background = isMain
      ? 'rgba(200,160,255,0.85)'
      : 'rgba(180,140,230,0.55)';
    r2.appendChild(dot2);
  }});

  // Twinkling stars scattered in the space
  var cosmos = document.querySelector('.cosmos');
  [
    {{x:52, y:88, s:2.5, d:1.2}},  {{x:340, y:75, s:2, d:2.1}},
    {{x:68, y:300, s:3, d:1.7}},   {{x:330, y:310, s:2, d:0.9}},
    {{x:145, y:40, s:2, d:2.5}},   {{x:265, y:48, s:1.5, d:1.4}},
    {{x:38, y:195, s:2, d:3.0}},   {{x:358, y:200, s:2.5, d:1.8}},
    {{x:175, y:370, s:2, d:2.2}},  {{x:228, y:362, s:1.5, d:0.8}}
  ].forEach(function(s) {{
    var star = document.createElement('div');
    star.className = 'star';
    star.style.width  = s.s + 'px';
    star.style.height = s.s + 'px';
    star.style.left   = s.x + 'px';
    star.style.top    = s.y + 'px';
    star.style.animation = 'twinkle ' + (s.d + 1.5) + 's ease-in-out ' + (s.d * 0.4) + 's infinite';
    cosmos.appendChild(star);
  }});
}})();
</script>
</body>
</html>
"""
    components.html(html, height=440, scrolling=False)


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
        st.download_button(
            "⬇ Save Reading",
            data=_build_markdown_export(phase_b, phase_a).encode("utf-8"),
            file_name="palm_reading.md",
            mime="text/markdown",
            use_container_width=True,
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