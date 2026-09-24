"""Blast-radius metrics (INV-001 uses G_p)."""

from __future__ import annotations

import networkx as nx

from cirda_core.analysis.blast_radius import compute_blast_radius
from cirda_core.config.policy import PolicyConfig
from cirda_core.graph.kernel import build_digraph

from cirda_bench.methods.base import InferenceResult


def _critical_blast_set(graph: nx.DiGraph, source_id: str) -> frozenset[str]:
    policy = PolicyConfig()
    blast = compute_blast_radius(
        graph,
        source_id,
        criticality_threshold=policy.critical_threshold,
    )
    return blast.critical_reachable


def _graph_for_blast(result: InferenceResult) -> nx.DiGraph:
    return result.blast_graph if result.blast_graph is not None else result.possible_graph


def blast_recall(
    result: InferenceResult,
    truth_graph: nx.DiGraph,
    targets: tuple[str, ...],
) -> float:
    """Mean recall of critical blast nodes against ground truth."""
    graph = _graph_for_blast(result)
    recalls: list[float] = []
    for target in targets:
        true_blast = _critical_blast_set(truth_graph, target)
        if not true_blast:
            continue
        predicted = _critical_blast_set(graph, target)
        recalls.append(len(predicted & true_blast) / len(true_blast))
    if not recalls:
        return 0.0
    return sum(recalls) / len(recalls)


def blast_precision(
    result: InferenceResult,
    truth_graph: nx.DiGraph,
    targets: tuple[str, ...],
) -> float:
    """Mean precision of predicted critical blast against ground truth."""
    graph = _graph_for_blast(result)
    precisions: list[float] = []
    for target in targets:
        predicted = _critical_blast_set(graph, target)
        if not predicted:
            continue
        true_blast = _critical_blast_set(truth_graph, target)
        precisions.append(len(predicted & true_blast) / len(predicted))
    if not precisions:
        return 0.0
    return sum(precisions) / len(precisions)


def build_truth_graph(entities, edges) -> nx.DiGraph:
    """Build ground-truth possible graph."""
    return build_digraph(list(entities), list(edges))
