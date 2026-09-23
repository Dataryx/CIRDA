"""Criticality analysis."""

from __future__ import annotations

from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import Criticality


_CRITICALITY_RANK: dict[Criticality, int] = {
    Criticality.CRITICAL: 4,
    Criticality.HIGH: 3,
    Criticality.MEDIUM: 2,
    Criticality.LOW: 1,
    Criticality.UNKNOWN: 0,
}


def is_at_or_above(entity: Entity, threshold: Criticality) -> bool:
    """Return True if entity criticality meets or exceeds threshold."""
    return _CRITICALITY_RANK[entity.criticality] >= _CRITICALITY_RANK[threshold]


def max_criticality(entities: list[Entity]) -> Criticality:
    """Return highest criticality among entities."""
    if not entities:
        return Criticality.UNKNOWN
    return max(entities, key=lambda e: _CRITICALITY_RANK[e.criticality]).criticality
