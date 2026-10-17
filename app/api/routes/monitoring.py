"""Model monitoring (spec: model-monitoring): metrics per model version, calibration on signed cases, rolling
drift alerts and incidents as Flags (design D8), de-identified export of consented signed cases, audit view.

The rates are pure functions over case rows (one per DiagnosticReport), aggregated in Python (demo volume).
"""
import base64
import csv
import io
import logging
import uuid
import zipfile
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel

import deps
from rules.text import CONFIG
from fhir import mapping as m
from fhir.crypto import KeyDestroyed
from analysis import version
from routes.cases import NO_MODEL, device
from routes.patients import consent, mode_of
from routes.review import code, readable, record, reviews
from vision import quality

router = APIRouter(tags=["monitoring"])
ADMIN, VIEWERS, CLINICIANS = deps.role("admin"), deps.role("admin", "reviewer"), deps.role("gp", "reviewer")
log = logging.getLogger("api")


def _cfg():
    return {k: v["value"] for k, v in CONFIG["monitoring"].items()}


def row(rep: dict) -> dict | None:
    rec = record(rep)
    if not rec:  # seeded history without an AI record
        return None
    sign = next((r for r in reviews(rep) if r.get("action") == "sign"), {})
    crao = rec.get("crao") or {}
    return {"id": rep["id"], "version": rec.get("model_version", NO_MODEL), "mode": rec.get("mode"),
            "issued": rep.get("issued", ""), "accept": rec["quality"]["accept"], "band": crao.get("band"),
            "p": crao.get("probability"), "level": code(rep), "signed": rep["status"] in ("final", "amended"),
            "decision": sign.get("decision"), "reason": sign.get("reason"), "crao": sign.get("crao")}


def _rate(hits: int, n: int) -> dict:
    return {"value": None if n == 0 else round(hits / n, 3), "n": n}


def metrics(rows: list[dict]) -> list[dict]:
    """Per model version, each rate with the number of cases it is based on."""
    out = []
    for v in sorted({r["version"] for r in rows}):
        rs = [r for r in rows if r["version"] == v]
        em = [r for r in rs if r["band"] is not None]
        signed = [r for r in rs if r["decision"]]
        out.append({"version": v, "cases": len(rs), "by_mode": dict(Counter(r["mode"] for r in rs)),
                    "quality_rejection_rate": _rate(sum(not r["accept"] for r in rs), len(rs)),
                    "uncertain_rate": _rate(sum(r["band"] == "uncertain" for r in em), len(em)),
                    "agreement_rate": _rate(sum(r["decision"] == "confirm" for r in signed), len(signed)),
                    "override_reasons": dict(Counter(r["reason"] for r in signed if r["decision"] == "override")),
                    "triage_levels": dict(Counter(r["level"] for r in rs if r["mode"] == "emergency"))})
    return out


def calibration(rows: list[dict], version: str) -> dict:
    """Predicted band vs clinician-confirmed CRAO on signed Emergency cases; needs calibration_min cases."""
    need = _cfg()["calibration_min"]
    # only cases that produced a band (no-model and quality-rejected cases have none)
    rs = [r for r in rows if r["version"] == version and r["mode"] == "emergency" and r["signed"] and r["band"]]
    if len(rs) < need:
        return {"status": "insufficient data", "n": len(rs), "needed": need, "text": f"insufficient data ({len(rs)} of {need})"}
    bands = {}
    for b in ("unlikely", "uncertain", "likely"):
        x = [r for r in rs if r["band"] == b and r["crao"] is not None]
        bands[b] = {"n": len(x), "mean_p": round(sum(r["p"] for r in x) / len(x), 3) if x else None,
                    "observed_crao_rate": round(sum(r["crao"] for r in x) / len(x), 3) if x else None}
    return {"status": "ok", "n": len(rs), "needed": need, "bands": bands}


def drift(rows: list[dict]) -> list[dict]:
    """Alerts over the last `window` cases (rates only once the window is full, so one case cannot alarm)."""
    c = _cfg()
    w = c["window"]
    last = lambda rs: sorted(rs, key=lambda r: r["issued"])[-w:]  # noqa: E731
    cases, em, signed = last(rows), last([r for r in rows if r["band"] is not None]), last([r for r in rows if r["decision"]])
    checks = [
        ("quality_rejection_rate", cases, sum(not r["accept"] for r in cases), c["quality_reject_max"], "cases"),
        ("uncertain_rate", em, sum(r["band"] == "uncertain" for r in em), c["uncertain_max"], "Emergency cases"),
        ("override_rate", signed, sum(r["decision"] == "override" for r in signed), c["override_max"], "signed cases"),
        ("agreement_rate", signed, sum(r["decision"] == "confirm" for r in signed), c["agreement_max"], "signed cases"),
    ]
    out = []
    for metric, rs, hits, limit, what in checks:
        if len(rs) == w and hits / w > limit:
            msg = f"{metric.replace('_', ' ')} {hits}/{w} ({hits / w:.0%}) over the last {w} {what} exceeds {limit:.0%}"
            if metric == "agreement_rate":
                msg += ": possible rubber-stamping, review for automation bias"
            out.append({"metric": metric, "value": hits / w, "limit": limit, "n": w, "message": msg,
                        "newest": rs[-1]["issued"]})
    return out


def _site() -> str:
    o = {"resourceType": "Organization", "name": "Demo site",
         "identifier": [{"system": f"{m.LOCAL}/site", "value": "demo-site"}]}
    return f"Organization/{deps.fhir().create(o, if_none_exist=f'identifier={m.LOCAL}/site|demo-site')['id']}"


def _device_ref() -> str:
    d, ident = device(deps.model())
    return f"Device/{deps.fhir().create(d, if_none_exist=f'identifier={m.LOCAL}/device|{ident}')['id']}"


def _flags(category: str, active: bool = False) -> list[dict]:
    """Filtered here: IRIS ignores Flag?status= (it answers with an OperationOutcome instead)."""
    return [f for f in deps.fhir().search("Flag") if f["category"][0]["coding"][0]["code"] == category
            and (f["status"] == "active" or not active)]


VERSION_SYSTEM = f"{m.LOCAL}/model-version"


def _coded(f, system):
    return next((c["code"] for c in f["code"].get("coding", []) if c["system"] == system), None)


def _metric(f):
    return _coded(f, m.LOCAL)


def all_rows() -> list[dict]:
    reps = deps.fhir().search("DiagnosticReport", code=f"{m.LOCAL}|retinal-ai-report")
    return [r for r in map(row, reps) if r]


def check_drift(rows: list[dict] | None = None):
    """Raise a drift Flag per exceeded limit for the deployed version, unless one is open or was acknowledged
    after the newest case in the window. Flags stay until an admin acknowledges them."""
    v = version(deps.model()) or NO_MODEL
    rows = [r for r in (rows if rows is not None else all_rows()) if r["version"] == v]
    alerts = drift(rows)
    if not alerts:
        return
    existing = _flags("drift")
    for a in alerts:
        same = [f for f in existing if _metric(f) == a["metric"] and _coded(f, VERSION_SYSTEM) == v]
        if any(f["status"] == "active" or f.get("period", {}).get("end", "") >= a["newest"] for f in same):
            continue
        f = m.flag(_site(), _device_ref(), "drift", f"[{v}] {a['message']}")
        f["code"]["coding"] = [{"system": m.LOCAL, "code": a["metric"]}, {"system": VERSION_SYSTEM, "code": v}]
        f["period"] = {"start": m.now()}
        deps.fhir().create(f)
        log.warning("drift alert version=%s metric=%s value=%.3f limit=%.3f", v, a["metric"], a["value"], a["limit"])


def _flag_view(f: dict) -> dict:
    case = next((x["valueReference"]["reference"] for x in f.get("extension", []) if x["url"] == f"{m.LOCAL}/case"), None)
    return {"id": f["id"], "status": f["status"], "metric": _metric(f), "text": f["code"]["text"],
            "case": case, "opened": f.get("period", {}).get("start")}


@router.get("/monitoring")
def dashboard(days: int = 30, u: dict = Depends(VIEWERS)):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = all_rows()
    check_drift(rows)
    current = version(deps.model()) or NO_MODEL
    return {"period_days": days, "current_version": current,
            "metrics": metrics([r for r in rows if r["issued"] >= since]),
            "calibration": calibration(rows, current),
            "alerts": [_flag_view(f) for f in _flags("drift", active=True)],
            "incidents": [_flag_view(f) for f in _flags("ai-incident", active=True)]}


class Note(BaseModel):
    note: deps.Text


def _close(fid: str, category: str, note: str, u: dict):
    f = deps.fhir().read("Flag", fid)
    if f["category"][0]["coding"][0]["code"] != category or f["status"] != "active":
        raise HTTPException(409, "not an open flag of this kind")
    f["status"] = "inactive"
    f.setdefault("period", {})["end"] = m.now()
    f.setdefault("extension", []).append({"url": f"{m.LOCAL}/closing-note", "valueString": f"{u['username']}: {note}"})
    deps.fhir().update(f)
    return _flag_view(f)


@router.post("/monitoring/alerts/{fid}/acknowledge")
def acknowledge(fid: deps.FhirId, body: Note, u: dict = Depends(ADMIN)):
    return _close(fid, "drift", body.note, u)


class Incident(BaseModel):
    description: deps.Text


@router.post("/cases/{rid}/incident")
def flag_incident(rid: deps.FhirId, body: Incident, request: Request, u: dict = Depends(CLINICIANS)):
    """Any clinician can flag a suspected AI safety incident on a case they can read; it stays on the dashboard
    until an admin closes it."""
    request.state.audit = ("C", f"DiagnosticReport/{rid}")
    readable(rid, u)
    f = m.flag(_site(), _device_ref(), "ai-incident", body.description)
    f["period"] = {"start": m.now()}
    f["extension"].append({"url": f"{m.LOCAL}/case", "valueReference": m.ref(f"DiagnosticReport/{rid}")})
    return _flag_view(deps.fhir().create(f))


@router.post("/monitoring/incidents/{fid}/close")
def close_incident(fid: deps.FhirId, body: Note, u: dict = Depends(ADMIN)):
    return _close(fid, "ai-incident", body.note, u)


@router.get("/monitoring/export")
def export(request: Request, u: dict = Depends(ADMIN)):
    """De-identified zip of signed cases with active model-improvement consent: images/ + labels.csv.
    Labels are structured (decision, clinician-confirmed CRAO, AI code), never free text; images are
    re-encoded from pixels (no metadata); file names are random. The AuditEvent lists the exported cases."""
    f, ks, buf, done = deps.fhir(), deps.keys(), io.BytesIO(), []
    lines = io.StringIO()
    w = csv.writer(lines)
    w.writerow(["file", "mode", "status", "decision", "crao_confirmed", "ai_code", "ai_probability", "model_version"])
    with zipfile.ZipFile(buf, "w") as z:
        for rep in f.search("DiagnosticReport", code=f"{m.LOCAL}|retinal-ai-report"):
            pid = rep["subject"]["reference"].split("/")[1]
            rec = record(rep)
            if rep["status"] not in ("final", "amended") or not rec or not consent(pid)["model_improvement"]:
                continue
            fundus = next((x["link"]["reference"] for x in rep.get("media", []) if x.get("comment") == "fundus"), None)
            if not fundus:
                continue
            med = f.read(*fundus.split("/"))
            kid = next((e["valueString"] for x in med.get("extension", []) for e in x.get("extension", [])
                        if e["url"] == "keyId"), None)
            try:
                png = quality.intake(ks.decrypt(pid, base64.b64decode(med["content"]["data"]), kid))[1]
            except (KeyDestroyed, quality.Rejected):
                continue  # erased (withdrawn) or unreadable: never exported
            name = f"images/{uuid.uuid4().hex}.png"
            z.writestr(name, png)
            sign = next((r for r in reviews(rep) if r.get("action") == "sign"), {})
            w.writerow([name, mode_of(rep), rep["status"], sign.get("decision"), sign.get("crao"), code(rep),
                        (rec.get("crao") or {}).get("probability"), rec.get("model_version")])
            done.append(f"DiagnosticReport/{rep['id']}")
        z.writestr("labels.csv", lines.getvalue())
    request.state.audit = ("E", done)
    return Response(buf.getvalue(), media_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="reviewed-cases.zip"'})


@router.get("/audit")
def audit_log(days: int = 1, u: dict = Depends(ADMIN)):
    """Read-only view; the API has no route that changes or deletes an AuditEvent."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    evs = deps.fhir().search("AuditEvent", date=f"ge{since}")
    return [{"id": e["id"], "time": e["recorded"], "user": e["agent"][0]["who"].get("display"),
             "role": e["agent"][0]["role"][0]["text"], "action": e["action"], "outcome": e["outcome"],
             "resource": e["entity"][0]["what"].get("reference") or e["entity"][0]["what"].get("display")}
            for e in sorted(evs, key=lambda e: e["recorded"], reverse=True)]
