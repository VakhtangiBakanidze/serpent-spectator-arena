"""Tests for /leaderboard and /scores endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


SIGNUP_PAYLOAD = {
    "username": "scoreuser",
    "email": "score@example.com",
    "password": "password123",
}


class TestLeaderboard:
    def test_leaderboard_empty(self, client: TestClient):
        resp = client.get("/leaderboard")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_leaderboard_returns_scores(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        client.post("/scores", json={"score": 100, "mode": "walls"})
        resp = client.get("/leaderboard")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["score"] == 100
        assert data[0]["mode"] == "walls"
        assert data[0]["username"] == "scoreuser"

    def test_leaderboard_sorted_descending(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        client.post("/scores", json={"score": 50, "mode": "walls"})
        client.post("/scores", json={"score": 200, "mode": "walls"})
        client.post("/scores", json={"score": 10, "mode": "walls"})
        resp = client.get("/leaderboard")
        data = resp.json()
        scores = [e["score"] for e in data]
        assert scores == sorted(scores, reverse=True)

    def test_leaderboard_top_10(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        for i in range(15):
            client.post("/scores", json={"score": i * 10, "mode": "walls"})
        resp = client.get("/leaderboard")
        assert len(resp.json()) == 10

    def test_leaderboard_filter_by_mode(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        client.post("/scores", json={"score": 100, "mode": "walls"})
        client.post("/scores", json={"score": 200, "mode": "pass-through"})

        resp_walls = client.get("/leaderboard?mode=walls")
        assert all(e["mode"] == "walls" for e in resp_walls.json())

        resp_pt = client.get("/leaderboard?mode=pass-through")
        assert all(e["mode"] == "pass-through" for e in resp_pt.json())


class TestSubmitScore:
    def test_submit_score_success(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        resp = client.post("/scores", json={"score": 42, "mode": "walls"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["score"] == 42
        assert data["mode"] == "walls"
        assert data["username"] == "scoreuser"
        assert "date" in data

    def test_submit_score_unauthenticated(self, client: TestClient):
        resp = client.post("/scores", json={"score": 42, "mode": "walls"})
        assert resp.status_code == 401

    def test_submit_score_negative(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        resp = client.post("/scores", json={"score": -1, "mode": "walls"})
        assert resp.status_code == 422

    def test_submit_score_invalid_mode(self, client: TestClient):
        client.post("/auth/signup", json=SIGNUP_PAYLOAD)
        resp = client.post("/scores", json={"score": 10, "mode": "invalid"})
        assert resp.status_code == 422
