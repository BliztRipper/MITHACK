import pytest

from fhir.client import FhirClient, FhirUnavailable


def pytest_configure(config):
    config.addinivalue_line("markers", "fhir: needs a running IRIS FHIR server (skipped if unreachable)")


@pytest.fixture(scope="session")
def fhir():
    c = FhirClient(timeout=60)
    try:
        c.health_check()
    except FhirUnavailable:
        pytest.skip("IRIS FHIR server unreachable (cd app/fhir && docker compose up -d)")
    return c
