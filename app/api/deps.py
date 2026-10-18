"""Shared services, sessions and role checks (design D10).

Services are created on first use; routes call deps.fhir() / deps.keys() / deps.model() at request time so
tests can swap them with monkeypatch.
"""
import functools
import os
import pathlib
from typing import Annotated

import bcrypt
import yaml
from fastapi import Depends, HTTPException, Path, Request
from pydantic import StringConstraints
from itsdangerous import BadSignature, URLSafeTimedSerializer

from fhir import mapping as m
from fhir.client import FhirClient
from fhir.crypto import KeyStore, master_key_from_env

API = pathlib.Path(__file__).resolve().parent
COOKIE, IDLE = "session", 30 * 60  # 30-minute sliding expiry (spec: idle session expires)
ROLES = ("gp", "reviewer", "admin")
ID_PATTERN = r"^[A-Za-z0-9\-.]{1,64}$"  # FHIR logical id; blocks "a,Patient/b" OR-injection into searches
FhirId = Annotated[str, Path(pattern=ID_PATTERN)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


def _secret():
    s = os.environ.get("SESSION_SECRET")
    if not s:
        raise RuntimeError("SESSION_SECRET is not set; refusing to start")
    return s


SIGNER = URLSafeTimedSerializer(_secret(), salt="session")
_DUMMY = bcrypt.hashpw(b"x", bcrypt.gensalt())  # same bcrypt cost for unknown users (no username probing by timing)


@functools.cache
def users() -> dict:
    return yaml.safe_load(pathlib.Path(os.environ.get("USERS_FILE", API / "users.yaml")).read_text())["users"]


def check_password(username: str, password: str) -> dict | None:
    u = users().get(username)
    ok = bcrypt.checkpw(password.encode(), u["hash"].encode() if u else _DUMMY)
    return u if u and ok else None


def set_session(response, username: str):
    response.set_cookie(COOKIE, SIGNER.dumps(username), max_age=IDLE, httponly=True, samesite="lax",
                        secure=os.environ.get("COOKIE_SECURE") == "1")  # 1 behind HTTPS; the local demo is http


def user(request: Request) -> dict:
    """401 unless the cookie is validly signed and less than IDLE seconds old (each request re-issues it)."""
    tok = request.cookies.get(COOKIE)
    try:
        name = SIGNER.loads(tok, max_age=IDLE) if tok else None
    except BadSignature:  # includes SignatureExpired
        name = None
    u = users().get(name) if name else None
    if not u:
        raise HTTPException(401, "not signed in")
    request.state.user = {"username": name, "role": u["role"], "name": u["name"]}
    return request.state.user


def role(*allowed: str):
    def dep(u: dict = Depends(user)) -> dict:
        if u["role"] not in allowed:
            raise HTTPException(403, "your role cannot do this")
        return u
    return dep


@functools.cache
def fhir() -> FhirClient:
    return FhirClient()


def practitioner(u: dict) -> str:
    """The signed-in user's Practitioner reference (conditional create: one per username)."""
    ident = f"{m.LOCAL}/user|{u['username']}"
    r = fhir().create(m.practitioner(u["username"], u["name"], u["username"]), if_none_exist=f"identifier={ident}")
    return f"Practitioner/{r['id']}"


def may_read(u: dict, rep: dict) -> bool:
    """Spec "Role-based permissions": a GP reads (and signs) the cases they created; a reviewer reads their own
    cases and ESCALATE cases from anyone; admins never read cases (role checks keep them out first)."""
    if u["role"] not in ("gp", "reviewer"):
        return False
    if rep["performer"][0]["reference"] == practitioner(u):
        return True
    escalated = any(c["coding"][0]["code"] == "ESCALATE" for c in rep.get("conclusionCode", []))
    return u["role"] == "reviewer" and escalated


@functools.cache
def keys() -> KeyStore:
    return KeyStore(master_key_from_env())


@functools.cache
def model():
    """None when CRAO_MODEL is unset or missing: results then say "no model loaded"."""
    path = os.environ.get("CRAO_MODEL")
    if not path:  # no torch import: the demo image has none
        return None
    from vision import crao_model
    return crao_model.load(path)
