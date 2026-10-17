import pytest

from fhir import mapping as m
from fhir import seed

pytestmark = pytest.mark.fhir


def test_seed_idempotent_20_patients(fhir):
    seed.run(fhir)
    seed.run(fhir)
    pats = fhir.search("Patient", **{"identifier": m.SEED_SYSTEM + "|"})  # all seed-tagged
    assert len(pats) == 20
    ages = sorted(2026 - int(p["birthDate"][:4]) for p in pats)
    assert ages[0] >= 30 and ages[-1] <= 79
    finals = [r for r in fhir.search("DiagnosticReport") if r["status"] == "final"]
    assert len(finals) == 3
    assert len(fhir.search("Observation", code=m.LOINC + "|8480-6")) == 20
    assert all(any("฀" <= c <= "๿" for c in p["name"][0]["family"]) for p in pats)
