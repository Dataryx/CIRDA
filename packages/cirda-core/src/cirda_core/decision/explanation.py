"""Decision explanation builder."""

from __future__ import annotations

from cirda_core.domain.decision import DecisionExplanation, GateDecision
from cirda_core.domain.enums import Verdict
from cirda_core.decision.runbook import default_runbook_for_verdict


def explain_decision(
    decision: GateDecision,
    entity_id: str,
    *,
    ingest_lag_seconds: float | None = None,
    max_ingest_lag_seconds: float | None = None,
) -> DecisionExplanation:
    """Build human-readable explanation for a gate decision."""
    if decision.verdict == Verdict.UNSAFE:
        summary = (
            f"Entity {entity_id} is UNSAFE: critical descendants reachable "
            f"({len(decision.critical_reachable)} nodes)."
        )
    elif decision.verdict == Verdict.SAFE:
        summary = f"Entity {entity_id} is SAFE: coverage {decision.coverage:.2f} meets threshold."
    elif "ingest_lag_exceeded" in decision.reason_codes:
        summary = (
            f"Entity {entity_id} is INDETERMINATE: ingest lag exceeds policy "
            f"(stale observability)."
        )
    else:
        summary = f"Entity {entity_id} is INDETERMINATE: insufficient evidence or coverage."

    details = _detail_lines(
        decision,
        ingest_lag_seconds=ingest_lag_seconds,
        max_ingest_lag_seconds=max_ingest_lag_seconds,
    )
    runbook = default_runbook_for_verdict(decision.verdict, entity_id)
    return DecisionExplanation(
        verdict=decision.verdict,
        summary=summary,
        details=details,
        suggested_runbook=runbook,
    )


def _detail_lines(
    decision: GateDecision,
    *,
    ingest_lag_seconds: float | None,
    max_ingest_lag_seconds: float | None,
) -> tuple[str, ...]:
    lines: list[str] = []
    for code in sorted(decision.reason_codes):
        if (
            code == "ingest_lag_exceeded"
            and ingest_lag_seconds is not None
            and max_ingest_lag_seconds is not None
        ):
            lines.append(
                f"ingest_lag_exceeded: max channel lag {ingest_lag_seconds:.0f}s "
                f"exceeds policy max_ingest_lag_seconds={max_ingest_lag_seconds:.0f}s"
            )
        else:
            lines.append(code)
    return tuple(lines)
