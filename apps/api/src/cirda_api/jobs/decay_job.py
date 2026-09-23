"""Periodic decay / stale edge review job."""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


async def run_decay_job(container: object) -> None:
    logger.info("decay_job_started")
    # Decay is applied at read time in cirda_core; job refreshes channel health signals.
    if hasattr(container, "coverage_service"):
        svc = container.coverage_service  # type: ignore[attr-defined]
        for channel in ("trace", "database", "messaging", "iam"):
            await svc.coverage_repo.upsert_channel_health(channel, health_score=1.0)  # type: ignore[attr-defined]
    logger.info("decay_job_completed")
