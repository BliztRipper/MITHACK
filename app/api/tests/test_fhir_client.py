import pytest

from fhir.client import FhirClient, FhirError, FhirUnavailable

pytestmark = pytest.mark.fhir


def test_patient_round_trip(fhir):
    p = fhir.create({"resourceType": "Patient", "name": [{"family": "TestRoundTrip"}]})
    try:
        assert fhir.read("Patient", p["id"])["name"][0]["family"] == "TestRoundTrip"
        assert any(r["id"] == p["id"] for r in fhir.search("Patient", family="TestRoundTrip"))
        assert len(fhir.history("Patient", p["id"])) >= 1
    finally:
        fhir.delete("Patient", p["id"])


def test_failed_transaction_leaves_nothing(fhir):
    ident = "urn:test|atomic-1"
    good = {"resourceType": "Patient", "identifier": [{"system": "urn:test", "value": "atomic-1"}]}
    bad = {"resourceType": "Observation", "status": "bogus"}  # invalid status, no code
    entries = [
        {"resource": good, "request": {"method": "POST", "url": "Patient"}},
        {"resource": bad, "request": {"method": "POST", "url": "Observation"}},
    ]
    with pytest.raises(FhirError):
        fhir.transaction(entries)
    assert fhir.search("Patient", identifier=ident) == []


def test_unreachable_server_raises(monkeypatch):
    monkeypatch.setenv("FHIR_USER", "x"), monkeypatch.setenv("FHIR_PASS", "x")
    with pytest.raises(FhirUnavailable, match="record store unavailable"):
        FhirClient(base="http://127.0.0.1:9/x", timeout=2).health_check()
