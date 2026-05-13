"""
ui_streamlit/views/palm_pdf.py
================================
Premium PDF builder for palm readings.

Structural difference from astro_pdf.py: palm has its own two-column
observations grid (lines + mounts) and a cover with the isolated hand photo.
Everything else (palette, base class, section rendering, closing page) is
imported from astro_pdf.py so both files stay in sync automatically.
"""

import io
import re
import datetime

# Shared palette, helpers, and base class from astro_pdf
from ui_streamlit.views.astro_pdf import (
    AstroPDF, _safe, _draw_sections,
    GOLD, GOLD_DIM, NIGHT, DEEP, CREAM, INK, INK_SOFT,
    PAGE_W, PAGE_H, MARGIN,
)


# ══════════════════════════════════════════════════════════════════════════════
# PDF CLASS
# ══════════════════════════════════════════════════════════════════════════════


# PalmReadingPDF is AstroPDF with 'Palm Reading' as the feature title
class PalmReadingPDF(AstroPDF):
    def __init__(self):
        super().__init__('Palm Reading')


# _safe_text is an alias for the shared _safe imported from astro_pdf
_safe_text = _safe

def _draw_cover(pdf: PalmReadingPDF, palm_png_bytes: bytes, user_name: str, date_str: str):
    pdf._is_cover = True
    pdf.add_page()

    # Full-bleed deep midnight background
    pdf.set_fill_color(*NIGHT)
    pdf.rect(0, 0, PAGE_W, PAGE_H, "F")

    # Soft purple gradient via overlapping translucent rects (approximation)
    pdf.set_fill_color(*DEEP)
    pdf.rect(0, 0, PAGE_W, 140, "F")

    # Top ornament: thin gold rule
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    pdf.line(PAGE_W/2 - 30, 32, PAGE_W/2 + 30, 32)

    # Eyebrow
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(0, 38)
    pdf.cell(PAGE_W, 6, "SAMUDRIKA SHASTRA", align="C")

    # Title
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(245, 240, 230)
    pdf.set_xy(0, 50)
    pdf.cell(PAGE_W, 16, "Palm Reading", align="C")

    # Subtitle
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(195, 185, 170)
    pdf.set_xy(0, 72)
    pdf.cell(PAGE_W, 5, _safe_text("A kundli-aware reading of your hand"), align="C")

    # Palm photo — centred, with soft gold border
    if palm_png_bytes:
        try:
            img_size = 95  # mm
            img_x = (PAGE_W - img_size) / 2
            img_y = 95
            pdf.set_draw_color(*GOLD)
            pdf.set_line_width(0.6)
            # Outer frame
            pdf.rect(img_x - 2, img_y - 2, img_size + 4, img_size + 4)
            pdf.image(io.BytesIO(palm_png_bytes), x=img_x, y=img_y, w=img_size, h=img_size)
        except Exception:
            pass

    # Lower ornament
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    pdf.line(PAGE_W/2 - 30, 218, PAGE_W/2 + 30, 218)

    # Name + date block at bottom
    pdf.set_text_color(245, 240, 230)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(0, 224)
    pdf.cell(PAGE_W, 5, "PREPARED FOR", align="C")

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(0, 231)
    pdf.cell(PAGE_W, 10, _safe_text(user_name or "—"), align="C")

    pdf.set_text_color(195, 185, 170)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_xy(0, 248)
    pdf.cell(PAGE_W, 5, _safe_text(date_str), align="C")

    pdf._is_cover = False


# ══════════════════════════════════════════════════════════════════════════════
# OBSERVATIONS PAGE
# ══════════════════════════════════════════════════════════════════════════════

_LINE_LABELS = {
    "heart": "Heart Line",
    "head":  "Head Line",
    "life":  "Life Line",
    "fate":  "Fate Line",
    "sun":   "Sun Line",
}

_MOUNT_ORDER = ["Jupiter", "Saturn", "Sun", "Mercury", "Venus", "Mars", "Luna"]


def _vis_label(vis):
    return {
        "clear":          "Clearly visible",
        "faint":          "Faintly visible",
        "fragmented":     "Present but broken",
        "not_visible":    "Not present",
        "not_assessable": "Could not assess",
    }.get(vis, vis or "-")


def _fullness_label(f):
    return {
        "prominent":      "Well developed",
        "moderate":       "Moderate",
        "flat":           "Underdeveloped",
        "not_assessable": "Could not assess",
    }.get(f, f or "-")


def _draw_observations(pdf: PalmReadingPDF, phase_a: dict, signals: dict, agreement: tuple):
    pdf.add_page()
    pdf.set_fill_color(*CREAM)
    pdf.rect(0, 0, PAGE_W, PAGE_H, "F")

    # Section title
    pdf.set_text_color(*GOLD)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(MARGIN, 26)
    pdf.cell(0, 10, "What I Observed")

    pdf.set_text_color(*INK_SOFT)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_xy(MARGIN, 38)
    pdf.multi_cell(0, 5, _safe_text(
        "This page lists what was clearly visible in your photo. The reading "
        "that follows interprets only these confirmed observations - lines marked "
        "'could not assess' have been honestly left out of the reading."
    ))

    # ── Signals summary (top) ─────────────────────────────────────────────────
    pdf.set_y(58)
    pdf.set_draw_color(*GOLD_DIM)
    pdf.set_line_width(0.3)
    pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())

    pdf.ln(5)
    pdf.set_text_color(*INK)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(60, 6, "Hand Type"); pdf.cell(60, 6, "Ruling Planet"); pdf.cell(0, 6, "Life Energy")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(60, 6, _safe_text(signals.get("hand_type", "-")))
    pdf.cell(60, 6, _safe_text(signals.get("planet", "-")))
    pdf.cell(0, 6, _safe_text(signals.get("vitality", "-")))
    pdf.ln(10)

    # ── Agreement badge ───────────────────────────────────────────────────────
    if agreement and agreement[0] and agreement[0] != "cannot_assess":
        level, note = agreement
        # Soft gold bar
        pdf.set_fill_color(245, 235, 210)
        pdf.set_draw_color(*GOLD)
        pdf.rect(MARGIN, pdf.get_y(), PAGE_W - 2*MARGIN, 18, "DF")
        pdf.set_text_color(*GOLD_DIM)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(MARGIN + 4, pdf.get_y() + 2)
        pdf.cell(0, 5, _safe_text(f"CHART & PALM: {level.upper()} AGREEMENT"))
        pdf.set_text_color(*INK)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(MARGIN + 4, pdf.get_y() + 7)
        pdf.multi_cell(PAGE_W - 2*MARGIN - 8, 4, _safe_text(note or ""))
        pdf.ln(4)

    # ── Two-column grid: Lines | Mounts ───────────────────────────────────────
    col_w   = (PAGE_W - 2*MARGIN - 8) / 2
    col1_x  = MARGIN
    col2_x  = MARGIN + col_w + 8
    grid_y  = pdf.get_y() + 5

    # Lines column
    pdf.set_xy(col1_x, grid_y)
    pdf.set_text_color(*GOLD_DIM)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(col_w, 7, "Major Lines")
    pdf.ln(7)
    lines = (phase_a or {}).get("lines", {}) or {}
    for key, label in _LINE_LABELS.items():
        ld = lines.get(key) or {}
        vis = ld.get("visibility", "-")
        pdf.set_x(col1_x)
        pdf.set_text_color(*INK)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(col_w, 5, _safe_text(label))
        pdf.ln(4)
        pdf.set_x(col1_x)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*INK_SOFT)
        pdf.cell(col_w, 5, _safe_text(_vis_label(vis)))
        pdf.ln(4)
        path = ld.get("path") or ""
        if path and vis in ("clear", "faint", "fragmented"):
            pdf.set_x(col1_x)
            pdf.set_font("Helvetica", "I", 8)
            pdf.multi_cell(col_w, 4, _safe_text(path))
        pdf.ln(2)

    lines_end_y = pdf.get_y()

    # Mounts column (same start y)
    pdf.set_xy(col2_x, grid_y)
    pdf.set_text_color(*GOLD_DIM)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(col_w, 7, "Planetary Mounts")
    pdf.ln(7)
    mounts = (phase_a or {}).get("mounts", {}) or {}
    for m in _MOUNT_ORDER:
        md = mounts.get(m) or {}
        full = md.get("fullness", "-")
        marks = md.get("marks", "") or ""
        pdf.set_x(col2_x)
        pdf.set_text_color(*INK)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(col_w, 5, _safe_text(m))
        pdf.ln(4)
        pdf.set_x(col2_x)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*INK_SOFT)
        pdf.cell(col_w, 5, _safe_text(_fullness_label(full)))
        pdf.ln(4)
        if marks and "no notable" not in marks.lower() and marks not in ("-", ""):
            pdf.set_x(col2_x)
            pdf.set_font("Helvetica", "I", 8)
            pdf.multi_cell(col_w, 4, _safe_text("Mark: " + marks))
        pdf.ln(2)

    mounts_end_y = pdf.get_y()

    # Continue below the taller column
    pdf.set_y(max(lines_end_y, mounts_end_y) + 4)

    # ── Fingers & thumb row ───────────────────────────────────────────────────
    fingers = (phase_a or {}).get("fingers", {}) or {}
    thumb   = (phase_a or {}).get("thumb",   {}) or {}
    if fingers or thumb:
        pdf.set_draw_color(*GOLD_DIM)
        pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
        pdf.ln(4)
        pdf.set_text_color(*GOLD_DIM)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 7, "Fingers & Thumb")
        pdf.ln(7)

        pdf.set_text_color(*INK)
        pdf.set_font("Helvetica", "", 9)
        items = []
        if fingers.get("tip_shape_dominant") and fingers["tip_shape_dominant"] != "not_assessable":
            items.append(("Finger tips", fingers["tip_shape_dominant"]))
        if fingers.get("spacing") and fingers["spacing"] != "not_assessable":
            items.append(("Finger spacing", fingers["spacing"]))
        knot = fingers.get("knotted_joints", "")
        if knot in ("yes", "no"):
            items.append(("Knotted joints", knot))
        if thumb.get("set") and thumb["set"] != "not_assessable":
            items.append(("Thumb set", thumb["set"]))
        if thumb.get("flexibility_estimate") and thumb["flexibility_estimate"] != "not_assessable":
            items.append(("Thumb flexibility", thumb["flexibility_estimate"]))

        for label, val in items:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(50, 5, _safe_text(label))
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 5, _safe_text(val))
            pdf.ln(5)


# ══════════════════════════════════════════════════════════════════════════════
# READING PAGES
# ══════════════════════════════════════════════════════════════════════════════

def _draw_reading(pdf: PalmReadingPDF, phase_b: str):
    """Typeset the reading. Markdown H2 (## Heading) becomes a styled section title."""
    pdf.add_page()
    pdf.set_fill_color(*CREAM)
    pdf.rect(0, 0, PAGE_W, PAGE_H, "F")

    # Top title
    pdf.set_text_color(*GOLD)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(MARGIN, 26)
    pdf.cell(0, 10, "Your Reading")
    pdf.ln(15)

    text = (phase_b or "").strip()
    if not text:
        pdf.set_text_color(*INK_SOFT)
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 6, "No reading available.")
        return

    # Split by lines, render each block appropriately
    paragraphs = text.split("\n\n")
    body_width = PAGE_W - 2 * MARGIN

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # H2 heading
        if para.startswith("## "):
            heading = para[3:].strip()
            # Reserve space — start fresh on a new page if not enough room
            if pdf.get_y() > PAGE_H - 40:
                pdf.add_page()
                pdf.set_fill_color(*CREAM)
                pdf.rect(0, 0, PAGE_W, PAGE_H, "F")
                pdf.set_y(26)
            pdf.ln(4)
            pdf.set_draw_color(*GOLD_DIM)
            pdf.set_line_width(0.25)
            pdf.line(MARGIN, pdf.get_y(), MARGIN + 12, pdf.get_y())
            pdf.ln(3)
            pdf.set_text_color(*GOLD_DIM)
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(body_width, 7, _safe_text(heading))
            pdf.ln(2)
            continue

        # Body paragraph — render with markdown-style **bold** and *italic*
        pdf.set_text_color(*INK)
        _render_markdown_paragraph(pdf, para, body_width)
        pdf.ln(4)


def _render_markdown_paragraph(pdf, text, width):
    """Render a paragraph with **bold** and *italic* inline markup."""
    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text)
    line_height = 5.5
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*INK)
    base_x = pdf.get_x()
    base_y = pdf.get_y()
    full_text = ""
    for tok in tokens:
        if not tok:
            continue
        full_text += _unwrap_md(tok)
    # Single multi_cell with the unwrapped text (loses inline styling but keeps clean flow)
    # For inline bold/italic we'd need write() with font switching — kept simple here for reliability.
    pdf.set_xy(base_x, base_y)
    pdf.multi_cell(width, line_height, _safe_text(full_text))


def _unwrap_md(tok):
    if tok.startswith("**") and tok.endswith("**"):
        return tok[2:-2]
    if tok.startswith("*") and tok.endswith("*"):
        return tok[1:-1]
    return tok


# ══════════════════════════════════════════════════════════════════════════════
# AGREEMENT + CLOSING PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _draw_closing(pdf: PalmReadingPDF):
    if pdf.get_y() > PAGE_H - 50:
        pdf.add_page()
        pdf.set_fill_color(*CREAM)
        pdf.rect(0, 0, PAGE_W, PAGE_H, "F")

    pdf.ln(15)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    pdf.line(PAGE_W/2 - 25, pdf.get_y(), PAGE_W/2 + 25, pdf.get_y())
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*INK_SOFT)
    pdf.multi_cell(0, 5, _safe_text(
        "This reading is an interpretation grounded in Samudrika Shastra and your "
        "personal birth chart. It is offered as a tool for reflection, not as a "
        "definitive forecast. The most accurate guide to your life remains your "
        "own honest observation of yourself."
    ), align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*GOLD_DIM)
    pdf.cell(0, 5, "Astro Suite  ·  Samudrika Shastra", align="C")


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def build_palm_pdf(
    phase_b: str,
    phase_a: dict,
    signals: dict,
    palm_png_bytes: bytes = None,
    user_name: str = "",
) -> bytes:
    """
    Build the full PDF and return as bytes.

    Args:
        phase_b:         the markdown reading
        phase_a:         the structured observations dict
        signals:         {"hand_type": str, "planet": str, "vitality": str}
        palm_png_bytes:  bytes of the isolated hand PNG (for cover image), or None
        user_name:       name to print on the cover
    """
    pdf = PalmReadingPDF()
    date_str = datetime.datetime.now().strftime("%B %d, %Y")

    # Cover
    _draw_cover(pdf, palm_png_bytes, user_name, date_str)
    pdf._content_started = True   # all subsequent pages get header/footer

    # Observations
    agreement = (
        (phase_a or {}).get("kundli_palm_agreement", ""),
        (phase_a or {}).get("kundli_palm_agreement_note", ""),
    )
    _draw_observations(pdf, phase_a or {}, signals or {}, agreement)

    # Reading
    _draw_reading(pdf, phase_b or "")

    # Closing
    _draw_closing(pdf)

    # Output
    out = pdf.output(dest="S")
    if isinstance(out, str):
        return out.encode("latin-1", "ignore")
    return bytes(out)
