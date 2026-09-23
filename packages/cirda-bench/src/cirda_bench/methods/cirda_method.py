"""Full CIRDA method using cirda_core."""

from __future__ import annotations

from cirda_core.config.policy import PolicyConfig
from cirda_core.coverage.benchmark_estimator import benchmark_coverage
from cirda_core.coverage.inputs import CoverageInputs
from cirda_core.decision.gate import evaluate_gate_from_layers
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import GraphLayer
from cirda_core.graph.layers import classify_layer
from cirda_core.inference.fusion import fuse_channels, has_direct_evidence

from cirda_bench.generator.telemetry import TelemetryBundle, to_channel_observations
from cirda_bench.methods.base import (
    InferenceResult,
    Method,
    build_layer_graphs,
)


class CirdaMethod(Method):
    """CIRDA pipeline: fusion, G_c/G_p layering, benchmark coverage gate."""

    name = "cirda"

    def infer(
        self,
        *,
        entities: tuple[Entity, ...],
        ground_truth_edges: tuple[DependencyEdge, ...],
        telemetry: TelemetryBundle,
        targets: tuple[str, ...],
    ) -> InferenceResult:
        policy = PolicyConfig()
        confirmed: list[DependencyEdge] = []
        possible: list[DependencyEdge] = []

        # Fuse ALL telemetry including weak noise — no oracle spurious filter.
        # Edge F1 is measured on the confirmed graph (S >= theta_c), matching the paper.
        for record in telemetry.edge_telemetry:
            obs = to_channel_observations(record.observations)
            if not obs:
                continue

            strength = fuse_channels(obs)
            layer = classify_layer(
                strength,
                has_direct_evidence(obs),
                policy=policy,
            )
            if layer is None:
                continue
            edge = DependencyEdge(
                source_id=record.source_id,
                target_id=record.target_id,
                relation=record.relation,
                layer=layer,
                confidence=strength,
                evidence_count=sum(o.count for o in obs),
                edge_id=record.edge_id,
            )
            if layer == GraphLayer.CONFIRMED:
                confirmed.append(edge)
            else:
                possible.append(edge)

        # Confirmed edges are also members of G_p (INV-001 blast reads G_p).
        possible_all = possible + confirmed
        g_c, g_p = build_layer_graphs(entities, confirmed, possible_all)

        entity_ids = frozenset(entity.entity_id for entity in entities)
        coverage_inputs = CoverageInputs(
            observed_entity_ids=entity_ids,
            total_entity_ids=entity_ids,
        )
        coverage = benchmark_coverage(telemetry.loss, coverage_inputs).coverage

        decisions = {}
        for target in targets:
            decisions[target] = evaluate_gate_from_layers(
                confirmed_graph=g_c,
                possible_graph=g_p,
                source_entity_id=target,
                coverage=coverage,
                policy=policy,
            )

        return InferenceResult(
            method_name=self.name,
            inferred_edges=tuple(confirmed),
            confirmed_graph=g_c,
            possible_graph=g_p,
            gate_decisions=decisions,
        )
