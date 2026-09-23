"""Graph snapshot archival job."""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


async def run_snapshot_job(container: object) -> None:
    logger.info("snapshot_job_started")
    if hasattr(container, "graph_service"):
        await container.graph_service.get_graph_payload()  # type: ignore[attr-defined]
    logger.info("snapshot_job_completed")
