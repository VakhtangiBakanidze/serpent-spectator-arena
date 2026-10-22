"""Authentication helpers: session management and dependency injection."""
from __future__ import annotations

import secrets

from fastapi import Cookie, HTTPException, Response, status

from . import database as db
from .models import User

SESSION_COOKIE_NAME = "session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 1 week


def create_session(username: str) -> str:
    token = secrets.token_urlsafe(32)
    db.sessions[token] = username
    return token


def delete_session(token: str) -> None:
    db.sessions.pop(token, None)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, httponly=True, samesite="lax")


def get_current_user(session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> User:
    """FastAPI dependency – resolves session cookie to User or raises 401."""
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    username = db.sessions.get(session)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    # Find the user record
    for record in db.users.values():
        if record["username"] == username:
            return User(username=record["username"], email=record["email"])

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
