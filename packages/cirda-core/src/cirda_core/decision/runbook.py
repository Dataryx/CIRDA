"""Runbook stage definitions."""

from __future__ import annotations

from cirda_core.domain.decision import RunbookAction
from cirda_core.domain.enums import RunbookStage, Verdict

STANDARD_RUNBOOK: tuple[RunbookStage, ...] = (
    RunbookStage.REPORT_AND_REMEDIATE,
    RunbookStage.DISABLE_NEW_WORK,
    RunbookStage.OBSERVE_DOWNSTREAM,
    RunbookStage.REVOKE_CREDENTIALS,
    RunbookStage.DELETE_IDENTITY,
)

_STAGE_DESCRIPTIONS: dict[RunbookStage, str] = {
    RunbookStage.REPORT_AND_REMEDIATE: "Report finding and begin remediation.",
    RunbookStage.DISABLE_NEW_WORK: "Disable new work for affected entity.",
    RunbookStage.OBSERVE_DOWNSTREAM: "Observe downstream impact.",
    RunbookStage.REVOKE_CREDENTIALS: "Revoke credentials associated with entity.",
    RunbookStage.DELETE_IDENTITY: "Delete identity after downstream quiescence.",
}


def default_runbook_for_verdict(verdict: Verdict, entity_id: str) -> tuple[RunbookAction, ...]:
    """Return staged runbook actions for a verdict."""
    if verdict == Verdict.SAFE:
        return ()
    stages = STANDARD_RUNBOOK if verdict == Verdict.UNSAFE else STANDARD_RUNBOOK[:2]
    return tuple(
        RunbookAction(
            stage=stage,
            description=_STAGE_DESCRIPTIONS[stage],
            entity_id=entity_id,
        )
        for stage in stages
    )
