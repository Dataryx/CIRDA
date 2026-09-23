"""Gate decision metrics."""

from __future__ import annotations

import networkx as nx

from cirda_core.config.policy import PolicyConfig
from cirda_core.decision.gate import evaluate_gate
from cirda_core.domain.enums import Verdict

from cirda_bench.methods.base import InferenceResult


def _ground_truth_unsafe(truth_graph: nx.DiGraph, target_id: str) -> bool:
    policy = PolicyConfig(c_min=0.001)
    decision = evaluate_gate(
        possible_graph=truth_graph,
        source_entity_id=target_id,
        coverage=1.0,
        policy=policy,
    )
    return decision.verdict == Verdict.UNSAFE


def false_safe_rate(
    result: InferenceResult,
    truth_graph: nx.DiGraph,
    targets: tuple[str, ...],
) -> float:
    """Fraction of truly-UNSAFE targets incorrectly classified SAFE."""
    unsafe_total = 0
    false_safe = 0

    for target in targets:
        if not _ground_truth_unsafe(truth_graph, target):
            continue
        unsafe_total += 1
        if result.gate_decisions[target].verdict == Verdict.SAFE:
            false_safe += 1

    if unsafe_total == 0:
        return 0.0
    return false_safe / unsafe_total


def decision_coverage(result: InferenceResult, targets: tuple[str, ...]) -> float:
    """Fraction of targets receiving SAFE or UNSAFE (not INDETERMINATE)."""
    if not targets:
        return 0.0
    covered = sum(
        1
        for target in targets
        if result.gate_decisions[target].verdict in {Verdict.SAFE, Verdict.UNSAFE}
    )
    return covered / len(targets)
