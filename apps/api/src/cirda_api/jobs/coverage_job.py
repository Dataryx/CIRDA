"""Coverage snapshot job."""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


async def run_coverage_job(container: object) -> None:
    logger.info("coverage_job_started")
    if hasattr(container, "coverage_service"):
        await container.coverage_service.snapshot(scope="scheduled")  # type: ignore[attr-defined]
    logger.info("coverage_job_completed")
