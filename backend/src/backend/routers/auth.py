"""Auth router: /auth/signup, /auth/login, /auth/logout, /auth/me"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import database as db
from ..auth import (
    clear_session_cookie,
    create_session,
    get_current_user,
    set_session_cookie,
)
from ..database import SessionDB, UserDB, get_db
from ..models import LogInRequest, SignUpRequest, User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
def signup(
    body: SignUpRequest,
    response: Response,
    db_session: Session = Depends(get_db),
) -> User:
    # Check email uniqueness
    if db_session.query(UserDB).filter(UserDB.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Check username uniqueness
    if db_session.query(UserDB).filter(UserDB.username == body.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    hashed = db.hash_password(body.password)
    user_record = UserDB(
        username=body.username,
        email=body.email,
        hashed_password=hashed,
    )
    db_session.add(user_record)
    db_session.commit()

    token = create_session(db_session, body.username)
    set_session_cookie(response, token)

    return User(username=body.username, email=body.email)


@router.post("/login", response_model=User, status_code=status.HTTP_200_OK)
def login(
    body: LogInRequest,
    response: Response,
    db_session: Session = Depends(get_db),
) -> User:
    user_record = db_session.query(UserDB).filter(UserDB.email == body.email).first()
    if not user_record or not db.verify_password(body.password, user_record.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_session(db_session, user_record.username)
    set_session_cookie(response, token)

    return User(username=user_record.username, email=user_record.email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> None:
    # Remove sessions for this user
    db_session.query(SessionDB).filter(SessionDB.username == current_user.username).delete()
    db_session.commit()
    clear_session_cookie(response)


@router.get("/me", response_model=User)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
