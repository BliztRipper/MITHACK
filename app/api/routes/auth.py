"""Login, logout and the signed-in user (design D10)."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

import deps

router = APIRouter(tags=["auth"])


class Login(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def login(body: Login, request: Request, response: Response):
    key = deps.throttle(deps.LOGIN_FAILS, request)
    u = deps.check_password(body.username, body.password)
    if not u:
        if key:
            deps.LOGIN_FAILS.hit(key)
        raise HTTPException(401, "wrong username or password")
    deps.set_session(response, body.username)
    return {"username": body.username, "role": u["role"], "name": u["name"]}


@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(deps.COOKIE)
    return {"ok": True}


@router.get("/auth/me")
def me(u: dict = Depends(deps.user)):
    return u
