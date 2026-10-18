"""Cases: create (analysis + preliminary save) and encrypted image access."""
import base64
import hashlib
import json
import logging
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError

import analysis
import deps
from fhir import mapping as m
from fhir.client import FhirError, FhirUnavailable
from fhir.crypto import ConsentWithdrawn, KeyDestroyed
from routes.patients import WITHDRAWN, consent, read_patient
from vision import quality

router = APIRouter(tags=["cases"])
CLINICIANS = deps.role("gp", "reviewer")  # admins never open images (spec: admin cannot view images)
log = logging.getLogger("api")


def analysis_error(case_id: str, e: Exception) -> HTTPException:
    """Log case id and error only (no image bytes, no names); the client gets a generic 5xx, never str(e),
    which can hold server paths, and never "retake": this is our failure, not the photo's."""
    log.error("analysis failed case=%s error=%s: %s", case_id, type(e).__name__, e)
    return HTTPException(500, "analysis service error")


AI_LABEL = "AI-assisted, not a diagnosis"
NOT_SAVED = "record store unavailable, not saved"
NO_MODEL = "no-model"
DEMO_PHOTO_ONLY = {"code": "demo_photo_only", "message": "this public demo analyses only its demo photos: pick one of them"}
CONSENT_REQUIRED = {"code": "consent_required", "message": "no active consent for retinal image processing"}


class EmergencyInputs(BaseModel):
    hours_since_onset: float | None = Field(None, ge=0, le=24 * 365)  # None = unknown
    sudden_painless_monocular: bool
    gca_symptoms: bool


class ScreeningInputs(BaseModel):
    """Plausibility limits reject typos (e.g. SBP 400, TC 5) and name the accepted range; the narrower
    equation ranges are applied by the rules and give "not valid", never a clamped number."""
    age: int = Field(ge=18, le=110)
    sex: Literal["male", "female"]
    smoking: Literal["never", "former", "current"]
    diabetes: bool = False  # not asked in the form: the retina model is meant to flag it
    sbp: float = Field(ge=60, le=260)
    dbp: float | None = Field(None, ge=30, le=160)
    treated_htn: bool = False  # not asked in the form, same reason
    tc: float = Field(ge=50, le=500)   # required: spec "Risk factor inputs" (PCE needs both)
    hdl: float = Field(ge=10, le=200)
    ldl: float | None = Field(None, ge=10, le=400)
    african_american: bool
    ascvd: bool
    arcus_senilis: bool = False
    clinical_enhancers: list[str] = Field(default_factory=list, max_length=10)


def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def _observations(mode, inputs, img, out) -> dict:
    q = {"quality_score": round(img["quality"]["score"], 3)}
    if mode == "emergency":
        o = {"onset_hours": "unknown" if inputs.hours_since_onset is None else inputs.hours_since_onset,
             "sudden_painless_monocular": inputs.sudden_painless_monocular, "gca_symptoms": inputs.gca_symptoms, **q}
        if img["p"] is not None:
            o["crao_probability"] = round(img["p"], 4)
        return o
    o = {k: getattr(inputs, k) for k in ("sbp", "dbp", "tc", "hdl", "ldl") if getattr(inputs, k) is not None}
    o.update(smoking=inputs.smoking, arcus_senilis=inputs.arcus_senilis, **q)
    if out["measurements"] and out["measurements"]["avr"]["value"] is not None:
        o["vessel_avr"] = round(out["measurements"]["avr"]["value"], 3)
    return o


def _conditions(mode, inputs) -> list:
    if mode != "screening":
        return []
    c = (("diabetes", "Diabetes mellitus"), ("treated_htn", "Hypertension"), ("ascvd", "Atherosclerotic cardiovascular disease"))
    return [(text, key.replace("treated_htn", "hypertension")) for key, text in c if getattr(inputs, key)]


def device(model) -> tuple[dict, str]:
    """The Device for a model version, and its identifier value (conditional create: one per version)."""
    info = model.info() if model else {"model": "none", "version": NO_MODEL, "calibration_date": None}
    ident = f"{info['model']}-{info['version']}"
    d = m.device(f"crao-{info['model']}", info["version"] or "unversioned", info["calibration_date"] or "uncalibrated")
    d["identifier"] = [{"system": f"{m.LOCAL}/device", "value": ident}]
    return d, ident


def save(pid, u, model, fundus, pngs, mode, obs, risks, conditions, conclusion, code, record) -> str:
    """One transaction Bundle (all or nothing): images encrypted first, so only ciphertext reaches FHIR."""
    ks, pref = deps.keys(), f"Patient/{pid}"
    cts = [(k, *ks.encrypt(pid, b)) for k, b in [("fundus", fundus), *((k, pngs[k]) for k in analysis.OVERLAYS if k in pngs)]]
    (d, ident), dev = device(model), m.urn()
    es, rep = m.case_bundle(mode, pref, deps.practitioner(u), dev, cts, obs, risks, conditions,
                            status="preliminary", conclusion=conclusion)
    es = [m.entry(dev, d, f"identifier={m.LOCAL}/device|{ident}")] + \
         [e for e in es if e["resource"]["resourceType"] != "AuditEvent"]  # the middleware writes the one event
    r = next(e["resource"] for e in es if e["fullUrl"] == rep)
    r["category"] = [{"coding": [{"system": m.LOCAL, "code": mode}]}]
    r["conclusionCode"] = [{"coding": [{"system": m.LOCAL, "code": code}]}]
    for link, (kind, _, _) in zip(r.get("media", []), cts):
        link["comment"] = kind  # fundus | vessel | artery_vein | disc | heatmap
    r["presentedForm"] = [{"contentType": "application/json", "title": "analysis", "data": _b64(json.dumps(record).encode())}]
    out = deps.fhir().transaction(es)
    i = next(n for n, e in enumerate(es) if e["fullUrl"] == rep)
    return out["entry"][i]["response"]["location"].split("/_history")[0].rsplit("/", 1)[-1]


@router.post("/cases")
def create_case(request: Request, patient_id: str = Form(pattern=deps.ID_PATTERN), mode: Literal["screening", "emergency"] = Form(),
                inputs: str = Form("{}"), image: UploadFile = File(), u: dict = Depends(CLINICIANS)):
    """mode + inputs (JSON) + image -> quality gate -> segmentation -> Screening risk or Emergency triage ->
    explanation, saved as a preliminary case. If the record store is down the analysis is still returned."""
    if key := deps.throttle(deps.CASES, request):
        deps.CASES.hit(key)
    case_id = str(uuid.uuid4())
    request.state.audit = ("C", f"Patient/{patient_id}")
    try:
        inp = (EmergencyInputs if mode == "emergency" else ScreeningInputs).model_validate_json(inputs)
    except ValidationError as e:
        raise RequestValidationError(e.errors(include_url=False, include_context=False)) from None
    raw = image.file.read(quality.MAX_BYTES + 1)
    model, sha = deps.model(), hashlib.sha256(raw).hexdigest()
    hit = analysis.cache_get(sha, model)
    if deps.DEMO and hit is None:  # before any consent read, decode, encryption or write: nothing of it is kept
        raise HTTPException(422, DEMO_PHOTO_ONLY)
    try:  # fail closed: no verified consent, no image processing (PDPA s.26)
        read_patient(patient_id)  # 404 for an unknown patient
        if not consent(patient_id)["care"]:
            raise HTTPException(403, CONSENT_REQUIRED)
    except FhirUnavailable:
        raise HTTPException(503, "record store unavailable: consent cannot be checked") from None
    try:
        rgb, fundus = quality.intake(raw)
    except quality.Rejected as e:
        raise HTTPException(400, str(e)) from None  # stores nothing
    try:
        img, pngs = hit or analysis.image_stage(rgb, model, features=mode == "screening", crao=mode == "emergency")
    except RuntimeError as e:  # SegmentationError and AutoMorph's plain RuntimeError
        raise analysis_error(case_id, e) from None
    if mode == "emergency":
        out = analysis.emergency(img, pngs, inp.hours_since_onset, inp.sudden_painless_monocular, inp.gca_symptoms, model)
        code = out["triage"]["level"]
    else:
        out = analysis.screening(img, inp)
        band = out.pop("band")
        code = "bypass" if out["risk"]["bypass"] else f"pce-{band}" if band else "not-valid"
    risks = out.pop("risks", [])
    q = img["quality"]
    seg = img["segmentation"]
    result = {"case_id": case_id, "report_id": None, "saved": False, "save_error": None, "status": "preliminary",
              "label": AI_LABEL, "mode": mode, "patient_id": patient_id, "cached": hit is not None,
              "model_version": analysis.version(model) or NO_MODEL,
              "quality": {"accept": q["accept"], "score": q["score"], "reasons": q["reasons"], "parts": q["parts"]},
              "segmentation": None if seg is None else {"disc_found": seg["disc_centre"] is not None,
                                                         "disc_centre": seg["disc_centre"], "disc_diameter": seg["disc_diameter"]},
              "inputs": inp.model_dump(), **out}
    try:
        result["report_id"] = save(patient_id, u, model, fundus, pngs, mode, _observations(mode, inp, img, out), risks,
                                   _conditions(mode, inp), out["conclusion"], code, result)
        result["saved"] = True
        request.state.audit = ("C", f"DiagnosticReport/{result['report_id']}")
    except ConsentWithdrawn:
        raise HTTPException(409, WITHDRAWN) from None
    except (FhirUnavailable, FhirError) as e:  # all-or-nothing transaction: nothing was stored
        log.error("case save failed case=%s error=%s: %s", case_id, type(e).__name__, e)
        result["save_error"] = NOT_SAVED if isinstance(e, FhirUnavailable) else "record store refused the save, not saved"
    result["overlays"] = {k: _b64(pngs[k]) if k in pngs else None for k in analysis.OVERLAYS}
    return result


@router.get("/media/{mid}")
def media(mid: deps.FhirId, request: Request, u: dict = Depends(CLINICIANS)):
    request.state.audit = ("R", f"Media/{mid}")
    try:
        med = deps.fhir().read("Media", mid)
    except FhirError as e:
        raise HTTPException(404 if e.status in (404, 410) else 502, "image not found") from None
    # Fail closed: find the case through the Media's own encounter link, then keep only reports that really
    # list this Media. An image is readable only through a case you may read.
    enc = med.get("encounter", {}).get("reference")
    reps = [r for r in (deps.fhir().search("DiagnosticReport", encounter=enc) if enc else [])
            if f"Media/{mid}" in [x["link"]["reference"] for x in r.get("media", [])]]
    if not any(deps.may_read(u, r) for r in reps):
        raise HTTPException(403, "not one of your cases or an escalated case")
    kid = next((e["valueString"] for x in med.get("extension", []) for e in x.get("extension", [])
                if e["url"] == "keyId"), None)
    if kid is None:  # never serve or guess at an image stored without its encryption metadata
        log.error("media without keyId media=%s", mid)
        raise HTTPException(500, "image record is malformed")
    try:
        png = deps.keys().decrypt(med["subject"]["reference"], base64.b64decode(med["content"]["data"]), kid)
    except KeyDestroyed:
        raise HTTPException(410, "image erased (consent withdrawn)") from None
    return Response(png, media_type="image/png", headers={"Cache-Control": "no-store"})
