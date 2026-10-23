"""Tests for SQLAlchemy database models and utilities."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.database import (
    Base,
    ScoreDB,
    SessionDB,
    UserDB,
    hash_password,
    init_db,
    seed_scores,
    seed_users,
    verify_password,
)


def test_password_hashing():
    pw = "supersecret123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_database_seeding():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(target_engine=engine)

    with Session(engine) as session:
        users = session.query(UserDB).all()
        assert len(users) >= 5
        neonviper = session.query(UserDB).filter_by(username="neonviper").first()
        assert neonviper is not None
        assert neonviper.email == "neonviper@snake.dev"
        assert verify_password("demo123", neonviper.hashed_password) is True

        scores = session.query(ScoreDB).all()
        assert len(scores) >= 10
        # Calling seed again shouldn't duplicate
        seed_users(session)
        seed_scores(session)
        assert len(session.query(UserDB).all()) == len(users)
        assert len(session.query(ScoreDB).all()) == len(scores)


def test_postgres_url_normalization():
    from backend.database import DEFAULT_DB_URL
    import os

    # Test the normalization logic
    pg_url = "postgresql://user:pass@localhost:5432/snake"
    normalized = pg_url.replace("postgresql://", "postgresql+psycopg://", 1)
    assert normalized == "postgresql+psycopg://user:pass@localhost:5432/snake"

    heroku_style = "postgres://user:pass@localhost:5432/snake"
    normalized_heroku = heroku_style.replace("postgres://", "postgresql+psycopg://", 1)
    assert normalized_heroku == "postgresql+psycopg://user:pass@localhost:5432/snake"
