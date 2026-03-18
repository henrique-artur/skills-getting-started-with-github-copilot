import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities store after each test."""
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


def test_root_redirects_to_static_index():
    client = TestClient(app)

    # TestClient follows redirects by default, so disable it to assert the redirect response.
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure():
    client = TestClient(app)

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert data["Basketball"]["max_participants"] == 15


def test_signup_for_activity_succeeds():
    client = TestClient(app)
    email = "test_student@example.com"

    response = client.post("/activities/Basketball/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities["Basketball"]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_for_activity_fails_when_already_signed_up():
    client = TestClient(app)
    email = "alex@mergington.edu"

    response = client.post("/activities/Basketball/signup", params={"email": email})

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_for_unknown_activity_returns_404():
    client = TestClient(app)

    response = client.post("/activities/Nonexistent/signup", params={"email": "x@example.com"})

    assert response.status_code == 404


def test_unregister_from_activity_succeeds():
    client = TestClient(app)
    email = "alex@mergington.edu"

    response = client.delete("/activities/Basketball/participants", params={"email": email})

    assert response.status_code == 200
    assert email not in activities["Basketball"]["participants"]
    assert "Unregistered" in response.json()["message"]


def test_unregister_from_activity_fails_when_not_registered():
    client = TestClient(app)
    email = "not-registered@example.com"

    response = client.delete("/activities/Basketball/participants", params={"email": email})

    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()


def test_unregister_from_unknown_activity_returns_404():
    client = TestClient(app)

    response = client.delete("/activities/Nonexistent/participants", params={"email": "x@example.com"})

    assert response.status_code == 404
