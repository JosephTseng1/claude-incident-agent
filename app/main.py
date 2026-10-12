import logging

from fastapi import FastAPI, HTTPException

from app.agent import ask_claude
from app.models import IncidentRequest, IncidentReport


app = FastAPI(title="AI Incident Investigation Agent")

logger = logging.getLogger(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/investigate", response_model=IncidentReport)
def investigate(incident: IncidentRequest):
    try:
        report = ask_claude(
            service=incident.service,
            description=incident.description,
        )

        return report

    except Exception as e:
        logger.exception("Incident investigation failed")

        raise HTTPException(
            status_code=500,
            detail="Incident investigation failed",
        ) from e