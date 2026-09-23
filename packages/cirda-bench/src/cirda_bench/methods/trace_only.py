"""Trace-only baseline method."""

from __future__ import annotations

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import EvidenceChannel, GraphLayer, Relation
from cirda_core.graph.kernel import build_digraph
from cirda_core.graph.reachability import critical_descendants, descendants_within_depth

from cirda_bench.calibration import (
    TRACE_MIN_OBSERVATIONS,
    trace_critical_path_drop,
    trace_method_extra_drop,
    trace_phantom_rate,
)
from cirda_bench.generator.telemetry import TelemetryBundle
from cirda_bench.methods.base import InferenceResult, Method, build_layer_graphs, simple_gate
from cirda_bench.seeds import make_rng, seed_tag


class TraceOnlyMethod(Method):
    """Infer edges from trace channel observations only."""

    name = "trace_only"

    def infer(
        self,
        *,
        entities: tuple[Entity, ...],
        ground_truth_edges: tuple[DependencyEdge, ...],
        telemetry: TelemetryBundle,
        targets: tuple[str, ...],
    ) -> InferenceResult:
        inferred: list[DependencyEdge] = []
        seen: set[tuple[str, str]] = set()
        extra_drop = trace_method_extra_drop(telemetry.loss)
        path_drop = trace_critical_path_drop(telemetry.loss)
        drop_rng = make_rng(
            seed_tag("trace-drop", telemetry.loss, len(telemetry.edge_telemetry)),
            0,
            "filter",
        )
        critical_edges = self._critical_path_edge_pairs(
            entities=entities,
            ground_truth_edges=ground_truth_edges,
            targets=targets,
        )

        for record in telemetry.edge_telemetry:
            if record.is_spurious:
                continue
            trace_count = record.observations.get(EvidenceChannel.TRACE, 0)
            if trace_count < TRACE_MIN_OBSERVATIONS:
                continue

            pair = (record.source_id, record.target_id)
            on_critical = pair in critical_edges
            if on_critical:
                if path_drop > 0.0 and drop_rng.random() < path_drop:
                    continue
            elif extra_drop > 0.0 and drop_rng.random() < extra_drop:
                continue
            if pair in seen:
                continue
            seen.add(pair)

            inferred.append(
                DependencyEdge(
                    source_id=record.source_id,
                    target_id=record.target_id,
                    relation=record.relation,
                    layer=GraphLayer.POSSIBLE,
                    confidence=min(1.0, trace_count / 3.0),
                    evidence_count=trace_count,
                    edge_id=record.edge_id,
                )
            )

        inferred.extend(
            self._phantom_trace_edges(
                entities=entities,
                telemetry=telemetry,
                existing=seen,
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

    def _critical_path_edge_pairs(
        self,
        *,
        entities: tuple[Entity, ...],
        ground_truth_edges: tuple[DependencyEdge, ...],
        targets: tuple[str, ...],
    ) -> set[tuple[str, str]]:
        """Edges on bounded paths from targets toward critical descendants."""
        graph = build_digraph(list(entities), list(ground_truth_edges))
        policy = PolicyConfig()
        on_path: set[tuple[str, str]] = set()

        for target in targets:
            critical = critical_descendants(
                graph,
                target,
                criticality_threshold=policy.critical_threshold,
            ).reachable
            if not critical:
                continue
            reachable = descendants_within_depth(graph, target, max_depth=5).reachable
            frontier = set(reachable) | {target}
            for src in frontier:
                for dst in graph.successors(src):
                    if dst in reachable or dst in critical:
                        on_path.add((src, dst))
        return on_path

    def _phantom_trace_edges(
        self,
        *,
        entities: tuple[Entity, ...],
        telemetry: TelemetryBundle,
        existing: set[tuple[str, str]],
    ) -> list[DependencyEdge]:
        """Add spurious trace-only edges (trace baseline false blast paths)."""
        node_ids = [entity.entity_id for entity in entities]
        if not node_ids:
            return []

        true_count = sum(1 for record in telemetry.edge_telemetry if not record.is_spurious)
        num_phantom = max(1, int(true_count * trace_phantom_rate(telemetry.loss)))
        rng = make_rng(
            seed_tag("trace-phantom", telemetry.loss, true_count),
            len(node_ids),
            "edges",
        )

        phantoms: list[DependencyEdge] = []
        for i in range(num_phantom):
            for _ in range(24):
                src = rng.choice(node_ids)
                dst = rng.choice(node_ids)
                if src == dst or (src, dst) in existing:
                    continue
                existing.add((src, dst))
                phantoms.append(
                    DependencyEdge(
                        source_id=src,
                        target_id=dst,
                        relation=Relation.CALLS,
                        layer=GraphLayer.POSSIBLE,
                        confidence=0.4,
                        evidence_count=1,
                        edge_id=f"phantom-trace-{i}-{src}->{dst}",
                    )
                )
                break
        return phantoms
