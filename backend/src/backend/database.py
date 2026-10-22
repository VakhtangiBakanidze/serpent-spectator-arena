"""In-memory mock database and helper utilities."""
from __future__ import annotations

import copy
import hashlib
import hmac
import os
import random
from datetime import date
from typing import Any

from .models import Direction, GameState, LivePlayer, Mode, Point, ScoreEntry

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

users: dict[str, dict[str, Any]] = {}          # email -> {username, email, hashed_password}
sessions: dict[str, str] = {}                   # session_token -> username
scores: list[dict[str, Any]] = []              # list of ScoreEntry dicts
live_players: dict[str, dict[str, Any]] = {}   # player_id -> LivePlayer-ish dict


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
# Seeded fake live players
# ---------------------------------------------------------------------------

GRID_W = 20
GRID_H = 20


def _make_snake(head_x: int, head_y: int, direction: Direction, length: int) -> list[dict]:
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
            "width": GRID_W, "height": GRID_H,
            "snake": _make_snake(8, 5, Direction.right, 5),
            "dir": Direction.right.value, "pendingDir": Direction.right.value,
            "food": {"x": 14, "y": 3}, "score": 240, "alive": True,
            "mode": Mode.walls.value,
        },
    }
    live_players["bot-2"] = {
        "id": "bot-2",
        "username": "PhantomSnek",
        "mode": Mode.pass_through.value,
        "state": {
            "width": GRID_W, "height": GRID_H,
            "snake": _make_snake(10, 12, Direction.down, 7),
            "dir": Direction.down.value, "pendingDir": Direction.down.value,
            "food": {"x": 6, "y": 17}, "score": 380, "alive": True,
            "mode": Mode.pass_through.value,
        },
    }
    live_players["bot-3"] = {
        "id": "bot-3",
        "username": "CobraClaw",
        "mode": Mode.walls.value,
        "state": {
            "width": GRID_W, "height": GRID_H,
            "snake": _make_snake(15, 15, Direction.left, 6),
            "dir": Direction.left.value, "pendingDir": Direction.left.value,
            "food": {"x": 2, "y": 11}, "score": 310, "alive": True,
            "mode": Mode.walls.value,
        },
    }
    live_players["bot-4"] = {
        "id": "bot-4",
        "username": "NeonViper",
        "mode": Mode.pass_through.value,
        "state": {
            "width": GRID_W, "height": GRID_H,
            "snake": _make_snake(3, 17, Direction.up, 4),
            "dir": Direction.up.value, "pendingDir": Direction.up.value,
            "food": {"x": 18, "y": 2}, "score": 150, "alive": True,
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

        # Shift snake (keep length at most 5 for sim simplicity)
        new_snake = [{"x": new_x, "y": new_y}] + state["snake"][:4]
        state["snake"] = new_snake
        state["score"] += 1


def reset_db() -> None:
    """Reset all in-memory state (used in tests)."""
    users.clear()
    sessions.clear()
    scores.clear()
    seed_live_players()


# ---------------------------------------------------------------------------
# Seeded fake users & scores
# ---------------------------------------------------------------------------

def seed_users() -> None:
    """Seed a handful of demo user accounts."""
    demo_accounts = [
        ("neonviper",   "neonviper@snake.dev",   "demo123"),
        ("pixelpython", "pixelpython@snake.dev", "demo123"),
        ("cobraclaw",   "cobraclaw@snake.dev",   "demo123"),
        ("slitherbot",  "slitherbot@snake.dev",  "demo123"),
        ("phantomsnek", "phantomsnek@snake.dev", "demo123"),
    ]
    for username, email, password in demo_accounts:
        users[email] = {
            "username": username,
            "email": email,
            "hashed_password": hash_password(password),
        }


def seed_scores() -> None:
    """Seed a realistic leaderboard with scores across both modes."""
    scores.clear()
    fake_scores = [
        # walls mode
        ("neonviper",   820, Mode.walls.value,        "2026-10-20"),
        ("cobraclaw",   740, Mode.walls.value,        "2026-10-21"),
        ("slitherbot",  610, Mode.walls.value,        "2026-10-19"),
        ("phantomsnek", 580, Mode.walls.value,        "2026-10-18"),
        ("pixelpython", 430, Mode.walls.value,        "2026-10-22"),
        # pass-through mode
        ("pixelpython", 950, Mode.pass_through.value, "2026-10-21"),
        ("neonviper",   870, Mode.pass_through.value, "2026-10-20"),
        ("phantomsnek", 760, Mode.pass_through.value, "2026-10-19"),
        ("cobraclaw",   690, Mode.pass_through.value, "2026-10-18"),
        ("slitherbot",  520, Mode.pass_through.value, "2026-10-17"),
        # extra entries (won't show in top-10 per-mode but visible in combined)
        ("neonviper",   310, Mode.walls.value,        "2026-10-15"),
        ("pixelpython", 290, Mode.pass_through.value, "2026-10-14"),
    ]
    for username, score, mode, recorded_date in fake_scores:
        scores.append({
            "username": username,
            "score":    score,
            "mode":     mode,
            "date":     recorded_date,
        })


def seed_all() -> None:
    """Seed users, scores, and live players."""
    seed_users()
    seed_scores()
    seed_live_players()


def reset_db() -> None:
    """Reset all in-memory state (used in tests)."""
    users.clear()
    sessions.clear()
    scores.clear()
    seed_live_players()


# Seed on module load
seed_all()
