from fastapi import FastAPI

app = FastAPI(title="AI Incident Investigation Agent")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/investigate")
def investigate():
    return {"status": "investigation_started"}