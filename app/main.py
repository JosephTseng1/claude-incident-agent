from fastapi import FastAPI
from app.models import IncidentRequest

app = FastAPI(title="AI Incident Investigation Agent")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/investigate")
def investigate(incident: IncidentRequest):
    return {
        "service": incident.service,
        "description": incident.description,
        "status": "investigation_started"
    }