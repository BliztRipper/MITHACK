"""FastAPI app (design D8-D12). Run from app/api:

    set -a; . ./demo-logins.txt; set +a   # SESSION_SECRET, APP_MASTER_KEY
    FHIR_USER=... FHIR_PASS=... python main.py

`python main.py` runs uvicorn with RUN (no access log: a request line can carry a query string, and patient
data must never reach logs). With the uvicorn CLI, pass --no-access-log.
"""
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

import analysis
import deps
from fhir import mapping as m
from fhir.client import FhirError, FhirUnavailable
from rules.text import CONFIG
from routes import auth, cases, monitoring, patients, review

app = FastAPI(title="Retina CVD/CRAO API")
for r in (auth, patients, cases, review, monitoring):
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
    ev = m.audit_event(u["username"], u["role"], action, "", "0" if status < 400 else "4" if status < 500 else "8")
    refs = entity if isinstance(entity, list) else [entity] if entity else []  # a list: e.g. the exported cases
    ev["entity"] = [{"what": m.ref(r)} for r in refs] or [{"what": {"display": request.url.path}}]
    try:
        deps.fhir().create(ev)
    except Exception as e:  # the record store may be down; the request itself must still answer
        log.error("audit write failed path=%s error=%s", request.url.path, type(e).__name__)


@app.middleware("http")
async def session_and_audit(request: Request, call_next):
    audited = request.url.path.startswith(PATIENT_DATA)
    try:
        response = await call_next(request)
    except Exception:  # unhandled error: still audit the attempt (outcome 8), then let it propagate
        if audited:
            await run_in_threadpool(audit, request, 500)
        raise
    u = getattr(request.state, "user", None)
    if u:  # every authenticated request restarts the 30-minute idle window
        deps.set_session(response, u["username"])
    if audited:
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


@app.get("/about")
def about(u: dict = Depends(deps.user)):
    """Thresholds with their validation status, and the loaded model (spec: thresholds visible)."""
    model = deps.model()
    lo, hi = analysis.thresholds(model)
    return {"config": {k: CONFIG[k] for k in ("triage", "risk", "monitoring")},
            "crao_thresholds": {"p_low": lo, "p_high": hi, "source": "model checkpoint" if model else "config.yaml"},
            "model": model.info() if model else None, "model_status": "loaded" if model else "no model loaded"}


RUN = {"host": "127.0.0.1", "port": 8000, "access_log": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, **RUN)
