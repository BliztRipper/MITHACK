"""Shared services, sessions and role checks (design D10).

Services are created on first use; routes call deps.fhir() / deps.keys() / deps.model() at request time so
tests can swap them with monkeypatch.
"""
import functools
import math
import os
import pathlib
import threading
import time
from collections import defaultdict, deque
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
DEMO = os.environ.get("DEMO_MODE") == "1"  # public demo (live-demo-deployment): curated photos only, rate limits
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
    d = yaml.safe_load(pathlib.Path(os.environ.get("USERS_FILE", API / "users.yaml")).read_text())
    return d["users"] if DEMO or not d.get("demo_only") else {}  # published demo accounts: demo mode only


if DEMO and not yaml.safe_load(pathlib.Path(os.environ.get("USERS_FILE", API / "users.yaml")).read_text()).get("demo_only"):
    raise RuntimeError("DEMO_MODE=1 needs a demo_only users file (USERS_FILE=users.demo.yaml); "
                       "refusing to start with real accounts on the public demo")


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


class Limiter:
    """Sliding window: at most n hits per window seconds per client (design D5, demo mode only).
    shortcut: in-process memory, right for one API machine; move to Redis if the API ever scales out."""
    MAX_KEYS = 10_000  # forged client keys must not grow memory without bound

    def __init__(self, n: int, window: float):
        self.n, self.window, self.hits, self.lock = n, window, defaultdict(deque), threading.Lock()

    def wait(self, key: str) -> int:
        """Seconds until key may act again (0 = now)."""
        with self.lock:
            q, now = self.hits[key], time.monotonic()
            while q and q[0] <= now - self.window:
                q.popleft()
            if not q:
                del self.hits[key]  # idle clients cost no memory
                return 0
            return 0 if len(q) < self.n else math.ceil(q[0] + self.window - now)

    def hit(self, key: str):
        with self.lock:
            now = time.monotonic()
            self.hits[key].append(now)
            if len(self.hits) > self.MAX_KEYS:
                for k in [k for k, q in self.hits.items() if not q or q[-1] <= now - self.window]:
                    del self.hits[k]
                while len(self.hits) > self.MAX_KEYS:  # still over: drop the oldest-inserted keys
                    del self.hits[next(iter(self.hits))]


LOGIN_FAILS, CASES = Limiter(10, 10 * 60), Limiter(30, 60 * 60)


def client_ip(request: Request) -> str:
    """The first X-Forwarded-For hop (Vercel sets it), else the socket peer."""
    # shortcut: direct requests to the Space can forge X-Forwarded-For, the daily reset bounds the damage; upgrade to a Vercel shared-secret header if abuse appears
    return (request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown"))


def throttle(lim: Limiter, request: Request) -> str | None:
    """Demo mode: 429 with Retry-After once this client used up lim. Returns the client key (None outside demo)."""
    if not DEMO:
        return None
    key = client_ip(request)
    if s := lim.wait(key):
        raise HTTPException(429, "too many requests: try again later", headers={"Retry-After": str(s)})
    return key


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
