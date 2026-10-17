"""FastAPI app (design D8-D12). Run from app/api:

    set -a; . ./demo-logins.txt; set +a   # SESSION_SECRET, APP_MASTER_KEY
    FHIR_USER=... FHIR_PASS=... uvicorn main:app --port 8000
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

import deps
from fhir import mapping as m
from fhir.client import FhirError, FhirUnavailable
from routes import auth, cases, patients, review

app = FastAPI(title="Retina CVD/CRAO API")
for r in (auth, patients, cases, review):
    app.include_router(r.router)


log = logging.getLogger("api")
PATIENT_DATA = ("/patients", "/cases", "/media", "/review", "/monitoring/export", "/monitoring/incidents")
ACTIONS = {"GET": "R", "POST": "C", "PUT": "U", "PATCH": "U", "DELETE": "D"}


def audit(request: Request, status: int):
    """One AuditEvent per patient-data request (design D10). Handlers may set request.state.audit =
    (action, "Type/id"); otherwise the URL path is recorded. Never the query string (it can hold names)."""
    a = getattr(request.state, "audit", None)
    if a == "written":  # the handler already recorded its own event (consent withdrawal)
        return
    u = getattr(request.state, "user", None) or {"username": "anonymous", "role": "none"}
    action, entity = a or (ACTIONS.get(request.method, "E"), None)
    ev = m.audit_event(u["username"], u["role"], action, entity or "", "0" if status < 400 else "4" if status < 500 else "8")
    if not entity:
        ev["entity"] = [{"what": {"display": request.url.path}}]
    try:
        deps.fhir().create(ev)
    except Exception as e:  # the record store may be down; the request itself must still answer
        log.error("audit write failed path=%s error=%s", request.url.path, type(e).__name__)


@app.middleware("http")
async def session_and_audit(request: Request, call_next):
    response = await call_next(request)
    u = getattr(request.state, "user", None)
    if u:  # every authenticated request restarts the 30-minute idle window
        deps.set_session(response, u["username"])
    if request.url.path.startswith(PATIENT_DATA):
        await run_in_threadpool(audit, request, response.status_code)
    return response


@app.exception_handler(FhirUnavailable)
def store_down(request: Request, e: FhirUnavailable):
    return JSONResponse({"detail": "record store unavailable"}, status_code=503)


@app.get("/health")
def health():
    """No auth. record_store drives the "record store unavailable" banner."""
    try:
        deps.fhir().health_check()
        store = "available"
    except (FhirUnavailable, FhirError, RuntimeError):
        store = "unavailable"
    return {"api": "ok", "record_store": store}
