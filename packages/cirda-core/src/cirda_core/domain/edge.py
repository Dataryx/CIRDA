"""Dependency edge domain model."""

from __future__ import annotations

from dataclasses import dataclass, field

from cirda_core.domain.enums import GraphLayer, Necessity, Relation


@dataclass(frozen=True, slots=True)
class DependencyEdge:
    """A directed dependency edge in the graph."""

    source_id: str
    target_id: str
    relation: Relation
    layer: GraphLayer
    confidence: float
    necessity: Necessity = Necessity.UNKNOWN
    evidence_count: int = 0
    last_observed_epoch: float | None = None
    edge_id: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id:
            raise ValueError("source_id and target_id must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        if self.evidence_count < 0:
            raise ValueError("evidence_count must be non-negative")
