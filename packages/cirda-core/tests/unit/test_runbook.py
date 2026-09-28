"""Unit tests for verdict-scoped runbook stages."""

from __future__ import annotations

from cirda_core.decision.runbook import STANDARD_RUNBOOK, default_runbook_for_verdict
from cirda_core.domain.enums import Verdict


def test_safe_gets_full_staged_runbook() -> None:
    actions = default_runbook_for_verdict(Verdict.SAFE, "legacy-csv-export-agent")
    assert len(actions) == len(STANDARD_RUNBOOK)
    assert [a.stage for a in actions] == list(STANDARD_RUNBOOK)


def test_unsafe_gets_full_runbook() -> None:
    actions = default_runbook_for_verdict(Verdict.UNSAFE, "invoice-agent")
    assert len(actions) == len(STANDARD_RUNBOOK)


def test_indeterminate_gets_prefix() -> None:
    actions = default_runbook_for_verdict(Verdict.INDETERMINATE, "vendor-risk-agent")
    assert len(actions) == 2
    assert actions[0].stage == STANDARD_RUNBOOK[0]
