"""Clinician review: queue, case view, sign (confirm/override), amend, history, patient summary
(specs: clinician-review, fhir-clinical-records "Report status follows review")."""
import base64
import json
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

import deps
from fhir import mapping as m
from fhir.client import FhirError
from rules.text import templates
from routes.cases import AI_LABEL
from routes.patients import mode_of, summary as patient_summary

router = APIRouter(tags=["review"])
CLINICIANS = deps.role("gp", "reviewer")
REVIEW = f"{m.LOCAL}/review"
REASONS = ("image misread", "clinical findings disagree", "poor image", "other")


def record(rep: dict) -> dict:
    """The analysis JSON saved with the case (AI outputs, inputs, model version)."""
    for f in rep.get("presentedForm", []):
        if f.get("title") == "analysis":
            return json.loads(base64.b64decode(f["data"]))
    return {}


def code(rep: dict) -> str | None:
    return next((c["coding"][0]["code"] for c in rep.get("conclusionCode", [])), None)


def reviews(rep: dict) -> list[dict]:
    return [json.loads(x["valueString"]) for x in rep.get("extension", []) if x["url"] == REVIEW]


def media(rep: dict) -> list[dict]:
    return [{"id": x["link"]["reference"].split("/")[1], "kind": x.get("comment")} for x in rep.get("media", [])]


def load(rid: str) -> dict:
    try:
        rep = deps.fhir().read("DiagnosticReport", rid)
    except FhirError as e:
        if e.status in (404, 410):
            raise HTTPException(404, "case not found") from None
        raise
    if rep.get("code", {}).get("coding", [{}])[0].get("code") != "retinal-ai-report":
        raise HTTPException(404, "case not found")
    return rep


def readable(rid: str, u: dict) -> dict:
    """The case, if this user may read it (deps.may_read); 403 otherwise."""
    rep = load(rid)
    if not deps.may_read(u, rep):
        raise HTTPException(403, "not one of your cases or an escalated case")
    return rep


def item(rep: dict) -> dict:
    rec, issued = record(rep), rep.get("issued")
    waited = (datetime.now(timezone.utc) - datetime.fromisoformat(issued)).total_seconds() / 60 if issued else None
    return {"report_id": rep["id"], "patient_id": rep["subject"]["reference"].split("/")[1], "mode": mode_of(rep),
            "status": rep["status"], "level": code(rep), "issued": issued,
            "waiting_minutes": None if waited is None else round(waited, 1), "conclusion": rep.get("conclusion"),
            "inputs": rec.get("inputs"), "media": media(rep)}


@router.get("/review/queue")
def queue(request: Request, u: dict = Depends(CLINICIANS)):
    """Awaiting signature: Emergency first, then longest waiting. Reviewers see ESCALATE cases from anyone."""
    reps = deps.fhir().search("DiagnosticReport", code=f"{m.LOCAL}|retinal-ai-report", status="preliminary")
    me = deps.practitioner(u)
    mine = [r for r in reps if r["performer"][0]["reference"] == me or (u["role"] == "reviewer" and code(r) == "ESCALATE")]
    pid = lambda r: r["subject"]["reference"].split("/")[1]  # noqa: E731
    pats = {p: patient_summary(deps.fhir().read("Patient", p)) for p in {pid(r) for r in mine}}
    # name and HN let the reviewer identify who is waiting; response body only, never in a URL or log
    items = [{**item(r), "patient": {k: pats[pid(r)][k] for k in ("name", "hn")}} for r in mine]
    return sorted(items, key=lambda i: (i["mode"] != "emergency", i["issued"] or ""))


@router.get("/cases/{rid}")
def case(rid: deps.FhirId, request: Request, u: dict = Depends(CLINICIANS)):
    """Everything the final report shows (spec: Final clinician report); images via GET /media/{id}."""
    request.state.audit = ("R", f"DiagnosticReport/{rid}")
    rep = readable(rid, u)
    pat = deps.fhir().read("Patient", rep["subject"]["reference"].split("/")[1])
    return {**item(rep), "label": AI_LABEL, "patient": patient_summary(pat), "analysis": record(rep),
            "reviews": reviews(rep), "can_sign": rep["status"] == "preliminary" and deps.may_read(u, rep)}


LAYERS = ("vessel", "artery_vein", "disc", "heatmap")


class Layers(BaseModel):
    """Overlays visible when the clinician signed (spec: report shows the image "with the overlays shown at signing")."""
    visible: list[Literal[LAYERS]] = Field(max_length=len(LAYERS))
    opacity: int = Field(ge=0, le=100)


class Sign(BaseModel):
    decision: Literal["confirm", "override"]
    finding: deps.Text | None = None      # the clinician's own finding (required for override)
    reason: Literal[REASONS] | None = None
    reason_text: deps.Text | None = None  # required when reason is "other"
    crao: bool | None = None          # Emergency: clinician-confirmed CRAO yes/no (calibration label)
    layers: Layers | None = None      # stored with the review entry; None = not recorded (older clients)


class Amend(BaseModel):
    finding: deps.Text
    reason_text: deps.Text


def _write(rep: dict, u: dict, entry: dict):
    """Report update and its Provenance (clinician as author) in one transaction."""
    prac = deps.practitioner(u)
    rep.setdefault("extension", []).append({"url": REVIEW, "valueString": json.dumps(
        {**entry, "by": prac, "user": u["username"], "at": m.now()})})
    deps.fhir().transaction([
        {"resource": rep, "request": {"method": "PUT", "url": f"DiagnosticReport/{rep['id']}"}},
        {"fullUrl": m.urn(), "resource": m.provenance([f"DiagnosticReport/{rep['id']}"], prac, "author"),
         "request": {"method": "POST", "url": "Provenance"}}])
    return load(rep["id"])


@router.post("/cases/{rid}/sign")
def sign(rid: deps.FhirId, body: Sign, request: Request, u: dict = Depends(CLINICIANS)):
    request.state.audit = ("U", f"DiagnosticReport/{rid}")
    rep = readable(rid, u)  # who may read a case may sign it: own cases; reviewers also escalated ones
    if rep["status"] != "preliminary":
        raise HTTPException(409, "already signed: use amend")
    if body.decision == "override":
        if not body.reason:
            raise HTTPException(422, "choose an override reason")
        if not body.finding or (body.reason == "other" and not body.reason_text):
            raise HTTPException(422, "an override needs your finding (and a description for 'other')")
    if mode_of(rep) == "emergency" and body.crao is None:
        raise HTTPException(422, "state whether CRAO is clinically confirmed")
    rep["status"] = "final"
    if body.decision == "override":  # the clinician finding is authoritative; the AI output stays in presentedForm
        rep["conclusion"] = body.finding
    out = _write(rep, u, {"action": "sign", "ai_conclusion": record(rep).get("conclusion"), **body.model_dump()})
    from routes import monitoring  # import here: monitoring builds on this module
    try:
        monitoring.check_drift()  # drift is re-checked on every signature
    except Exception as e:  # the signature is saved; a failed check is retried when the dashboard opens
        monitoring.log.error("drift check failed error=%s", type(e).__name__)
    return {**item(out), "reviews": reviews(out)}


@router.post("/cases/{rid}/amend")
def amend(rid: deps.FhirId, body: Amend, request: Request, u: dict = Depends(CLINICIANS)):
    """After signing: status amended; FHIR history keeps the prior version."""
    request.state.audit = ("U", f"DiagnosticReport/{rid}")
    rep = readable(rid, u)
    if rep["status"] not in ("final", "amended"):
        raise HTTPException(409, "not signed yet: sign it instead")
    rep["status"], rep["conclusion"] = "amended", body.finding
    out = _write(rep, u, {"action": "amend", **body.model_dump()})
    return {**item(out), "reviews": reviews(out)}


@router.get("/cases/{rid}/history")
def history(rid: deps.FhirId, request: Request, u: dict = Depends(CLINICIANS)):
    request.state.audit = ("R", f"DiagnosticReport/{rid}")
    readable(rid, u)
    return [{"version": r["meta"]["versionId"], "status": r["status"], "conclusion": r.get("conclusion"),
             "updated": r["meta"].get("lastUpdated")} for r in deps.fhir().history("DiagnosticReport", rid)]


@router.get("/cases/{rid}/summary")
def patient_summary_text(rid: deps.FhirId, request: Request, lang: Literal["en", "th"] = "en", u: dict = Depends(CLINICIANS)):
    """Fixed-template patient summary of a signed result, with when to seek emergency care."""
    request.state.audit = ("R", f"DiagnosticReport/{rid}")
    rep = readable(rid, u)
    if rep["status"] == "preliminary":
        raise HTTPException(409, "the summary is available after signing")
    t = templates(lang)
    return {"lang": lang, "text": [t[summary_key(rep)], t["summary.seek_care"]]}


def summary_key(rep: dict) -> str:
    """Template key for a signed report. Overridden, amended or legacy reports without an AI code (e.g. seeded
    history) get the clinician-led sentence: the AI band is not the authoritative result there."""
    c = code(rep)
    if c is None or rep["status"] == "amended" or any(r.get("decision") == "override" for r in reviews(rep)):
        return "summary.override"
    if mode_of(rep) == "emergency":
        return f"summary.emergency.{c}"
    if c == "not-valid":
        return "summary.screening.not_valid"
    return "summary.screening.bypass" if c == "bypass" else f"summary.screening.pce.{c.removeprefix('pce-')}"
