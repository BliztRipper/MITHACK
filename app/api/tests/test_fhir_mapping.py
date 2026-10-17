import pytest

from fhir import mapping as m
from fhir.client import FhirError

pytestmark = pytest.mark.fhir
CASE_TYPES = {"Encounter", "Media", "Observation", "RiskAssessment", "Condition", "DiagnosticReport", "Provenance", "AuditEvent"}


@pytest.fixture
def actors(fhir, request):
    made = []
    request.addfinalizer(lambda: [fhir.delete(t, i) for t, i in reversed(made)])
    def mk(res):
        r = fhir.create(res); made.append((r["resourceType"], r["id"])); return f"{r['resourceType']}/{r['id']}"
    refs = dict(
        patient=mk(m.patient("TEST-MAP-1", "Testmap", "Somchai", "male", "1970-01-01")),
        prac=mk(m.practitioner("test-gp", "Testprac", "Gp")),
        dev=mk(m.device("retina-test-model", "0.0.1", "2026-10-01")),
    )
    refs["consents"] = [mk(m.consent(refs["patient"], "care")), mk(m.consent(refs["patient"], "model-improvement"))]
    org = mk({"resourceType": "Organization", "name": "test-site"})
    refs["flag"] = mk(m.flag(org, refs["dev"], "drift", "test drift"))
    return refs


def _save_and_cleanup(fhir, entries, want):
    resp = fhir.transaction(entries)
    created = [e["response"]["location"] for e in resp["entry"]]
    try:
        types = {l.split("/")[-3] if "_history" in l else l.split("/")[-2] for l in created}
        assert want <= types
        return resp
    finally:
        for l in created:
            parts = l.split("/")
            i = parts.index("_history") - 1 if "_history" in parts else len(parts) - 1
            fhir.delete(parts[i - 1], parts[i])


def test_screening_bundle_accepted(fhir, actors):
    a = actors
    es, rep = m.case_bundle(
        "screening", a["patient"], a["prac"], a["dev"], [("fundus", b"\x01" * 32, "k1"), ("overlay", b"\x02" * 32, "k1")],
        {"sbp": 140, "dbp": 90, "tc": 220, "hdl": 45, "ldl": 140, "smoking": "never", "arcus_senilis": True,
         "quality_score": 0.9, "vessel_avr": 0.6},
        risks=[("Thai CV Risk (lab)", 12.5), ("PCE (white)", 15.0)], conditions=[("Hypertension", "hypertension")],
        conclusion="Moderate risk")
    media = {e["resource"]["type"]["coding"][0]["code"]: e["resource"] for e in es if e["resource"]["resourceType"] == "Media"}
    assert media["overlay"]["device"] == {"reference": a["dev"]} and "device" not in media["fundus"]
    resp = _save_and_cleanup(fhir, es, CASE_TYPES)
    assert all(e["response"]["status"].startswith("201") for e in resp["entry"])


def test_emergency_bundle_accepted(fhir, actors):
    a = actors
    es, rep = m.case_bundle(
        "emergency", a["patient"], a["prac"], a["dev"], [("fundus", b"\x03" * 32, "k1")],
        {"crao_probability": 0.87, "quality_score": 0.8}, status="preliminary", conclusion="ESCALATE")
    _save_and_cleanup(fhir, es, CASE_TYPES - {"Condition", "RiskAssessment"})


def test_iris_rejects_invalid_resource(fhir, actors):
    bad = m.observation("sbp", 120, actors["patient"], actors["patient"])
    bad["status"] = "bogus"
    with pytest.raises(FhirError):
        fhir.create(bad)


def test_height_waist_are_loinc():
    assert m.OBS_CODES["height"][:2] == (m.LOINC, "8302-2") and m.OBS_CODES["waist"][:2] == (m.LOINC, "8280-0")


def test_loinc_codes_exact():
    assert {k: m.OBS_CODES[k][1] for k in ("sbp", "dbp", "tc", "hdl", "ldl", "smoking")} == {
        "sbp": "8480-6", "dbp": "8462-4", "tc": "2093-3", "hdl": "2085-9", "ldl": "18262-6", "smoking": "72166-2"}
