"""Apply high-confidence necessity hints (flag-gated auto-mutate)."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_core.domain.enums import Necessity
from cirda_core.graph.necessity_suggester import NecessityHint


@dataclass(frozen=True, slots=True)
class NecessityMutation:
    """A proposed necessity write derived from a hint."""

    edge_id: str
    source_id: str
    target_id: str
    from_necessity: str
    to_necessity: str
    confidence: float
    rationale: str


def select_auto_mutations(
    hints: list[NecessityHint],
    *,
    min_confidence: float = 0.85,
    allowed_labels: frozenset[str] | None = None,
) -> list[NecessityMutation]:
    """
    Select hints eligible for auto-mutate.

    Default safety: only ``required`` at high confidence (load-bearing cuts).
    Optional/redundant require an expanded allow-list.
    """
    allowed = allowed_labels or frozenset({Necessity.REQUIRED.value})
    selected: list[NecessityMutation] = []
    for hint in hints:
        if hint.current_necessity != Necessity.UNKNOWN.value:
            continue
        if hint.suggested_necessity not in allowed:
            continue
        if hint.confidence < min_confidence:
            continue
        selected.append(
            NecessityMutation(
                edge_id=hint.edge_id,
                source_id=hint.source_id,
                target_id=hint.target_id,
                from_necessity=hint.current_necessity,
                to_necessity=hint.suggested_necessity,
                confidence=hint.confidence,
                rationale=hint.rationale,
            )
        )
    return selected
