"""5.1: login/logout, signed HTTP-only cookie with 30-minute sliding expiry, roles (spec: patient-data-protection)."""
import time

import pytest

import deps
from conftest import login


def test_login_sets_signed_http_only_cookie(api):
    r = login(api, "gp1")
    assert r.json() == {"username": "gp1", "role": "gp", "name": "Test gp"}
    c = r.headers["set-cookie"].lower()
    assert "httponly" in c and "samesite=lax" in c and "max-age=1800" in c
    assert api.get("/auth/me").json()["role"] == "gp"


def test_wrong_password_and_unknown_user_refused(api):
    assert api.post("/auth/login", json={"username": "gp1", "password": "nope"}).status_code == 401
    assert api.post("/auth/login", json={"username": "ghost", "password": "test-pass"}).status_code == 401


def test_users_file_holds_bcrypt_hashes_only():
    import yaml
    for u in yaml.safe_load((deps.API / "users.yaml").read_text())["users"].values():
        assert u["hash"].startswith("$2b$") and set(u) == {"role", "name", "hash"}
        assert u["role"] in deps.ROLES


@pytest.mark.parametrize("path", ["/auth/me", "/media/1"])
def test_no_session_is_401_with_no_data(api, path):
    r = api.get(path)
    assert r.status_code == 401 and r.json() == {"detail": "not signed in"}


def test_tampered_cookie_is_401(api):
    login(api, "gp1")
    api.cookies.set(deps.COOKIE, api.cookies.get(deps.COOKIE)[:-2] + "xx")
    assert api.get("/auth/me").status_code == 401


def test_idle_session_expires_after_30_minutes(api, monkeypatch):
    login(api, "gp1")
    now = time.time()
    monkeypatch.setattr(time, "time", lambda: now + 29 * 60)
    assert api.get("/auth/me").status_code == 200       # activity re-issues the cookie (sliding)
    monkeypatch.setattr(time, "time", lambda: now + 58 * 60)
    assert api.get("/auth/me").status_code == 200       # 29 min after the last request: still fine
    monkeypatch.setattr(time, "time", lambda: now + 89 * 60)
    assert api.get("/auth/me").status_code == 401       # 31 min idle: sign in again


def test_logout_clears_cookie(api):
    login(api, "gp1")
    api.post("/auth/logout")
    assert api.get("/auth/me").status_code == 401


def test_admin_cannot_open_an_image(api, monkeypatch):
    monkeypatch.setattr(deps, "fhir", lambda: pytest.fail("admin must be refused before any record access"))
    login(api, "admin1")
    assert api.get("/media/1").status_code == 403


def test_missing_session_secret_refuses_to_start(monkeypatch):
    monkeypatch.delenv("SESSION_SECRET")
    with pytest.raises(RuntimeError, match="SESSION_SECRET"):
        deps._secret()
