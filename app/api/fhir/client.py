"""Thin httpx wrapper over FHIR R4 REST on plain dicts (design D8)."""
import os

import httpx


def _auth():
    u, p = os.environ.get("FHIR_USER"), os.environ.get("FHIR_PASS")
    if not (u and p):
        raise RuntimeError("FHIR_USER and FHIR_PASS must be set (IRIS login, see app/fhir/README.md)")
    return u, p


BASE = os.environ.get("FHIR_BASE", "http://localhost:32783/csp/healthshare/demo/fhir/r4")
_HDR = {"Accept": "application/fhir+json", "Content-Type": "application/fhir+json", "Prefer": "return=representation"}


class FhirUnavailable(Exception):
    """Record store cannot be reached ("record store unavailable")."""


def _issues(r):
    """Only severity:code of each OperationOutcome issue; the body can echo patient data."""
    try:
        return ",".join(f"{i.get('severity')}:{i.get('code')}" for i in r.json().get("issue", []))
    except ValueError:
        return ""


class FhirError(Exception):
    def __init__(self, status, outcome):
        super().__init__(f"FHIR {status}: {outcome}")
        self.status, self.outcome = status, outcome


class FhirClient:
    def __init__(self, base=BASE, timeout=30):
        self.http = httpx.Client(base_url=base.rstrip("/"), headers=_HDR, auth=_auth(), timeout=timeout)

    def _req(self, method, path, **kw):
        try:
            r = self.http.request(method, path, **kw)
        except httpx.TransportError as e:
            raise FhirUnavailable("record store unavailable") from e
        if r.status_code >= 400:
            raise FhirError(r.status_code, _issues(r))
        return r.json() if r.content else {}

    def health_check(self):
        """Start-up check: raises FhirUnavailable unless the server answers /metadata."""
        return self._req("GET", "/metadata", params={"_summary": "true"})["resourceType"] == "CapabilityStatement"

    def read(self, rtype, rid):
        return self._req("GET", f"/{rtype}/{rid}")

    def search(self, rtype, **params):
        """Returns all matching resources (follows next links)."""
        out, bundle = [], self._req("GET", f"/{rtype}", params={"_count": 100, **params})
        while True:
            # skip search.mode "outcome" entries (IRIS adds an OperationOutcome for some parameters)
            out += [e["resource"] for e in bundle.get("entry", []) if e.get("search", {}).get("mode") != "outcome"]
            nxt = next((l["url"] for l in bundle.get("link", []) if l["relation"] == "next"), None)
            if not nxt:
                return out
            bundle = self._req("GET", nxt)

    def create(self, resource, if_none_exist=None):
        h = {"If-None-Exist": if_none_exist} if if_none_exist else {}
        return self._req("POST", f"/{resource['resourceType']}", json=resource, headers=h)

    def update(self, resource):
        return self._req("PUT", f"/{resource['resourceType']}/{resource['id']}", json=resource)

    def transaction(self, entries):
        """entries: list of {resource, request} dicts. All or nothing."""
        return self._req("POST", "/", json={"resourceType": "Bundle", "type": "transaction", "entry": entries})

    def history(self, rtype, rid):
        return [e["resource"] for e in self._req("GET", f"/{rtype}/{rid}/_history").get("entry", []) if "resource" in e]

    def vread(self, rtype, rid, vid):
        return self._req("GET", f"/{rtype}/{rid}/_history/{vid}")

    def delete(self, rtype, rid):
        return self._req("DELETE", f"/{rtype}/{rid}")
