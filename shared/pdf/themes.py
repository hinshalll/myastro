"""shared.pdf.themes — palette + chart-SVG defaults.

Seven premium themes for the kundli PDF (classic_vedic, ganesha, krishna,
shiva, durga, lakshmi, saraswati, royal_gold). To add a new theme: drop a
new key into THEMES with the same keys as the existing entries.

DEFAULT_THEME is the SVG-chart fallback (used when no theme is passed to
the chart renderer).
"""

# ══════════════════════════════════════════════════════════════════════════
# THEMES
# ══════════════════════════════════════════════════════════════════════════

THEMES: dict[str, dict] = {
    # ── Classic Vedic — warm parchment, saffron-cardinal, traditional ─────
    "classic_vedic": {
        "name":              "Classic Vedic",
        "primary":           "#A0522D",
        "accent":            "#D62828",
        "secondary":         "#E9A21B",
        "ink":               "#2D1B0E",
        "paper":             "#FAF3E3",
        "paper_alt":         "#F5EAD2",
        "muted":             "#A38968",
        "soft_bg":           "rgba(160, 82, 45, 0.06)",
        "card_border":       "rgba(160, 82, 45, 0.18)",
        "heading_font":      "'Cormorant Garamond', 'Cinzel', serif",
        "body_font":         "'Inter', 'Source Sans 3', system-ui, sans-serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Janma Kundli",
        "ornament":          "lotus",
        "page_numeral_color":"#A0522D",
    },
    # ── Ganesha — warm terracotta + coral + buttery yellow ────────────────
    "ganesha": {
        "name":              "Ganesha",
        "primary":           "#C97B3A",
        "accent":            "#E07B5F",
        "secondary":         "#F2C14E",
        "ink":               "#3A2418",
        "paper":             "#FFF8EC",
        "paper_alt":         "#FEEDD3",
        "muted":             "#A98763",
        "soft_bg":           "rgba(242, 193, 78, 0.10)",
        "card_border":       "rgba(201, 123, 58, 0.20)",
        "heading_font":      "'Cormorant Garamond', 'Cinzel', serif",
        "body_font":         "'Inter', 'Source Sans 3', system-ui, sans-serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Janma Kundli",
        "ornament":          "ganesha",
        "page_numeral_color":"#C97B3A",
    },
    # ── Krishna — deep midnight blue + antique gold + cream ───────────────
    "krishna": {
        "name":              "Krishna",
        "primary":           "#1E3A5F",
        "accent":            "#D4A856",
        "secondary":         "#7CA8C5",
        "ink":               "#0F1F33",
        "paper":             "#FBF7EC",
        "paper_alt":         "#F1EBD8",
        "muted":             "#6B7B8F",
        "soft_bg":           "rgba(30, 58, 95, 0.06)",
        "card_border":       "rgba(30, 58, 95, 0.18)",
        "heading_font":      "'Cormorant Garamond', 'Cinzel', serif",
        "body_font":         "'Inter', 'Source Sans 3', system-ui, sans-serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Janma Kundli",
        "ornament":          "peacock_feather",
        "page_numeral_color":"#1E3A5F",
    },
    # ── Shiva — soft indigo-silver, ascetic, calm ─────────────────────────
    "shiva": {
        "name":              "Shiva",
        "primary":           "#3D3361",
        "accent":            "#8E8BA7",
        "secondary":         "#BFC9D9",
        "ink":               "#1F1B2E",
        "paper":             "#F6F5FA",
        "paper_alt":         "#ECEAF3",
        "muted":             "#8580A0",
        "soft_bg":           "rgba(61, 51, 97, 0.06)",
        "card_border":       "rgba(61, 51, 97, 0.16)",
        "heading_font":      "'Cormorant Garamond', 'Cinzel', serif",
        "body_font":         "'Inter', 'Source Sans 3', system-ui, sans-serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Janma Kundli",
        "ornament":          "trishul",
        "page_numeral_color":"#3D3361",
    },
    # ── Durga — rich crimson + saffron, regal warmth ──────────────────────
    "durga": {
        "name":              "Durga",
        "primary":           "#9B2233",
        "accent":            "#E8923D",
        "secondary":         "#D4A856",
        "ink":               "#3B0F18",
        "paper":             "#FCF6EE",
        "paper_alt":         "#F8E9D6",
        "muted":             "#A87858",
        "soft_bg":           "rgba(155, 34, 51, 0.07)",
        "card_border":       "rgba(155, 34, 51, 0.20)",
        "heading_font":      "'Cormorant Garamond', 'Cinzel', serif",
        "body_font":         "'Inter', 'Source Sans 3', system-ui, sans-serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Janma Kundli",
        "ornament":          "trishul_lion",
        "page_numeral_color":"#9B2233",
    },
    # ── Lakshmi — rose-gold + blush + champagne, abundant softness ────────
    "lakshmi": {
        "name":              "Lakshmi",
        "primary":           "#B07559",
        "accent":            "#E8A5B5",
        "secondary":         "#F2D58D",
        "ink":               "#3F2A1F",
        "paper":             "#FEF7F0",
        "paper_alt":         "#FCEBE0",
        "muted":             "#B9947C",
        "soft_bg":           "rgba(232, 165, 181, 0.10)",
        "card_border":       "rgba(176, 117, 89, 0.20)",
        "heading_font":      "'Cormorant Garamond', 'Cinzel', serif",
        "body_font":         "'Inter', 'Source Sans 3', system-ui, sans-serif",
        "devanagari_font":   "'Noto Sans Devanagari', serif",
        "cover_subtitle":    "Janma Kundli",
        "ornament":          "lotus_gold",
        "page_numeral_color":"#B07559",
    },
}

DEFAULT_THEME = {
    "frame_color":          "#7B3F00",
    "frame_width":          2,
    "bg_color":             "#FBF6E9",
    "house_text":           "#5C3317",
    "sign_text":            "#5C3317",
    "planet_text":          "#2B1810",
    "muted":                "#8A6E4E",
    "planet_font_size":     14,
    "house_font_size":      10,
    "title_color":          "#7B3F00",
    "title_font_size":      14,
    "lagna_marker_color":   "#C41E3A",
    "retro_color":          "#C41E3A",
}
