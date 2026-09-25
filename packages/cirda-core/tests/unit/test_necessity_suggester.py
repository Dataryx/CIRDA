"""Unit tests for suggest-only necessity heuristics."""

from __future__ import annotations

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import Criticality, EntityType, GraphLayer, Necessity, Relation
from cirda_core.graph.kernel import build_digraph
from cirda_core.graph.necessity_suggester import suggest_necessity


def _entity(eid: str, crit: Criticality) -> Entity:
    return Entity(
        entity_id=eid,
        entity_type=EntityType.SERVICE,
        name=eid,
        criticality=crit,
    )


def _edge(
    src: str,
    tgt: str,
    *,
    necessity: Necessity = Necessity.UNKNOWN,
    confidence: float = 0.9,
    relation: Relation = Relation.WRITES,
) -> DependencyEdge:
    return DependencyEdge(
        source_id=src,
        target_id=tgt,
        relation=relation,
        layer=GraphLayer.POSSIBLE,
        confidence=confidence,
        necessity=necessity,
        edge_id=f"{src}->{tgt}:{relation.value}",
    )


def test_sole_bridge_to_critical_suggests_required() -> None:
    g = build_digraph(
        [
            _entity("A", Criticality.LOW),
            _entity("B", Criticality.CRITICAL),
        ],
        [_edge("A", "B")],
        GraphLayer.POSSIBLE,
    )
    hints = suggest_necessity(g, "A")
    assert len(hints) == 1
    assert hints[0].suggested_necessity == Necessity.REQUIRED.value
    assert hints[0].signals.get("is_critical_bridge") is True


def test_parallel_paths_suggest_redundant_for_secondary() -> None:
    # A→B→C(critical) and A→C; neither edge is a sole cut.
    g = build_digraph(
        [
            _entity("A", Criticality.LOW),
            _entity("B", Criticality.LOW),
            _entity("C", Criticality.CRITICAL),
        ],
        [
            _edge("A", "B", confidence=0.95),
            _edge("B", "C", confidence=0.9),
            _edge("A", "C", confidence=0.5),
        ],
        GraphLayer.POSSIBLE,
    )
    hints = suggest_necessity(g, "A")
    by_edge = {h.edge_id: h for h in hints}
    assert by_edge["A->C:writes"].suggested_necessity == Necessity.REDUNDANT.value
    assert by_edge["A->B:writes"].suggested_necessity == Necessity.REDUNDANT.value
    assert by_edge["B->C:writes"].suggested_necessity == Necessity.REDUNDANT.value


def test_optional_when_target_not_critical() -> None:
    g = build_digraph(
        [
            _entity("A", Criticality.LOW),
            _entity("ledger", Criticality.CRITICAL),
            _entity("queue", Criticality.LOW),
        ],
        [
            _edge("A", "ledger", confidence=0.95),
            _edge("A", "queue", confidence=0.8, relation=Relation.PUBLISHES),
        ],
        GraphLayer.POSSIBLE,
    )
    hints = suggest_necessity(g, "A")
    by_edge = {h.edge_id: h for h in hints}
    assert by_edge["A->ledger:writes"].suggested_necessity == Necessity.REQUIRED.value
    assert by_edge["A->queue:publishes"].suggested_necessity == Necessity.OPTIONAL.value


def test_already_annotated_edges_skipped() -> None:
    g = build_digraph(
        [
            _entity("A", Criticality.LOW),
            _entity("B", Criticality.CRITICAL),
        ],
        [_edge("A", "B", necessity=Necessity.OPTIONAL)],
        GraphLayer.POSSIBLE,
    )
    assert suggest_necessity(g, "A") == []


def test_missing_source_returns_empty() -> None:
    g = build_digraph([_entity("A", Criticality.LOW)], [], GraphLayer.POSSIBLE)
    assert suggest_necessity(g, "missing") == []
