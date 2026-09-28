"""Decision explanation builder tests."""

from __future__ import annotations

from cirda_core.decision.explanation import explain_decision
from cirda_core.domain.decision import GateDecision
from cirda_core.domain.enums import Verdict


def test_explain_ingest_lag_exceeded_includes_threshold_detail() -> None:
    decision = GateDecision(
        verdict=Verdict.INDETERMINATE,
        coverage=0.95,
        truncated=False,
        hard_blocks=frozenset(),
        reason_codes=frozenset({"ingest_lag_exceeded"}),
    )
    explanation = explain_decision(
        decision,
        "agent-a",
        ingest_lag_seconds=14_400.0,
        max_ingest_lag_seconds=3_600.0,
    )
    assert "INDETERMINATE" in explanation.summary
    assert "ingest lag" in explanation.summary.lower()
    assert any("14400" in line and "3600" in line for line in explanation.details)
