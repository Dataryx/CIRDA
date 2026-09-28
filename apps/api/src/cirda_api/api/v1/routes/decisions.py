"""Decision endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.common import PageMeta
from cirda_api.api.v1.schemas.decisions import (
    DecisionEvaluateRequest,
    DecisionReport,
    ProbeApplyRequest,
    ProbeApplyResult,
    RunbookExecutionListResponse,
    RunbookExecutionSchema,
    RunbookExecutionUpdate,
)
from cirda_api.observability.metrics import DECISIONS
from cirda_api.security.rbac import RequireApprover, RequireViewer
from pydantic import BaseModel


class DecisionListResponse(BaseModel):
    items: list[DecisionReport]
    page: PageMeta


router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.post("/evaluate", response_model=DecisionReport, status_code=201)
async def evaluate_decision(
    body: DecisionEvaluateRequest,
    container: ContainerDep,
    principal: RequireApprover,
) -> DecisionReport:
    report = await container.decision_service.evaluate(
        body.entity_id,
        as_of=body.as_of,
        change_type=body.change_type,
        created_by=principal.principal_id,
    )
    DECISIONS.labels(verdict=report["verdict"]).inc()
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="decision.evaluate",
        resource_type="decision",
        resource_id=report["decision_id"],
        details={"verdict": report["verdict"]},
    )
    return DecisionReport(**report)


@router.post("/probes/apply", response_model=ProbeApplyResult)
async def apply_probes(
    body: ProbeApplyRequest,
    container: ContainerDep,
    principal: RequireApprover,
) -> ProbeApplyResult:
    try:
        result = await container.decision_service.apply_probes(
            body.entity_id,
            body.channels,
            as_of=body.as_of,
        )
    except PermissionError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="decision.probe_apply",
        resource_type="entity",
        resource_id=body.entity_id,
        details={
            "channels": result["channels"],
            "actual_delta_c": result["actual_delta_c"],
            "mode": result["mode"],
        },
    )
    return ProbeApplyResult(**result)


@router.get("/by-entity/{entity_id}", response_model=DecisionListResponse)
async def list_entity_decisions(
    entity_id: str,
    container: ContainerDep,
    _principal: RequireViewer,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> DecisionListResponse:
    items, total = await container.decision_service.list_for_entity(entity_id, offset=offset, limit=limit)
    return DecisionListResponse(
        items=[DecisionReport(**i) for i in items],
        page=PageMeta(total=total, offset=offset, limit=limit),
    )


@router.get("/{decision_id}/runbook", response_model=RunbookExecutionListResponse)
async def list_runbook(
    decision_id: str,
    container: ContainerDep,
    _principal: RequireViewer,
) -> RunbookExecutionListResponse:
    try:
        items = await container.decision_service.list_runbook_executions(decision_id)
    except KeyError as exc:
        raise HTTPException(404, "Decision not found") from exc
    return RunbookExecutionListResponse(
        decision_id=decision_id,
        items=[RunbookExecutionSchema(**i) for i in items],
    )


@router.patch("/{decision_id}/runbook/{execution_id}", response_model=RunbookExecutionSchema)
async def update_runbook_stage(
    decision_id: str,
    execution_id: str,
    body: RunbookExecutionUpdate,
    container: ContainerDep,
    principal: RequireApprover,
) -> RunbookExecutionSchema:
    try:
        updated = await container.decision_service.update_runbook_execution(
            decision_id,
            execution_id,
            status=body.status,
            notes=body.notes,
        )
    except KeyError as exc:
        raise HTTPException(404, "Decision not found") from exc
    except LookupError as exc:
        raise HTTPException(404, "Runbook execution not found") from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="runbook.stage_update",
        resource_type="decision",
        resource_id=decision_id,
        details={
            "execution_id": execution_id,
            "status": updated["status"],
            "stage": updated["stage"],
        },
    )
    return RunbookExecutionSchema(**updated)


@router.get("/{decision_id}", response_model=DecisionReport)
async def get_decision(decision_id: str, container: ContainerDep, _principal: RequireViewer) -> DecisionReport:
    row = await container.decision_service.get(decision_id)
    if not row:
        raise HTTPException(404, "Decision not found")
    return DecisionReport(**row)


@router.post("/{decision_id}/rerun", response_model=DecisionReport, status_code=201)
async def rerun_decision(
    decision_id: str,
    container: ContainerDep,
    principal: RequireApprover,
) -> DecisionReport:
    try:
        report = await container.decision_service.rerun(decision_id, created_by=principal.principal_id)
    except KeyError as exc:
        raise HTTPException(404, "Decision not found") from exc
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="decision.rerun",
        resource_type="decision",
        resource_id=report["decision_id"],
        details={"supersedes": decision_id},
    )
    return DecisionReport(**report)
