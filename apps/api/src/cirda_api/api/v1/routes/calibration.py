"""Calibration endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from cirda_api.api.dependencies import ContainerDep
from cirda_api.security.rbac import RequireAdmin, RequireViewer
from pydantic import BaseModel, Field


class CalibrationProfile(BaseModel):
    profile_id: str
    name: str
    theta_c: float = Field(alias="theta_c")
    theta_p: float = Field(alias="theta_p")
    c_min: float
    is_active: bool = True

    model_config = {"populate_by_name": True}


class CalibrationUpdate(BaseModel):
    theta_c: float
    theta_p: float
    c_min: float


router = APIRouter(prefix="/calibration", tags=["calibration"])


@router.get("", response_model=CalibrationProfile)
async def get_calibration(container: ContainerDep, _principal: RequireViewer) -> CalibrationProfile:
    row = await container.calibration_service.get_active()
    return CalibrationProfile(**row)


@router.put("", response_model=CalibrationProfile)
async def update_calibration(
    body: CalibrationUpdate,
    container: ContainerDep,
    principal: RequireAdmin,
) -> CalibrationProfile:
    row = await container.calibration_service.update(theta_c=body.theta_c, theta_p=body.theta_p, c_min=body.c_min)
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="calibration.update",
        resource_type="calibration",
        resource_id=row["profile_id"],
    )
    return CalibrationProfile(**row)
