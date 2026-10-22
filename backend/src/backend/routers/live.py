"""Live players router: GET /live and WebSocket /ws/live"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .. import database as db
from ..models import LivePlayer

router = APIRouter(tags=["live"])

TICK_INTERVAL = 0.14  # 140ms


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()
        self._tick_task: asyncio.Task[None] | None = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        # Start background tick if not running
        if self._tick_task is None or self._tick_task.done():
            self._tick_task = asyncio.create_task(self._ticker())

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in list(self.active_connections):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active_connections.discard(ws)

    def _players_snapshot(self) -> list[dict[str, Any]]:
        return list(db.live_players.values())

    async def _ticker(self) -> None:
        while self.active_connections:
            await asyncio.sleep(TICK_INTERVAL)
            db.tick_live_players()
            players = self._players_snapshot()
            await self.broadcast({"type": "tick", "players": players})
        self._tick_task = None


manager = ConnectionManager()


@router.get("/live", response_model=list[LivePlayer])
def get_live() -> list[LivePlayer]:
    """Snapshot of all current live players."""
    return [LivePlayer(**p) for p in db.live_players.values()]


@router.websocket("/ws/live")
async def ws_live(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    # Send initial snapshot
    snapshot = {
        "type": "snapshot",
        "players": manager._players_snapshot(),
    }
    await websocket.send_json(snapshot)

    try:
        while True:
            # Keep connection alive; client can send pings or we just wait
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
