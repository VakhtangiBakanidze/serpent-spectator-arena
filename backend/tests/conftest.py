"""Shared pytest fixtures using an in-memory SQLite database."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db, reset_db
from backend.main import create_app

# Use an in-memory SQLite database for isolated and fast tests
TEST_DB_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset the database schema and seed live players before every test."""
    reset_db(test_engine)
    yield
    reset_db(test_engine)


@pytest.fixture()
def client() -> TestClient:
    app = create_app()

    def override_get_db():
        db: Session = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_client(client: TestClient) -> TestClient:
    """A TestClient that is already logged in as testuser."""
    payload = {"username": "testuser", "email": "test@example.com", "password": "secret123"}
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 201
    return client
