"""SQLAlchemy database setup, models, and in-memory live player simulation."""
from __future__ import annotations

import hashlib
import hmac
import os
import random
import secrets
from datetime import datetime, timezone
from typing import Any, Generator

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .models import Direction, GameState, LivePlayer, Mode, Point, ScoreEntry

# ---------------------------------------------------------------------------
# Database URL & Engine Configuration (Postgres and SQLite)
# ---------------------------------------------------------------------------

DEFAULT_DB_URL = "sqlite:///./serpent.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Normalize PostgreSQL URLs for psycopg 3
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# SQLAlchemy Models
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class SessionDB(Base):
    __tablename__ = "sessions"

    token = Column(String, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class ScoreDB(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    score = Column(Integer, nullable=False)
    mode = Column(String, nullable=False)
    date = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Hash a password using PBKDF2-SHA256."""
    salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260000)
    return f"pbkdf2$sha256${salt}${hashed.hex()}"


def verify_password(plain: str, hashed_value: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    try:
        _, algo, salt, stored_hash = hashed_value.split("$")
        candidate = hashlib.pbkdf2_hmac(algo, plain.encode(), salt.encode(), 260000)
        return hmac.compare_digest(candidate.hex(), stored_hash)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# In-memory ephemeral live players (Snake WebSocket spectator stream)
# ---------------------------------------------------------------------------

GRID_W = 20
GRID_H = 20

live_players: dict[str, dict[str, Any]] = {}


def _make_snake(head_x: int, head_y: int, direction: Direction, length: int) -> list[dict[str, int]]:
    """Build a snake body trailing behind the head in the opposite direction."""
    dx, dy = 0, 0
    if direction == Direction.right:
        dx = -1
    elif direction == Direction.left:
        dx = 1
    elif direction == Direction.down:
        dy = -1
    elif direction == Direction.up:
        dy = 1
    return [
        {"x": (head_x + dx * i) % GRID_W, "y": (head_y + dy * i) % GRID_H}
        for i in range(length)
    ]


def seed_live_players() -> None:
    """Seed 4 fake live players with realistic snake bodies for demo purposes."""
    live_players.clear()
    live_players["bot-1"] = {
        "id": "bot-1",
        "username": "SlitherBot",
        "mode": Mode.walls.value,
        "state": {
            "width": GRID_W,
            "height": GRID_H,
            "snake": _make_snake(8, 5, Direction.right, 5),
            "dir": Direction.right.value,
            "pendingDir": Direction.right.value,
            "food": {"x": 14, "y": 3},
            "score": 0,
            "alive": True,
            "mode": Mode.walls.value,
        },
    }
    live_players["bot-2"] = {
        "id": "bot-2",
        "username": "PhantomSnek",
        "mode": Mode.pass_through.value,
        "state": {
            "width": GRID_W,
            "height": GRID_H,
            "snake": _make_snake(10, 12, Direction.down, 7),
            "dir": Direction.down.value,
            "pendingDir": Direction.down.value,
            "food": {"x": 6, "y": 17},
            "score": 0,
            "alive": True,
            "mode": Mode.pass_through.value,
        },
    }
    live_players["bot-3"] = {
        "id": "bot-3",
        "username": "CobraClaw",
        "mode": Mode.walls.value,
        "state": {
            "width": GRID_W,
            "height": GRID_H,
            "snake": _make_snake(15, 15, Direction.left, 6),
            "dir": Direction.left.value,
            "pendingDir": Direction.left.value,
            "food": {"x": 2, "y": 11},
            "score": 0,
            "alive": True,
            "mode": Mode.walls.value,
        },
    }
    live_players["bot-4"] = {
        "id": "bot-4",
        "username": "NeonViper",
        "mode": Mode.pass_through.value,
        "state": {
            "width": GRID_W,
            "height": GRID_H,
            "snake": _make_snake(3, 17, Direction.up, 4),
            "dir": Direction.up.value,
            "pendingDir": Direction.up.value,
            "food": {"x": 18, "y": 2},
            "score": 0,
            "alive": True,
            "mode": Mode.pass_through.value,
        },
    }


def tick_live_players() -> None:
    """Advance each live player's snake head by one cell."""
    for player in live_players.values():
        state = player["state"]
        if not state["alive"]:
            continue

        head = state["snake"][0]
        direction = state["dir"]
        w, h = state["width"], state["height"]

        dx, dy = 0, 0
        if direction == Direction.right.value:
            dx = 1
        elif direction == Direction.left.value:
            dx = -1
        elif direction == Direction.up.value:
            dy = -1
        elif direction == Direction.down.value:
            dy = 1

        new_x = (head["x"] + dx) % w
        new_y = (head["y"] + dy) % h

        new_snake = [{"x": new_x, "y": new_y}] + state["snake"][:4]
        state["snake"] = new_snake
        state["score"] += 1


# ---------------------------------------------------------------------------
# Seeding Database (Users, Scores)
# ---------------------------------------------------------------------------

def seed_users(db: Session) -> None:
    """Seed demo accounts if users table is empty."""
    if db.query(UserDB).first() is not None:
        return

    demo_accounts = [
        ("neonviper",   "neonviper@snake.dev",   "demo123"),
        ("pixelpython", "pixelpython@snake.dev", "demo123"),
        ("cobraclaw",   "cobraclaw@snake.dev",   "demo123"),
        ("slitherbot",  "slitherbot@snake.dev",  "demo123"),
        ("phantomsnek", "phantomsnek@snake.dev", "demo123"),
    ]
    for username, email, password in demo_accounts:
        user = UserDB(
            username=username,
            email=email,
            hashed_password=hash_password(password),
        )
        db.add(user)
    db.commit()


def seed_scores(db: Session) -> None:
    """Seed a realistic leaderboard if scores table is empty."""
    if db.query(ScoreDB).first() is not None:
        return

    fake_scores = [
        ("neonviper",   0, Mode.walls.value,        "2026-10-20"),
        ("cobraclaw",   0, Mode.walls.value,        "2026-10-21"),
        ("slitherbot",  0, Mode.walls.value,        "2026-10-19"),
        ("phantomsnek", 0, Mode.walls.value,        "2026-10-18"),
        ("pixelpython", 0, Mode.walls.value,        "2026-10-22"),
        ("pixelpython", 0, Mode.pass_through.value, "2026-10-21"),
        ("neonviper",   0, Mode.pass_through.value, "2026-10-20"),
        ("phantomsnek", 0, Mode.pass_through.value, "2026-10-19"),
        ("cobraclaw",   0, Mode.pass_through.value, "2026-10-18"),
        ("slitherbot",  0, Mode.pass_through.value, "2026-10-17"),
        ("neonviper",   0, Mode.walls.value,        "2026-10-15"),
        ("pixelpython", 0, Mode.pass_through.value, "2026-10-14"),
    ]
    for username, score, mode, recorded_date in fake_scores:
        entry = ScoreDB(
            username=username,
            score=score,
            mode=mode,
            date=recorded_date,
        )
        db.add(entry)
    db.commit()


def init_db(target_engine=None) -> None:
    """Create all tables and seed initial demo data."""
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
    with Session(eng) as session:
        seed_users(session)
        seed_scores(session)
    seed_live_players()


def reset_db(target_engine=None) -> None:
    """Reset database tables and seed live players."""
    eng = target_engine or engine
    Base.metadata.drop_all(bind=eng)
    Base.metadata.create_all(bind=eng)
    seed_live_players()


# Seed in-memory live players on module load
seed_live_players()
