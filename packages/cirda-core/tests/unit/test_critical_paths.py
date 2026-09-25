"""Unit tests for critical path enumeration."""

from __future__ import annotations

from cirda_core.analysis.critical_paths import enumerate_critical_paths
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import Criticality, EntityType, GraphLayer, Necessity, Relation
from cirda_core.graph.kernel import build_digraph


def _entity(eid: str, crit: Criticality) -> Entity:
    return Entity(entity_id=eid, entity_type=EntityType.SERVICE, name=eid, criticality=crit)


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


def test_enumerates_path_to_critical() -> None:
    g = build_digraph(
        [
            _entity("A", Criticality.LOW),
            _entity("B", Criticality.CRITICAL),
        ],
        [_edge("A", "B", confidence=0.8)],
        GraphLayer.POSSIBLE,
    )
    paths = enumerate_critical_paths(g, "A")
    assert len(paths) == 1
    assert paths[0].path_nodes == ("A", "B")
    assert paths[0].path_confidence == 0.8
    assert paths[0].is_critical_path is True


def test_skips_optional_edge_on_critical_path() -> None:
    g = build_digraph(
        [
            _entity("A", Criticality.LOW),
            _entity("ledger", Criticality.CRITICAL),
            _entity("queue", Criticality.HIGH),
        ],
        [
            _edge("A", "ledger", confidence=0.95),
            _edge("A", "queue", confidence=0.9, necessity=Necessity.OPTIONAL, relation=Relation.PUBLISHES),
        ],
        GraphLayer.POSSIBLE,
    )
    paths = enumerate_critical_paths(g, "A")
    assert len(paths) == 1
    assert paths[0].path_nodes == ("A", "ledger")
    assert all("queue" not in p.path_nodes for p in paths)


def test_target_filter_and_empty_source() -> None:
    g = build_digraph(
        [
            _entity("A", Criticality.LOW),
            _entity("B", Criticality.CRITICAL),
            _entity("C", Criticality.CRITICAL),
        ],
        [_edge("A", "B"), _edge("A", "C", confidence=0.5)],
        GraphLayer.POSSIBLE,
    )
    only_c = enumerate_critical_paths(g, "A", target_id="C")
    assert len(only_c) == 1
    assert only_c[0].path_nodes == ("A", "C")
    assert enumerate_critical_paths(g, "missing") == []
