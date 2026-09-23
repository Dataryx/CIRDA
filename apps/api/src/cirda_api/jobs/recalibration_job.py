"""Calibration profile validation job."""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


async def run_recalibration_job(container: object) -> None:
    logger.info("recalibration_job_started")
    if hasattr(container, "calibration_service"):
        await container.calibration_service.get_active()  # type: ignore[attr-defined]
    logger.info("recalibration_job_completed")
