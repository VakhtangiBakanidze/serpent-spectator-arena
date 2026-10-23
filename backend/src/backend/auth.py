"""Authentication helpers: session management and dependency injection."""
from __future__ import annotations

import secrets

from fastapi import Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from . import database as db
from .database import SessionDB, UserDB, get_db
from .models import User

SESSION_COOKIE_NAME = "session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 1 week


def create_session(db_session: Session, username: str) -> str:
    token = secrets.token_urlsafe(32)
    session_record = SessionDB(token=token, username=username)
    db_session.add(session_record)
    db_session.commit()
    return token


def delete_session(db_session: Session, token: str) -> None:
    db_session.query(SessionDB).filter(SessionDB.token == token).delete()
    db_session.commit()


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


def get_current_user(
    session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    db_session: Session = Depends(get_db),
) -> User:
    """FastAPI dependency – resolves session cookie to User or raises 401."""
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session_record = db_session.query(SessionDB).filter(SessionDB.token == session).first()
    if not session_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    user_record = db_session.query(UserDB).filter(UserDB.username == session_record.username).first()
    if not user_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return User(username=user_record.username, email=user_record.email)
