"""Admin maintenance endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from cirda_api.api.dependencies import ContainerDep
from cirda_api.jobs.coverage_job import run_coverage_job
from cirda_api.jobs.decay_job import run_decay_job
from cirda_api.jobs.recalibration_job import run_recalibration_job
from cirda_api.jobs.snapshot_job import run_snapshot_job
from cirda_api.security.rbac import RequireAdmin

router = APIRouter(prefix="/admin", tags=["admin"])


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


@router.get("/jobs")
async def list_jobs(_principal: RequireAdmin) -> dict[str, object]:
    return {
        "jobs": [
            {"id": "decay", "description": "Refresh channel health / decay signals"},
            {"id": "coverage", "description": "Capture coverage snapshot"},
            {"id": "snapshot", "description": "Graph snapshot archival"},
            {"id": "recalibration", "description": "Validate calibration profile"},
        ]
    }
