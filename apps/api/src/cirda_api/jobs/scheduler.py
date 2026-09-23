"""APScheduler background jobs."""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cirda_api.jobs.coverage_job import run_coverage_job
from cirda_api.jobs.decay_job import run_decay_job
from cirda_api.jobs.recalibration_job import run_recalibration_job
from cirda_api.jobs.snapshot_job import run_snapshot_job
from cirda_api.settings import Settings


def create_scheduler(settings: Settings, container: object) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    if not settings.scheduler_enabled:
        return scheduler

    scheduler.add_job(
        run_decay_job,
        "interval",
        seconds=settings.decay_job_interval_seconds,
        args=[container],
        id="decay",
        replace_existing=True,
    )
    scheduler.add_job(
        run_coverage_job,
        "interval",
        seconds=settings.coverage_job_interval_seconds,
        args=[container],
        id="coverage",
        replace_existing=True,
    )
    scheduler.add_job(
        run_snapshot_job,
        "interval",
        seconds=settings.snapshot_job_interval_seconds,
        args=[container],
        id="snapshot",
        replace_existing=True,
    )
    scheduler.add_job(
        run_recalibration_job,
        "interval",
        seconds=settings.recalibration_job_interval_seconds,
        args=[container],
        id="recalibration",
        replace_existing=True,
    )
    return scheduler
