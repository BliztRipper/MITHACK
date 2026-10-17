"""5.2: one AuditEvent per patient-data request; no image bytes or names in logs (spec: patient-data-protection)."""
import logging

import pytest

from conftest import login
from fhir import mapping as m
from vision.segment import SegmentationError

PNG = b"\x89PNG\r\n\x1a\n" + b"fake-fundus-pixels" * 40


def audits(fhir, entity):
    return fhir.search("AuditEvent", entity=entity)


@pytest.mark.fhir
def test_opening_an_image_writes_one_read_audit_event(live, fhir, patient, caplog):
    import deps
    blob, kid = deps.keys().encrypt(patient, PNG)
    pref = f"Patient/{patient}"
    enc = fhir.create(m.encounter(pref, "screening", deps.practitioner({"username": "gp1", "name": "Test gp"})))["id"]
    mid = fhir.create(m.media(pref, f"Encounter/{enc}", blob, kid))["id"]
    prac = deps.practitioner({"username": "gp1", "name": "Test gp"})
    fhir.create(m.diagnostic_report(pref, f"Encounter/{enc}", "preliminary", "x", [], [f"Media/{mid}"], prac))
    login(live, "gp1")
    with caplog.at_level(logging.DEBUG):
        r = live.get(f"/media/{mid}")
    assert r.status_code == 200 and r.content == PNG and r.headers["content-type"] == "image/png"
    [ev] = audits(fhir, f"Media/{mid}")
    assert ev["action"] == "R" and ev["outcome"] == "0" and ev["recorded"]
    assert ev["agent"][0]["who"]["display"] == "gp1" and ev["agent"][0]["role"][0]["text"] == "gp"
    logs = caplog.text
    assert "Somsri" not in logs and "Testapi" not in logs and "fake-fundus" not in logs
    assert "Somsri" not in str(ev)


@pytest.mark.fhir
def test_refused_request_is_audited_as_a_failure(live, fhir, patient):
    start = m.now()
    login(live, "admin1")
    assert live.get("/media/999999").status_code == 403
    [ev] = [a for a in fhir.search("AuditEvent", date=f"ge{start}") if a["agent"][0]["who"]["display"] == "admin1"]
    assert ev["outcome"] == "4" and ev["entity"][0]["what"]["display"] == "/media/999999"


def test_audit_has_no_update_or_delete_route(api):
    login(api, "admin1")
    for method in ("put", "patch", "delete"):
        assert getattr(api, method)("/audit/1").status_code in (404, 405)


def test_each_patient_data_request_writes_exactly_one_event(api):
    login(api, "admin1")
    api.get("/media/5")
    api.get("/auth/me")  # not patient data: no event
    assert [e["entity"][0]["what"]["display"] for e in api.store.created] == ["/media/5"]


def test_analysis_exception_log_line_has_only_case_id_and_error(caplog):
    from routes.cases import analysis_error
    with caplog.at_level(logging.ERROR, logger="api"):
        exc = analysis_error("case-123", SegmentationError("AutoMorph run.sh exited 1"))
    [rec] = caplog.records
    assert rec.getMessage() == "analysis failed case=case-123 error=SegmentationError: AutoMorph run.sh exited 1"
    assert exc.status_code == 500 and exc.detail == "analysis service error"


class Store:
    def __init__(self, media):
        self.media, self.created = media, []

    def read(self, rtype, rid):
        return self.media

    def search(self, rtype, **kw):
        return [{"performer": [{"reference": "Practitioner/7"}]}]

    def create(self, r, if_none_exist=None):
        self.created.append(r)
        return {**r, "id": "7"}  # the gp1 Practitioner is "7", so the case is readable


def test_media_without_key_id_is_a_clean_audited_500(api, monkeypatch):
    import deps
    s = Store({"resourceType": "Media", "subject": {"reference": "Patient/1"}, "content": {"data": ""}})
    monkeypatch.setattr(deps, "fhir", lambda: s)
    login(api, "gp1")
    r = api.get("/media/5")
    assert r.status_code == 500 and r.json() == {"detail": "image record is malformed"}
    assert [e["outcome"] for e in s.created if e["resourceType"] == "AuditEvent"] == ["8"]


def test_unhandled_exception_is_still_audited(api, monkeypatch):
    import deps
    from fastapi.testclient import TestClient
    import main
    s = Store({"resourceType": "Media", "subject": {"reference": "Patient/1"}, "content": {"data": ""},
               "extension": [{"url": m.ENC_EXT, "extension": [{"url": "keyId", "valueString": "k"}]}]})
    monkeypatch.setattr(deps, "fhir", lambda: s)

    class Boom:
        def decrypt(self, *a):
            raise ValueError("unexpected")
    monkeypatch.setattr(deps, "keys", lambda: Boom())
    c = TestClient(main.app, raise_server_exceptions=False)
    login(c, "gp1")
    assert c.get("/media/5").status_code == 500
    [ev] = [e for e in s.created if e["resourceType"] == "AuditEvent"]
    assert ev["outcome"] == "8" and ev["entity"][0]["what"]["reference"] == "Media/5"
