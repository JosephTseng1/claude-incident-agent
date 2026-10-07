import json
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"


def load_json(filename):
    with open(DATA_DIR / filename) as file:
        return json.load(file)


def search_logs(service: str, keyword: str):
    logs = load_json("logs.json")

    return [
        log
        for log in logs
        if log["service"] == service
        and keyword.lower() in log["message"].lower()
    ]


def get_metric(service: str, metric_name: str):
    metrics = load_json("metrics.json")
    service_metrics = metrics.get(service, {})

    return {
        "service": service,
        "metric": metric_name,
        "value": service_metrics.get(metric_name)
    }


def get_recent_deployments(service: str):
    deployments = load_json("deployments.json")

    return [
        deployment
        for deployment in deployments
        if deployment["service"] == service
    ]


def get_service_health(service: str):
    metrics = load_json("metrics.json")
    service_metrics = metrics.get(service)

    if not service_metrics:
        return {
            "service": service,
            "status": "unknown"
        }

    if service_metrics.get("error_rate", 0) > 0.05:
        return {
            "service": service,
            "status": "unhealthy"
        }

    return {
        "service": service,
        "status": "healthy"
    }