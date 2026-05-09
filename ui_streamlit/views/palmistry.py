import streamlit as st
import PIL.Image
import base64
import io
import cv2
import numpy as np

from math_engine.palm_vision import (
    analyze_palm_hybrid,
    slice_xray_mounts,
    score_to_label,
    LINE_LABELS,
    estimate_mount_elevations_relative,
    enhance_crop_for_ai,
)
from math_engine.dossier_builder import generate_astrology_dossier
from ai_engine.prompts import build_premium_palmistry_prompt
from ai_engine.palm_vision_ai import (
    fetch_reference_grid,
    scan_mount_for_symbols,
    snipe_ancient_text,
    analyze_fingers_with_ai,
)
from ui_streamlit.components import stream_ai_with_followup
from ui_streamlit.state import get_default_profile


# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════

def _to_pil(arr):
    """Convert numpy array (RGB or BGR) to PIL Image."""
    if arr is None:
        return None
    if isinstance(arr, PIL.Image.Image):
        return arr
    if arr.ndim == 3 and arr.shape[2] == 3:
        return PIL.Image.fromarray(arr.astype(np.uint8))
    return PIL.Image.fromarray(cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_BGR2RGB))


def _arr_b64(rgb_arr):
    """Convert RGB numpy array to base64 JPEG string."""
    buf = io.BytesIO()
    _to_pil(rgb_arr).save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


def _pil_b64(pil_img):
    """Convert PIL Image to base64 JPEG string."""
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def _score_bar(score):
    """Render a coloured progress bar for a 0-100 score."""
    pct = int(score)
    col = "#6adb8e" if pct >= 60 else "#d4a84b" if pct >= 35 else "#9a6ab5"
    return (
        f"<div style='background:rgba(255,255,255,0.08);border-radius:6px;"
        f"height:8px;margin:3px 0 10px'>"
        f"<div style='width:{pct}%;background:{col};height:8px;border-radius:6px'>"
        f"</div></div>"
    )


def _mount_grid(crops_dict, cols=4, caption_prefix="Mt."):
    """Display square-padded mount crops in a tidy responsive grid."""
    keys = list(crops_dict.keys())
    for row_start in range(0, len(keys), cols):
        row_keys = keys[row_start:row_start + cols]
        cs = st.columns(len(row_keys))
        for i, k in enumerate(row_keys):
            with cs[i]:
                img = crops_dict[k]
                st.image(
                    _to_pil(img) if isinstance(img, np.ndarray) else img,
                    caption=f"{caption_prefix} {k}",
                    use_container_width=True
                )


# ══════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════

def show_palmistry():
    st.markdown(
        "<h1 style='margin-bottom:0.2rem'>✋ Diagnostic Palmistry</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:rgba(200,190,220,.6);font-size:.9rem;margin-top:0'>"
        "Samudrika Shastra · Frangi Ridge Engine · Kundli Cross-Reference</p>",
        unsafe_allow_html=True
    )

    dp, _ = get_default_profile()
    if not dp:
        st.warning("⚠️ Set a ⭐ Default Profile in 'Saved Profiles' first.")
        return

    uploaded_file = st.file_uploader(
        "Upload a clear, well-lit photo of your palm "
        "(flat, fingers together, full hand visible in frame)",
        type=["jpg", "jpeg", "png"],
        help="Best: natural daylight, no shadows across lines, "
             "full hand including all fingers in frame."
    )

    if uploaded_file is None:
        _render_tips()
        return

    st.markdown("---")
    file_bytes = uploaded_file.getvalue()
    cache_key  = uploaded_file.name + str(len(file_bytes))

    if (st.session_state.get("palm_cache_key") != cache_key
            or "palm_scan_cache" not in st.session_state):
        with st.spinner("✨ Running Frangi Ridge Engine & Anatomical Mapping…"):
            palm_data, diag_xray, best_frame, lm_dict = analyze_palm_hybrid(file_bytes)
            enh_rgb = palm_data.get("enhanced_rgb")
            xray_crops, orig_crops, orig_crops_raw = slice_xray_mounts(
                best_frame, diag_xray, lm_dict, enh_rgb
            )
            st.session_state.palm_scan_cache = (
                palm_data, diag_xray, best_frame,
                lm_dict, xray_crops, orig_crops, orig_crops_raw
            )
            st.session_state.palm_cache_key = cache_key
            st.session_state.pop("premium_report_text", None)
            st.session_state.pop("palm_sync_chat", None)

    (palm_data, diag_xray, best_frame,
     lm_dict, xray_crops, orig_crops, orig_crops_raw) = st.session_state.palm_scan_cache

    # ── TOP ROW: Ridge Map + Quick Stats ─────────────────────────────────────
    col_img, col_stats = st.columns([1, 2], gap="large")

    with col_img:
        st.image(
            _to_pil(cv2.cvtColor(diag_xray, cv2.COLOR_BGR2RGB)),
            caption="Frangi Ridge Map",
            use_container_width=True
        )
        if not palm_data.get("landmarks_found"):
            st.warning("⚠️ Landmarks not detected. Try a clearer photo.")

    with col_stats:
        st.markdown("### 🔬 Geometric Profile")
        st.markdown(f"**Energy Signature:** {palm_data.get('ui_vitality', '—')}")
        st.markdown(f"*{palm_data.get('vitality_hsv', '')}*")
        st.markdown("<br>", unsafe_allow_html=True)

        fd = palm_data.get("finger_data", {})
        if fd:
            st.markdown(f"**Hand Type:** {fd.get('hand_type', '—')}")
            st.markdown(
                f"<span style='color:rgba(200,185,220,.7);font-size:.82rem'>"
                f"{fd.get('hand_type_vedic', '')}</span>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"**2D:4D Ratio:** `{fd.get('ratio_2d4d', 0):.3f}` — "
                f"<span style='color:rgba(200,185,220,.7);font-size:.82rem'>"
                f"{fd.get('ratio_reading', '')}</span>",
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

        pr = int(palm_data.get("persistence_ratio", 0) * 100)
        st.markdown(f"**Line Persistence:** `{pr}%`")
        st.markdown(_score_bar(pr), unsafe_allow_html=True)

        topo = palm_data.get("topology", {})
        if topo.get("simian_line"):
            st.markdown(
                "<div style='background:rgba(205,140,80,.18);border:1px solid "
                "rgba(205,140,80,.5);border-radius:8px;padding:8px 14px;"
                "margin-top:8px;font-size:.88rem;color:#d4944a'>"
                "⚡ <b>Simian Line Detected</b> — an exceptionally rare marking. "
                "Head and Heart lines fused. Indicates singular focus and intense destiny.</div>",
                unsafe_allow_html=True
            )

    # ── FRANGI LINE ANALYSIS ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Frangi Line Analysis")
    st.markdown(
        "<p style='color:rgba(200,190,220,.6);font-size:.83rem;margin-top:-8px'>"
        "Mathematically scored from ridge density per anatomical zone.</p>",
        unsafe_allow_html=True
    )

    zone_scores = palm_data.get("zone_scores", {})
    if zone_scores:
        z_cols = st.columns(len(zone_scores))
        for i, (key, score) in enumerate(zone_scores.items()):
            with z_cols[i]:
                label = LINE_LABELS.get(key, key.replace("_", " ").title())
                st.markdown(
                    f"<div style='text-align:center'>"
                    f"<div style='font-size:.78rem;color:rgba(200,185,220,.7)'>{label}</div>"
                    f"<div style='font-size:1.5rem;font-weight:700'>{score}</div>"
                    f"<div style='font-size:.72rem;color:rgba(200,185,220,.55)'>"
                    f"{score_to_label(score)}</div></div>",
                    unsafe_allow_html=True
                )
                st.markdown(_score_bar(score), unsafe_allow_html=True)

    if topo:
        t1, t2, t3 = st.columns(3)
        t1.metric(
            "Line Forks / Branches", topo.get("line_forks", 0),
            help="Branch points in the skeleton — forks, crossings, divergences"
        )
        t2.metric(
            "Line Breaks / Endpoints", topo.get("line_endpoints", 0),
            help="Termination points — breaks, gaps, islands"
        )
        t3.metric(
            "Complexity Score", topo.get("line_complexity", 0),
            help="Forks / endpoints x 100 — higher = more complex destiny web"
        )

    # ── MOUNT DIAGNOSTIC FEED (X-RAY) ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 👁️ AI Diagnostic Feed — Planetary Mounts")
    st.markdown(
        "<p style='color:rgba(200,190,220,.6);font-size:.83rem;margin-top:-8px'>"
        "Heatmap slices — all 7 mounts, square-padded for alignment. "
        "Symbol detection uses original palm crops.</p>",
        unsafe_allow_html=True
    )
    if xray_crops:
        _mount_grid(xray_crops, cols=4)

    # ── WHAT THE AI ACTUALLY SEES ─────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔬 What the AI is actually reading (CLAHE-enhanced original crops)"):
        st.markdown(
            "<p style='color:rgba(200,190,220,.6);font-size:.82rem'>"
            "These contrast-enhanced crops are what Gemini Vision receives. "
            "Lines are more visible here than in the heatmap. "
            "The full hand image (including fingers) is also sent separately "
            "for Samudrika Shastra finger analysis.</p>",
            unsafe_allow_html=True
        )

        # Full hand image — sent for finger analysis
        full_hand = palm_data.get("enhanced_rgb")
        if full_hand is not None:
            st.markdown("**Full Hand (sent for finger analysis):**")
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(
                    _to_pil(full_hand),
                    caption="Full CLAHE-enhanced hand",
                    use_container_width=True
                )
            st.markdown("---")

        # Mount crops
        if orig_crops:
            st.markdown("**Mount Crops (sent for symbol detection):**")
            _mount_grid(orig_crops, cols=4, caption_prefix="Original —")

    # ── MOUNT ELEVATION ───────────────────────────────────────────────────────
    elevations = (palm_data.get("depth_elevations")
                  or estimate_mount_elevations_relative(orig_crops_raw))
    method_label = ("Depth Anything V2"
                    if palm_data.get("used_depth_model")
                    else "brightness heuristic")

    if elevations:
        st.markdown("---")
        st.markdown("### 🏔️ Mount Prominence Estimates")
        st.caption(f"Method: {method_label}")
        ev_cols = st.columns(len(elevations))
        for i, (mname, ev) in enumerate(elevations.items()):
            with ev_cols[i]:
                st.markdown(
                    f"<div style='text-align:center;font-size:.76rem'>"
                    f"<div style='color:rgba(200,185,220,.7)'>{mname}</div>"
                    f"<div style='font-size:.72rem;color:#e2e0ec'>"
                    f"{ev['elevation']}</div></div>",
                    unsafe_allow_html=True
                )
                st.markdown(_score_bar(ev["score"]), unsafe_allow_html=True)

    # ── GENERATE REPORT ───────────────────────────────────────────────────────
    st.markdown("---")
    if "premium_report_text" not in st.session_state:
        st.session_state.premium_report_text = ""

    if st.button(
        "✨ Generate Full Palm Reading",
        type="primary",
        use_container_width=True
    ):
        _run_full_report(
            dp, palm_data, diag_xray,
            orig_crops_raw, elevations, orig_crops
        )


# ══════════════════════════════════════════════════════════════════════
# REPORT GENERATION PIPELINE
# ══════════════════════════════════════════════════════════════════════

def _run_full_report(dp, palm_data, diag_xray,
                     orig_crops_raw, elevations, orig_crops_padded):
    status = st.empty()

    # Step 1 — Finger analysis (full hand image to Gemini)
    status.info("🖐️ Analysing finger profile (Samudrika Shastra)…")
    finger_analysis = {}
    full_hand_rgb   = palm_data.get("enhanced_rgb")

    if full_hand_rgb is not None:
        try:
            full_hand_enh = enhance_crop_for_ai(full_hand_rgb)
            full_hand_pil = PIL.Image.fromarray(full_hand_enh)
            finger_analysis = analyze_fingers_with_ai(
                full_hand_pil,
                palm_data.get("finger_data", {})
            )
        except Exception:
            finger_analysis = {}

    # Step 2 — Symbol detection on original crops
    status.info("👁️ Running Vision Engine on original palm crops…")
    ref_grid = (fetch_reference_grid("aiguide/reference_grid_56.jpg")
                or fetch_reference_grid("reference_grid_56.jpg"))

    verified_symbols    = ["None detected"]
    mount_symbol_detail = []

    if ref_grid and orig_crops_raw:
        findings = scan_mount_for_symbols(orig_crops_raw, ref_grid)
        valid = [
            f for f in findings
            if isinstance(f, dict) and f.get("confidence_score", 0) >= 75
        ]
        if valid:
            verified_symbols    = [f.get("symbol", "?") for f in valid]
            mount_symbol_detail = valid
            st.toast(f"👁️ {len(valid)} mark(s) verified at 75%+ confidence!")
        else:
            st.toast("👁️ No symbols met the confidence threshold.")
    elif not ref_grid:
        st.warning("⚠️ Reference grid unavailable.")

    # Step 3 — Ancient text sniper
    status.info("📜 Sniping ancient Vedic texts…")
    sniper_text = snipe_ancient_text(
        "aiguide/palm_miner_output.json",
        "aiguide/palm_glossary.json",
        verified_symbols
    )

    # Step 4 — Kundli dossier
    status.info("🪐 Loading Kundli dossier…")
    dossier = generate_astrology_dossier(dp)

    # Step 5 — Build prompt
    prompt = build_premium_palmistry_prompt(
        palm_data,
        verified_symbols,
        sniper_text,
        dossier,
        mount_symbol_detail=mount_symbol_detail,
        mount_elevations=elevations,
        finger_analysis=finger_analysis
    )

    # Prepare images for PDF
    main_b64 = _arr_b64(cv2.cvtColor(diag_xray, cv2.COLOR_BGR2RGB))

    crop_b64_list = []
    for mname, crop in orig_crops_padded.items():
        if crop is None:
            continue
        try:
            pil = _to_pil(crop) if isinstance(crop, np.ndarray) else crop
            crop_b64_list.append((mname, _pil_b64(pil)))
        except Exception:
            pass

    full_hand_b64 = ""
    if full_hand_rgb is not None:
        try:
            full_hand_b64 = _arr_b64(full_hand_rgb)
        except Exception:
            pass

    status.empty()

    report_text = stream_ai_with_followup(
        prompt=prompt,
        memory_key="palm_sync_chat",
        spinner_text="✨ Weaving your Samudrika Shastra reading…",
        image_b64=main_b64,
        hide_user_prompt=True,
        show_share_buttons=False
    )

    st.session_state.premium_report_text = report_text

    if report_text:
        _render_palm_pdf(report_text, main_b64, crop_b64_list, full_hand_b64)


# ══════════════════════════════════════════════════════════════════════
# PDF GENERATOR
# ══════════════════════════════════════════════════════════════════════

def _render_palm_pdf(report_text, main_xray_b64, crop_b64_list, full_hand_b64=""):
    """
    Renders Save as PDF button. PDF includes:
    1. Frangi Ridge Map
    2. Full CLAHE-enhanced hand photo (for finger reference)
    3. 4-column mount crop grid (what the AI read)
    4. Full reading text
    Scale set to 1.5 (down from 2.0) to prevent content cut-off.
    """
    import streamlit.components.v1 as components
    import base64 as b64mod

    b64_text = b64mod.b64encode(report_text.encode("utf-8")).decode("utf-8")

    # Build mount crops HTML grid
    crops_html = ""
    if crop_b64_list:
        crops_html = (
            "<div style='margin:14px 0'>"
            "<h3 style='color:#1a1a1a;font-size:13px;margin-bottom:8px'>"
            "AI Diagnostic Feed — Mount Crops</h3>"
            "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:6px'>"
        )
        for mname, b64 in crop_b64_list:
            crops_html += (
                f"<div style='text-align:center'>"
                f"<img src='data:image/jpeg;base64,{b64}' "
                f"style='width:100%;border-radius:4px;border:1px solid #ddd'>"
                f"<div style='font-size:8px;color:#666;margin-top:2px'>"
                f"Mt. {mname}</div></div>"
            )
        crops_html += "</div></div>"

    full_hand_html = ""
    if full_hand_b64:
        full_hand_html = (
            f"<div style='text-align:center;margin:10px 0'>"
            f"<img src='data:image/jpeg;base64,{full_hand_b64}' "
            f"style='max-height:200px;border-radius:8px;border:1px solid #D4AF37'>"
            f"<div style='font-size:9px;color:#666;margin-top:3px'>"
            f"Full Hand — CLAHE Enhanced</div></div>"
        )

    html = f"""
<div style="font-family:'Source Sans Pro',sans-serif;padding:5px">
  <button id="pdfBtn" style="width:100%;padding:.5rem 1rem;
    background:linear-gradient(135deg,rgba(144,98,222,.3),rgba(205,140,80,.3));
    color:#fff;border:1px solid rgba(205,140,80,.5);border-radius:.5rem;
    cursor:pointer;font-size:1rem;font-weight:bold">
    📄 Save as PDF
  </button>
</div>
<div id="msg" style="text-align:center;font-size:.8rem;margin-top:5px;
  color:#999;opacity:0;transition:opacity .3s"></div>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<script>
var rawText   = decodeURIComponent(escape(window.atob('{b64_text}')));
var mainImg   = '{main_xray_b64}';
var cropsHtml = `{crops_html}`;
var fullHand  = `{full_hand_html}`;
var msg       = document.getElementById('msg');

function showMsg(t) {{
  msg.innerText = t;
  msg.style.opacity = 1;
  setTimeout(function() {{ msg.style.opacity = 0; }}, 3000);
}}

document.getElementById('pdfBtn').addEventListener('click', function() {{
  showMsg('Generating PDF…');
  var parsed  = marked.parse(rawText);
  var wrapper = document.createElement('div');
  wrapper.style.cssText = 'padding:28px;background:#fff;color:#1a1a1a;' +
    'font-family:Helvetica,Arial,sans-serif;line-height:1.6;font-size:12px';

  var mainImgHtml = mainImg
    ? '<div style="text-align:center;margin-bottom:12px">' +
      '<img src="data:image/jpeg;base64,' + mainImg + '" ' +
      'style="max-height:260px;border-radius:8px;border:2px solid #D4AF37">' +
      '<div style="font-size:9px;color:#666;margin-top:3px">Frangi Ridge Map</div></div>'
    : '';

  wrapper.innerHTML =
    '<style>p,li,h1,h2,h3{{page-break-inside:avoid;break-inside:avoid;margin-bottom:10px}}</style>' +
    '<div style="text-align:center;margin-bottom:20px;border-bottom:2px solid ' +
    'rgba(212,175,55,.5);padding-bottom:14px">' +
    '<h1 style="color:#1a1a1a;font-size:22px;letter-spacing:2px;margin:0">' +
    'PALMISTRY READING</h1>' +
    '<p style="color:#555;font-size:10px;text-transform:uppercase;margin-top:3px">' +
    'Samudrika Shastra · Astro Suite</p></div>' +
    mainImgHtml +
    fullHand +
    cropsHtml +
    '<div style="font-size:12px;color:#1a1a1a">' + parsed + '</div>' +
    '<div style="margin-top:28px;text-align:center;font-size:9px;color:#999;' +
    'border-top:1px solid #eee;padding-top:10px">' +
    'Generated by Astro Suite Engine</div>';

  html2pdf().set({{
    margin: [12, 12, 12, 12],
    filename: 'Palm_Reading_Report.pdf',
    image: {{ type: 'jpeg', quality: 0.95 }},
    html2canvas: {{ scale: 1.5, useCORS: true, backgroundColor: '#ffffff', logging: false }},
    jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'portrait' }},
    pagebreak: {{ mode: ['css', 'legacy'] }}
  }}).from(wrapper).save().then(function() {{ showMsg('PDF Downloaded!'); }});
}});
</script>
"""
    st.markdown("<br>", unsafe_allow_html=True)
    components.html(html, height=85)


# ══════════════════════════════════════════════════════════════════════
# UPLOAD TIPS
# ══════════════════════════════════════════════════════════════════════

def _render_tips():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
<div style='background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
border-radius:14px;padding:1.4rem 1.6rem'>
<h4 style='margin-top:0'>📸 For the most accurate reading:</h4>
<ul style='color:rgba(200,185,220,.75);font-size:.88rem;line-height:1.8'>
  <li>Use <strong>natural daylight</strong> — avoid flash or harsh overhead light</li>
  <li>Hold palm <strong>flat and fully open</strong>, all fingers visible in frame</li>
  <li>Camera <strong>directly above</strong>, not at an angle</li>
  <li>No shadows across the palm lines</li>
  <li>Use your <strong>dominant hand</strong> for primary reading</li>
  <li>Minimum resolution: <strong>1080p</strong></li>
</ul></div>
        """,
        unsafe_allow_html=True
    )