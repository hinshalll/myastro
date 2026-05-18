"""
pdf_engine/charts/east_indian.py
================================

East Indian (Bengali) chart SVG renderer.

Layout: similar to South Indian (fixed sign positions) but with the corner
cells drawn as inscribed diamonds rather than plain squares — the visual
signature of the Bengali / Oriya style.

Sign positions match the South Indian convention:

       Pisces   Aries   Taurus  Gemini
       Aquarius                 Cancer
       Capricorn                Leo
       Sagittarius Scorpio Libra Virgo

The four corner cells (Pisces, Gemini, Sagittarius, Virgo) get an inset
diamond shape. The eight side cells remain as rectangles.

Lagna marker: a small filled triangle in the top-right of the Lagna cell.
"""

from __future__ import annotations

from pdf_engine.charts.south_indian import (
    CELL_TO_SIGN, SIGN_ABBR_3, PLANET_ABBR, _esc,
)


CORNER_CELLS = {(0, 0), (3, 0), (3, 3), (0, 3)}


def render(*, lagna_sign_idx: int, planet_signs: dict[str, int],
           theme: dict | None = None, size: int = 400,
           title: str = "", retrograde: set[str] | None = None,
           combust: set[str] | None = None) -> str:
    """Render an East Indian (Bengali) chart as an SVG string."""
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

    parts.append(
        f'<rect x="0" y="0" width="{size}" height="{size}" '
        f'fill="{t["bg_color"]}" stroke="{t["frame_color"]}" '
        f'stroke-width="{t["frame_width"]}"/>'
    )

    sign_planets: dict[int, list[str]] = {i: [] for i in range(12)}
    for p, sidx in planet_signs.items():
        sign_planets[sidx].append(p)

    for (col, row), sign_idx in CELL_TO_SIGN.items():
        x = col * cell
        y = row * cell

        if (col, row) in CORNER_CELLS:
            # Inset diamond — connects midpoints of the cell sides
            cx, cy = x + cell / 2, y + cell / 2
            half = cell / 2
            parts.append(
                f'<polygon points="{cx},{y} {x + cell},{cy} {cx},{y + cell} {x},{cy}" '
                f'fill="none" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
            )
            # Sign label centered inside diamond
            parts.append(
                f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" '
                f'fill="{t["sign_text"]}" font-family="serif" '
                f'font-size="{t["house_font_size"]}" font-style="italic">'
                f'{SIGN_ABBR_3[sign_idx]}</text>'
            )
            text_cx, text_cy = cx, cy + 12
        else:
            # Plain rectangle
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'fill="none" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
            )
            parts.append(
                f'<text x="{x + 6}" y="{y + 16}" '
                f'fill="{t["sign_text"]}" font-family="serif" '
                f'font-size="{t["house_font_size"]}" font-style="italic">'
                f'{SIGN_ABBR_3[sign_idx]}</text>'
            )
            text_cx, text_cy = x + cell / 2, y + cell / 2 + 4

        # Lagna marker (small filled triangle, top-right of cell)
        if sign_idx == lagna_sign_idx:
            tri = (f"{x + cell - 4},{y + 4} {x + cell - 14},{y + 4} "
                   f"{x + cell - 4},{y + 14}")
            parts.append(
                f'<polygon points="{tri}" fill="{t["lagna_marker_color"]}"/>'
            )

        # Planets
        planets = sign_planets[sign_idx]
        if planets:
            spacing = t["planet_font_size"] * 1.15
            start_y = text_cy - (len(planets) - 1) * spacing / 2
            for i, p in enumerate(planets):
                label = PLANET_ABBR.get(p, p[:2])
                if p in retrograde: label += "ᴿ"
                if p in combust:    label += "©"
                color = t["retro_color"] if p in retrograde else t["planet_text"]
                parts.append(
                    f'<text x="{text_cx}" y="{start_y + i * spacing:.1f}" '
                    f'text-anchor="middle" fill="{color}" font-family="serif" '
                    f'font-weight="bold" font-size="{t["planet_font_size"]}">'
                    f'{label}</text>'
                )

    # Central hollow border (matches SI)
    parts.append(
        f'<rect x="{cell}" y="{cell}" width="{2*cell}" height="{2*cell}" '
        f'fill="{t["bg_color"]}" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
    )

    parts.append('</g>')
    parts.append('</svg>')
    return "".join(parts)
