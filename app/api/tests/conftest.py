import base64
import os
import tempfile

import bcrypt
import pytest

# API settings must exist before main/deps are imported (they refuse to start without them).
os.environ.setdefault("SESSION_SECRET", "test-session-secret")
os.environ.setdefault("APP_MASTER_KEY", base64.b64encode(os.urandom(32)).decode())
TEST_PASSWORD = "test-pass"
_h = bcrypt.hashpw(TEST_PASSWORD.encode(), bcrypt.gensalt(4)).decode()
_users = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
_users.write("users:\n" + "".join(f"  {u}:\n    role: {r}\n    name: Test {r}\n    hash: \"{_h}\"\n"
                                  for u, r in (("gp1", "gp"), ("gp2", "gp"), ("oph1", "reviewer"), ("admin1", "admin"))))
_users.close()
os.environ["USERS_FILE"] = _users.name

from fhir.client import FhirClient, FhirUnavailable  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "fhir: needs a running IRIS FHIR server (skipped if unreachable)")


@pytest.fixture(scope="session")
def fhir():
    try:
        c = FhirClient(timeout=60)
        c.health_check()
    except FhirUnavailable:
        pytest.skip("IRIS FHIR server unreachable (cd app/fhir && docker compose up -d)")
    except RuntimeError as e:  # FHIR_USER / FHIR_PASS unset
        pytest.skip(str(e))
    return c


class Recorder:
    """Stand-in record store: keeps created resources (audit events), refuses anything else."""
    def __init__(self):
        self.created = []

    def create(self, r, if_none_exist=None):
        self.created.append(r)
        return {**r, "id": str(len(self.created))}

    def __getattr__(self, name):
        raise AssertionError(f"unexpected record-store call: {name}")


@pytest.fixture
def api(monkeypatch, tmp_path):
    """TestClient with a throwaway key file and a Recorder store (api.store). login(client, user) signs in."""
    from fastapi.testclient import TestClient

    import deps
    from fhir.crypto import KeyStore
    import main
    ks = KeyStore(os.urandom(32), tmp_path / "keys.json")
    monkeypatch.setattr(deps, "keys", lambda: ks)
    c = TestClient(main.app)
    c.store = Recorder()
    monkeypatch.setattr(deps, "fhir", lambda: c.store)
    return c


@pytest.fixture
def live(api, fhir, monkeypatch):
    """The api client wired to the real IRIS store."""
    import deps
    monkeypatch.setattr(deps, "fhir", lambda: fhir)
    api.store = fhir
    return api


def login(client, user):
    r = client.post("/auth/login", json={"username": user, "password": TEST_PASSWORD})
    assert r.status_code == 200, r.text
    return r


SUBJECT_TYPES = ("DiagnosticReport", "RiskAssessment", "Observation", "Condition", "Media", "Encounter")


def purge(fhir, pid):
    """Delete a test patient and everything that points at it (tests only: the API never deletes audit)."""
    pref = f"Patient/{pid}"
    for rep in fhir.search("DiagnosticReport", subject=pref):
        for p in fhir.search("Provenance", target=f"DiagnosticReport/{rep['id']}"):
            fhir.delete("Provenance", p["id"])
    for t in SUBJECT_TYPES:
        for r in fhir.search(t, subject=pref):
            fhir.delete(t, r["id"])
    for c in fhir.search("Consent", patient=pref):
        fhir.delete("Consent", c["id"])
    fhir.delete("Patient", pid)


@pytest.fixture
def patient(fhir, request):
    """A throwaway patient (no consent) and cleanup of it plus the AuditEvents the test wrote."""
    from fhir import mapping as m
    start = m.now()
    pid = fhir.create(m.patient(f"TEST-API-{request.node.name[:20]}", "Testapi", "Somsri", "female", "1960-01-01"))["id"]
    yield pid
    purge(fhir, pid)
    for a in fhir.search("AuditEvent", date=f"ge{start}"):
        if a["agent"][0]["who"].get("display") in ("gp1", "gp2", "oph1", "admin1", "anonymous"):
            fhir.delete("AuditEvent", a["id"])
