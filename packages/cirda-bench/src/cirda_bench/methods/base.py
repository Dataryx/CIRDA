"""Base method interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import networkx as nx

from cirda_core.domain.decision import GateDecision
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import Verdict
from cirda_core.graph.kernel import build_digraph

from cirda_bench.generator.telemetry import TelemetryBundle, primary_channel


@dataclass(frozen=True, slots=True)
class InferenceResult:
    """Output of one method on one ecosystem at one loss level."""

    method_name: str
    inferred_edges: tuple[DependencyEdge, ...]
    confirmed_graph: nx.DiGraph
    possible_graph: nx.DiGraph
    gate_decisions: dict[str, GateDecision] = field(default_factory=dict)
    edge_f1_edges: tuple[DependencyEdge, ...] = ()

    def edges_for_f1(self) -> tuple[DependencyEdge, ...]:
        """Edges used for Table II edge-F1 (defaults to inferred_edges)."""
        return self.edge_f1_edges if self.edge_f1_edges else self.inferred_edges


class Method(ABC):
    """Benchmark method contract."""

    name: str

    @abstractmethod
    def infer(
        self,
        *,
        entities: tuple[Entity, ...],
        ground_truth_edges: tuple[DependencyEdge, ...],
        telemetry: TelemetryBundle,
        targets: tuple[str, ...],
    ) -> InferenceResult:
        """Run inference and gate evaluation for all targets."""


def simple_gate(
    possible_graph: nx.DiGraph,
    target_id: str,
    *,
    coverage: float = 1.0,
) -> GateDecision:
    """Baseline gate without CIRDA coverage threshold (trace/direct/weak baselines)."""
    from cirda_core.config.policy import PolicyConfig
    from cirda_core.decision.gate import evaluate_gate

    policy = PolicyConfig(c_min=0.001)
    return evaluate_gate(
        possible_graph=possible_graph,
        source_entity_id=target_id,
        coverage=coverage,
        policy=policy,
    )


def direct_primary_edges(telemetry: TelemetryBundle) -> tuple[DependencyEdge, ...]:
    """Edges with primary-channel direct observations (direct_union F1 basis)."""
    from cirda_core.domain.enums import GraphLayer

    inferred: list[DependencyEdge] = []
    for record in telemetry.edge_telemetry:
        primary = primary_channel(record.relation)
        count = record.observations.get(primary, 0)
        if count <= 0:
            continue
        inferred.append(
            DependencyEdge(
                source_id=record.source_id,
                target_id=record.target_id,
                relation=record.relation,
                layer=GraphLayer.POSSIBLE,
                confidence=min(1.0, count / 3.0),
                evidence_count=count,
                edge_id=record.edge_id,
            )
        )
    return tuple(inferred)


def edge_set(edges: list[DependencyEdge] | tuple[DependencyEdge, ...]) -> set[tuple[str, str]]:
    """Normalize edges to (source, target) pairs."""
    return {(edge.source_id, edge.target_id) for edge in edges}


def build_layer_graphs(
    entities: tuple[Entity, ...],
    confirmed: list[DependencyEdge],
    possible: list[DependencyEdge],
) -> tuple[nx.DiGraph, nx.DiGraph]:
    """Build G_c and G_p graphs.

    G_p includes every inferred edge (confirmed edges are a subset of possible).
    """
    from cirda_core.domain.enums import GraphLayer

    g_c = build_digraph(list(entities), confirmed, layer=GraphLayer.CONFIRMED)
    g_p = build_digraph(list(entities), possible)
    return g_c, g_p


def verdict_map(decisions: dict[str, GateDecision]) -> dict[str, Verdict]:
    return {entity_id: decision.verdict for entity_id, decision in decisions.items()}
