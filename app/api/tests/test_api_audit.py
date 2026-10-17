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
