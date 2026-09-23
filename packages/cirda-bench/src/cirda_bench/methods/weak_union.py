"""Direct union plus weak-channel union baseline."""

from __future__ import annotations

from cirda_core.config.channels import CHANNEL_PROFILES
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import ChannelClass, GraphLayer

from cirda_bench.generator.telemetry import (
    WEAK_UNION_MIN_OBSERVATIONS,
    TelemetryBundle,
    to_channel_observations,
)
from cirda_bench.methods.base import InferenceResult, Method, build_layer_graphs, simple_gate


class WeakUnionMethod(Method):
    """Direct union plus weak channels when observation count threshold met."""

    name = "weak_union"

    def infer(
        self,
        *,
        entities: tuple[Entity, ...],
        ground_truth_edges: tuple[DependencyEdge, ...],
        telemetry: TelemetryBundle,
        targets: tuple[str, ...],
    ) -> InferenceResult:
        inferred: list[DependencyEdge] = []

        for record in telemetry.edge_telemetry:
            obs = to_channel_observations(record.observations)
            direct_count = sum(
                o.count
                for o in obs
                if CHANNEL_PROFILES[o.channel].channel_class == ChannelClass.DIRECT
            )
            weak_count = sum(
                o.count
                for o in obs
                if CHANNEL_PROFILES[o.channel].channel_class == ChannelClass.WEAK
            )

            accepted = direct_count > 0 or weak_count >= WEAK_UNION_MIN_OBSERVATIONS
            if not accepted:
                continue

            total = direct_count + weak_count
            inferred.append(
                DependencyEdge(
                    source_id=record.source_id,
                    target_id=record.target_id,
                    relation=record.relation,
                    layer=GraphLayer.POSSIBLE,
                    confidence=min(1.0, total / 8.0),
                    evidence_count=total,
                    edge_id=record.edge_id,
                )
            )

        g_c, g_p = build_layer_graphs(entities, [], inferred)
        decisions = {target: simple_gate(g_p, target) for target in targets}

        return InferenceResult(
            method_name=self.name,
            inferred_edges=tuple(inferred),
            confirmed_graph=g_c,
            possible_graph=g_p,
            gate_decisions=decisions,
        )
