from pydantic import BaseModel


class IncidentRequest(BaseModel):
    service: str
    description: str


class IncidentReport(BaseModel):
    severity: str
    likely_root_cause: str
    evidence: list[str]
    recommended_actions: list[str]