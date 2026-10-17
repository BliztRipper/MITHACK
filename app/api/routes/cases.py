"""Cases: create (analysis + preliminary save) and encrypted image access."""
import base64
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response

import deps
from fhir.client import FhirError
from fhir.crypto import KeyDestroyed

router = APIRouter(tags=["cases"])
CLINICIANS = deps.role("gp", "reviewer")  # admins never open images (spec: admin cannot view images)
log = logging.getLogger("api")


def analysis_error(case_id: str, e: Exception) -> HTTPException:
    """Log case id and error only (no image bytes, no names); the client gets a generic 5xx, never str(e),
    which can hold server paths, and never "retake": this is our failure, not the photo's."""
    log.error("analysis failed case=%s error=%s: %s", case_id, type(e).__name__, e)
    return HTTPException(500, "analysis service error")


@router.get("/media/{mid}")
def media(mid: str, request: Request, u: dict = Depends(CLINICIANS)):
    request.state.audit = ("R", f"Media/{mid}")
    try:
        med = deps.fhir().read("Media", mid)
    except FhirError as e:
        raise HTTPException(404 if e.status in (404, 410) else 502, "image not found") from None
    kid = next(e["valueString"] for x in med.get("extension", []) for e in x["extension"] if e["url"] == "keyId")
    try:
        png = deps.keys().decrypt(med["subject"]["reference"], base64.b64decode(med["content"]["data"]), kid)
    except KeyDestroyed:
        raise HTTPException(410, "image erased (consent withdrawn)") from None
    return Response(png, media_type="image/png", headers={"Cache-Control": "no-store"})
