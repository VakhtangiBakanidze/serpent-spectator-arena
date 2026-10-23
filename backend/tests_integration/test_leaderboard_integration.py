"""Integration tests for leaderboard and score persistence with SQLite database."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database import ScoreDB


def test_submit_score_lifecycle_and_db_persistence(client: TestClient, db_session: Session):
    # 1. Anonymous attempt fails
    anon_submit = client.post("/scores", json={"score": 100, "mode": "walls"})
    assert anon_submit.status_code == 401

    # 2. Register user
    client.post("/auth/signup", json={
        "username": "arcade_ace",
        "email": "ace@snake.dev",
        "password": "password123",
    })

    # 3. Submit score
    submit_res = client.post("/scores", json={"score": 450, "mode": "walls"})
    assert submit_res.status_code == 201
    score_data = submit_res.json()
    assert score_data["score"] == 450
    assert score_data["mode"] == "walls"
    assert score_data["username"] == "arcade_ace"
    assert "date" in score_data

    # 4. Verify persisted in SQLite
    db_session.expire_all()
    records = db_session.query(ScoreDB).filter_by(username="arcade_ace").all()
    assert len(records) == 1
    assert records[0].score == 450
    assert records[0].mode == "walls"


def test_leaderboard_ordering_and_mode_filtering(client: TestClient):
    # Setup two users
    client.post("/auth/signup", json={"username": "player1", "email": "p1@snake.dev", "password": "pass12345"})
    client.post("/scores", json={"score": 150, "mode": "walls"})
    client.post("/scores", json={"score": 500, "mode": "pass-through"})
    client.post("/scores", json={"score": 300, "mode": "walls"})

    client.post("/auth/logout")

    client.post("/auth/signup", json={"username": "player2", "email": "p2@snake.dev", "password": "pass12345"})
    client.post("/scores", json={"score": 220, "mode": "walls"})
    client.post("/scores", json={"score": 400, "mode": "pass-through"})

    # Check unfiltered leaderboard
    all_res = client.get("/leaderboard")
    assert all_res.status_code == 200
    all_scores = [entry["score"] for entry in all_res.json()]
    assert all_scores == [500, 400, 300, 220, 150]

    # Check walls mode
    walls_res = client.get("/leaderboard?mode=walls")
    assert walls_res.status_code == 200
    walls_scores = [entry["score"] for entry in walls_res.json()]
    assert walls_scores == [300, 220, 150]
    assert all(e["mode"] == "walls" for e in walls_res.json())

    # Check pass-through mode
    pass_res = client.get("/leaderboard?mode=pass-through")
    assert pass_res.status_code == 200
    pass_scores = [entry["score"] for entry in pass_res.json()]
    assert pass_scores == [500, 400]
    assert all(e["mode"] == "pass-through" for e in pass_res.json())


def test_leaderboard_top_10_limit(client: TestClient):
    client.post("/auth/signup", json={"username": "spammer", "email": "spammer@snake.dev", "password": "pass12345"})

    for i in range(15):
        client.post("/scores", json={"score": (i + 1) * 10, "mode": "walls"})

    res = client.get("/leaderboard")
    assert res.status_code == 200
    scores = res.json()
    assert len(scores) == 10
    # Top score should be 150, 10th should be 60
    assert scores[0]["score"] == 150
    assert scores[-1]["score"] == 60
