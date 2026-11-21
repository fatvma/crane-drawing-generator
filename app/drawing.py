"""Builds the 2D drawing as an SVG string (plain text, no extra libraries).

Layout: front view on top, plan view in the middle, data table at the bottom.

Scale: distances ALONG the crane (span, overall length, wheel base, hook
approach) follow the real proportions. Vertical sizes in the front view are
schematic and NOT to scale, like the reference drawing ("DRAWING NOT IN SCALE").
Every number printed is the real value in mm, whatever size it is drawn at.
"""

from html import escape

WIDTH = 1100
HEIGHT = 880
MARGIN_X = 90
DRAW_W = WIDTH - 2 * MARGIN_X  # pixels available for the overall length

STYLE = """
.obj { stroke: #111; stroke-width: 1.5; fill: none; }
.light { fill: #e6e6e6; }
.dim { stroke: #0b5394; stroke-width: 1; }
.ext { stroke: #888; stroke-width: 0.7; stroke-dasharray: 3 2; }
.txt { font: 12px Arial, sans-serif; fill: #111; }
.dimtxt { font: 12px Arial, sans-serif; fill: #0b5394; }
.title { font: bold 14px Arial, sans-serif; fill: #111; }
.note { font: 11px Arial, sans-serif; fill: #555; }
.warn { font: 11px Arial, sans-serif; fill: #a61c00; }
"""

ARROW = (
    '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
    'markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="#0b5394"/></marker>'
)


# ---- small drawing helpers ------------------------------------------------
def _n(value):
    return f"{value:.1f}"


def _line(x1, y1, x2, y2, cls="obj"):
    return (f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}" '
            f'class="{cls}"/>')


def _rect(x, y, w, h, cls="obj"):
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" '
            f'class="{cls}"/>')


def _circle(cx, cy, r, cls="obj"):
    return f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}" class="{cls}"/>'


def _text(x, y, content, cls="txt", anchor="middle", rotate=0):
    """Text is always escaped, so a design name cannot inject markup."""
    turn = f' transform="rotate({rotate} {_n(x)} {_n(y)})"' if rotate else ""
    return (f'<text x="{_n(x)}" y="{_n(y)}" class="{cls}" '
            f'text-anchor="{anchor}"{turn}>{escape(str(content))}</text>')


def _hdim(x1, x2, y, label, ext_y=None):
    """Horizontal dimension line from x1 to x2 at height y."""
    parts = []
    if ext_y is not None:
        end = y + (4 if y > ext_y else -4)
        parts += [_line(x1, ext_y, x1, end, "ext"), _line(x2, ext_y, x2, end, "ext")]
    parts.append(
        f'<line x1="{_n(x1)}" y1="{_n(y)}" x2="{_n(x2)}" y2="{_n(y)}" class="dim" '
        'marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
    )
    parts.append(_text((x1 + x2) / 2, y - 5, label, "dimtxt"))
    return "".join(parts)


def _vdim(x, y1, y2, label, ext_x=None, side="left"):
    """Vertical dimension line from y1 to y2 at position x. Label on one side."""
    parts = []
    if ext_x is not None:
        end = x + (4 if x > ext_x else -4)
        parts += [_line(ext_x, y1, end, y1, "ext"), _line(ext_x, y2, end, y2, "ext")]
    parts.append(
        f'<line x1="{_n(x)}" y1="{_n(y1)}" x2="{_n(x)}" y2="{_n(y2)}" class="dim" '
        'marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
    )
    mid = (y1 + y2) / 2
    if side == "left":
        parts.append(_text(x - 6, mid, label, "dimtxt", rotate=-90))
    else:
        parts.append(_text(x + 6, mid, label, "dimtxt", rotate=90))
    return "".join(parts)


# ---- the drawing ----------------------------------------------------------
def build_svg(design):
    """`design` is the dictionary returned by crane.compute_design()
    (optionally with a "name" added)."""
    dims = design["dimensions_mm"]
    inputs = design["inputs"]
    basis = design["basis"]
    name = design.get("name") or "Unsaved preview"

    overall = dims["overall_length_mm"]
    span = dims["span_mm"]
    sx = DRAW_W / overall  # pixels per mm along the crane

    x0 = MARGIN_X
    rail_l = x0 + (overall - span) / 2 * sx  # left rail centre line
    rail_r = rail_l + span * sx              # right rail centre line
    x_mid = (rail_l + rail_r) / 2
    # End carriage width along the span, kept at least 12 px so it stays visible.
    ec_w = max(12, (overall - span) * sx)

    p = []

    # ---------------- FRONT VIEW ----------------
    top, girder_h, rail_y, floor_y, hook_y = 130, 30, 200, 360, 250
    p.append(_text(MARGIN_X, 30, "FRONT VIEW", "title", "start"))
    p.append(_text(WIDTH - MARGIN_X, 30, name, "title", "end"))

    p.append(_hdim(x0, x0 + DRAW_W, 62, f"Overall length {overall}", ext_y=top))
    p.append(_hdim(rail_l, rail_r, 95, f"Span {span}", ext_y=top))

    for rx in (rail_l, rail_r):  # end carriages
        p.append(_rect(rx - ec_w / 2, top - 10, ec_w, rail_y - top + 10, "obj light"))
    p.append(_rect(rail_l, top, span * sx, girder_h, "obj light"))  # girder
    p.append(_line(x0 - 25, rail_y, x0 + DRAW_W + 25, rail_y))      # runway rail
    p.append(_text(x0 - 25, rail_y - 6, "Rail", "note", "start"))

    p.append(_rect(x_mid - 30, top + girder_h, 60, 28))            # trolley + hoist
    p.append(_line(x_mid, top + girder_h + 28, x_mid, hook_y - 6))  # rope
    p.append(_circle(x_mid, hook_y, 6))                            # hook

    p.append(_line(x0 - 30, floor_y, x0 + DRAW_W + 30, floor_y))
    p.append(_text(x0 - 30, floor_y + 14, "Floor", "note", "start"))
    p.append(_vdim(x_mid + 110, hook_y, floor_y,
                   f"Lifting height {dims['lifting_height_mm']}",
                   ext_x=x_mid + 8, side="right"))
    p.append(_vdim(rail_l - 40, top, top + girder_h,
                   f"Girder depth {dims['girder_depth_mm']} (est.)",
                   ext_x=rail_l, side="left"))
    p.append(_text(x0 + DRAW_W, floor_y + 18,
                   "Vertical sizes are schematic (not to scale)", "note", "end"))

    # ---------------- PLAN VIEW ----------------
    yc = 520
    ec_len = dims["end_carriage_length_mm"] * sx
    wb = dims["wheel_base_mm"] * sx
    p.append(_text(MARGIN_X, 410, "PLAN VIEW", "title", "start"))

    p.append(_rect(rail_l, yc - 7, span * sx, 14, "obj light"))  # girder
    for rx in (rail_l, rail_r):
        p.append(_rect(rx - ec_w / 2, yc - ec_len / 2, ec_w, ec_len, "obj light"))
        for wy in (yc - wb / 2, yc + wb / 2):  # wheels
            p.append(_circle(rx, wy, 5))
    p.append(_rect(x_mid - 22, yc - 18, 44, 36))  # trolley (schematic size)

    hook_l = rail_l + dims["hook_approach_left_mm"] * sx
    hook_r = rail_r - dims["hook_approach_right_mm"] * sx
    p.append(_circle(hook_l, yc, 4))
    p.append(_circle(hook_r, yc, 4))

    p.append(_vdim(rail_r + 45, yc - wb / 2, yc + wb / 2,
                   f"Wheel base {dims['wheel_base_mm']} (est.)",
                   ext_x=rail_r, side="right"))
    p.append(_vdim(rail_l - 45, yc - ec_len / 2, yc + ec_len / 2,
                   f"End carriage {dims['end_carriage_length_mm']} (est.)",
                   ext_x=rail_l, side="left"))
    p.append(_hdim(rail_l, hook_l, 650, str(dims["hook_approach_left_mm"]), ext_y=yc))
    p.append(_hdim(hook_r, rail_r, 650, str(dims["hook_approach_right_mm"]), ext_y=yc))
    p.append(_text(rail_l, 668, "Hook approach (est.)", "note", "start"))
    p.append(_text(rail_r, 668, "Hook approach (est.)", "note", "end"))

    # ---------------- DATA TABLE ----------------
    def est(key):
        return " (est.)" if "Estimate" in basis[key] else ""

    left_col = [
        ("Capacity", f"{inputs['capacity_t']:g} t"),
        ("Span", f"{span} mm"),
        ("Lifting height", f"{dims['lifting_height_mm']} mm"),
        ("Duty group", inputs["duty_group"]),
    ]
    right_col = [
        ("Overall length", f"{overall} mm{est('overall_length_mm')}"),
        ("Wheel base", f"{dims['wheel_base_mm']} mm{est('wheel_base_mm')}"),
        ("End carriage length",
         f"{dims['end_carriage_length_mm']} mm{est('end_carriage_length_mm')}"),
        ("Girder depth", f"{dims['girder_depth_mm']} mm{est('girder_depth_mm')}"),
        ("Hook approach left / right",
         f"{dims['hook_approach_left_mm']} / {dims['hook_approach_right_mm']} mm"
         f"{est('hook_approach_left_mm')}"),
    ]
    p.append(_text(MARGIN_X, 705, "TECHNICAL DATA", "title", "start"))
    for i, (label, value) in enumerate(left_col):
        y = 727 + i * 18
        p.append(_text(MARGIN_X, y, label, "txt", "start"))
        p.append(_text(MARGIN_X + 150, y, value, "txt", "start"))
    for i, (label, value) in enumerate(right_col):
        y = 727 + i * 18
        p.append(_text(MARGIN_X + 380, y, label, "txt", "start"))
        p.append(_text(MARGIN_X + 590, y, value, "txt", "start"))

    for i, warning in enumerate(design.get("warnings", [])):
        p.append(_text(MARGIN_X, 835 + i * 15, f"WARNING: {warning}", "warn", "start"))
    p.append(_text(MARGIN_X, HEIGHT - 10,
                   "PRELIMINARY - values marked (est.) are estimates, not verified. "
                   "Not for manufacture.", "note", "start"))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">'
        f"<style>{STYLE}</style><defs>{ARROW}</defs>"
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>'
        + "".join(p)
        + "</svg>"
    )