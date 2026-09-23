"""Decision explanation builder."""

from __future__ import annotations

from cirda_core.domain.decision import DecisionExplanation, GateDecision, RunbookAction
from cirda_core.domain.enums import Verdict
from cirda_core.decision.runbook import default_runbook_for_verdict


def explain_decision(decision: GateDecision, entity_id: str) -> DecisionExplanation:
    """Build human-readable explanation for a gate decision."""
    if decision.verdict == Verdict.UNSAFE:
        summary = (
            f"Entity {entity_id} is UNSAFE: critical descendants reachable "
            f"({len(decision.critical_reachable)} nodes)."
        )
        details = tuple(sorted(decision.reason_codes))
    elif decision.verdict == Verdict.SAFE:
        summary = f"Entity {entity_id} is SAFE: coverage {decision.coverage:.2f} meets threshold."
        details = tuple(sorted(decision.reason_codes))
    else:
        summary = f"Entity {entity_id} is INDETERMINATE: insufficient evidence or coverage."
        details = tuple(sorted(decision.reason_codes))

    runbook = default_runbook_for_verdict(decision.verdict, entity_id)
    return DecisionExplanation(
        verdict=decision.verdict,
        summary=summary,
        details=details,
        suggested_runbook=runbook,
    )
