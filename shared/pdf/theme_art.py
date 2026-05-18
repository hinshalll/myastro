"""
shared.pdf/theme_art.py — Premium theme art system.

Each theme has multiple decorative elements appearing INSIDE content
(no page frames — those caused border-overflow bugs). Theme distinctiveness
comes from per-theme deity-symbolic elements stamped throughout:

    cover_art(theme)       — large centerpiece for cover page
    section_icon(theme)    — small icon before every H2 section header
    ornament_divider(theme)— themed divider between subsections
    page_watermark(theme)  — large faded deity art behind page content
    table_accent(theme)    — subtle deity motif for table headers
    bullet_marker(theme)   — themed bullet character/SVG for lists

Raster path: if PNG exists at static/themes/<theme>/cover.png or
watermark.png, it overrides the SVG. Generated via generate_theme_assets.py.
"""

from __future__ import annotations

import base64
from pathlib import Path


_STATIC_DIR = Path(__file__).parent / "static" / "themes"


def _svg_data_url(svg_str: str) -> str:
    b64 = base64.b64encode(svg_str.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def _png_data_url(path: Path) -> str | None:
    if not path.exists():
        return None
    return f"data:image/png;base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def _theme_slug(theme: dict) -> str:
    name = theme.get("name", "").lower().split()[0] or theme.get("ornament", "lotus")
    return {"classic": "classic_vedic"}.get(name, name)


def _raster_cover(theme: dict) -> str | None:
    return _png_data_url(_STATIC_DIR / _theme_slug(theme) / "cover.png")


def _raster_watermark(theme: dict) -> str | None:
    return _png_data_url(_STATIC_DIR / _theme_slug(theme) / "watermark.png")


# ═══════════════════════════════════════════════════════════════════════════
# Per-theme deity-symbolic SVG primitives.
# ═══════════════════════════════════════════════════════════════════════════
# Each theme defines a "deity symbol" SVG that gets used at multiple scales:
#   - tiny (14×14) for section header icons
#   - medium (240×60) for ornament dividers
#   - large (400×400) for cover art and watermark
# All single-path / single-stroke for clean line-art look.

def _classic_vedic_glyph(color: str, accent: str) -> str:
    """Stylised Om (ॐ) glyph — single path."""
    return f'''
    <g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <!-- Om main curl -->
      <path d="M 35 60 C 22 60 22 80 42 84 C 60 86 70 76 70 64 C 70 52 55 46 42 54"/>
      <path d="M 70 64 C 82 64 90 58 88 48 C 86 40 76 38 70 46"/>
      <path d="M 80 38 C 90 28 102 28 105 38"/>
      <circle cx="95" cy="22" r="2.5" fill="{accent}"/>
      <path d="M 84 28 Q 95 20 106 28" stroke="{accent}"/>
    </g>'''


def _ganesha_glyph(color: str, accent: str) -> str:
    """Stylised Ganesha head silhouette with trunk curl."""
    return f'''
    <g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <!-- Head -->
      <circle cx="55" cy="48" r="24" fill="{accent}" fill-opacity="0.15"/>
      <!-- Crown tuft -->
      <path d="M 45 26 Q 55 18 65 26"/>
      <circle cx="55" cy="20" r="2" fill="{accent}"/>
      <!-- Ears -->
      <path d="M 32 44 Q 22 52 30 64 Q 36 58 38 54" fill="{accent}" fill-opacity="0.2"/>
      <path d="M 78 44 Q 88 52 80 64 Q 74 58 72 54" fill="{accent}" fill-opacity="0.2"/>
      <!-- Trunk curl -->
      <path d="M 55 58 C 55 70 48 76 50 84 C 52 92 66 92 70 84"/>
      <!-- Tusks -->
      <path d="M 47 64 L 43 72"/>
      <path d="M 63 64 L 67 72"/>
      <!-- Third eye -->
      <circle cx="55" cy="34" r="1.5" fill="{accent}"/>
    </g>'''


def _krishna_glyph(color: str, accent: str) -> str:
    """Peacock feather glyph — distinctive Krishna symbol."""
    return f'''
    <g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <!-- Feather stem -->
      <path d="M 55 86 L 55 38"/>
      <!-- Eye of the feather (oval) -->
      <ellipse cx="55" cy="30" rx="14" ry="20" fill="{accent}" fill-opacity="0.18"/>
      <ellipse cx="55" cy="30" rx="9" ry="13" fill="{accent}" fill-opacity="0.35"/>
      <ellipse cx="55" cy="30" rx="4" ry="6" fill="{color}"/>
      <!-- Fronds (3 each side) -->
      <path d="M 55 60 Q 46 58 42 54"/>
      <path d="M 55 68 Q 44 66 38 62"/>
      <path d="M 55 76 Q 42 74 34 70"/>
      <path d="M 55 60 Q 64 58 68 54"/>
      <path d="M 55 68 Q 66 66 72 62"/>
      <path d="M 55 76 Q 68 74 76 70"/>
      <!-- Tuft on top -->
      <path d="M 52 12 L 55 6 L 58 12"/>
    </g>'''


def _shiva_glyph(color: str, accent: str) -> str:
    """Trishul (trident) with crescent moon."""
    return f'''
    <g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <!-- Crescent moon at top -->
      <path d="M 42 16 A 13 13 0 1 0 68 16 A 9 9 0 1 1 42 16 Z" fill="{accent}" fill-opacity="0.35"/>
      <!-- Trishul shaft -->
      <path d="M 55 32 L 55 92"/>
      <!-- Center prong (leaf shape) -->
      <path d="M 55 30 Q 47 42 55 56 Q 63 42 55 30 Z" fill="{accent}" fill-opacity="0.25"/>
      <!-- Side prongs -->
      <path d="M 38 42 L 38 30 L 41 56 Z" fill="{accent}" fill-opacity="0.25"/>
      <path d="M 72 42 L 72 30 L 69 56 Z" fill="{accent}" fill-opacity="0.25"/>
      <!-- Cross bar -->
      <path d="M 36 62 L 74 62"/>
      <!-- Third eye dot -->
      <circle cx="55" cy="78" r="2" fill="{accent}"/>
    </g>'''


def _durga_glyph(color: str, accent: str) -> str:
    """Trishul rising from lotus."""
    return f'''
    <g fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <!-- Trishul rising -->
      <path d="M 55 14 L 55 56"/>
      <path d="M 55 14 Q 49 22 55 30 Q 61 22 55 14 Z" fill="{accent}" fill-opacity="0.3"/>
      <path d="M 44 22 L 44 14 L 47 30 Z" fill="{accent}" fill-opacity="0.3"/>
      <path d="M 66 22 L 66 14 L 63 30 Z" fill="{accent}" fill-opacity="0.3"/>
      <path d="M 42 34 L 68 34"/>
      <!-- 8-petal lotus base -->
      <g transform="translate(55 76)">
        <ellipse cx="0" cy="-12" rx="5" ry="14" fill="{accent}" fill-opacity="0.20"/>
        <ellipse cx="0" cy="-12" rx="5" ry="14" transform="rotate(45)" fill="{accent}" fill-opacity="0.20"/>
        <ellipse cx="0" cy="-12" rx="5" ry="14" transform="rotate(90)" fill="{accent}" fill-opacity="0.20"/>
        <ellipse cx="0" cy="-12" rx="5" ry="14" transform="rotate(135)" fill="{accent}" fill-opacity="0.20"/>
        <ellipse cx="0" cy="-12" rx="5" ry="14" transform="rotate(180)" fill="{accent}" fill-opacity="0.20"/>
        <ellipse cx="0" cy="-12" rx="5" ry="14" transform="rotate(225)" fill="{accent}" fill-opacity="0.20"/>
        <ellipse cx="0" cy="-12" rx="5" ry="14" transform="rotate(270)" fill="{accent}" fill-opacity="0.20"/>
        <ellipse cx="0" cy="-12" rx="5" ry="14" transform="rotate(315)" fill="{accent}" fill-opacity="0.20"/>
        <circle r="3" fill="{color}"/>
      </g>
    </g>'''


def _lakshmi_glyph(color: str, accent: str) -> str:
    """Open layered lotus with falling coins."""
    return f'''
    <g fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <!-- Outer 8-petal lotus -->
      <g transform="translate(55 50)">
        <ellipse cx="0" cy="-25" rx="7" ry="22" fill="{accent}" fill-opacity="0.18"/>
        <ellipse cx="0" cy="-25" rx="7" ry="22" transform="rotate(45)" fill="{accent}" fill-opacity="0.18"/>
        <ellipse cx="0" cy="-25" rx="7" ry="22" transform="rotate(90)" fill="{accent}" fill-opacity="0.18"/>
        <ellipse cx="0" cy="-25" rx="7" ry="22" transform="rotate(135)" fill="{accent}" fill-opacity="0.18"/>
        <ellipse cx="0" cy="-25" rx="7" ry="22" transform="rotate(180)" fill="{accent}" fill-opacity="0.18"/>
        <ellipse cx="0" cy="-25" rx="7" ry="22" transform="rotate(225)" fill="{accent}" fill-opacity="0.18"/>
        <ellipse cx="0" cy="-25" rx="7" ry="22" transform="rotate(270)" fill="{accent}" fill-opacity="0.18"/>
        <ellipse cx="0" cy="-25" rx="7" ry="22" transform="rotate(315)" fill="{accent}" fill-opacity="0.18"/>
      </g>
      <!-- Inner 4 petals brighter -->
      <g transform="translate(55 50)" stroke="{accent}">
        <ellipse cx="0" cy="-14" rx="4" ry="12" fill="{accent}" fill-opacity="0.40"/>
        <ellipse cx="0" cy="-14" rx="4" ry="12" transform="rotate(90)" fill="{accent}" fill-opacity="0.40"/>
        <ellipse cx="0" cy="-14" rx="4" ry="12" transform="rotate(180)" fill="{accent}" fill-opacity="0.40"/>
        <ellipse cx="0" cy="-14" rx="4" ry="12" transform="rotate(270)" fill="{accent}" fill-opacity="0.40"/>
      </g>
      <!-- Center bindu -->
      <circle cx="55" cy="50" r="3" fill="{color}"/>
    </g>'''


_GLYPH_FN = {
    "lotus":           _classic_vedic_glyph,
    "ganesha":         _ganesha_glyph,
    "peacock_feather": _krishna_glyph,
    "trishul":         _shiva_glyph,
    "trishul_lion":    _durga_glyph,
    "lotus_gold":      _lakshmi_glyph,
}


def _get_glyph(theme: dict, viewBox: str = "0 0 110 100") -> str:
    """Return the bare theme glyph wrapped in an SVG with given viewBox."""
    fn = _GLYPH_FN.get(theme.get("ornament", "lotus"), _classic_vedic_glyph)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" fill="none">'
            f'{fn(theme["primary"], theme["accent"])}'
            f'</svg>')


# ═══════════════════════════════════════════════════════════════════════════
# Public — section_icon, ornament_divider, page_watermark
# ═══════════════════════════════════════════════════════════════════════════

def section_icon_data_url(theme: dict) -> str:
    """Small theme glyph (used before H2 section titles)."""
    return _svg_data_url(_get_glyph(theme, viewBox="10 5 90 90"))


def ornament_divider_svg(theme: dict) -> str:
    """A horizontal divider with the theme glyph centered + decorative wings.
    Rendered at 240×40pt typically."""
    primary = theme["primary"]
    accent  = theme["accent"]
    muted   = theme["muted"]
    glyph = _GLYPH_FN.get(theme.get("ornament", "lotus"), _classic_vedic_glyph)(primary, accent)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 40" fill="none">
      <!-- Left line with end ornament -->
      <line x1="6"   y1="20" x2="98"  y2="20" stroke="{muted}" stroke-width="0.6"/>
      <circle cx="98" cy="20" r="1.5" fill="{accent}"/>
      <!-- Right line with end ornament -->
      <line x1="222" y1="20" x2="314" y2="20" stroke="{muted}" stroke-width="0.6"/>
      <circle cx="222" cy="20" r="1.5" fill="{accent}"/>
      <!-- Center theme glyph at 55-pixel radius scale -->
      <g transform="translate(105 -10) scale(0.6)">{glyph}</g>
    </svg>'''


def page_watermark_svg(theme: dict) -> str:
    """Large faded glyph (used as page background watermark)."""
    primary = theme["primary"]
    accent  = theme["accent"]
    glyph = _GLYPH_FN.get(theme.get("ornament", "lotus"), _classic_vedic_glyph)(primary, accent)
    # Wrap in low-opacity group
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 110 100" fill="none">'
            f'<g opacity="0.06">{glyph}</g></svg>')


def page_watermark_data_url(theme: dict) -> str | None:
    raster = _raster_watermark(theme)
    if raster:
        return raster
    return _svg_data_url(page_watermark_svg(theme))


# ═══════════════════════════════════════════════════════════════════════════
# COVER ART — elaborate, theme-specific (kept from previous version)
# ═══════════════════════════════════════════════════════════════════════════

def _svg_open(view: str = "0 0 400 400", w: int = 360, h: int = 360) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" '
            f'width="{w}" height="{h}" fill="none" stroke-linecap="round" '
            f'stroke-linejoin="round">')


def _classic_vedic_cover(primary: str, accent: str, muted: str) -> str:
    return _svg_open() + f'''
    <defs>
      <radialGradient id="cvBg" cx="50%" cy="50%" r="55%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.15"/>
        <stop offset="100%" stop-color="{primary}" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="200" cy="200" r="190" fill="url(#cvBg)"/>
    <g stroke="{accent}" stroke-width="1" opacity="0.55">
      {''.join(f'<line x1="200" y1="38" x2="200" y2="56" transform="rotate({i * 15} 200 200)"/>' for i in range(24))}
    </g>
    <circle cx="200" cy="200" r="155" stroke="{primary}" stroke-width="1.4"/>
    <g stroke="{primary}" stroke-width="1.4" fill="{accent}" fill-opacity="0.10">
      {''.join(f'<ellipse cx="200" cy="120" rx="14" ry="40" transform="rotate({i * 22.5} 200 200)"/>' for i in range(16))}
    </g>
    <circle cx="200" cy="200" r="65" stroke="{primary}" stroke-width="1.6"/>
    <g stroke="{primary}" stroke-width="3.2" fill="none">
      <path d="M165 210 C 148 210 148 235 175 240 C 200 244 218 232 218 215 C 218 198 195 190 178 200"/>
      <path d="M218 215 C 235 215 245 205 242 188 C 240 178 225 175 218 188"/>
      <path d="M232 175 C 245 158 262 158 268 175"/>
      <circle cx="250" cy="148" r="4" fill="{accent}" stroke="none"/>
      <path d="M238 155 Q 250 142 262 155" stroke="{accent}" stroke-width="2"/>
    </g>
    <circle cx="200" cy="200" r="3" fill="{primary}"/>
    </svg>'''


def _ganesha_cover(primary: str, accent: str, muted: str) -> str:
    return _svg_open() + f'''
    <defs>
      <radialGradient id="gnBg" cx="50%" cy="55%" r="60%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.20"/>
        <stop offset="100%" stop-color="{primary}" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="200" cy="220" r="190" fill="url(#gnBg)"/>
    <circle cx="200" cy="200" r="135" stroke="{primary}" stroke-width="1.2" opacity="0.7"/>
    <g stroke="{primary}" stroke-width="1.3" fill="{accent}" fill-opacity="0.10">
      {''.join(f'<ellipse cx="200" cy="118" rx="11" ry="32" transform="rotate({i * 30} 200 210)"/>' for i in range(12))}
    </g>
    <!-- Ornate crown -->
    <path d="M150 160 Q 200 110 250 160 L 245 175 Q 200 130 155 175 Z"
          stroke="{primary}" stroke-width="1.6" fill="{accent}" fill-opacity="0.40"/>
    <circle cx="200" cy="125" r="6" fill="{accent}"/>
    <!-- Head -->
    <circle cx="200" cy="195" r="58" stroke="{primary}" stroke-width="2.2" fill="{accent}" fill-opacity="0.15"/>
    <!-- Ears -->
    <path d="M148 180 Q 116 195 130 230 Q 138 215 148 205 Z"
          stroke="{primary}" stroke-width="2" fill="{accent}" fill-opacity="0.25"/>
    <path d="M252 180 Q 284 195 270 230 Q 262 215 252 205 Z"
          stroke="{primary}" stroke-width="2" fill="{accent}" fill-opacity="0.25"/>
    <!-- Closed eyes (meditative) -->
    <path d="M182 195 Q 188 191 194 195" stroke="{primary}" stroke-width="1.8"/>
    <path d="M206 195 Q 212 191 218 195" stroke="{primary}" stroke-width="1.8"/>
    <!-- Tilak -->
    <path d="M198 175 L 200 165 L 202 175 Z" fill="{accent}"/>
    <!-- Trunk -->
    <path d="M200 220 C 200 240 188 250 188 264 C 188 280 212 286 226 274 C 238 263 230 252 218 252 C 210 252 208 258 210 263"
          stroke="{primary}" stroke-width="2.6" fill="{accent}" fill-opacity="0.15"/>
    <!-- Tusks -->
    <path d="M178 232 L 168 250" stroke="{primary}" stroke-width="2"/>
    <path d="M222 232 L 232 250" stroke="{primary}" stroke-width="2"/>
    <!-- Belly hint -->
    <path d="M170 268 Q 200 305 240 270" stroke="{primary}" stroke-width="2"
          fill="{accent}" fill-opacity="0.10"/>
    <!-- Lotus pedestal -->
    <g stroke="{primary}" stroke-width="1.4" fill="{accent}" fill-opacity="0.15">
      <path d="M140 325 Q 200 305 260 325 Q 250 340 200 332 Q 150 340 140 325 Z"/>
      <path d="M170 345 Q 200 333 230 345 Q 222 355 200 350 Q 178 355 170 345 Z"/>
    </g>
    </svg>'''


def _krishna_cover(primary: str, accent: str, muted: str) -> str:
    return _svg_open() + f'''
    <defs>
      <radialGradient id="krBg" cx="50%" cy="50%" r="60%">
        <stop offset="0%" stop-color="{primary}" stop-opacity="0.18"/>
        <stop offset="100%" stop-color="{primary}" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="200" cy="200" r="190" fill="url(#krBg)"/>
    <g fill="{accent}" opacity="0.6">
      <circle cx="80" cy="100" r="1.5"/><circle cx="120" cy="60" r="1"/>
      <circle cx="320" cy="80" r="1.4"/><circle cx="340" cy="140" r="1"/>
      <circle cx="60" cy="220" r="1.2"/><circle cx="350" cy="250" r="1"/>
      <circle cx="80" cy="320" r="1.4"/><circle cx="310" cy="340" r="1"/>
    </g>
    <circle cx="200" cy="200" r="170" stroke="{primary}" stroke-width="1" opacity="0.45"/>
    <g stroke="{primary}" stroke-width="1.5" opacity="0.9">
      <path d="M200 360 Q 200 280 200 180"/>
      {''.join(f'<path d="M200 {300 - i*8} Q {180 - i*1.5} {290 - i*8} {172 - i*2.2} {280 - i*8}"/>' for i in range(14))}
      {''.join(f'<path d="M200 {300 - i*8} Q {220 + i*1.5} {290 - i*8} {228 + i*2.2} {280 - i*8}"/>' for i in range(14))}
    </g>
    <ellipse cx="200" cy="170" rx="28" ry="42" stroke="{primary}" stroke-width="2.4" fill="{primary}" fill-opacity="0.3"/>
    <ellipse cx="200" cy="170" rx="22" ry="34" stroke="{accent}" stroke-width="1.8" fill="{accent}" fill-opacity="0.4"/>
    <ellipse cx="200" cy="170" rx="14" ry="22" fill="{primary}"/>
    <ellipse cx="200" cy="170" rx="8" ry="14" fill="{accent}"/>
    <ellipse cx="200" cy="170" rx="3" ry="6" fill="{primary}"/>
    <path d="M188 110 Q 200 90 212 110" stroke="{accent}" stroke-width="2.4" fill="{accent}" fill-opacity="0.4"/>
    <path d="M194 96 L 200 80 L 206 96" stroke="{primary}" stroke-width="2"/>
    <circle cx="200" cy="78" r="3" fill="{accent}"/>
    <g stroke="{accent}" stroke-width="3" opacity="0.85">
      <line x1="80" y1="320" x2="320" y2="220"/>
    </g>
    <g fill="{primary}" opacity="0.85">
      <circle cx="130" cy="298" r="2"/><circle cx="155" cy="288" r="2"/>
      <circle cx="180" cy="278" r="2"/><circle cx="205" cy="268" r="2"/>
      <circle cx="230" cy="258" r="2"/><circle cx="255" cy="248" r="2"/>
    </g>
    </svg>'''


def _shiva_cover(primary: str, accent: str, muted: str) -> str:
    return _svg_open() + f'''
    <defs>
      <radialGradient id="shBg" cx="50%" cy="55%" r="60%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.20"/>
        <stop offset="100%" stop-color="{primary}" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="200" cy="200" r="190" fill="url(#shBg)"/>
    <path d="M30 320 L 110 200 L 160 270 L 200 180 L 250 270 L 290 220 L 370 320 Z"
          fill="{primary}" fill-opacity="0.10" stroke="{primary}" stroke-width="0.8" opacity="0.6"/>
    <circle cx="200" cy="200" r="170" stroke="{primary}" stroke-width="1" opacity="0.5"/>
    <path d="M168 70 A 32 32 0 1 0 232 70 A 24 24 0 1 1 168 70 Z"
          stroke="{accent}" stroke-width="2" fill="{accent}" fill-opacity="0.45"/>
    <ellipse cx="200" cy="105" rx="8" ry="3" fill="{accent}"/>
    <line x1="200" y1="115" x2="200" y2="320" stroke="{primary}" stroke-width="3"/>
    <path d="M200 75 Q 188 100 200 130 Q 212 100 200 75 Z" stroke="{primary}" stroke-width="2.4" fill="{primary}" fill-opacity="0.3"/>
    <path d="M158 95 L 158 70 L 165 130 Z" stroke="{primary}" stroke-width="2.4" fill="{primary}" fill-opacity="0.3"/>
    <path d="M242 95 L 242 70 L 235 130 Z" stroke="{primary}" stroke-width="2.4" fill="{primary}" fill-opacity="0.3"/>
    <line x1="148" y1="140" x2="252" y2="140" stroke="{primary}" stroke-width="2.4"/>
    <g stroke="{accent}" stroke-width="2" fill="{accent}" fill-opacity="0.30">
      <path d="M178 200 L 222 215 L 178 215 L 222 200 Z"/>
    </g>
    <g stroke="{primary}" stroke-width="1.3" opacity="0.7">
      <path d="M80 168 Q 200 158 320 168"/>
    </g>
    </svg>'''


def _durga_cover(primary: str, accent: str, muted: str) -> str:
    return _svg_open() + f'''
    <defs>
      <radialGradient id="duBg" cx="50%" cy="50%" r="60%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.22"/>
        <stop offset="100%" stop-color="{primary}" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="200" cy="200" r="190" fill="url(#duBg)"/>
    <g stroke="{primary}" stroke-width="1.4" fill="{accent}" fill-opacity="0.18">
      {''.join(f'<path d="M200 65 Q 210 85 200 110 Q 190 85 200 65 Z" transform="rotate({i * 22.5} 200 200)"/>' for i in range(16))}
    </g>
    <g stroke="{accent}" stroke-width="1.8" fill="{accent}" fill-opacity="0.25">
      {''.join(f'<ellipse cx="200" cy="130" rx="14" ry="38" transform="rotate({i * 45 + 22.5} 200 200)"/>' for i in range(8))}
    </g>
    <g stroke="{primary}" stroke-width="1.8" fill="{primary}" fill-opacity="0.35">
      {''.join(
          f'<g transform="rotate({i * 45} 200 200)">'
          f'<line x1="200" y1="170" x2="200" y2="120" stroke-width="2"/>'
          f'<path d="M190 130 L 190 115 L 194 138 Z"/>'
          f'<path d="M210 130 L 210 115 L 206 138 Z"/>'
          f'<path d="M200 115 Q 196 125 200 138 Q 204 125 200 115 Z"/>'
          f'</g>' for i in range(8))}
    </g>
    <circle cx="200" cy="200" r="55" stroke="{primary}" stroke-width="2" fill="{accent}" fill-opacity="0.10"/>
    <g stroke="{primary}" stroke-width="1.5">
      <polygon points="200,170 175,213 225,213" fill="{accent}" fill-opacity="0.20"/>
      <polygon points="200,230 175,187 225,187" fill="{accent}" fill-opacity="0.20"/>
    </g>
    <circle cx="200" cy="200" r="3" fill="{primary}"/>
    </svg>'''


def _lakshmi_cover(primary: str, accent: str, muted: str) -> str:
    return _svg_open() + f'''
    <defs>
      <radialGradient id="lkBg" cx="50%" cy="50%" r="55%">
        <stop offset="0%" stop-color="{primary}" stop-opacity="0.20"/>
        <stop offset="100%" stop-color="{primary}" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="200" cy="200" r="190" fill="url(#lkBg)"/>
    <g stroke="{primary}" stroke-width="0.8" opacity="0.55">
      {''.join(f'<line x1="200" y1="50" x2="200" y2="68" transform="rotate({i * 12} 200 200)"/>' for i in range(30))}
    </g>
    <g stroke="{primary}" stroke-width="1.4" fill="{primary}" fill-opacity="0.10">
      {''.join(f'<ellipse cx="200" cy="100" rx="14" ry="50" transform="rotate({i * 22.5} 200 210)"/>' for i in range(16))}
    </g>
    <g stroke="{primary}" stroke-width="1.6" fill="{accent}" fill-opacity="0.20">
      {''.join(f'<ellipse cx="200" cy="125" rx="11" ry="38" transform="rotate({i * 30 + 15} 200 210)"/>' for i in range(12))}
    </g>
    <g stroke="{accent}" stroke-width="1.8" fill="{accent}" fill-opacity="0.35">
      {''.join(f'<ellipse cx="200" cy="150" rx="9" ry="28" transform="rotate({i * 45 + 22.5} 200 210)"/>' for i in range(8))}
    </g>
    <circle cx="200" cy="210" r="14" stroke="{primary}" stroke-width="1.8" fill="{accent}" fill-opacity="0.6"/>
    <circle cx="200" cy="210" r="6" fill="{primary}"/>
    <g stroke="{accent}" stroke-width="0.8" fill="{accent}" fill-opacity="0.6">
      <circle cx="56" cy="270" r="7"/><circle cx="72" cy="292" r="6"/>
      <circle cx="50" cy="300" r="5"/><circle cx="68" cy="320" r="6"/>
      <circle cx="344" cy="270" r="7"/><circle cx="328" cy="292" r="6"/>
      <circle cx="350" cy="300" r="5"/><circle cx="332" cy="320" r="6"/>
    </g>
    </svg>'''


_COVER_FN = {
    "lotus":           _classic_vedic_cover,
    "ganesha":         _ganesha_cover,
    "peacock_feather": _krishna_cover,
    "trishul":         _shiva_cover,
    "trishul_lion":    _durga_cover,
    "lotus_gold":      _lakshmi_cover,
}


def cover_art(theme: dict) -> str:
    fn = _COVER_FN.get(theme.get("ornament", "lotus"), _classic_vedic_cover)
    return fn(theme["primary"], theme["accent"], theme["muted"])


def cover_image_data_url(theme: dict) -> str | None:
    return _raster_cover(theme)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE BORDER — drawn strictly in the @page margin strip (0-10mm from edge)
# Content lives at @page margin (12mm × 11mm), so decoration NEVER overlaps.
# All elements live in:
#     top strip:    y ∈ [0, 10mm]
#     bottom strip: y ∈ [287, 297mm]
#     left strip:   x ∈ [0, 9mm]
#     right strip:  x ∈ [201, 210mm]
# Corners get a small theme deity glyph for distinctiveness.
# ═══════════════════════════════════════════════════════════════════════════

def _page_border_inner(theme: dict, *, cover: bool = False) -> str:
    """Returns the inner content of the page-border SVG (no outer <svg> tag)."""
    primary   = theme["primary"]
    accent    = theme["accent"]
    muted     = theme["muted"]
    secondary = theme.get("secondary", accent)
    paper     = theme.get("paper_alt", theme["paper"])

    # Tiny corner deity glyph — 7mm × 7mm centered at (4.5mm, 4.5mm) from corners.
    # Source glyph viewBox is "0 0 110 100" — we scale it to 7mm and position.
    glyph_fn = _GLYPH_FN.get(theme.get("ornament", "lotus"), _classic_vedic_glyph)
    glyph_body = glyph_fn(primary, accent)
    # Scale factor: target 7mm wide, source viewBox is ~110 wide.
    # 7mm / 110 = 0.0636
    scale = 0.0636
    # Source glyph is offset (10-100 x range); we center it.
    # Translate so the glyph centers at corner_x, corner_y
    def corner_glyph(cx: float, cy: float) -> str:
        # Source bounding ~5,5 to ~108,95 (rough center 56.5, 50)
        tx = cx - 56.5 * scale
        ty = cy - 50.0 * scale
        return (f'<g transform="translate({tx} {ty}) scale({scale})" '
                f'opacity="0.85">{glyph_body}</g>')

    # Cover gets a richer frame; interior gets a simpler one
    stroke_outer = 0.6 if not cover else 0.8
    stroke_inner = 0.35 if not cover else 0.45

    parts = []

    # === Outer rectangle at 4mm from edge ===
    parts.append(
        f'<rect x="4" y="4" width="202" height="289" rx="1.5" ry="1.5"'
        f' fill="none" stroke="{primary}" stroke-width="{stroke_outer}"/>'
    )

    # === Inner rectangle at 7mm from edge (extra detail line) ===
    parts.append(
        f'<rect x="7" y="7" width="196" height="283" rx="1" ry="1"'
        f' fill="none" stroke="{muted}" stroke-width="{stroke_inner}" opacity="0.7"/>'
    )

    # === Corner deity glyphs (4 corners) ===
    # Position: small deity icon nested in the corner with a tinted circle backing
    for cx, cy in [(4.5, 4.5), (205.5, 4.5), (4.5, 292.5), (205.5, 292.5)]:
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="{accent}" fill-opacity="0.10"'
            f' stroke="{accent}" stroke-width="0.4"/>'
        )
        parts.append(corner_glyph(cx, cy))

    # === Mid-edge medallions (4 edges) ===
    # Centered: top (105, 4.5), bottom (105, 292.5), left (4.5, 148.5), right (205.5, 148.5)
    for mx, my in [(105, 4.5), (105, 292.5), (4.5, 148.5), (205.5, 148.5)]:
        parts.append(
            f'<circle cx="{mx}" cy="{my}" r="2" fill="{accent}" stroke="{primary}" stroke-width="0.4"/>'
        )
        parts.append(
            f'<circle cx="{mx}" cy="{my}" r="0.8" fill="{primary}"/>'
        )

    # === Quarter-edge accent dots (between corner and mid) ===
    # Top edge dots at x=55, x=155 (and y=4.5); similar on bottom; sides at y=75, y=222
    for dx, dy in [
        (55, 4.5), (155, 4.5),
        (55, 292.5), (155, 292.5),
        (4.5, 75), (4.5, 222),
        (205.5, 75), (205.5, 222),
    ]:
        parts.append(
            f'<circle cx="{dx}" cy="{dy}" r="0.8" fill="{primary}" opacity="0.75"/>'
        )

    # === Decorative thin connecting lines along edges (between dots) ===
    # Add light gradient-feel: alternating short dashes that look ornate
    # Top edge
    parts.append(
        f'<path d="M 15 4.5 L 50 4.5 M 60 4.5 L 100 4.5 M 110 4.5 L 150 4.5 '
        f'M 160 4.5 L 195 4.5" stroke="{primary}" stroke-width="0.3" opacity="0.55"/>'
    )
    # Bottom edge
    parts.append(
        f'<path d="M 15 292.5 L 50 292.5 M 60 292.5 L 100 292.5 M 110 292.5 L 150 292.5 '
        f'M 160 292.5 L 195 292.5" stroke="{primary}" stroke-width="0.3" opacity="0.55"/>'
    )
    # Left edge
    parts.append(
        f'<path d="M 4.5 15 L 4.5 70 M 4.5 80 L 4.5 144 M 4.5 154 L 4.5 217 '
        f'M 4.5 227 L 4.5 282" stroke="{primary}" stroke-width="0.3" opacity="0.55"/>'
    )
    # Right edge
    parts.append(
        f'<path d="M 205.5 15 L 205.5 70 M 205.5 80 L 205.5 144 M 205.5 154 L 205.5 217 '
        f'M 205.5 227 L 205.5 282" stroke="{primary}" stroke-width="0.3" opacity="0.55"/>'
    )

    return "".join(parts)


def page_border_svg(theme: dict, *, cover: bool = False,
                    include_watermark: bool = False) -> str:
    """Full page border SVG. Optionally embeds the watermark PNG centered
    inside the same SVG so a SINGLE @page background-image gives us BOTH
    the border decoration AND the deity watermark on every page.
    """
    body = _page_border_inner(theme, cover=cover)
    watermark_xml = ""
    if include_watermark:
        # Look for raster watermark first; fall back to SVG glyph
        slug = _theme_slug(theme)
        raster = _STATIC_DIR / slug / "watermark.png"
        if raster.exists():
            b64 = base64.b64encode(raster.read_bytes()).decode("ascii")
            mark_href = f"data:image/png;base64,{b64}"
        else:
            wm_inner = page_watermark_svg(theme)
            mark_href = _svg_data_url(wm_inner)
        # Centered watermark, ~85mm × 85mm, low opacity. Lives in the
        # content-area centre (not the border strip) so it shows behind text.
        # A4 = 210×297mm; center = (105, 148.5); square 85 ⇒ (62.5, 106)
        watermark_xml = (
            f'<image x="62.5" y="106" width="85" height="85" '
            f'href="{mark_href}" opacity="0.10" preserveAspectRatio="xMidYMid meet"/>'
        )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297" '
            f'preserveAspectRatio="none" width="210mm" height="297mm">'
            f'{watermark_xml}{body}'
            f'</svg>')


def page_border_data_url(theme: dict) -> str:
    # Interior pages: border + watermark in one SVG (reliable single bg-image)
    return _svg_data_url(page_border_svg(theme, cover=False, include_watermark=True))


def cover_page_border_data_url(theme: dict) -> str:
    # Cover: border only — no watermark on cover (cover has its own art)
    return _svg_data_url(page_border_svg(theme, cover=True, include_watermark=False))


def corner_ornament(theme: dict) -> str:
    return _get_glyph(theme, viewBox="0 0 110 100")


def section_divider(theme: dict) -> str:
    return ornament_divider_svg(theme)
