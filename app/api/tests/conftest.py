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


@pytest.fixture
def api(monkeypatch, tmp_path):
    """TestClient with a throwaway key file. login(client, user) signs in."""
    from fastapi.testclient import TestClient

    import deps
    from fhir.crypto import KeyStore
    import main
    ks = KeyStore(os.urandom(32), tmp_path / "keys.json")
    monkeypatch.setattr(deps, "keys", lambda: ks)
    return TestClient(main.app)


def login(client, user):
    r = client.post("/auth/login", json={"username": user, "password": TEST_PASSWORD})
    assert r.status_code == 200, r.text
    return r
