"""FastAPI app (design D8-D12). Run from app/api:

    set -a; . ./demo-logins.txt; set +a   # SESSION_SECRET, APP_MASTER_KEY
    FHIR_USER=... FHIR_PASS=... uvicorn main:app --port 8000
"""
from fastapi import FastAPI, Request

import deps
from fhir.client import FhirError, FhirUnavailable
from routes import auth, cases

app = FastAPI(title="Retina CVD/CRAO API")
for r in (auth, cases):
    app.include_router(r.router)


@app.middleware("http")
async def sliding_session(request: Request, call_next):
    response = await call_next(request)
    u = getattr(request.state, "user", None)
    if u:  # every authenticated request restarts the 30-minute idle window
        deps.set_session(response, u["username"])
    return response


@app.get("/health")
def health():
    """No auth. record_store drives the "record store unavailable" banner."""
    try:
        deps.fhir().health_check()
        store = "available"
    except (FhirUnavailable, FhirError, RuntimeError):
        store = "unavailable"
    return {"api": "ok", "record_store": store}
