"""
pdf_engine/charts/north_indian.py
=================================

North Indian (Diamond) chart SVG renderer.

Layout: a square with both diagonals + an inner diamond connecting the
midpoints of the sides. This creates exactly 12 regions:

    - 4 kite-shaped central regions inside the inner diamond
      (houses 1, 4, 7, 10 = the kendras)
    - 8 corner triangles around the outside
      (houses 2, 3, 5, 6, 8, 9, 11, 12)

House 1 is the top kite. Houses progress clockwise from there.

The Lagna SIGN goes in the top kite; the rest of the signs follow
sequentially around the wheel. Planets are placed inside the house
that contains their sign.
"""

from __future__ import annotations

# 12-house polygon coordinates within a 400×400 viewBox.
# Each entry: house_number → list of (x, y) points (closed implicit).
HOUSE_POLYGONS: dict[int, list[tuple[int, int]]] = {
    1:  [(200,  0), (300,100), (200,200), (100,100)],   # top kite
    2:  [(  0,  0), (200,  0), (100,100)],              # upper-left triangle
    3:  [(  0,  0), (100,100), (  0,200)],              # left-upper triangle
    4:  [(  0,200), (100,100), (200,200), (100,300)],   # left kite
    5:  [(  0,400), (  0,200), (100,300)],              # left-lower triangle
    6:  [(  0,400), (200,400), (100,300)],              # lower-left triangle
    7:  [(200,400), (100,300), (200,200), (300,300)],   # bottom kite
    8:  [(400,400), (200,400), (300,300)],              # lower-right triangle
    9:  [(400,200), (400,400), (300,300)],              # right-lower triangle
   10:  [(400,200), (300,100), (200,200), (300,300)],   # right kite
   11:  [(400,  0), (400,200), (300,100)],              # right-upper triangle
   12:  [(200,  0), (400,  0), (300,100)],              # upper-right triangle
}

# Text placement centroids per house (where the SIGN number goes)
SIGN_TEXT_POS: dict[int, tuple[int, int]] = {
    1:  (200, 80),    # near top of kite
    2:  (130, 30),
    3:  (30, 130),
    4:  (80, 200),
    5:  (30, 270),
    6:  (130, 370),
    7:  (200, 320),
    8:  (270, 370),
    9:  (370, 270),
   10:  (320, 200),
   11:  (370, 130),
   12:  (270, 30),
}

# Planet text base centroids (planets are stacked here)
PLANET_TEXT_POS: dict[int, tuple[int, int]] = {
    1:  (200, 125),
    2:  (120, 60),
    3:  (60, 120),
    4:  (125, 200),
    5:  (60, 280),
    6:  (120, 340),
    7:  (200, 275),
    8:  (280, 340),
    9:  (340, 280),
   10:  (275, 200),
   11:  (340, 120),
   12:  (280, 60),
}

# Sign glyph abbreviations (3-letter)
SIGN_ABBR = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]
PLANET_ABBR = {
    "Sun":"Su", "Moon":"Mo", "Mars":"Ma", "Mercury":"Me",
    "Jupiter":"Ju", "Venus":"Ve", "Saturn":"Sa", "Rahu":"Ra", "Ketu":"Ke",
}


def _polygon_d(points: list[tuple[int, int]]) -> str:
    """Convert a list of (x,y) points to an SVG <polygon> 'points' string."""
    return " ".join(f"{x},{y}" for x, y in points)


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def render(*, lagna_sign_idx: int, planet_signs: dict[str, int],
           theme: dict | None = None, size: int = 400,
           title: str = "", retrograde: set[str] | None = None,
           combust: set[str] | None = None) -> str:
    """
    Render a North Indian diamond chart as an SVG string.

    Parameters
    ----------
    lagna_sign_idx : int
        0..11 — the sign at the Ascendant.
    planet_signs : dict[str, int]
        {"Sun": 0..11, "Moon": …, …} — sign each planet occupies.
    theme : dict | None
        Overrides for the DEFAULT_THEME palette.
    size : int
        Output canvas size (square, pixels).
    title : str
        Optional title rendered above the chart.
    retrograde, combust : set[str] | None
        Planet names to mark with the retrograde/combust suffix.
    """
    from pdf_engine.charts import DEFAULT_THEME
    t = {**DEFAULT_THEME, **(theme or {})}
    retrograde = retrograde or set()
    combust    = combust    or set()

    # Build the house→planets mapping (assign each planet to its house number,
    # where house number = ((sign_idx - lagna_sign_idx) % 12) + 1)
    house_planets: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for p, sidx in planet_signs.items():
        h = ((sidx - lagna_sign_idx) % 12) + 1
        house_planets[h].append(p)

    # Build SVG
    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size+ (40 if title else 0)}" '
        f'width="{size}" height="{size + (40 if title else 0)}">'
    )

    if title:
        parts.append(
            f'<text x="{size/2}" y="24" text-anchor="middle" '
            f'fill="{t["title_color"]}" font-family="serif" '
            f'font-size="{t["title_font_size"]}" font-weight="bold">'
            f'{_esc(title)}</text>'
        )
        y_offset = 40
    else:
        y_offset = 0

    parts.append(f'<g transform="translate(0,{y_offset})">')

    # Scale 400→size
    scale = size / 400.0

    # Background frame
    parts.append(
        f'<rect x="0" y="0" width="{size}" height="{size}" '
        f'fill="{t["bg_color"]}" stroke="{t["frame_color"]}" '
        f'stroke-width="{t["frame_width"]}"/>'
    )

    # 12 house polygons (subtle stroke)
    for h, pts in HOUSE_POLYGONS.items():
        scaled = [(x * scale, y * scale) for x, y in pts]
        parts.append(
            f'<polygon points="{_polygon_d([(int(x), int(y)) for x,y in scaled])}" '
            f'fill="none" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
        )

    # Sign labels per house (1..12 → which sign sits there)
    for h in range(1, 13):
        sign_idx = (lagna_sign_idx + h - 1) % 12
        sx, sy = SIGN_TEXT_POS[h]
        sx, sy = sx * scale, sy * scale
        parts.append(
            f'<text x="{sx}" y="{sy}" text-anchor="middle" '
            f'fill="{t["sign_text"]}" font-family="serif" '
            f'font-size="{t["house_font_size"] * scale:.1f}" font-style="italic">'
            f'{SIGN_ABBR[sign_idx]}</text>'
        )

    # Lagna marker on house 1
    lx, ly = SIGN_TEXT_POS[1]
    parts.append(
        f'<text x="{lx * scale}" y="{(ly - 14) * scale:.1f}" text-anchor="middle" '
        f'fill="{t["lagna_marker_color"]}" font-family="serif" '
        f'font-size="{t["house_font_size"] * scale:.1f}" font-weight="bold">'
        f'Asc</text>'
    )

    # Planets in each house — stacked vertically
    for h, planets in house_planets.items():
        if not planets:
            continue
        bx, by = PLANET_TEXT_POS[h]
        bx, by = bx * scale, by * scale
        spacing = t["planet_font_size"] * scale * 1.1
        for i, p in enumerate(planets):
            label = PLANET_ABBR.get(p, p[:2])
            if p in retrograde:
                label += "ᴿ"
            if p in combust:
                label += "©"
            color = t["retro_color"] if p in retrograde else t["planet_text"]
            parts.append(
                f'<text x="{bx}" y="{by + i * spacing}" text-anchor="middle" '
                f'fill="{color}" font-family="serif" font-weight="bold" '
                f'font-size="{t["planet_font_size"] * scale:.1f}">{label}</text>'
            )

    parts.append('</g>')
    parts.append('</svg>')
    return "".join(parts)
