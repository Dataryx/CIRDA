"""Criticality sampling by entity type."""

from __future__ import annotations

import random

from cirda_core.domain.enums import Criticality, EntityType

_TYPE_WEIGHTS: dict[EntityType, list[tuple[Criticality, float]]] = {
    EntityType.AGENT: [
        (Criticality.CRITICAL, 0.08),
        (Criticality.HIGH, 0.22),
        (Criticality.MEDIUM, 0.35),
        (Criticality.LOW, 0.25),
        (Criticality.UNKNOWN, 0.10),
    ],
    EntityType.TOOL: [
        (Criticality.CRITICAL, 0.05),
        (Criticality.HIGH, 0.18),
        (Criticality.MEDIUM, 0.32),
        (Criticality.LOW, 0.30),
        (Criticality.UNKNOWN, 0.15),
    ],
    EntityType.SERVICE: [
        (Criticality.CRITICAL, 0.16),
        (Criticality.HIGH, 0.34),
        (Criticality.MEDIUM, 0.28),
        (Criticality.LOW, 0.14),
        (Criticality.UNKNOWN, 0.08),
    ],
    EntityType.DATA: [
        (Criticality.CRITICAL, 0.10),
        (Criticality.HIGH, 0.25),
        (Criticality.MEDIUM, 0.35),
        (Criticality.LOW, 0.20),
        (Criticality.UNKNOWN, 0.10),
    ],
    EntityType.QUEUE: [
        (Criticality.CRITICAL, 0.06),
        (Criticality.HIGH, 0.20),
        (Criticality.MEDIUM, 0.34),
        (Criticality.LOW, 0.28),
        (Criticality.UNKNOWN, 0.12),
    ],
    EntityType.CREDENTIAL: [
        (Criticality.CRITICAL, 0.28),
        (Criticality.HIGH, 0.40),
        (Criticality.MEDIUM, 0.18),
        (Criticality.LOW, 0.08),
        (Criticality.UNKNOWN, 0.06),
    ],
    EntityType.MODEL: [
        (Criticality.CRITICAL, 0.07),
        (Criticality.HIGH, 0.23),
        (Criticality.MEDIUM, 0.35),
        (Criticality.LOW, 0.25),
        (Criticality.UNKNOWN, 0.10),
    ],
}


def sample_criticality(entity_type: EntityType, rng: random.Random) -> Criticality:
    """Sample criticality independently for an entity type."""
    weights = _TYPE_WEIGHTS[entity_type]
    roll = rng.random()
    cumulative = 0.0
    for level, weight in weights:
        cumulative += weight
        if roll <= cumulative:
            return level
    return weights[-1][0]
