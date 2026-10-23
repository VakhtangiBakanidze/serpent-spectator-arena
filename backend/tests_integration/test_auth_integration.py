"""Integration tests for authentication workflows with SQLite database."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database import SessionDB, UserDB, verify_password


def test_auth_full_lifecycle(client: TestClient, db_session: Session):
    signup_data = {
        "username": "shadowsnake",
        "email": "shadow@snake.dev",
        "password": "shadowpassword123",
    }

    # 1. Sign up
    res = client.post("/auth/signup", json=signup_data)
    assert res.status_code == 201
    user_info = res.json()
    assert user_info["username"] == "shadowsnake"
    assert user_info["email"] == "shadow@snake.dev"
    assert "session" in res.cookies

    # 2. Verify record in SQLite database directly
    db_user = db_session.query(UserDB).filter_by(username="shadowsnake").first()
    assert db_user is not None
    assert db_user.email == "shadow@snake.dev"
    assert db_user.hashed_password != signup_data["password"]
    assert verify_password(signup_data["password"], db_user.hashed_password) is True

    # Verify session in SQLite database
    cookie_token = res.cookies["session"]
    db_sess = db_session.query(SessionDB).filter_by(token=cookie_token).first()
    assert db_sess is not None
    assert db_sess.username == "shadowsnake"

    # 3. Access protected /auth/me
    me_res = client.get("/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "shadowsnake"

    # 4. Clear client cookies and verify unauthorized
    client.cookies.clear()
    unauth_res = client.get("/auth/me")
    assert unauth_res.status_code == 401

    # 5. Log in with credentials
    login_res = client.post("/auth/login", json={
        "email": "shadow@snake.dev",
        "password": "shadowpassword123",
    })
    assert login_res.status_code == 200
    assert "session" in login_res.cookies

    # 6. Log out and verify session removal in SQLite
    logout_res = client.post("/auth/logout")
    assert logout_res.status_code == 204

    db_session.expire_all()
    remaining_sessions = db_session.query(SessionDB).filter_by(username="shadowsnake").all()
    assert len(remaining_sessions) == 0

    # Verify /auth/me fails after logout
    post_logout_me = client.get("/auth/me")
    assert post_logout_me.status_code == 401


def test_auth_duplicate_constraints(client: TestClient):
    signup_data = {
        "username": "firstuser",
        "email": "first@snake.dev",
        "password": "password123",
    }
    res1 = client.post("/auth/signup", json=signup_data)
    assert res1.status_code == 201

    # Duplicate email
    res_dup_email = client.post("/auth/signup", json={
        "username": "seconduser",
        "email": "first@snake.dev",
        "password": "password123",
    })
    assert res_dup_email.status_code == 409
    assert "Email already registered" in res_dup_email.json()["detail"]

    # Duplicate username
    res_dup_username = client.post("/auth/signup", json={
        "username": "firstuser",
        "email": "other@snake.dev",
        "password": "password123",
    })
    assert res_dup_username.status_code == 409
    assert "Username already taken" in res_dup_username.json()["detail"]

