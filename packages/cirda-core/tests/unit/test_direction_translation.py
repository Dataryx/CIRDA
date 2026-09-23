"""Direction translation tests (INV-005)."""

from __future__ import annotations

import pytest

from cirda_core.domain.enums import GraphLayer, Relation
from cirda_core.inference.direction import RETAINED, REVERSED, translate_to_dependency_edge


def test_reversed_relations_flip_direction() -> None:
    edge = translate_to_dependency_edge(
        actor_id="A",
        counterpart_id="B",
        relation=Relation.CALLS,
        layer=GraphLayer.POSSIBLE,
        confidence=0.5,
    )
    assert edge.source_id == "B"
    assert edge.target_id == "A"


def test_retained_relations_keep_direction() -> None:
    edge = translate_to_dependency_edge(
        actor_id="A",
        counterpart_id="D",
        relation=Relation.WRITES,
        layer=GraphLayer.POSSIBLE,
        confidence=0.5,
    )
    assert edge.source_id == "A"
    assert edge.target_id == "D"


def test_relation_partition_covers_all() -> None:
    assert REVERSED | RETAINED == set(Relation)


@pytest.mark.parametrize("relation", list(REVERSED))
def test_all_reversed(relation: Relation) -> None:
    edge = translate_to_dependency_edge(
        actor_id="X",
        counterpart_id="Y",
        relation=relation,
        layer=GraphLayer.POSSIBLE,
        confidence=0.3,
    )
    assert edge.source_id == "Y"
    assert edge.target_id == "X"


@pytest.mark.parametrize("relation", list(RETAINED))
def test_all_retained(relation: Relation) -> None:
    edge = translate_to_dependency_edge(
        actor_id="X",
        counterpart_id="Y",
        relation=relation,
        layer=GraphLayer.POSSIBLE,
        confidence=0.3,
    )
    assert edge.source_id == "X"
    assert edge.target_id == "Y"
