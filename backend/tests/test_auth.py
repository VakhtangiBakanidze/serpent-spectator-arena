"""Tests for /auth endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


SIGNUP_PAYLOAD = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "password123",
}


class TestSignUp:
    def test_signup_success(self, client: TestClient):
        resp = client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert "session" in resp.cookies

    def test_signup_duplicate_email(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        resp = client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        assert resp.status_code == 409

    def test_signup_short_username(self, client: TestClient):
        payload = {**SIGNUP_PAYLOAD, "username": "ab"}
        resp = client.post("/auth/signup", json=payload)
        assert resp.status_code == 422

    def test_signup_short_password(self, client: TestClient):
        payload = {**SIGNUP_PAYLOAD, "password": "abc"}
        resp = client.post("/auth/signup", json=payload)
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        # Clear cookies to simulate fresh login
        client.cookies.clear()
        resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "password123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "alice"
        assert "session" in resp.cookies

    def test_login_wrong_password(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        client.cookies.clear()
        resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "wrongpass"})
        assert resp.status_code == 401

    def test_login_unknown_email(self, client: TestClient):
        resp = client.post("/auth/login", json={"email": "nobody@example.com", "password": "password123"})
        assert resp.status_code == 401


class TestLogout:
    def test_logout_success(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        resp = client.post("/auth/logout")
        assert resp.status_code == 204

    def test_logout_unauthenticated(self, client: TestClient):
        resp = client.post("/auth/logout")
        assert resp.status_code == 401


class TestMe:
    def test_me_authenticated(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        resp = client.get("/auth/me")
        assert resp.status_code == 200
        assert resp.json()["username"] == "alice"

    def test_me_unauthenticated(self, client: TestClient):
        resp = client.get("/auth/me")
        assert resp.status_code == 401
