"""Kernel scalability benchmark for Table III."""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass

import networkx as nx

from cirda_bench.generator.ecosystem import generate_ecosystem
from cirda_bench.generator.topology import TABLE_III_COUNTS, expected_build_complexity
from cirda_bench.metrics.blast_metrics import build_truth_graph
from cirda_core.analysis.blast_radius import compute_blast_radius
from cirda_core.config.policy import PolicyConfig


@dataclass(frozen=True, slots=True)
class ScalingRow:
    agents: int
    nodes: int
    edges: int
    build_ms: float
    p95_query_ms: float
    complexity_proxy: float


def _measure_build(agents: int, iterations: int = 3) -> tuple[int, int, float]:
    timings: list[float] = []
    nodes = edges = 0
    for i in range(iterations):
        start = time.perf_counter()
        eco = generate_ecosystem(i, num_agents=agents, losses=(0.0,), exact_scaling=True)
        graph = build_truth_graph(eco.entities, eco.ground_truth_edges)
        elapsed = (time.perf_counter() - start) * 1000.0
        timings.append(elapsed)
        nodes = len(eco.entities)
        edges = len(eco.ground_truth_edges)
    return nodes, edges, statistics.mean(timings)


def _measure_queries(graph: nx.DiGraph, samples: int = 64) -> float:
    if not graph:
        return 0.0
    nodes = list(graph.nodes)
    timings: list[float] = []
    policy = PolicyConfig()
    for i in range(samples):
        source = nodes[i % len(nodes)]
        start = time.perf_counter()
        compute_blast_radius(
            graph,
            source,
            criticality_threshold=policy.critical_threshold,
        )
        timings.append((time.perf_counter() - start) * 1000.0)
    timings.sort()
    idx = int(0.95 * (len(timings) - 1))
    return timings[idx]


def run_scaling_benchmark(
    agent_counts: tuple[int, ...] = (50, 100, 250, 500, 1000),
) -> list[ScalingRow]:
    """Run scaling benchmark and return Table III rows."""
    rows: list[ScalingRow] = []
    for agents in agent_counts:
        expected_nodes, expected_edges = TABLE_III_COUNTS[agents]
        nodes, edges, build_ms = _measure_build(agents)
        assert nodes == expected_nodes, f"nodes {nodes} != {expected_nodes}"
        assert edges == expected_edges, f"edges {edges} != {expected_edges}"
        eco = generate_ecosystem(0, num_agents=agents, losses=(0.0,), exact_scaling=True)
        graph = build_truth_graph(eco.entities, eco.ground_truth_edges)
        p95 = _measure_queries(graph)
        rows.append(
            ScalingRow(
                agents=agents,
                nodes=nodes,
                edges=edges,
                build_ms=build_ms,
                p95_query_ms=p95,
                complexity_proxy=expected_build_complexity(nodes, edges),
            )
        )
    return rows
