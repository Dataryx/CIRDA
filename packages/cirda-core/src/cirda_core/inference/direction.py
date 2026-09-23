"""Relation-to-dependency direction translation (INV-005)."""

from __future__ import annotations

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import GraphLayer, Relation
from cirda_core.domain.errors import InvalidEdgeError

REVERSED: frozenset[Relation] = frozenset(
    {
        Relation.DELEGATES,
        Relation.CALLS,
        Relation.READS,
        Relation.CONSUMES,
        Relation.AUTHENTICATES,
        Relation.USES_MODEL,
    }
)

RETAINED: frozenset[Relation] = frozenset(
    {
        Relation.WRITES,
        Relation.PUBLISHES,
    }
)

assert REVERSED | RETAINED == set(Relation), "Relation partition must cover all relations"


def translate_to_dependency_edge(
    *,
    actor_id: str,
    counterpart_id: str,
    relation: Relation,
    layer: GraphLayer,
    confidence: float,
    evidence_count: int = 0,
    last_observed_epoch: float | None = None,
) -> DependencyEdge:
    """
    Construct a dependency edge from an observed relation (INV-005).

    REVERSED relations flip direction: actor depends on counterpart becomes
    counterpart -> actor. RETAINED relations keep actor -> counterpart.
    """
    if relation in REVERSED:
        source_id, target_id = counterpart_id, actor_id
    elif relation in RETAINED:
        source_id, target_id = actor_id, counterpart_id
    else:
        raise InvalidEdgeError(f"Unknown relation: {relation}")

    return DependencyEdge(
        source_id=source_id,
        target_id=target_id,
        relation=relation,
        layer=layer,
        confidence=confidence,
        evidence_count=evidence_count,
        last_observed_epoch=last_observed_epoch,
        edge_id=f"{source_id}->{target_id}:{relation.value}",
    )
