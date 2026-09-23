"""Generator shape validation."""

from __future__ import annotations

import statistics

import pytest

from cirda_bench.generator.ecosystem import generate_ecosystem
from cirda_bench.generator.topology import EDGE_COUNT_MAX, EDGE_COUNT_MIN, TABLE_III_COUNTS
from cirda_core.domain.enums import EntityType


def test_reference_ecosystem_has_145_nodes_and_50_agents() -> None:
    eco = generate_ecosystem(0)
    assert len(eco.entities) == 145
    agents = [e for e in eco.entities if e.entity_type == EntityType.AGENT]
    assert len(agents) == 50


def test_edge_counts_within_normative_range() -> None:
    counts = [len(generate_ecosystem(i).ground_truth_edges) for i in range(150)]
    assert EDGE_COUNT_MIN <= min(counts) <= max(counts) <= EDGE_COUNT_MAX
    assert 580 <= statistics.mean(counts) <= 610


def test_exact_table_iii_scaling_counts() -> None:
    for agents, (nodes, edges) in TABLE_III_COUNTS.items():
        eco = generate_ecosystem(0, num_agents=agents, exact_scaling=True)
        assert len(eco.entities) == nodes
        assert len(eco.ground_truth_edges) == edges


def test_sixty_targets_per_ecosystem() -> None:
    eco = generate_ecosystem(7)
    assert len(eco.target_entity_ids) == 60
