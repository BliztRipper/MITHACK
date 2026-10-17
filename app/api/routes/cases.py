"""Cases: create (analysis + preliminary save) and encrypted image access."""
import base64

from fastapi import APIRouter, Depends, HTTPException, Request, Response

import deps
from fhir.client import FhirError
from fhir.crypto import KeyDestroyed

router = APIRouter(tags=["cases"])
CLINICIANS = deps.role("gp", "reviewer")  # admins never open images (spec: admin cannot view images)


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
