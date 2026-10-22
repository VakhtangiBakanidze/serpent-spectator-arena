"""Auth router: /auth/signup, /auth/login, /auth/logout, /auth/me"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .. import database as db
from ..auth import (
    clear_session_cookie,
    create_session,
    get_current_user,
    set_session_cookie,
)
from ..models import LogInRequest, SignUpRequest, User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
def signup(body: SignUpRequest, response: Response) -> User:
    if body.email in db.users:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Also check username uniqueness
    for record in db.users.values():
        if record["username"] == body.username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    hashed = db.hash_password(body.password)
    db.users[body.email] = {
        "username": body.username,
        "email": body.email,
        "hashed_password": hashed,
    }

    token = create_session(body.username)
    set_session_cookie(response, token)

    return User(username=body.username, email=body.email)


@router.post("/login", response_model=User, status_code=status.HTTP_200_OK)
def login(body: LogInRequest, response: Response) -> User:
    record = db.users.get(body.email)
    if not record or not db.verify_password(body.password, record["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_session(record["username"])
    set_session_cookie(response, token)

    return User(username=record["username"], email=record["email"])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> None:
    # Remove all sessions for this user
    tokens_to_remove = [t for t, u in db.sessions.items() if u == current_user.username]
    for t in tokens_to_remove:
        db.sessions.pop(t, None)
    clear_session_cookie(response)


@router.get("/me", response_model=User)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
