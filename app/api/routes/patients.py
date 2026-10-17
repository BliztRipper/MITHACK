"""Patient search/detail and purpose-limited consent (specs: fhir-clinical-records, patient-data-protection)."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

import deps
from fhir import mapping as m
from fhir.client import FhirError
from fhir.withdrawal import withdraw

router = APIRouter(tags=["patients"])
CLINICIANS = deps.role("gp", "reviewer")
PURPOSES = {"care": "care", "model-improvement": "model_improvement"}
OBS_KEYS = {code: k for k, (_, code, _) in m.OBS_CODES.items()}
INPUT_KEYS = ("sbp", "dbp", "tc", "hdl", "ldl", "smoking", "waist", "height", "arcus_senilis")


def summary(p: dict) -> dict:
    name = (p.get("name") or [{}])[0]
    hn = next((i["value"] for i in p.get("identifier", []) if i["system"] == m.MRN), None)
    return {"id": p["id"], "hn": hn, "name": " ".join([*name.get("given", []), name.get("family", "")]).strip(),
            "gender": p.get("gender"), "birth_date": p.get("birthDate")}


def consent(pid: str) -> dict:
    """Active consent per purpose: {"care": bool, "model_improvement": bool}."""
    out = dict.fromkeys(PURPOSES.values(), False)
    for c in deps.fhir().search("Consent", patient=f"Patient/{pid}", status="active"):
        for p in c.get("provision", {}).get("purpose", []):
            if p.get("code") in PURPOSES:
                out[PURPOSES[p["code"]]] = True
    return out


def read_patient(pid: str) -> dict:
    try:
        return deps.fhir().read("Patient", pid)
    except FhirError as e:
        if e.status in (404, 410):
            raise HTTPException(404, "patient not found") from None
        raise


def mode_of(rep: dict) -> str | None:
    for c in rep.get("category", []):
        return c["coding"][0]["code"]
    enc = deps.fhir().read(*rep["encounter"]["reference"].split("/"))  # seeded reports carry the mode on the Encounter
    return enc["type"][0]["coding"][0]["code"]


class Search(BaseModel):
    q: deps.Text  # name or hospital number; in the body, never the URL (URLs reach access logs)


@router.post("/patients/search")
def search(body: Search, request: Request, u: dict = Depends(CLINICIANS)):
    """Find by name or hospital number."""
    request.state.audit = ("R", None)
    f = deps.fhir()
    found = {p["id"]: p for p in f.search("Patient", name=body.q) + f.search("Patient", identifier=f"{m.MRN}|{body.q}")}
    return [summary(p) for p in found.values()]


@router.get("/patients/{pid}")
def detail(pid: deps.FhirId, request: Request, u: dict = Depends(CLINICIANS)):
    request.state.audit = ("R", f"Patient/{pid}")
    p, f, pref = read_patient(pid), deps.fhir(), f"Patient/{pid}"
    since = (datetime.now(timezone.utc) - timedelta(days=365)).date().isoformat()
    latest = {}
    for o in sorted(f.search("Observation", subject=pref, date=f"ge{since}"), key=lambda o: o.get("effectiveDateTime", "")):
        k = OBS_KEYS.get(o["code"]["coding"][0]["code"])
        if k in INPUT_KEYS:  # pre-fill values with their dates (spec: inputs pre-filled from record)
            v = o.get("valueQuantity", {}).get("value", o.get("valueBoolean", o.get("valueCodeableConcept", {}).get("text")))
            latest[k] = {"value": v, "date": o.get("effectiveDateTime")}
    reps = sorted(f.search("DiagnosticReport", subject=pref, code=f"{m.LOCAL}|retinal-ai-report"),
                  key=lambda r: r.get("issued", ""), reverse=True)
    cases = [{"report_id": r["id"], "date": r.get("issued"), "mode": mode_of(r), "status": r["status"],
              "result": r.get("conclusion")} for r in reps]
    return {"patient": summary(p), "consent": consent(pid), "latest": latest, "cases": cases}


class ConsentIn(BaseModel):
    care: bool                        # required to process images
    model_improvement: bool = False   # optional, gates retraining export
    retention_years: int
    right_to_withdraw_explained: bool


@router.get("/patients/{pid}/consent")
def get_consent(pid: deps.FhirId, request: Request, u: dict = Depends(CLINICIANS)):
    request.state.audit = ("R", f"Patient/{pid}")
    return consent(pid)


@router.post("/patients/{pid}/consent")
def record_consent(pid: deps.FhirId, body: ConsentIn, request: Request, u: dict = Depends(CLINICIANS)):
    """Explicit consent (PDPA s.26): purpose, retention period and right to withdraw, with time and recorder."""
    request.state.audit = ("C", f"Patient/{pid}")
    if not (body.care and body.right_to_withdraw_explained) or body.retention_years < 1:
        raise HTTPException(422, "care consent, a retention period and the right to withdraw are all required")
    read_patient(pid)
    have, rec = consent(pid), deps.practitioner(u)
    end = (datetime.now(timezone.utc) + timedelta(days=365 * body.retention_years)).date().isoformat()
    for purpose, key in PURPOSES.items():
        if getattr(body, key) and not have[key]:
            c = m.consent(f"Patient/{pid}", purpose)
            c["provision"]["period"] = {"start": c["dateTime"], "end": end}  # retention period
            c["extension"] = [{"url": f"{m.LOCAL}/consent-recorder", "valueReference": m.ref(rec)},
                              {"url": f"{m.LOCAL}/right-to-withdraw-explained", "valueBoolean": True}]
            deps.fhir().create(c)
    return consent(pid)


@router.post("/patients/{pid}/withdraw")
def withdraw_consent(pid: deps.FhirId, request: Request, u: dict = Depends(CLINICIANS)):
    """Erase images (crypto-shredding), keep signed report text, record the withdrawal."""
    read_patient(pid)
    request.state.audit = "written"  # withdraw() records its own "D" AuditEvent
    withdraw(deps.fhir(), deps.keys(), pid, u["username"], u["role"])
    return consent(pid)
