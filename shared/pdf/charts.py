"""shared.pdf.charts — SVG renderers for North / South / East Indian charts.

Public API:
    render(style, *, lagna_sign_idx, planet_signs, ...) -> str
    render_chart_for_chart(chart, *, varga, style, ...) -> str
    SIGN_ABBR, SIGN_ABBR_3, PLANET_ABBR
    STYLES — dict mapping style name to render function

Each render_X function returns a self-contained SVG string suitable for
embedding in HTML / WebView / PDF.
"""

from shared.pdf.themes import THEMES, DEFAULT_THEME


SIGN_ABBR    = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]
SIGN_ABBR_3  = ["Ari","Tau","Gem","Can","Leo","Vir",
                "Lib","Sco","Sag","Cap","Aqu","Pis"]
PLANET_ABBR  = {
    "Sun":"Su", "Moon":"Mo", "Mars":"Ma", "Mercury":"Me",
    "Jupiter":"Ju", "Venus":"Ve", "Saturn":"Sa", "Rahu":"Ra", "Ketu":"Ke",
    # Outer planets — modern additions (some apps include them in D1)
    "Uranus":"Ur", "Neptune":"Ne", "Pluto":"Pl",
}


def _esc(s: str) -> str:
    return (s.replace("&","&amp;").replace("<","&lt;")
             .replace(">","&gt;").replace('"',"&quot;"))


# Adaptive label-fitting: dynamically shrink the font and (if still too tight)
# drop the degree suffix so planet labels NEVER spill outside their cell.
# Returns (font_size_in_viewBox_units, possibly-shortened-labels).

def _fit_planet_labels(labels: list[str], max_width: float, max_height: float,
                       base_font: float, line_factor: float = 1.18,
                       min_font: float = 6.5) -> tuple[float, list[str]]:
    if not labels:
        return base_font, labels
    n = len(labels)
    longest = max(len(l) for l in labels)
    # Empirically: bold serif averages ~0.55 of font_size per character width.
    char_w = 0.55

    width_ok  = (longest * char_w * base_font) <= max_width
    height_ok = (n * base_font * line_factor) <= max_height
    if width_ok and height_ok:
        return base_font, labels

    # Shrink to fit both dimensions
    font_w = max_width  / (longest * char_w) if longest else base_font
    font_h = max_height / (n * line_factor)  if n       else base_font
    font   = min(base_font, font_w, font_h)

    # Last resort: drop the "14°" suffix from each label
    if font < base_font * 0.78 and any('°' in l for l in labels):
        short = []
        for l in labels:
            head = l.split(' ', 1)[0]
            tail = ''
            for ch in reversed(l):
                if ch in ('ᴿ', '©'): tail = ch + tail
                else: break
            short.append(head + tail)
        labels = short
        longest = max(len(l) for l in short)
        font_w = max_width / (longest * char_w)
        font   = min(base_font, font_w, font_h)

    return max(min_font, font), labels


# Per-cell usable text area (width, height) in the 400×400 viewBox.
# Computed conservatively for each cell's narrowest dimension at the
# planet-text position. Text MUST fit strictly inside the polygon walls
# — the _fit_planet_labels helper will shrink the font until it does.
NI_CELL_USABLE: dict[int, tuple[float, float]] = {
    1:  (140, 75),   # top kite (wide horizontally)
    2:  ( 75, 55),   # top-left triangle
    3:  ( 55, 75),   # left-top triangle
    4:  (140, 75),   # left kite
    5:  ( 55, 75),   # left-bottom triangle
    6:  ( 75, 55),   # bottom-left triangle
    7:  (140, 75),   # bottom kite
    8:  ( 75, 55),   # bottom-right triangle
    9:  ( 55, 75),   # right-bottom triangle
   10:  (140, 75),   # right kite
   11:  ( 55, 75),   # right-top triangle
   12:  ( 75, 55),   # top-right triangle
}


def _build_labels(planets: list[str], planet_degrees: dict[str, float],
                  retrograde: set[str], combust: set[str]) -> list[str]:
    out = []
    for p in planets:
        label = PLANET_ABBR.get(p, p[:2])
        if p in planet_degrees:
            label = f"{label} {int(planet_degrees[p])}°"
        if p in retrograde:   label += "ᴿ"
        elif p in combust:    label += "©"
        out.append(label)
    return out


# ─── NORTH INDIAN (Diamond) ────────────────────────────────────────────────

NI_HOUSE_POLYGONS: dict[int, list[tuple[int, int]]] = {
    1:  [(200,  0), (300,100), (200,200), (100,100)],
    2:  [(  0,  0), (200,  0), (100,100)],
    3:  [(  0,  0), (100,100), (  0,200)],
    4:  [(  0,200), (100,100), (200,200), (100,300)],
    5:  [(  0,400), (  0,200), (100,300)],
    6:  [(  0,400), (200,400), (100,300)],
    7:  [(200,400), (100,300), (200,200), (300,300)],
    8:  [(400,400), (200,400), (300,300)],
    9:  [(400,200), (400,400), (300,300)],
   10:  [(400,200), (300,100), (200,200), (300,300)],
   11:  [(400,  0), (400,200), (300,100)],
   12:  [(200,  0), (400,  0), (300,100)],
}

NI_SIGN_TEXT_POS: dict[int, tuple[int, int]] = {
    # Sign abbrs sit at the OUTER vertex/edge of each cell.
    # For triangles, at one of two outer corners; for kites, at outer vertex.
    1:  (200, 22),    2:  (40, 22),    3:  (22, 40),    4:  (22, 200),
    5:  (22, 360),    6:  (40, 378),   7:  (200, 378),  8:  (360, 378),
    9:  (378, 360),  10:  (378, 200), 11:  (378, 40),  12:  (360, 22),
}

NI_HOUSE_NUM_POS: dict[int, tuple[int, int]] = {
    # House numbers sit at the OTHER outer corner (triangles) or
    # offset toward the chart center (kites). Always well separated from sign.
    1:  (200, 42),   2:  (160, 22),   3:  (22, 160),   4:  (42, 200),
    5:  (22, 240),   6:  (160, 378),  7:  (200, 358),  8:  (240, 378),
    9:  (378, 240), 10:  (358, 200), 11:  (378, 160), 12:  (240, 22),
}

NI_PLANET_TEXT_POS: dict[int, tuple[int, int]] = {
    # Repositioned to each cell's actual centroid (kite) / wide-side anchor
    # (triangle). Triangle cells were previously placed too close to the
    # narrow tip, causing text to spill outside the polygon walls.
    1:  (200, 115),   # top kite — center, slightly down (sign at top)
    2:  (100,  45),   # top-left triangle — near wide top edge
    3:  ( 45, 100),   # left-top triangle — near wide left edge
    4:  (115, 200),   # left kite
    5:  ( 45, 300),   # left-bottom triangle
    6:  (100, 355),   # bottom-left triangle — near wide bottom edge
    7:  (200, 285),   # bottom kite
    8:  (300, 355),   # bottom-right triangle — near wide bottom edge
    9:  (355, 300),   # right-bottom triangle — near wide right edge
   10:  (285, 200),   # right kite
   11:  (355, 100),   # right-top triangle — near wide right edge
   12:  (300,  45),   # top-right triangle — near wide top edge
}


def _polygon_d(points: list[tuple[int, int]]) -> str:
    return " ".join(f"{x},{y}" for x, y in points)


def render_north(*, lagna_sign_idx: int, planet_signs: dict[str, int],
                 theme: dict | None = None, size: int = 400,
                 title: str = "", retrograde: set[str] | None = None,
                 combust: set[str] | None = None,
                 planet_degrees: dict[str, float] | None = None,
                 show_house_numbers: bool = True,
                 show_sign_abbr: bool = True,
                 minimal: bool = False) -> str:
    """If minimal=True, hides sign abbrs + house nums for clean small thumbnails."""
    if minimal:
        show_house_numbers = False
        show_sign_abbr = False
    t = {**DEFAULT_THEME, **(theme or {})}
    retrograde = retrograde or set()
    combust    = combust    or set()
    planet_degrees = planet_degrees or {}

    house_planets: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for p, sidx in planet_signs.items():
        h = ((sidx - lagna_sign_idx) % 12) + 1
        house_planets[h].append(p)

    parts: list[str] = []
    title_offset = 30 if title else 0
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size + title_offset}" '
        f'width="{size}" height="{size + title_offset}">'
    )
    if title:
        parts.append(
            f'<text x="{size/2}" y="20" text-anchor="middle" '
            f'fill="{t["title_color"]}" font-family="serif" '
            f'font-size="{t["title_font_size"]}" font-weight="bold">'
            f'{_esc(title)}</text>'
        )
    parts.append(f'<g transform="translate(0,{title_offset})">')

    scale = size / 400.0

    parts.append(
        f'<rect x="0" y="0" width="{size}" height="{size}" '
        f'fill="{t["bg_color"]}" stroke="{t["frame_color"]}" '
        f'stroke-width="{t["frame_width"]}"/>'
    )

    for h, pts in NI_HOUSE_POLYGONS.items():
        scaled = [(x * scale, y * scale) for x, y in pts]
        parts.append(
            f'<polygon points="{_polygon_d([(int(x), int(y)) for x,y in scaled])}" '
            f'fill="none" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
        )

    for h in range(1, 13):
        sign_idx = (lagna_sign_idx + h - 1) % 12
        sx, sy = NI_SIGN_TEXT_POS[h]
        sx, sy = sx * scale, sy * scale
        if show_sign_abbr:
            parts.append(
                f'<text x="{sx}" y="{sy}" text-anchor="middle" '
                f'fill="{t["sign_text"]}" font-family="serif" '
                f'font-size="{10.5 * scale:.1f}" font-style="italic" font-weight="600">'
                f'{SIGN_ABBR[sign_idx]}</text>'
            )
        if show_house_numbers:
            hx, hy = NI_HOUSE_NUM_POS[h]
            hx, hy = hx * scale, hy * scale
            # House number — larger, distinct color from sign
            parts.append(
                f'<text x="{hx}" y="{hy}" text-anchor="middle" '
                f'fill="{t.get("muted", t["sign_text"])}" '
                f'font-family="serif" font-size="{9.5 * scale:.1f}" '
                f'font-weight="700" opacity="0.9">'
                f'H{h}</text>'
            )

    lx, ly = NI_SIGN_TEXT_POS[1]
    parts.append(
        f'<text x="{lx * scale}" y="{(ly + 12) * scale:.1f}" text-anchor="middle" '
        f'fill="{t["lagna_marker_color"]}" font-family="serif" '
        f'font-size="{8 * scale:.1f}" font-weight="bold">Asc</text>'
    )

    base_font_vb = 11.0  # bigger base font for readability (was 9.5)
    for h, planets in house_planets.items():
        if not planets:
            continue
        # Strict per-cell fit using each cell's usable area
        max_w_vb, max_h_vb = NI_CELL_USABLE[h]
        labels = _build_labels(planets, planet_degrees, retrograde, combust)
        font_vb, labels = _fit_planet_labels(
            labels, max_w_vb, max_h_vb, base_font_vb, min_font=7.0,
        )
        font_px = font_vb * scale
        line_height = font_px * 1.18

        bx, by = NI_PLANET_TEXT_POS[h]
        bx, by = bx * scale, by * scale
        n = len(planets)
        start_y = by - (n - 1) * line_height / 2 + font_px / 3
        for i, (p, label) in enumerate(zip(planets, labels)):
            color = t["retro_color"] if p in retrograde else t["planet_text"]
            parts.append(
                f'<text x="{bx}" y="{start_y + i * line_height:.1f}" '
                f'text-anchor="middle" fill="{color}" font-family="serif" '
                f'font-weight="600" font-size="{font_px:.1f}">{label}</text>'
            )

    parts.append('</g></svg>')
    return "".join(parts)


# ─── SOUTH INDIAN (Square) ─────────────────────────────────────────────────

SI_CELL_TO_SIGN: dict[tuple[int, int], int] = {
    (0, 0): 11, (1, 0): 0,  (2, 0): 1,  (3, 0): 2,
    (3, 1): 3,  (3, 2): 4,
    (3, 3): 5,  (2, 3): 6,  (1, 3): 7,  (0, 3): 8,
    (0, 2): 9,  (0, 1): 10,
}


def render_south(*, lagna_sign_idx: int, planet_signs: dict[str, int],
                 theme: dict | None = None, size: int = 400,
                 title: str = "", retrograde: set[str] | None = None,
                 combust: set[str] | None = None,
                 planet_degrees: dict[str, float] | None = None,
                 show_house_numbers: bool = True,
                 show_sign_abbr: bool = True,
                 minimal: bool = False) -> str:
    if minimal:
        show_house_numbers = False
        show_sign_abbr = False
    t = {**DEFAULT_THEME, **(theme or {})}
    retrograde = retrograde or set()
    combust    = combust    or set()
    planet_degrees = planet_degrees or {}

    cell = size / 4.0
    title_offset = 30 if title else 0

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size + title_offset}" '
        f'width="{size}" height="{size + title_offset}">'
    )
    if title:
        parts.append(
            f'<text x="{size/2}" y="20" text-anchor="middle" '
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

    # Bigger base planet font for SI — was 8.5–11.5, now 10–13
    base_planet_font = max(10.0, min(13.0, cell * 0.125))
    cell_w_usable = cell - 12
    cell_h_usable = cell - 24

    for (col, row), sign_idx in SI_CELL_TO_SIGN.items():
        x = col * cell
        y = row * cell
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'fill="none" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
        )
        if show_sign_abbr:
            if show_sign_abbr:
                parts.append(
                    f'<text x="{x + 5}" y="{y + 13}" '
                    f'fill="{t["sign_text"]}" font-family="serif" '
                    f'font-size="{cell * 0.085:.1f}" font-style="italic">'
                    f'{SIGN_ABBR_3[sign_idx]}</text>'
                )
        if show_house_numbers:
            house_num = ((sign_idx - lagna_sign_idx) % 12) + 1
            parts.append(
                f'<text x="{x + cell - 5}" y="{y + 13}" text-anchor="end" '
                f'fill="{t.get("muted", t["sign_text"])}" font-family="serif" '
                f'font-size="{cell * 0.08:.1f}" font-weight="600" opacity="0.85">'
                f'H{house_num}</text>'
            )
        if sign_idx == lagna_sign_idx:
            parts.append(
                f'<line x1="{x + cell - 14}" y1="{y + cell - 6}" '
                f'x2="{x + cell - 6}" y2="{y + cell - 14}" '
                f'stroke="{t["lagna_marker_color"]}" stroke-width="2.5"/>'
            )
            parts.append(
                f'<text x="{x + cell - 5}" y="{y + cell - 4}" text-anchor="end" '
                f'fill="{t["lagna_marker_color"]}" font-family="serif" '
                f'font-size="{cell * 0.085:.1f}" font-weight="bold">As</text>'
            )
        planets = sign_planets[sign_idx]
        if planets:
            labels = _build_labels(planets, planet_degrees, retrograde, combust)
            font, labels = _fit_planet_labels(
                labels, cell_w_usable, cell_h_usable,
                base_planet_font, min_font=6.5,
            )
            line_height = font * 1.18
            n = len(planets)
            start_y = y + cell / 2 + 4 - (n - 1) * line_height / 2 + font / 3
            for i, (p, label) in enumerate(zip(planets, labels)):
                color = t["retro_color"] if p in retrograde else t["planet_text"]
                parts.append(
                    f'<text x="{x + cell / 2}" y="{start_y + i * line_height:.1f}" '
                    f'text-anchor="middle" fill="{color}" font-family="serif" '
                    f'font-weight="600" font-size="{font:.1f}">{label}</text>'
                )

    parts.append(
        f'<rect x="{cell}" y="{cell}" width="{2*cell}" height="{2*cell}" '
        f'fill="{t["bg_color"]}" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
    )
    parts.append('</g></svg>')
    return "".join(parts)


# ─── EAST INDIAN (Bengali) ─────────────────────────────────────────────────

EI_CORNER_CELLS = {(0, 0), (3, 0), (3, 3), (0, 3)}


def render_east(*, lagna_sign_idx: int, planet_signs: dict[str, int],
                theme: dict | None = None, size: int = 400,
                title: str = "", retrograde: set[str] | None = None,
                combust: set[str] | None = None,
                planet_degrees: dict[str, float] | None = None,
                show_house_numbers: bool = True,
                show_sign_abbr: bool = True,
                minimal: bool = False) -> str:
    if minimal:
        show_house_numbers = False
        show_sign_abbr = False
    t = {**DEFAULT_THEME, **(theme or {})}
    retrograde = retrograde or set()
    combust    = combust    or set()
    planet_degrees = planet_degrees or {}

    cell = size / 4.0
    title_offset = 30 if title else 0

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size + title_offset}" '
        f'width="{size}" height="{size + title_offset}">'
    )
    if title:
        parts.append(
            f'<text x="{size/2}" y="20" text-anchor="middle" '
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

    # Bigger base for EI — was 8.5–11.5, now 10–13
    base_planet_font = max(10.0, min(13.0, cell * 0.125))
    sq_w_usable = cell - 12
    sq_h_usable = cell - 24
    di_w_usable = cell - 36
    di_h_usable = cell - 36

    for (col, row), sign_idx in SI_CELL_TO_SIGN.items():
        x = col * cell
        y = row * cell
        if (col, row) in EI_CORNER_CELLS:
            cx, cy = x + cell / 2, y + cell / 2
            parts.append(
                f'<polygon points="{cx},{y} {x + cell},{cy} {cx},{y + cell} {x},{cy}" '
                f'fill="none" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
            )
            if show_sign_abbr:
                parts.append(
                    f'<text x="{cx}" y="{y + 18}" text-anchor="middle" '
                    f'fill="{t["sign_text"]}" font-family="serif" '
                    f'font-size="{cell * 0.08:.1f}" font-style="italic">'
                    f'{SIGN_ABBR_3[sign_idx]}</text>'
                )
            if show_house_numbers:
                house_num = ((sign_idx - lagna_sign_idx) % 12) + 1
                parts.append(
                    f'<text x="{cx}" y="{y + cell - 8}" text-anchor="middle" '
                    f'fill="{t.get("muted", t["sign_text"])}" font-family="serif" '
                    f'font-size="{cell * 0.075:.1f}" font-weight="600" opacity="0.85">'
                    f'H{house_num}</text>'
                )
            text_cx, text_cy = cx, cy + 4
        else:
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'fill="none" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
            )
            if show_sign_abbr:
                parts.append(
                    f'<text x="{x + 5}" y="{y + 13}" '
                    f'fill="{t["sign_text"]}" font-family="serif" '
                    f'font-size="{cell * 0.085:.1f}" font-style="italic">'
                    f'{SIGN_ABBR_3[sign_idx]}</text>'
                )
            if show_house_numbers:
                house_num = ((sign_idx - lagna_sign_idx) % 12) + 1
                parts.append(
                    f'<text x="{x + cell - 5}" y="{y + 13}" text-anchor="end" '
                    f'fill="{t.get("muted", t["sign_text"])}" font-family="serif" '
                    f'font-size="{cell * 0.08:.1f}" font-weight="600" opacity="0.85">'
                    f'H{house_num}</text>'
                )
            text_cx, text_cy = x + cell / 2, y + cell / 2 + 4

        if sign_idx == lagna_sign_idx:
            tri = (f"{x + cell - 4},{y + 4} {x + cell - 16},{y + 4} "
                   f"{x + cell - 4},{y + 16}")
            parts.append(
                f'<polygon points="{tri}" fill="{t["lagna_marker_color"]}"/>'
            )

        planets = sign_planets[sign_idx]
        if planets:
            labels = _build_labels(planets, planet_degrees, retrograde, combust)
            is_diamond = (col, row) in EI_CORNER_CELLS
            mw = di_w_usable if is_diamond else sq_w_usable
            mh = di_h_usable if is_diamond else sq_h_usable
            font, labels = _fit_planet_labels(
                labels, mw, mh, base_planet_font, min_font=6.5,
            )
            line_height = font * 1.18
            n = len(planets)
            start_y = text_cy - (n - 1) * line_height / 2
            for i, (p, label) in enumerate(zip(planets, labels)):
                color = t["retro_color"] if p in retrograde else t["planet_text"]
                parts.append(
                    f'<text x="{text_cx}" y="{start_y + i * line_height:.1f}" '
                    f'text-anchor="middle" fill="{color}" font-family="serif" '
                    f'font-weight="600" font-size="{font:.1f}">{label}</text>'
                )

    parts.append(
        f'<rect x="{cell}" y="{cell}" width="{2*cell}" height="{2*cell}" '
        f'fill="{t["bg_color"]}" stroke="{t["frame_color"]}" stroke-width="1.2"/>'
    )
    parts.append('</g></svg>')
    return "".join(parts)


# ─── Dispatcher ────────────────────────────────────────────────────────────

STYLES = {
    "north_indian": render_north,
    "south_indian": render_south,
    "east_indian":  render_east,
}


def render(style: str, **kwargs) -> str:
    """Dispatch to the requested chart style."""
    if style not in STYLES:
        raise ValueError(f"Unknown chart style: {style}. Choose from: {list(STYLES)}")
    return STYLES[style](**kwargs)


def render_chart_for_chart(chart, *, varga: int = 1,
                            style: str = "north_indian",
                            size: int = 400,
                            theme_name: str = "classic_vedic",
                            theme: dict | None = None,
                            show_degrees: bool | None = None,
                            show_house_numbers: bool = True,
                            title: str = "") -> str:
    """Universal chart renderer — render any varga of a computed KundliChart
    as a self-contained SVG string. Use this anywhere in the app (free
    view, compatibility feature, transit overlay, mobile renderer) to
    display the same accurate, themed chart.

    Args:
        chart: A KundliChart from shared.astro.kundli.compute_chart().
        varga: Divisional chart number (1=Rasi/D1, 9=Navamsa/D9, etc.).
        style: 'north_indian' | 'south_indian' | 'east_indian'.
        size: SVG width/height in viewBox units (default 400).
        theme_name: One of THEMES keys (used if `theme` is None).
        theme: Pre-built SVG theme dict (overrides theme_name).
        show_degrees: Show 'Mo 14°' format. Defaults to True for D1, False otherwise.
        show_house_numbers: Show H1..H12 in cells.
        title: Optional title above the chart.

    Returns:
        SVG string suitable for embedding in HTML / WebView / PDF.
    """
    varga_obj = chart.divisional_charts.get(varga)
    if varga_obj is None:
        raise ValueError(
            f"Varga D{varga} not in chart.divisional_charts. "
            f"Available: {sorted(chart.divisional_charts.keys())}"
        )
    if theme is None:
        theme = _svg_theme_from(THEMES.get(theme_name, THEMES["classic_vedic"]))
    if show_degrees is None:
        show_degrees = (varga == 1)
    retrograde = {p for p, pp in chart.planets.items() if pp.is_retrograde}
    combust    = {p for p, pp in chart.planets.items() if pp.is_combust}
    planet_degrees = (
        {p: pp.longitude % 30 for p, pp in chart.planets.items()}
        if show_degrees else None
    )
    return render(
        style=style,
        lagna_sign_idx=varga_obj.lagna_sign_index,
        planet_signs=varga_obj.planet_signs,
        theme=theme, size=size, title=title,
        retrograde=retrograde, combust=combust,
        planet_degrees=planet_degrees,
        show_house_numbers=show_house_numbers,
    )


def _svg_theme_from(theme: dict) -> dict:
    return {
        "frame_color":        theme["primary"],
        "frame_width":        2,
        "bg_color":           theme["paper"],
        "house_text":         theme["muted"],
        "sign_text":          theme["muted"],
        "planet_text":        theme["ink"],
        "muted":              theme["muted"],
        "title_color":        theme["primary"],
        "lagna_marker_color": theme["accent"],
        "retro_color":        theme["accent"],
        "planet_font_size":   14,
        "house_font_size":    10,
        "title_font_size":    14,
    }
