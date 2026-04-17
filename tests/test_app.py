import copy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module
from src.app import app


_BASELINE_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    """Restore a clean copy of activities before each test."""
    clean = copy.deepcopy(_BASELINE_ACTIVITIES)
    monkeypatch.setattr(app_module, "activities", clean)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all(client):
    # Arrange — seed data pre-loaded

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_normalizes_email(client):
    # Arrange
    activity_name = "Chess Club"
    email = "  NewStudent@Mergington.edu  "
    normalized = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert normalized in response.json()["message"]
    assert normalized in client.get("/activities").json()[activity_name]["participants"]


def test_signup_invalid_email_returns_422(client):
    # Arrange
    activity_name = "Chess Club"
    invalid_email = "not-an-email"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={invalid_email}")

    # Assert
    assert response.status_code == 422


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already in seed data

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/unregister
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_normalizes_email(client):
    # Arrange
    activity_name = "Chess Club"
    email = "  MICHAEL@MERGINGTON.EDU  "
    normalized = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert normalized in response.json()["message"]
    assert normalized not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_not_registered_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"].lower()


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
