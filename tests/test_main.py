from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import IncidentReport


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.main.ask_claude")
def test_investigate_success(mock_ask_claude):
    mock_ask_claude.return_value = IncidentReport(
        severity="high",
        likely_root_cause="Database connection pool exhausted",
        evidence=["Error rate is 18%"],
        recommended_actions=["Roll back deployment"],
    )

    response = client.post(
        "/investigate",
        json={
            "service": "checkout",
            "description": "Checkout is returning 500 errors",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["severity"] == "high"
    assert data["likely_root_cause"] == (
        "Database connection pool exhausted"
    )
    assert data["evidence"] == ["Error rate is 18%"]
    assert data["recommended_actions"] == [
        "Roll back deployment"
    ]

    mock_ask_claude.assert_called_once_with(
        service="checkout",
        description="Checkout is returning 500 errors",
    )


def test_investigate_invalid_input():
    response = client.post(
        "/investigate",
        json={
            "service": "checkout"
        },
    )

    assert response.status_code == 422


@patch("app.main.ask_claude")
def test_investigate_claude_failure(mock_ask_claude):
    mock_ask_claude.side_effect = RuntimeError(
        "Claude API unavailable"
    )

    response = client.post(
        "/investigate",
        json={
            "service": "checkout",
            "description": "Checkout is returning 500 errors",
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Incident investigation failed"
    }