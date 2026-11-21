"""Crane geometry rules.

This file has no web code. It turns a few inputs into the dimensions we draw.
Every rule says where it came from and how sure we are (confidence).

Assumes inputs were already validated (see schemas.py, next step).
Units: inputs in metres/tonnes, all outputs in millimetres.
"""

# ---- Allowed input ranges -------------------------------------------------
# Source: ranges advertised by several single girder crane suppliers
# (about 1-20 t, spans 7.5-30 m, lift 1-30 m). These differ by supplier,
# so they are not a standard. Confidence: medium.
CAPACITY_T_RANGE = (1.0, 20.0)
SPAN_M_RANGE = (7.5, 30.0)
LIFT_M_RANGE = (3.0, 30.0)

# Duty groups (FEM/ISO classification letter+number, e.g. the reference shows A5).
# We only show it in the data table. It does not change the geometry.
DUTY_GROUPS = ("A3", "A4", "A5", "A6")

# ---- Rules read from the reference drawing (one data point each) ----------
# Reference: span 25000 -> overall length 25270.  Confidence: low.
OVERALL_LENGTH_EXTRA_MM = 270

# Reference: span 25000, wheel base about 3800 -> ratio about 6.6.
# A blog article also gives span/7 as a minimum. Confidence: low.
WHEEL_BASE_SPAN_RATIO = 6.6

# Reference shows "Min. 920" and "Min. 1150" hook approach (10 t crane).
# Real values depend on the hoist model. Same for every crane here.
# Confidence: low.
HOOK_APPROACH_LEFT_MM = 920
HOOK_APPROACH_RIGHT_MM = 1150

# ---- Pure estimates (NOT from a verified source) --------------------------
# Girder depth = span / 20, at least 400 mm. This is my own rough guess from
# general knowledge so the drawing looks plausible. I could not find a
# source for it. Confidence: very low. Ask an engineer.
GIRDER_DEPTH_SPAN_RATIO = 20
GIRDER_DEPTH_MIN_MM = 400

# ---- Soft guideline from a US crane dealer's table ------------------------
# (capacity in tonnes, max cost-effective span in feet)
# Source: Mazzella Companies, "Single Girder vs. Double Girder" article.
# Between table points we interpolate in a straight line (my assumption).
# This only produces a warning, never an error. Confidence: medium.
GUIDELINE_MAX_SPAN_FT = [(7.5, 80), (10, 75), (15, 65), (20, 60)]
FT_TO_M = 0.3048


def guideline_max_span_m(capacity_t):
    """Maximum 'cost-effective' span in metres for a given capacity."""
    points = GUIDELINE_MAX_SPAN_FT
    if capacity_t <= points[0][0]:
        feet = points[0][1]
    elif capacity_t >= points[-1][0]:
        feet = points[-1][1]
    else:
        feet = points[-1][1]
        for (c1, s1), (c2, s2) in zip(points, points[1:]):
            if c1 <= capacity_t <= c2:
                feet = s1 + (s2 - s1) * (capacity_t - c1) / (c2 - c1)
                break
    return feet * FT_TO_M


def _round10(value):
    """Round to the nearest 10 mm, as a whole number."""
    return int(round(value / 10) * 10)


def compute_design(span_m, capacity_t, lifting_height_m, duty_group):
    """Return the dimensions (mm), where each came from, and any warnings."""
    span_mm = int(round(span_m * 1000))

    dimensions = {
        "span_mm": span_mm,
        "overall_length_mm": span_mm + OVERALL_LENGTH_EXTRA_MM,
        "wheel_base_mm": _round10(span_mm / WHEEL_BASE_SPAN_RATIO),
        "girder_depth_mm": max(
            GIRDER_DEPTH_MIN_MM, _round10(span_mm / GIRDER_DEPTH_SPAN_RATIO)
        ),
        "lifting_height_mm": int(round(lifting_height_m * 1000)),
        "hook_approach_left_mm": HOOK_APPROACH_LEFT_MM,
        "hook_approach_right_mm": HOOK_APPROACH_RIGHT_MM,
    }

    basis = {
        "span_mm": "User input.",
        "overall_length_mm": "Span + 270 mm, from one data point in the reference drawing. Estimate.",
        "wheel_base_mm": "Span / 6.6, from one data point in the reference drawing. Estimate.",
        "girder_depth_mm": "Span / 20 (min 400 mm). Unverified guess, no source. Estimate.",
        "lifting_height_mm": "User input.",
        "hook_approach_left_mm": "Read from the reference drawing (10 t crane). Estimate.",
        "hook_approach_right_mm": "Read from the reference drawing (10 t crane). Estimate.",
    }

    warnings = []
    if capacity_t > 15:
        warnings.append(
            "Single girder cranes above about 15 t are rare; a double girder crane is usually chosen."
        )
    max_span = guideline_max_span_m(capacity_t)
    if span_m > max_span:
        warnings.append(
            f"Span {span_m} m is above the {max_span:.1f} m that one US dealer "
            f"suggests for {capacity_t} t single girder cranes (guideline only)."
        )

    return {
        "inputs": {
            "span_m": span_m,
            "capacity_t": capacity_t,
            "lifting_height_m": lifting_height_m,
            "duty_group": duty_group,
        },
        "dimensions_mm": dimensions,
        "basis": basis,
        "warnings": warnings,
    }