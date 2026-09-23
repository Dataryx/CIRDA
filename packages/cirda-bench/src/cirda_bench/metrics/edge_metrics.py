"""Edge recovery metrics."""

from __future__ import annotations

from cirda_core.domain.edge import DependencyEdge

from cirda_bench.methods.base import edge_set


def edge_precision(
    inferred: tuple[DependencyEdge, ...] | list[DependencyEdge],
    truth: tuple[DependencyEdge, ...] | list[DependencyEdge],
) -> float:
    inferred_pairs = edge_set(inferred)
    truth_pairs = edge_set(truth)
    if not inferred_pairs:
        return 0.0
    return len(inferred_pairs & truth_pairs) / len(inferred_pairs)


def edge_recall(
    inferred: tuple[DependencyEdge, ...] | list[DependencyEdge],
    truth: tuple[DependencyEdge, ...] | list[DependencyEdge],
) -> float:
    inferred_pairs = edge_set(inferred)
    truth_pairs = edge_set(truth)
    if not truth_pairs:
        return 1.0
    return len(inferred_pairs & truth_pairs) / len(truth_pairs)


def edge_f1(
    inferred: tuple[DependencyEdge, ...] | list[DependencyEdge],
    truth: tuple[DependencyEdge, ...] | list[DependencyEdge],
) -> float:
    precision = edge_precision(inferred, truth)
    recall = edge_recall(inferred, truth)
    if precision + recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)
