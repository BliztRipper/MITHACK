"""FastAPI app (design D8-D12). Run from app/api:

    set -a; . ./demo-logins.txt; set +a   # SESSION_SECRET, APP_MASTER_KEY
    FHIR_USER=... FHIR_PASS=... python main.py

`python main.py` runs uvicorn with RUN (no access log: a request line can carry a query string, and patient
data must never reach logs). With the uvicorn CLI, pass --no-access-log.
"""
import contextlib
import logging
import os
import threading
import time

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

import analysis
import deps
from fhir import mapping as m
from fhir import seed
from fhir.client import FhirError, FhirUnavailable
from rules.text import CONFIG
from routes import auth, cases, demo, monitoring, patients, review

log = logging.getLogger("api")
BOOTING = threading.Event()  # set while the demo store is being seeded: patient routes answer 503
BOOT_RETRY = 2.0
BOOT_DEADLINE = float(os.environ.get("BOOT_DEADLINE_S", 300))  # seconds before the bootstrap gives up


def preflight():
    """Config errors stop start-up here, with a log naming the variable (never its value)."""
    try:
        deps.keys()
    except RuntimeError as e:  # master_key_from_env: message names APP_MASTER_KEY
        log.error("demo start-up refused: %s", e)
        raise


def bootstrap():
    """Demo mode: wait for the record store, seed it if it came back empty, then open the patient routes.
    Gives up (patient routes stay 503) on an auth error or after BOOT_DEADLINE seconds."""
    deadline = time.monotonic() + BOOT_DEADLINE
    while True:
        try:
            seed.bootstrap(deps.fhir(), deps.keys().path)
            break
        except FhirError as e:
            if e.status in (401, 403):
                log.error("demo bootstrap failed, not retrying: record store refused the login (%s); check FHIR_USER and FHIR_PASS", e)
                return
            if e.status < 500:
                log.error("demo bootstrap failed, not retrying: %s: %s", type(e).__name__, e)
                return
            err = e  # 5xx: the store is still coming up
        except FhirUnavailable as e:  # store still booting
            err = e
        if time.monotonic() >= deadline:
            log.error("demo bootstrap giving up after %ss: %s: %s", BOOT_DEADLINE, type(err).__name__, err)
            return
        log.warning("demo bootstrap waiting: %s: %s", type(err).__name__, err)
        time.sleep(BOOT_RETRY)
    BOOTING.clear()
    log.info("demo bootstrap done")


@contextlib.asynccontextmanager
async def lifespan(app):
    if deps.DEMO:
        preflight()
        BOOTING.set()
        threading.Thread(target=bootstrap, daemon=True).start()
    yield


app = FastAPI(title="Retina CVD/CRAO API", lifespan=lifespan)
for r in (auth, patients, cases, review, monitoring, demo):
    app.include_router(r.router)


def _no_query(record: logging.LogRecord) -> bool:
    """uvicorn access lines carry the full path; drop the query string (it could hold patient data)."""
    if isinstance(record.args, tuple) and len(record.args) >= 3 and isinstance(record.args[2], str):
        record.args = (*record.args[:2], record.args[2].split("?", 1)[0], *record.args[3:])
    return True


logging.getLogger("uvicorn.access").addFilter(_no_query)  # holds for `uvicorn main:app` and `python main.py`
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
    if audited and BOOTING.is_set():  # the store is being reset and seeded: nothing to read or write yet
        return JSONResponse({"detail": "record store is starting, try again shortly"}, status_code=503)
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
    out = {"api": "ok", "record_store": store, "demo": deps.DEMO}
    if deps.DEMO:  # public by design (design D4): the login screen lists them. Values from the DEMO_PASSWORDS
        # host secret ("gp1:pw,oph1:pw,..."), so none sit in the repo; users.demo.yaml holds only their hashes.
        pairs = (x.split(":", 1) for x in os.environ.get("DEMO_PASSWORDS", "").split(",") if ":" in x)
        out["demo_accounts"] = [{"username": u, "role": deps.users()[u]["role"], "password": p}
                                for u, p in pairs if u in deps.users()]
    return out


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
