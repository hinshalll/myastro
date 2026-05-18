"""
ui_streamlit/views/astro_pdf.py
================================
General-purpose premium PDF builder for all Astro Suite features.

Replaces math_engine/pdf_builder.py entirely.

Usage:
    from ui_streamlit.views.astro_pdf import build_astro_pdf

    pdf_bytes = build_astro_pdf(
        feature_title     = "Daily Horoscope",
        feature_emoji     = "★",
        sections          = [
            {"heading": "Today's Energy", "body": "Mars transits your 10th house..."},
            {"heading": "Love",           "body": "Venus favours deep conversations..."},
        ],
        user_name         = "Hinshal Sharma",
        cover_image_bytes = None,          # optional bytes of any image
        metadata          = {"Sign": "Pisces", "Date": "May 11, 2026"},
    )

Design language matches palm_pdf.py:
  - Midnight blue cover  (#0e1117)
  - Gold (#d4af37) headers and rules
  - Cream (#faf7f0) body pages, dark ink text
  - 18mm margins, 1.78 line height

Also exports:
  _safe(s)          — latin-1 text sanitiser
  AstroPDF          — the base FPDF subclass
  GOLD / CREAM / …  — shared palette constants

palm_pdf.py imports these so the design stays in sync automatically.

Mobile-app note: when you move to FastAPI, call build_astro_pdf() from any
route and return Response(content=pdf_bytes, media_type="application/pdf").
The function has zero Streamlit dependencies — it's plain Python.
"""

import io
import re
import datetime
from fpdf import FPDF


# ── Shared palette ─────────────────────────────────────────────────────────────
GOLD      = (212, 175, 55)
GOLD_DIM  = (180, 145, 35)
NIGHT     = (14,  17,  23)
DEEP      = (23,  19,  44)
CREAM     = (250, 247, 240)
INK       = (38,  34,  28)
INK_SOFT  = (105, 100, 92)

PAGE_W    = 210   # A4 mm
PAGE_H    = 297
MARGIN    = 18


# ── Sanitiser (strips anything fpdf core fonts can't render) ──────────────────

def _safe(s: str) -> str:
    if not s:
        return ""
    return (
        str(s)
        .replace("\u2014", "-").replace("\u2013", "-")
        .replace("\u2018", "'").replace("\u2019", "'")
        .replace("\u201c", '"').replace("\u201d", '"')
        .replace("\u2026", "...").replace("\u00b7", "•")
        .replace("\u2605", "*").replace("\u2606", "*")
        .replace("\u2728", "*").replace("\u2733", "*")
        # Strip remaining non-latin-1 safely
        .encode("latin-1", "ignore").decode("latin-1")
    )


# ── Markdown stripping (for body text from AI responses) ─────────────────────

def _strip_md(text: str) -> str:
    """
    Convert markdown to plain text suitable for fpdf multi_cell.
    Preserves paragraph breaks. Converts ## headers to UPPERCASE lines.
    Strips **, *, `code`, and bullet list markers.
    """
    if not text:
        return ""
    lines = []
    for line in text.split("\n"):
        # H2/H3 → uppercase plain text acting as a heading
        if line.startswith("## "):
            lines.append("\n" + line[3:].strip().upper())
            continue
        if line.startswith("### "):
            lines.append("\n" + line[4:].strip())
            continue
        # Strip bold/italic markers
        line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        line = re.sub(r'\*(.+?)\*',     r'\1', line)
        line = re.sub(r'`(.+?)`',       r'\1', line)
        # Bullet/numbered list markers → indent
        line = re.sub(r'^\s*[-•]\s+',  '  - ', line)
        line = re.sub(r'^\s*\d+\.\s+', '  ',   line)
        lines.append(line)
    return "\n".join(lines).strip()


# ══════════════════════════════════════════════════════════════════════════════
# BASE PDF CLASS — zero Streamlit dependencies
# ══════════════════════════════════════════════════════════════════════════════

class AstroPDF(FPDF):
    def __init__(self, feature_title: str = "Astro Suite"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(MARGIN, MARGIN, MARGIN)
        self._feature_title   = feature_title
        self._content_started = False   # suppresses header/footer on cover

    def header(self):
        if not self._content_started:
            return
        # Cream background for all body pages
        self.set_fill_color(*CREAM)
        self.rect(0, 0, PAGE_W, PAGE_H, "F")
        # Gold rule
        self.set_draw_color(*GOLD_DIM)
        self.set_line_width(0.25)
        self.line(MARGIN, 14, PAGE_W - MARGIN, 14)
        # Header text
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*INK_SOFT)
        self.set_y(8)
        self.cell(0, 5, _safe(f"{self._feature_title}  ·  Astro Suite"), align="C")
        self.set_y(MARGIN + 4)

    def footer(self):
        if not self._content_started:
            return
        page_num = self.page_no() - 1
        if page_num < 1:
            return
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*INK_SOFT)
        self.cell(0, 5, f"Page {page_num}", align="C")


# ══════════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _draw_cover(
    pdf: AstroPDF,
    feature_title: str,
    feature_emoji: str,
    user_name: str,
    date_str: str,
    cover_image_bytes: bytes | None,
    metadata: dict | None,
):
    pdf.add_page()

    # Backgrounds
    pdf.set_fill_color(*NIGHT)
    pdf.rect(0, 0, PAGE_W, PAGE_H, "F")
    pdf.set_fill_color(*DEEP)
    pdf.rect(0, 0, PAGE_W, 130, "F")

    # Top ornament
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    pdf.line(PAGE_W/2 - 28, 34, PAGE_W/2 + 28, 34)

    # Eyebrow
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(0, 40)
    pdf.cell(PAGE_W, 5, "ASTRO SUITE", align="C")

    # Emoji (rendered as plain text; most emojis become boxes in core fonts
    # but the gold colour and size still looks premium)
    emoji_safe = _safe(feature_emoji) or "-"
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(245, 240, 230)
    pdf.set_xy(0, 50)
    pdf.cell(PAGE_W, 13, emoji_safe, align="C")

    # Title
    pdf.set_font("Helvetica", "B", 30)
    pdf.set_text_color(245, 240, 230)
    pdf.set_xy(0, 64)
    pdf.cell(PAGE_W, 13, _safe(feature_title), align="C")

    # Optional cover image
    img_bottom = 88
    if cover_image_bytes:
        try:
            img_size = 80
            img_x = (PAGE_W - img_size) / 2
            img_y = 90
            pdf.set_draw_color(*GOLD)
            pdf.set_line_width(0.5)
            pdf.rect(img_x - 1.5, img_y - 1.5, img_size + 3, img_size + 3)
            pdf.image(io.BytesIO(cover_image_bytes), x=img_x, y=img_y, w=img_size, h=img_size)
            img_bottom = img_y + img_size + 10
        except Exception:
            img_bottom = 88

    # Metadata block (Sign, Date, etc.)
    meta_y = img_bottom + 6
    if metadata:
        for k, v in metadata.items():
            if meta_y > 225:
                break
            pdf.set_text_color(195, 185, 170)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_xy(0, meta_y)
            pdf.cell(PAGE_W, 5, _safe(f"{k}:  {v}"), align="C")
            meta_y += 9

    # Bottom ornament
    rule_y = min(meta_y + 10, 238)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    pdf.line(PAGE_W/2 - 28, rule_y, PAGE_W/2 + 28, rule_y)

    # Prepared for
    name_y = rule_y + 9
    pdf.set_text_color(195, 185, 170)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(0, name_y)
    pdf.cell(PAGE_W, 5, "PREPARED FOR", align="C")

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(0, name_y + 9)
    pdf.cell(PAGE_W, 10, _safe(user_name or "—"), align="C")

    pdf.set_text_color(195, 185, 170)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_xy(0, name_y + 22)
    pdf.cell(PAGE_W, 5, _safe(date_str), align="C")


# ══════════════════════════════════════════════════════════════════════════════
# CONTENT PAGES
# ══════════════════════════════════════════════════════════════════════════════

def _draw_sections(pdf: AstroPDF, sections: list):
    """
    sections: list of dicts with keys:
        "heading" (str, optional) — rendered as a gold H2 with a small rule
        "body"    (str)           — rendered as flowing body paragraphs
        "pre"     (bool, optional) — if True, preserve whitespace (for tables etc.)
    """
    pdf.add_page()
    body_w = PAGE_W - 2 * MARGIN

    for sec in sections:
        heading = (sec.get("heading") or "").strip()
        body    = (sec.get("body")    or "").strip()
        if not heading and not body:
            continue

        if heading:
            if pdf.get_y() > PAGE_H - 48:
                pdf.add_page()
            pdf.ln(5)
            # Short gold rule before heading
            pdf.set_draw_color(*GOLD_DIM)
            pdf.set_line_width(0.25)
            pdf.line(MARGIN, pdf.get_y(), MARGIN + 10, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(*GOLD_DIM)
            pdf.multi_cell(body_w, 7, _safe(heading))
            pdf.ln(2)

        if body:
            clean = _strip_md(body)
            # Split into paragraphs for better control
            for para in re.split(r'\n{2,}', clean):
                para = para.strip()
                if not para:
                    continue
                if pdf.get_y() > PAGE_H - 30:
                    pdf.add_page()
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(*INK)
                pdf.multi_cell(body_w, 5.8, _safe(para))
                pdf.ln(3)


# ══════════════════════════════════════════════════════════════════════════════
# CLOSING PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _draw_closing(pdf: AstroPDF):
    if pdf.get_y() > PAGE_H - 55:
        pdf.add_page()
    pdf.ln(14)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    pdf.line(PAGE_W/2 - 24, pdf.get_y(), PAGE_W/2 + 24, pdf.get_y())
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*INK_SOFT)
    pdf.multi_cell(
        0, 5,
        _safe(
            "This reading is offered as a tool for reflection and self-inquiry. "
            "It is not a substitute for professional advice. The most accurate "
            "guide to your life remains your own honest observation of yourself."
        ),
        align="C",
    )
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*GOLD_DIM)
    pdf.cell(0, 5, "Astro Suite", align="C")


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API — zero Streamlit dependencies
# ══════════════════════════════════════════════════════════════════════════════

def build_astro_pdf(
    feature_title:     str,
    feature_emoji:     str        = "",
    sections:          list       = None,
    user_name:         str        = "",
    cover_image_bytes: bytes      = None,
    metadata:          dict       = None,
) -> bytes:
    """
    Build a premium A4 PDF and return as bytes.

    Args:
        feature_title:      e.g. "Daily Horoscope", "Numerology Report", "Tarot Reading"
        feature_emoji:      e.g. "★", "♦" (keep to ASCII/latin-1 for best rendering)
        sections:           list of {"heading": str, "body": str}
        user_name:          shown on the cover
        cover_image_bytes:  optional image bytes shown on the cover
        metadata:           dict shown on cover as key: value lines
                            e.g. {"Sun Sign": "Pisces", "Date": "May 11, 2026"}

    Returns:
        bytes — the raw PDF.

    FastAPI usage:
        from fastapi.responses import Response
        @app.post("/pdf")
        async def pdf_endpoint(req: PdfRequest):
            return Response(
                content=build_astro_pdf(**req.dict()),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=reading.pdf"},
            )
    """
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    pdf = AstroPDF(feature_title)

    # Cover (no header/footer)
    _draw_cover(pdf, feature_title, feature_emoji, user_name, date_str,
                cover_image_bytes, metadata)

    # Body (header/footer enabled from here)
    pdf._content_started = True
    _draw_sections(pdf, sections or [])
    _draw_closing(pdf)

    out = pdf.output(dest="S")
    return out.encode("latin-1", "ignore") if isinstance(out, str) else bytes(out)


# ── Backwards-compat shim so existing imports don't break ─────────────────────
# math_engine/pdf_builder.py previously exported generate_premium_pdf().
# Any view still importing that will get this wrapper instead.

def generate_premium_pdf(report_text: str, diagnostic_pil, user_name: str) -> bytes:
    """
    Backwards-compatible wrapper for the old math_engine/pdf_builder.generate_premium_pdf().
    diagnostic_pil is ignored (no longer embedded — was unreliable diagnostics).
    """
    sections = []
    current_heading = ""
    current_body    = []
    for line in (report_text or "").split("\n"):
        if line.startswith("## "):
            if current_body:
                sections.append({"heading": current_heading, "body": "\n".join(current_body).strip()})
                current_body = []
            current_heading = line[3:].strip()
        else:
            current_body.append(line)
    if current_body:
        sections.append({"heading": current_heading, "body": "\n".join(current_body).strip()})

    return build_astro_pdf(
        feature_title = "Astro Suite Report",
        feature_emoji = "*",
        sections      = sections,
        user_name     = user_name,
    )
