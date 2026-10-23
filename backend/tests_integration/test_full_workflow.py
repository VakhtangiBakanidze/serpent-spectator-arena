"""Full end-to-end workflow test testing real SQLite disk file persistence."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import ScoreDB, UserDB


def test_sqlite_file_persistence_across_connections(client: TestClient, integration_engine):
    _, db_file = integration_engine

    # 1. Create User via API
    signup_res = client.post("/auth/signup", json={
        "username": "persistence_tester",
        "email": "persist@snake.dev",
        "password": "strongpassword123",
    })
    assert signup_res.status_code == 201

    # 2. Submit scores
    client.post("/scores", json={"score": 880, "mode": "walls"})
    client.post("/scores", json={"score": 920, "mode": "pass-through"})

    # 3. Open a brand new, completely independent connection directly to the SQLite file
    fresh_engine = create_engine(f"sqlite:///{db_file}")
    with Session(fresh_engine) as fresh_session:
        # User should exist in SQLite file
        user = fresh_session.query(UserDB).filter_by(username="persistence_tester").first()
        assert user is not None
        assert user.email == "persist@snake.dev"

        # Scores should exist in SQLite file
        scores = fresh_session.query(ScoreDB).filter_by(username="persistence_tester").all()
        assert len(scores) == 2
        score_values = {s.score for s in scores}
        assert score_values == {880, 920}

    fresh_engine.dispose()


def test_full_spectator_and_game_flow(client: TestClient):
    # Check live players snapshot
    live_res = client.get("/live")
    assert live_res.status_code == 200
    live_players = live_res.json()
    assert len(live_players) >= 3
    assert all("state" in p and "snake" in p["state"] for p in live_players)

    # Test WebSocket live stream
    with client.websocket_connect("/ws/live") as ws:
        snapshot = ws.receive_json()
        assert snapshot["type"] == "snapshot"
        assert len(snapshot["players"]) >= 3
