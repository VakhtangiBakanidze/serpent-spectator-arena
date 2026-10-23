"""Fixtures for integration tests using real SQLite database files."""
from __future__ import annotations

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base, get_db, init_db
from backend.main import create_app


@pytest.fixture()
def integration_engine(tmp_path):
    """Create a temporary real on-disk SQLite database for integration testing."""
    db_file = tmp_path / "test_integration.db"
    db_url = f"sqlite:///{db_file}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    yield engine, db_file

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(integration_engine) -> Generator[Session, None, None]:
    """Provide a direct SQLAlchemy Session to inspect SQLite database state."""
    engine, _ = integration_engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(integration_engine) -> Generator[TestClient, None, None]:
    """TestClient wired to the temporary SQLite integration database."""
    engine, _ = integration_engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    app = create_app()

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()

