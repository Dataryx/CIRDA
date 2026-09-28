"""Live collector probes that emit real evidence when external checks succeed."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx

from cirda_core.domain.enums import EvidenceChannel, Relation
from cirda_core.domain.event import EvidenceEvent


async def collect_http_probe_events(
    *,
    entity_id: str,
    channels: list[EvidenceChannel],
    entity: dict[str, Any],
    neighbor_id: str | None = None,
) -> tuple[list[EvidenceEvent], list[dict[str, Any]]]:
    """
    Run an HTTP probe against entity metadata ``probe_url``.

    Only emits evidence when the HTTP request succeeds (2xx). No fabricated
    observations when the URL is missing or the probe fails.
    """
    metadata = entity.get("metadata") or {}
    probe_url = metadata.get("probe_url")
    if not isinstance(probe_url, str) or not probe_url.strip():
        return [], [{"entity_id": entity_id, "error": "probe_url missing in entity metadata"}]

    parsed = urlparse(probe_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return [], [{"entity_id": entity_id, "error": "probe_url must be http(s)"}]

    target = neighbor_id or str(metadata.get("probe_target_id") or entity_id)
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            response = await client.get(probe_url)
    except httpx.HTTPError as exc:
        return [], [{"entity_id": entity_id, "error": f"probe request failed: {exc}"}]

    if response.status_code >= 400:
        return [], [
            {
                "entity_id": entity_id,
                "error": f"probe returned HTTP {response.status_code}",
                "probe_url": probe_url,
            }
        ]

    now = datetime.now(timezone.utc)
    events: list[EvidenceEvent] = []
    for channel in channels:
        events.append(
            EvidenceEvent(
                event_id=f"probe-{channel.value}-{uuid.uuid4()}",
                source_id=entity_id,
                target_id=target,
                relation=Relation.CALLS,
                channel=channel,
                observed_at=now,
            )
        )
    return events, [{"entity_id": entity_id, "probe_url": probe_url, "status_code": response.status_code}]
