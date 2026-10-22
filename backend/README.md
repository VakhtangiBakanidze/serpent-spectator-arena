# Serpent Spectator Arena — Backend

FastAPI backend for the Snake multiplayer spectator game.  
Authentication uses HTTP-only session cookies. Real-time updates are delivered over WebSocket.

---

## Requirements

- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — package & project manager

---

## Setup

```bash
# 1. Move into the backend directory
cd backend

# 2. Install all dependencies from the lockfile
uv sync
```

---

## Running the Server

Using `make`:
```bash
make run
```

Or using `uv` directly:
```bash
uv run uvicorn backend.main:app --reload
```

The API will be available at **http://localhost:8000**.

| URL | Description |
|-----|-------------|
| http://localhost:8000 | API root |
| http://localhost:8000/docs | Swagger UI (interactive API docs) |
| http://localhost:8000/redoc | ReDoc API docs |
| ws://localhost:8000/ws/live | WebSocket — real-time game state stream |

> **Note:** `--reload` enables hot-reloading on file changes. Remove it in production.

### Custom host / port

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080
```

---

## Running Tests

```bash
uv run pytest tests/ -v
```

To run a specific test file:

```bash
uv run pytest tests/test_auth.py -v
uv run pytest tests/test_leaderboard.py -v
uv run pytest tests/test_live.py -v
```

---

## Project Structure

```
backend/
├── src/backend/
│   ├── main.py          # FastAPI app factory + CORS middleware
│   ├── models.py        # Pydantic schemas (User, ScoreEntry, GameState, …)
│   ├── database.py      # In-memory mock database (users, sessions, scores, live players)
│   ├── auth.py          # Session cookie helpers + get_current_user dependency
│   └── routers/
│       ├── auth.py      # POST /auth/signup  /auth/login  /auth/logout  GET /auth/me
│       ├── leaderboard.py  # GET /leaderboard  POST /scores
│       └── live.py      # GET /live  WS /ws/live
└── tests/
    ├── conftest.py      # Fixtures: reset DB between tests, HTTP client, authed client
    ├── test_auth.py
    ├── test_leaderboard.py
    └── test_live.py
```

---

## Adding Dependencies

```bash
# Runtime dependency
uv add <package>

# Dev-only dependency
uv add --dev <package>
```

---

## Environment Variables

No `.env` file is required to run locally — the server starts with sensible defaults.  
When moving to a real database, create a `.env` file (never commit it):

```env
# Example — not used yet
DATABASE_URL=postgresql://user:password@localhost:5432/serpent
SECRET_KEY=change-me
```

---

## API Overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/signup` | — | Register a new account |
| `POST` | `/auth/login` | — | Log in, receive session cookie |
| `POST` | `/auth/logout` | ✅ | End session, clear cookie |
| `GET` | `/auth/me` | ✅ | Get the current user |
| `GET` | `/leaderboard` | — | Top 10 scores (optional `?mode=walls\|pass-through`) |
| `POST` | `/scores` | ✅ | Submit a completed game score |
| `GET` | `/live` | — | Snapshot of all live players |
| `WS` | `/ws/live` | — | Real-time game state stream (140 ms ticks) |

Full schema reference: see [`openapi.yaml`](../openapi.yaml) at the repo root.

