"""WebSocket streaming endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from cirda_api.api.dependencies import get_app_container
from cirda_api.ws import topics

router = APIRouter(tags=["stream"])


@router.websocket("/stream")
async def websocket_stream(
    websocket: WebSocket,
    subscribe: str = Query("*"),
) -> None:
    container = get_app_container()
    topic_set = frozenset(subscribe.split(",")) if subscribe != "*" else frozenset({*topics.ALL_TOPICS, "*"})
    await container.ws_manager.connect(websocket, topic_set)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await container.ws_manager.disconnect(websocket)
