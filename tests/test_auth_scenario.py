from app.tools import (
    search_logs,
    get_metric,
    get_recent_deployments,
    get_service_health,
)


def test_auth_logs():
    logs = search_logs("auth", "timed out")

    assert len(logs) > 0
    assert all(log["service"] == "auth" for log in logs)


def test_auth_error_rate():
    result = get_metric("auth", "error_rate")

    assert result["value"] == 0.12


def test_auth_deployment():
    deployments = get_recent_deployments("auth")

    assert len(deployments) == 1
    assert deployments[0]["version"] == "v1.8.0"
    assert deployments[0]["change"] == (
        "Reduced upstream authentication timeout from 5s to 1s"
    )


def test_auth_health():
    health = get_service_health("auth")

    assert health["status"] == "unhealthy"