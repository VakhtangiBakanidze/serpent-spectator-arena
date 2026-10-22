"""Tests for /live and /ws/live endpoints."""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient


class TestLiveSnapshot:
    def test_live_returns_list(self, client: TestClient):
        resp = client.get("/live")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # Seeded bots should be present
        assert len(data) >= 1

    def test_live_player_schema(self, client: TestClient):
        resp = client.get("/live")
        player = resp.json()[0]
        assert "id" in player
        assert "username" in player
        assert "mode" in player
        assert "state" in player
        state = player["state"]
        assert "snake" in state
        assert "width" in state
        assert "height" in state
        assert "score" in state
        assert "alive" in state


class TestLiveWebSocket:
    def test_ws_receives_snapshot(self, client: TestClient):
        with client.websocket_connect("/ws/live") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "snapshot"
            assert "players" in msg
            assert isinstance(msg["players"], list)

    def test_ws_players_have_correct_fields(self, client: TestClient):
        with client.websocket_connect("/ws/live") as ws:
            msg = ws.receive_json()
            players = msg["players"]
            assert len(players) >= 1
            for player in players:
                assert "id" in player
                assert "username" in player
                assert "mode" in player
                assert "state" in player

