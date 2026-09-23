"""OTLP/HTTP trace receiver — converts span batches to trace evidence events."""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

import structlog

from cirda_ingest.pipeline.stages import InboundMessage

logger = structlog.get_logger(__name__)

MessageHandler = Callable[[InboundMessage], Awaitable[None]]


class OtlpReceiver:
    """Minimal OTLP JSON HTTP listener on a dedicated port."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._handler: MessageHandler | None = None
        self._server: asyncio.Server | None = None

    async def start(self, handler: MessageHandler) -> None:
        self._handler = handler
        self._server = await asyncio.start_server(self._handle, self._host, self._port)
        logger.info("otlp_receiver_started", host=self._host, port=self._port)

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            request_line = await reader.readline()
            parts = request_line.decode("utf-8", errors="replace").strip().split()
            method = parts[0] if parts else "GET"
            path = parts[1] if len(parts) > 1 else "/"

            headers: dict[str, str] = {}
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b"\n", b""):
                    break
                decoded = line.decode("utf-8", errors="replace").strip()
                if ":" in decoded:
                    key, value = decoded.split(":", 1)
                    headers[key.strip().lower()] = value.strip()

            body = b""
            content_length = int(headers.get("content-length", "0"))
            if content_length:
                body = await reader.readexactly(content_length)

            status = 404
            response_body = b"not found"
            if method == "POST" and path in {"/v1/traces", "/otlp/v1/traces"}:
                status = 202
                response_body = b'{"partialSuccess":{}}'
                await self._ingest_otlp_body(body)

            response = (
                f"HTTP/1.1 {status}\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + response_body
            writer.write(response)
            await writer.drain()
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def _ingest_otlp_body(self, body: bytes) -> None:
        if not body or self._handler is None:
            return
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            logger.warning("otlp_invalid_json")
            return

        for raw in self._spans_to_raw_events(payload):
            message = InboundMessage(
                raw=raw,
                message_id=str(uuid.uuid4()),
                source="otlp",
            )
            await self._handler(message)

    def _spans_to_raw_events(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for resource_span in payload.get("resourceSpans", []):
            for scope_span in resource_span.get("scopeSpans", []):
                for span in scope_span.get("spans", []):
                    raw = self._span_to_raw(span)
                    if raw:
                        events.append(raw)
        return events

    @staticmethod
    def _span_to_raw(span: dict[str, Any]) -> dict[str, Any] | None:
        trace_id = span.get("traceId") or span.get("trace_id")
        span_id = span.get("spanId") or span.get("span_id")
        if not trace_id or not span_id:
            return None

        name = span.get("name", "span")
        start_ns = int(span.get("startTimeUnixNano") or span.get("start_time_unix_nano") or 0)
        observed_at = datetime.fromtimestamp(start_ns / 1_000_000_000, tz=timezone.utc)

        attrs = {}
        for item in span.get("attributes", []):
            key = item.get("key")
            value = item.get("value", {})
            if key:
                attrs[key] = value.get("stringValue") or value.get("intValue") or value.get("boolValue")

        source_id = str(attrs.get("service.name") or attrs.get("source_id") or "unknown-source")
        target_id = str(attrs.get("peer.service") or attrs.get("target_id") or name)

        return {
            "source": "trace",
            "event_id": f"{trace_id}:{span_id}",
            "source_id": source_id,
            "target_id": target_id,
            "relation": "calls",
            "observed_at": observed_at.isoformat(),
            "payload": {"span_name": name, "attributes": attrs},
        }
