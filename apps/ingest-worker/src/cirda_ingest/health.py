"""Async HTTP health and metrics server."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from cirda_ingest.sinks.metrics_sink import metrics_payload


HealthProbe = Callable[[], Awaitable[dict[str, Any]]]


@dataclass
class HealthState:
    """Mutable worker health snapshot."""

    ready: bool = False
    kafka_connected: bool | None = None
    consumer_mode: str = "unknown"
    events_processed: int = 0
    last_error: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        status = "healthy" if self.ready else "starting"
        if self.last_error:
            status = "degraded"
        body: dict[str, Any] = {
            "status": status,
            "ready": self.ready,
            "consumer_mode": self.consumer_mode,
            "events_processed": self.events_processed,
            "kafka_connected": self.kafka_connected,
        }
        if self.last_error:
            body["last_error"] = self.last_error
        body.update(self.extra)
        return body


class HealthServer:
    """Minimal asyncio HTTP server for /health, /ready, and /metrics."""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        health: HealthState,
        metrics_enabled: bool = True,
        on_dev_publish: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._health = health
        self._metrics_enabled = metrics_enabled
        self._on_dev_publish = on_dev_publish
        self._server: asyncio.Server | None = None

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._handle, self._host, self._port)

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            request_line = await reader.readline()
            if not request_line:
                return
            parts = request_line.decode("utf-8", errors="replace").strip().split()
            method = parts[0] if parts else "GET"
            path = parts[1].split("?", 1)[0] if len(parts) > 1 else "/"

            headers: dict[str, str] = {}
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b"\n", b""):
                    break
                decoded = line.decode("utf-8", errors="replace").strip()
                if ":" in decoded:
                    key, value = decoded.split(":", 1)
                    headers[key.strip().lower()] = value.strip()

            body_bytes = b""
            if method in {"POST", "PUT", "PATCH"}:
                content_length = int(headers.get("content-length", "0"))
                if content_length:
                    body_bytes = await reader.readexactly(content_length)

            status, content_type, body = await self._route(method, path, body_bytes)
            response = (
                f"HTTP/1.1 {status}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + body
            writer.write(response)
            await writer.drain()
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def _route(self, method: str, path: str, body: bytes) -> tuple[int, str, bytes]:
        if path == "/health":
            payload = json.dumps(self._health.snapshot()).encode("utf-8")
            return 200, "application/json", payload

        if path == "/ready":
            if self._health.ready:
                return 200, "text/plain", b"ready\n"
            return 503, "text/plain", b"not ready\n"

        if path == "/metrics" and self._metrics_enabled:
            return 200, "text/plain; version=0.0.4", metrics_payload()

        if path == "/dev/publish" and method == "POST" and self._on_dev_publish is not None:
            try:
                raw = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                return 400, "application/json", b'{"error":"invalid json"}\n'
            if not isinstance(raw, dict):
                return 400, "application/json", b'{"error":"body must be object"}\n'
            await self._on_dev_publish(raw)
            return 202, "application/json", b'{"accepted":true}\n'

        return 404, "text/plain", b"not found\n"
