import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

from app.crane import compute_design
from app.drawing import build_svg
from app.main import app

client = TestClient(app)

GOOD = {"span_m": 25, "capacity_t": 10, "lifting_height_m": 7.9, "duty_group": "A5"}


def reference_design():
    return compute_design(span_m=25, capacity_t=10, lifting_height_m=7.9, duty_group="A5")


def test_svg_is_valid_xml_with_labelled_dimensions():
    svg = build_svg(reference_design())
    ET.fromstring(svg)  # raises an error if the SVG is not well-formed
    for expected in ("Span 25000", "Overall length 25270", "Lifting height 7900",
                     "Wheel base 3790", "A5"):
        assert expected in svg


def test_estimates_are_marked_in_the_drawing():
    assert "(est.)" in build_svg(reference_design())


def test_design_name_cannot_inject_markup():
    design = reference_design()
    design["name"] = "<script>alert(1)</script>"
    svg = build_svg(design)
    ET.fromstring(svg)
    assert "<script>" not in svg


def test_every_allowed_size_draws_without_error():
    for span in (7.5, 15, 30):
        for lift in (3, 30):
            ET.fromstring(build_svg(compute_design(span, 5, lift, "A5")))


def test_preview_drawing_endpoint():
    response = client.post("/api/preview/drawing", json=GOOD)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    bad = client.post("/api/preview/drawing", json={**GOOD, "span_m": 2})
    assert bad.status_code == 422


def test_preview_drawing_shows_the_given_name():
    response = client.post("/api/preview/drawing?name=Bay%203", json=GOOD)
    assert "Bay 3" in response.text
    too_long = client.post("/api/preview/drawing?name=" + "x" * 81, json=GOOD)
    assert too_long.status_code == 422