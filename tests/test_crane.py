from app.crane import compute_design


def reference():
    """The crane from the reference drawing: 25 m span, 10 t, 7.9 m lift."""
    return compute_design(span_m=25, capacity_t=10, lifting_height_m=7.9, duty_group="A5")


def test_reference_case_dimensions():
    dims = reference()["dimensions_mm"]
    assert dims["span_mm"] == 25000
    assert dims["overall_length_mm"] == 25270   # matches the reference drawing
    assert dims["lifting_height_mm"] == 7900
    assert dims["wheel_base_mm"] == 3790        # reference shows about 3800


def test_overall_length_is_always_span_plus_270():
    for span in (7.5, 12, 20.5, 30):
        dims = compute_design(span, 5, 6, "A5")["dimensions_mm"]
        assert dims["overall_length_mm"] == dims["span_mm"] + 270


def test_wheel_base_never_below_span_over_7():
    for span in (7.5, 12, 20.5, 30):
        dims = compute_design(span, 5, 6, "A5")["dimensions_mm"]
        assert dims["wheel_base_mm"] >= dims["span_mm"] / 7


def test_reference_case_warns_about_span():
    # 25 m is above the dealer guideline of about 22.9 m for 10 t.
    assert len(reference()["warnings"]) == 1


def test_small_crane_has_no_warnings():
    assert compute_design(10, 5, 6, "A4")["warnings"] == []


def test_every_dimension_has_a_basis_note():
    result = reference()
    assert set(result["dimensions_mm"]) == set(result["basis"])