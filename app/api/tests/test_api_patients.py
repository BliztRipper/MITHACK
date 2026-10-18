"""5.3: patient search/detail and consent record/check/withdraw (specs: fhir-clinical-records, patient-data-protection)."""
import pytest

from conftest import login

pytestmark = pytest.mark.fhir
CONSENT = {"care": True, "model_improvement": False, "retention_years": 10, "right_to_withdraw_explained": True}


def test_patient_record_needs_a_session(live, patient):
    r = live.get(f"/patients/{patient}")
    assert r.status_code == 401 and "Somsri" not in r.text


def test_search_by_name_and_hospital_number(live, patient):
    login(live, "gp1")
    r = live.post("/patients/search", json={"q": "Testapi"})
    assert "Testapi" not in str(r.request.url)  # names travel in the body, never the URL (access logs)
    by_name = r.json()
    assert patient in [p["id"] for p in by_name]
    hn = next(p["hn"] for p in by_name if p["id"] == patient)
    assert [p["id"] for p in live.post("/patients/search", json={"q": hn}).json()] == [patient]
    assert live.post("/patients/search", json={"q": "  "}).status_code == 422


def test_admin_cannot_search_patients(live):
    login(live, "admin1")
    assert live.post("/patients/search", json={"q": "x"}).status_code == 403


def test_seeded_patient_shows_prior_signed_screening_and_dated_vitals(live, fhir):
    """Seed patient HN-0001 has a prior signed screening (spec: prior results visible)."""
    from fhir import mapping as m
    [p] = fhir.search("Patient", identifier=f"{m.MRN}|HN-0001")
    login(live, "gp1")
    d = live.get(f"/patients/{p['id']}").json()
    assert d["patient"]["hn"] == "HN-0001"
    [prior] = [c for c in d["cases"] if c["status"] == "final"]
    assert prior["mode"] == "screening" and prior["date"].startswith("2026-03-10") and "PCE" in prior["result"]
    # 2026-09-01 seed vitals: within 12 months of today (2026-10-17) -> pre-filled with their dates
    assert d["latest"]["sbp"]["value"] > 0 and d["latest"]["sbp"]["date"].startswith("2026-09-01")


def test_consent_record_check_and_withdraw(live, fhir, patient):
    login(live, "gp1")
    assert live.get(f"/patients/{patient}/consent").json() == {"care": False, "model_improvement": False}
    assert live.post(f"/patients/{patient}/consent", json={**CONSENT, "right_to_withdraw_explained": False}).status_code == 422
    r = live.post(f"/patients/{patient}/consent", json={**CONSENT, "model_improvement": True})
    assert r.json() == {"care": True, "model_improvement": True}
    [c, _] = fhir.search("Consent", patient=f"Patient/{patient}")
    assert c["dateTime"] and c["provision"]["period"]["end"]  # timestamp and retention period
    assert c["extension"][0]["valueReference"]["reference"].startswith("Practitioner/")  # recorder
    assert live.post(f"/patients/{patient}/withdraw").json() == {"care": False, "model_improvement": False}
    assert {x["status"] for x in fhir.search("Consent", patient=f"Patient/{patient}")} == {"inactive"}
    assert len(fhir.search("AuditEvent", entity=f"Patient/{patient}", action="D")) == 1  # one event for the withdrawal


def test_no_route_takes_identifiers_in_the_query_string_and_access_log_is_off():
    import main
    query = {p["name"] for ops in main.app.openapi()["paths"].values() for op in ops.values()
             for p in op.get("parameters", []) if p["in"] == "query"}
    assert query <= {"days", "lang"}  # nothing that can hold a name, HN or date of birth
    assert main.RUN["access_log"] is False


def test_consent_after_withdrawal_is_409_not_a_new_consent(live, fhir, patient):
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    live.post(f"/patients/{patient}/withdraw")
    r = live.post(f"/patients/{patient}/consent", json=CONSENT)
    assert r.status_code == 409 and "re-enrolment is not supported" in r.json()["detail"]
    assert live.get(f"/patients/{patient}/consent").json()["care"] is False


def test_patient_view_lists_only_cases_the_user_may_open(live, fhir, patient, monkeypatch):
    import json
    import deps
    from test_api_cases import SCREENING, fake_seg, post
    from vision import segment
    monkeypatch.setattr(segment, "segment", fake_seg)
    monkeypatch.setattr(deps, "model", lambda: None)
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    rid = post(live, "screening", json.dumps(SCREENING), pid=patient).json()["report_id"]
    assert [c["report_id"] for c in live.get(f"/patients/{patient}").json()["cases"]] == [rid]
    login(live, "gp2")
    assert live.get(f"/patients/{patient}").json()["cases"] == []


def test_list_all_patients_only_in_demo_mode(live, patient, monkeypatch):
    """Demo dropdown: GET /patients lists every patient by HN; outside demo mode it does not exist."""
    import deps
    login(live, "gp1")
    assert live.get("/patients").status_code == 404
    monkeypatch.setattr(deps, "DEMO", True)
    rows = live.get("/patients").json()
    assert patient in [p["id"] for p in rows]
    hns = [p["hn"] for p in rows if p["hn"]]
    assert hns == sorted(hns)
