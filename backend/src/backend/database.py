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


def _make_game_state(mode: Mode, start_x: int, start_y: int, direction: Direction) -> dict[str, Any]:
    return {
        "width": GRID_W,
        "height": GRID_H,
        "snake": [{"x": start_x, "y": start_y}],
        "dir": direction.value,
        "pendingDir": direction.value,
        "food": {"x": random.randint(0, GRID_W - 1), "y": random.randint(0, GRID_H - 1)},
        "score": 0,
        "alive": True,
        "mode": mode.value,
    }


def seed_live_players() -> None:
    """Seed 3 fake live players for demo purposes."""
    live_players.clear()
    live_players["bot-1"] = {
        "id": "bot-1",
        "username": "SlitherBot",
        "mode": Mode.walls.value,
        "state": _make_game_state(Mode.walls, 5, 5, Direction.right),
    }
    live_players["bot-2"] = {
        "id": "bot-2",
        "username": "PhantomSnek",
        "mode": Mode.pass_through.value,
        "state": _make_game_state(Mode.pass_through, 10, 10, Direction.down),
    }
    live_players["bot-3"] = {
        "id": "bot-3",
        "username": "CobraClaw",
        "mode": Mode.walls.value,
        "state": _make_game_state(Mode.walls, 15, 15, Direction.left),
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


# Seed on module load
seed_live_players()
