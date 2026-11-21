from fastapi.testclient import TestClient

from app import crane
from app.main import app

client = TestClient(app)

GOOD = {"span_m": 25, "capacity_t": 10, "lifting_height_m": 7.9, "duty_group": "A5"}


def test_preview_returns_design():
    response = client.post("/api/preview", json=GOOD)
    assert response.status_code == 200
    assert response.json()["dimensions_mm"]["overall_length_mm"] == 25270


def test_limits_endpoint_matches_rules():
    data = client.get("/api/limits").json()
    assert data["span_m"]["max"] == crane.SPAN_M_RANGE[1]
    assert data["duty_groups"] == list(crane.DUTY_GROUPS)


def test_bad_inputs_are_rejected():
    bad_cases = {
        "span too small": {**GOOD, "span_m": 2},
        "span too large": {**GOOD, "span_m": 80},
        "capacity zero": {**GOOD, "capacity_t": 0},
        "negative lift": {**GOOD, "lifting_height_m": -5},
        "unknown duty group": {**GOOD, "duty_group": "A9"},
        "text instead of number": {**GOOD, "span_m": "abc"},
        "extra field": {**GOOD, "colour": "red"},
        "missing field": {k: v for k, v in GOOD.items() if k != "span_m"},
    }
    for label, payload in bad_cases.items():
        response = client.post("/api/preview", json=payload)
        assert response.status_code == 422, label


def test_limit_values_themselves_are_accepted():
    low = {"span_m": 7.5, "capacity_t": 1, "lifting_height_m": 3, "duty_group": "A3"}
    high = {"span_m": 30, "capacity_t": 20, "lifting_height_m": 30, "duty_group": "A6"}
    assert client.post("/api/preview", json=low).status_code == 200
    assert client.post("/api/preview", json=high).status_code == 200