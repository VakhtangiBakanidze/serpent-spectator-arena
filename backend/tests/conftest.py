"""Shared pytest fixtures."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend import database as db
from backend.main import create_app


@pytest.fixture(autouse=True)
def reset_database():
    """Reset the mock DB before every test."""
    db.reset_db()
    yield
    db.reset_db()


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture()
def auth_client(client: TestClient):
    """A TestClient that is already logged in as testuser."""
    payload = {"username": "testuser", "email": "test@example.com", "password": "secret123"}
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 201
    return client

