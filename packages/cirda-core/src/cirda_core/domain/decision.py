"""Decision domain model."""

from __future__ import annotations

from dataclasses import dataclass, field

from cirda_core.domain.enums import RunbookStage, Verdict


@dataclass(frozen=True, slots=True)
class GateDecision:
    """Tri-state safety gate outcome."""

    verdict: Verdict
    coverage: float
    truncated: bool = False
    hard_blocks: frozenset[str] = field(default_factory=frozenset)
    critical_reachable: frozenset[str] = field(default_factory=frozenset)
    reason_codes: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class RunbookAction:
    """A staged remediation action."""

    stage: RunbookStage
    description: str
    entity_id: str | None = None


@dataclass(frozen=True, slots=True)
class DecisionExplanation:
    """Human-readable explanation of a gate decision."""

    verdict: Verdict
    summary: str
    details: tuple[str, ...] = ()
    suggested_runbook: tuple[RunbookAction, ...] = ()
