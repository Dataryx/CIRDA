"""Admin maintenance endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from cirda_api.api.dependencies import ContainerDep
from cirda_api.jobs.coverage_job import run_coverage_job
from cirda_api.jobs.decay_job import run_decay_job
from cirda_api.jobs.recalibration_job import run_recalibration_job
from cirda_api.jobs.snapshot_job import run_snapshot_job
from cirda_api.security.rbac import RequireAdmin

router = APIRouter(prefix="/admin", tags=["admin"])


class ChannelHealthUpsert(BaseModel):
    channel: str
    health_score: float = Field(ge=0.0, le=1.0)
    lag_seconds: float = Field(default=0.0, ge=0.0)
    suppression_suspected: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


@router.post("/snapshot")
async def trigger_snapshot(container: ContainerDep, principal: RequireAdmin) -> dict[str, str]:
    await run_snapshot_job(container)
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="admin.snapshot",
        resource_type="system",
    )
    return {"status": "ok"}


@router.post("/decay")
async def trigger_decay(container: ContainerDep, principal: RequireAdmin) -> dict[str, str]:
    await run_decay_job(container)
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="admin.decay",
        resource_type="system",
    )
    return {"status": "ok"}


@router.post("/coverage")
async def trigger_coverage(container: ContainerDep, principal: RequireAdmin) -> dict[str, str]:
    await run_coverage_job(container)
    return {"status": "ok"}


@router.post("/recalibration")
async def trigger_recalibration(container: ContainerDep, principal: RequireAdmin) -> dict[str, str]:
    await run_recalibration_job(container)
    return {"status": "ok"}


@router.post("/channel-health")
async def upsert_channel_health(
    body: ChannelHealthUpsert,
    container: ContainerDep,
    principal: RequireAdmin,
) -> dict[str, str]:
    await container.coverage_service.coverage_repo.upsert_channel_health(
        body.channel,
        body.health_score,
        body.lag_seconds,
        details=body.details,
        suppression_suspected=body.suppression_suspected,
    )
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="admin.channel_health",
        resource_type="channel",
        resource_id=body.channel,
    )
    return {"status": "ok", "channel": body.channel}


@router.get("/jobs")
async def list_jobs(_principal: RequireAdmin) -> dict[str, object]:
    return {
        "jobs": [
            {"id": "decay", "description": "Refresh channel health / decay signals"},
            {"id": "coverage", "description": "Capture coverage snapshot"},
            {"id": "snapshot", "description": "Graph snapshot archival"},
            {"id": "recalibration", "description": "Validate calibration profile"},
            {"id": "channel-health", "description": "Upsert channel health / suppression"},
        ]
    }
