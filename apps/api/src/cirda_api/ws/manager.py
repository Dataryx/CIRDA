"""WebSocket connection manager."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket


@dataclass
class ConnectionManager:
    active: dict[WebSocket, frozenset[str]] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def connect(self, websocket: WebSocket, topics: frozenset[str]) -> None:
        await websocket.accept()
        async with self._lock:
            self.active[websocket] = topics

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self.active.pop(websocket, None)

    async def broadcast(self, topic: str, payload: dict[str, Any]) -> None:
        message = json.dumps({"topic": topic, "payload": payload})
        async with self._lock:
            targets = list(self.active.items())
        for ws, topics in targets:
            if topic in topics or "*" in topics:
                try:
                    await ws.send_text(message)
                except Exception:
                    await self.disconnect(ws)
