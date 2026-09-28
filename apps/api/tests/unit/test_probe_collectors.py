"""Unit tests for live HTTP probe collectors."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from cirda_api.services.probe_collectors import collect_http_probe_events
from cirda_core.domain.enums import EvidenceChannel


@pytest.mark.asyncio
async def test_probe_missing_url_emits_no_events() -> None:
    events, details = await collect_http_probe_events(
        entity_id="e1",
        channels=[EvidenceChannel.TRACE],
        entity={"metadata": {}},
    )
    assert events == []
    assert details[0]["error"] == "probe_url missing in entity metadata"


@pytest.mark.asyncio
async def test_probe_rejects_non_http_scheme() -> None:
    events, details = await collect_http_probe_events(
        entity_id="e1",
        channels=[EvidenceChannel.TRACE],
        entity={"metadata": {"probe_url": "ftp://example.com/check"}},
    )
    assert events == []
    assert "http(s)" in details[0]["error"]


@pytest.mark.asyncio
async def test_probe_success_emits_evidence_per_channel() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("cirda_api.services.probe_collectors.httpx.AsyncClient", return_value=mock_client):
        events, details = await collect_http_probe_events(
            entity_id="e1",
            channels=[EvidenceChannel.TRACE, EvidenceChannel.DATABASE],
            entity={"metadata": {"probe_url": "https://collector.example/health", "probe_target_id": "e2"}},
        )

    assert len(events) == 2
    assert {e.channel for e in events} == {EvidenceChannel.TRACE, EvidenceChannel.DATABASE}
    assert all(e.source_id == "e1" and e.target_id == "e2" for e in events)
    assert details[0]["status_code"] == 200


@pytest.mark.asyncio
async def test_probe_http_error_emits_no_events() -> None:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("cirda_api.services.probe_collectors.httpx.AsyncClient", return_value=mock_client):
        events, details = await collect_http_probe_events(
            entity_id="e1",
            channels=[EvidenceChannel.TRACE],
            entity={"metadata": {"probe_url": "https://collector.example/health"}},
        )

    assert events == []
    assert "probe request failed" in details[0]["error"]
