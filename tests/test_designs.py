import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app, get_db

GOOD = {
    "name": "Workshop crane",
    "span_m": 25,
    "capacity_t": 10,
    "lifting_height_m": 7.9,
    "duty_group": "A5",
}


@pytest.fixture
def client(tmp_path):
    """A test client wired to a fresh temporary database."""
    db_file = str(tmp_path / "test.db")
    setup = database.connect(db_file)
    database.init_db(setup)
    setup.close()

    def use_test_db():
        conn = database.connect(db_file)
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = use_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_then_open(client):
    created = client.post("/api/designs", json=GOOD)
    assert created.status_code == 201
    design_id = created.json()["id"]

    opened = client.get(f"/api/designs/{design_id}")
    assert opened.status_code == 200
    body = opened.json()
    assert body["name"] == "Workshop crane"
    assert body["inputs"]["span_m"] == 25
    assert body["dimensions_mm"]["overall_length_mm"] == 25270


def test_list_shows_saved_designs(client):
    client.post("/api/designs", json=GOOD)
    client.post("/api/designs", json={**GOOD, "name": "Second crane"})
    listed = client.get("/api/designs").json()
    assert len(listed) == 2
    assert {d["name"] for d in listed} == {"Workshop crane", "Second crane"}


def test_edit_changes_saved_design(client):
    design_id = client.post("/api/designs", json=GOOD).json()["id"]
    edited = client.put(
        f"/api/designs/{design_id}", json={**GOOD, "name": "Renamed", "span_m": 20}
    )
    assert edited.status_code == 200

    body = client.get(f"/api/designs/{design_id}").json()
    assert body["name"] == "Renamed"
    assert body["dimensions_mm"]["overall_length_mm"] == 20270


def test_missing_design_gives_404(client):
    assert client.get("/api/designs/999").status_code == 404
    assert client.put("/api/designs/999", json=GOOD).status_code == 404


def test_invalid_design_is_not_saved(client):
    response = client.post("/api/designs", json={**GOOD, "span_m": 2})
    assert response.status_code == 422
    assert client.get("/api/designs").json() == []


def test_blank_name_is_rejected(client):
    response = client.post("/api/designs", json={**GOOD, "name": "   "})
    assert response.status_code == 422