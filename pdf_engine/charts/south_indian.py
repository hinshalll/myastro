"""
pdf_engine/charts/south_indian.py
=================================

South Indian (Square) chart SVG renderer.

Layout: 4×4 grid with the center 2×2 hollow. Each outer cell is a fixed
zodiac sign — planets move; signs do not. Sign positions (clockwise from
top-left):

       Pisces  Aries  Taurus  Gemini
       Aquar.                 Cancer
       Capric.                Leo
       Sagitt. Scorp. Libra   Virgo

The Lagna is marked with a diagonal stroke inside its cell. The "title"
text typically goes inside the central hollow.
"""

from __future__ import annotations

# Cell positions in 4x4 grid (col, row) → sign index (0=Aries..11=Pisces)
# Standard SI layout:
CELL_TO_SIGN: dict[tuple[int, int], int] = {
    # top row L→R: Pisces, Aries, Taurus, Gemini
    (0, 0): 11, (1, 0): 0,  (2, 0): 1,  (3, 0): 2,
    # right column T→B (excluding top corner already): Cancer, Leo
    (3, 1): 3,  (3, 2): 4,
    # bottom row R→L (excluding right corner already): Virgo, Libra, Scorpio, Sagittarius
    (3, 3): 5,  (2, 3): 6,  (1, 3): 7,  (0, 3): 8,
    # left column B→T (excluding bottom corner already): Capricorn, Aquarius
    (0, 2): 9,  (0, 1): 10,
}

SIGN_TO_CELL = {v: k for k, v in CELL_TO_SIGN.items()}

SIGN_NAMES_FULL = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                   "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIGN_ABBR_3 = ["Ari","Tau","Gem","Can","Leo","Vir",
               "Lib","Sco","Sag","Cap","Aqu","Pis"]
PLANET_ABBR = {
    "Sun":"Su", "Moon":"Mo", "Mars":"Ma", "Mercury":"Me",
    "Jupiter":"Ju", "Venus":"Ve", "Saturn":"Sa", "Rahu":"Ra", "Ketu":"Ke",
}


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def render(*, lagna_sign_idx: int, planet_signs: dict[str, int],
           theme: dict | None = None, size: int = 400,
           title: str = "", retrograde: set[str] | None = None,
           combust: set[str] | None = None) -> str:
    """Render a South Indian square chart as an SVG string."""
    from pdf_engine.charts import DEFAULT_THEME
    t = {**DEFAULT_THEME, **(theme or {})}
    retrograde = retrograde or set()
    combust    = combust    or set()

    cell = size / 4.0
    title_offset = 40 if title else 0

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size + title_offset}" '
        f'width="{size}" height="{size + title_offset}">'
    )

    if title:
        parts.append(
            f'<text x="{size/2}" y="24" text-anchor="middle" '
            f'fill="{t["title_color"]}" font-family="serif" '
            f'font-size="{t["title_font_size"]}" font-weight="bold">'
            f'{_esc(title)}</text>'
        )

    parts.append(f'<g transform="translate(0,{title_offset})">')

    # Outer background
    parts.append(
        f'<rect x="0" y="0" width="{size}" height="{size}" '
        f'fill="{t["bg_color"]}" stroke="{t["frame_color"]}" '
        f'stroke-width="{t["frame_width"]}"/>'
    )

    # Build sign → planets mapping
    sign_planets: dict[int, list[str]] = {i: [] for i in range(12)}
    for p, sidx in planet_signs.items():
        sign_planets[sidx].append(p)

    # Render each outer cell
    for (col, row), sign_idx in CELL_TO_SIGN.items():
        x = col * cell
        y = row * cell
        # Cell border
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'fill="none" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
        )
        # Sign label (top-left of cell)
        parts.append(
            f'<text x="{x + 6}" y="{y + 16}" '
            f'fill="{t["sign_text"]}" font-family="serif" '
            f'font-size="{t["house_font_size"]}" font-style="italic">'
            f'{SIGN_ABBR_3[sign_idx]}</text>'
        )
        # Lagna marker — diagonal stroke
        if sign_idx == lagna_sign_idx:
            parts.append(
                f'<line x1="{x + cell - 12}" y1="{y + 6}" '
                f'x2="{x + cell - 6}" y2="{y + 12}" '
                f'stroke="{t["lagna_marker_color"]}" stroke-width="3"/>'
            )
            parts.append(
                f'<text x="{x + cell - 9}" y="{y + 26}" text-anchor="middle" '
                f'fill="{t["lagna_marker_color"]}" font-family="serif" '
                f'font-size="{t["house_font_size"]}" font-weight="bold">As</text>'
            )

        # Planets — stacked below sign label, centered in remaining area
        planets = sign_planets[sign_idx]
        if planets:
            spacing = t["planet_font_size"] * 1.15
            start_y = y + cell / 2 - (len(planets) - 1) * spacing / 2 + 4
            for i, p in enumerate(planets):
                label = PLANET_ABBR.get(p, p[:2])
                if p in retrograde: label += "ᴿ"
                if p in combust:    label += "©"
                color = t["retro_color"] if p in retrograde else t["planet_text"]
                parts.append(
                    f'<text x="{x + cell / 2}" y="{start_y + i * spacing:.1f}" '
                    f'text-anchor="middle" fill="{color}" font-family="serif" '
                    f'font-weight="bold" font-size="{t["planet_font_size"]}">'
                    f'{label}</text>'
                )

    # Center hollow — title or "Rasi Chakra"
    parts.append(
        f'<rect x="{cell}" y="{cell}" width="{2*cell}" height="{2*cell}" '
        f'fill="{t["bg_color"]}" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
    )

    parts.append('</g>')
    parts.append('</svg>')
    return "".join(parts)
