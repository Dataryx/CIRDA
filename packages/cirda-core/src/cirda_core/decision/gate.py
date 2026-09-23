"""Tri-state safety gate (INV-001)."""

from __future__ import annotations

import networkx as nx

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.decision import GateDecision
from cirda_core.domain.enums import GraphLayer, Verdict
from cirda_core.graph.reachability import critical_descendants


def evaluate_gate(
    *,
    possible_graph: nx.DiGraph,
    source_entity_id: str,
    coverage: float,
    policy: PolicyConfig | None = None,
    max_depth: int | None = None,
    max_nodes: int | None = None,
    ingest_lag_seconds: float = 0.0,
) -> GateDecision:
    """
    Evaluate tri-state safety gate using G_p (possible layer) only (INV-001).

    UNSAFE if critical descendant reachable in G_p.
    SAFE if none AND C >= C_min AND no hard blocks AND not truncated.
    INDETERMINATE otherwise.
    """
    cfg = policy or PolicyConfig()
    reason_codes: set[str] = set()

    reach = critical_descendants(
        possible_graph,
        source_entity_id,
        criticality_threshold=cfg.critical_threshold,
        max_depth=max_depth,
        max_nodes=max_nodes,
    )

    if reach.reachable:
        reason_codes.add("critical_descendant_reachable")
        return GateDecision(
            verdict=Verdict.UNSAFE,
            coverage=coverage,
            truncated=reach.truncated,
            hard_blocks=cfg.hard_blocks,
            critical_reachable=reach.reachable,
            reason_codes=frozenset(reason_codes),
        )

    if reach.truncated:
        reason_codes.add("truncated_traversal")
        return GateDecision(
            verdict=Verdict.INDETERMINATE,
            coverage=coverage,
            truncated=True,
            hard_blocks=cfg.hard_blocks,
            reason_codes=frozenset(reason_codes),
        )

    if coverage < cfg.c_min:
        reason_codes.add("coverage_below_threshold")
        return GateDecision(
            verdict=Verdict.INDETERMINATE,
            coverage=coverage,
            truncated=False,
            hard_blocks=cfg.hard_blocks,
            reason_codes=frozenset(reason_codes),
        )

    if ingest_lag_seconds > cfg.max_ingest_lag_seconds:
        reason_codes.add("ingest_lag_exceeded")
        return GateDecision(
            verdict=Verdict.INDETERMINATE,
            coverage=coverage,
            truncated=False,
            hard_blocks=cfg.hard_blocks,
            reason_codes=frozenset(reason_codes),
        )

    if cfg.hard_blocks:
        reason_codes.add("hard_block_present")
        return GateDecision(
            verdict=Verdict.INDETERMINATE,
            coverage=coverage,
            truncated=False,
            hard_blocks=cfg.hard_blocks,
            reason_codes=frozenset(reason_codes),
        )

    return GateDecision(
        verdict=Verdict.SAFE,
        coverage=coverage,
        truncated=False,
        hard_blocks=frozenset(),
        reason_codes=frozenset({"all_checks_passed"}),
    )


def evaluate_gate_from_layers(
    *,
    confirmed_graph: nx.DiGraph,
    possible_graph: nx.DiGraph,
    source_entity_id: str,
    coverage: float,
    policy: PolicyConfig | None = None,
    **kwargs: object,
) -> GateDecision:
    """
    Gate evaluation wrapper; blast radius always uses possible_graph (INV-001).

    confirmed_graph is accepted for API symmetry but never used for reachability.
    """
    _ = confirmed_graph
    _ = GraphLayer
    return evaluate_gate(
        possible_graph=possible_graph,
        source_entity_id=source_entity_id,
        coverage=coverage,
        policy=policy,
        **kwargs,  # type: ignore[arg-type]
    )
