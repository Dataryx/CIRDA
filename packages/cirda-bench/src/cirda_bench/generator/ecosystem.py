"""Synthetic ecosystem assembly."""

from __future__ import annotations

import random
from dataclasses import dataclass

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import EntityType
from cirda_core.graph.kernel import build_digraph
from cirda_core.graph.reachability import critical_descendants

from cirda_bench.generator.criticality import sample_criticality
from cirda_bench.generator.telemetry import TelemetryBundle, build_telemetry_bundle
from cirda_bench.generator.topology import (
    TopologySpec,
    generate_edges,
    non_agent_counts,
    resolve_topology,
)
from cirda_bench.seeds import make_rng, seed_tag


@dataclass(frozen=True, slots=True)
class Ecosystem:
    """One benchmark ecosystem with ground truth and telemetry."""

    ecosystem_id: int
    spec: TopologySpec
    entities: tuple[Entity, ...]
    ground_truth_edges: tuple  # tuple[DependencyEdge, ...]
    telemetry_by_loss: dict[float, TelemetryBundle]
    target_entity_ids: tuple[str, ...]


def _entity_id(entity_type: EntityType, index: int) -> str:
    return f"{entity_type.value}-{index:03d}"


def generate_ecosystem(
    ecosystem_id: int,
    *,
    num_agents: int = 50,
    losses: tuple[float, ...] = (0.0, 0.15, 0.30, 0.45, 0.60),
    exact_scaling: bool = False,
) -> Ecosystem:
    """Generate a deterministic ecosystem."""
    rng = make_rng(seed_tag("ecosystem", ecosystem_id), 0, "topology")
    spec = resolve_topology(num_agents, ecosystem_id, rng, exact_scaling=exact_scaling)

    entities: list[Entity] = []
    entity_ids_by_type: dict[EntityType, list[str]] = {}

    for i in range(spec.num_agents):
        entity_type = EntityType.AGENT
        entity_id = _entity_id(entity_type, i)
        crit_rng = make_rng(seed_tag("ecosystem", ecosystem_id), i, "criticality")
        entities.append(
            Entity(
                entity_id=entity_id,
                entity_type=entity_type,
                name=f"agent-{i}",
                criticality=sample_criticality(entity_type, crit_rng),
            )
        )
        entity_ids_by_type.setdefault(entity_type, []).append(entity_id)

    type_counts = non_agent_counts(spec.num_agents, spec.num_nodes)
    for entity_type, count in type_counts.items():
        for i in range(count):
            entity_id = _entity_id(entity_type, i)
            crit_rng = make_rng(
                seed_tag("ecosystem", ecosystem_id, entity_type.value),
                i,
                "criticality",
            )
            entities.append(
                Entity(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    name=f"{entity_type.value}-{i}",
                    criticality=sample_criticality(entity_type, crit_rng),
                )
            )
            entity_ids_by_type.setdefault(entity_type, []).append(entity_id)

    edge_rng = make_rng(seed_tag("ecosystem", ecosystem_id), 0, "edges")
    edges = generate_edges(entity_ids_by_type, spec.target_edges, edge_rng)

    all_node_ids = [entity.entity_id for entity in entities]
    telemetry_by_loss: dict[float, TelemetryBundle] = {}
    for loss in losses:
        tel_rng = make_rng(seed_tag("ecosystem", ecosystem_id), int(loss * 100), "telemetry")
        telemetry_by_loss[loss] = build_telemetry_bundle(edges, all_node_ids, loss, tel_rng)

    target_entity_ids = _select_targets(entities, edges, ecosystem_id, count=60)
    return Ecosystem(
        ecosystem_id=ecosystem_id,
        spec=spec,
        entities=tuple(entities),
        ground_truth_edges=tuple(edges),
        telemetry_by_loss=telemetry_by_loss,
        target_entity_ids=target_entity_ids,
    )


def _out_degree_by_source(edges: list) -> dict[str, int]:
    out_degree: dict[str, int] = {}
    for edge in edges:
        out_degree[edge.source_id] = out_degree.get(edge.source_id, 0) + 1
    return out_degree


def _ground_truth_unsafe_sources(entities: list[Entity], edges: list) -> set[str]:
    """Entities with at least one critical descendant in the ground-truth graph."""
    graph = build_digraph(list(entities), list(edges))
    policy = PolicyConfig()
    unsafe: set[str] = set()
    for entity in entities:
        reach = critical_descendants(
            graph,
            entity.entity_id,
            criticality_threshold=policy.critical_threshold,
        )
        if reach.reachable:
            unsafe.add(entity.entity_id)
    return unsafe


def _rank_by_outgoing(
    entity_ids: list[str],
    out_degree: dict[str, int],
    rng: random.Random,
    *,
    unsafe_sources: set[str] | None = None,
) -> list[str]:
    """Prefer ground-truth UNSAFE agents with higher out-degree."""
    unsafe_sources = unsafe_sources or set()
    by_tier: dict[tuple[int, int], list[str]] = {}
    for entity_id in entity_ids:
        tier = (1 if entity_id in unsafe_sources else 0, out_degree.get(entity_id, 0))
        by_tier.setdefault(tier, []).append(entity_id)

    ranked: list[str] = []
    for tier in sorted(by_tier.keys(), reverse=True):
        bucket = by_tier[tier]
        rng.shuffle(bucket)
        ranked.extend(bucket)
    return ranked


def _select_targets(
    entities: list[Entity],
    edges: list,
    ecosystem_id: int,
    count: int,
) -> tuple[str, ...]:
    """Select 60 deterministic change targets with outgoing dependency paths."""
    rng = make_rng(seed_tag("ecosystem", ecosystem_id), 0, "targets")
    out_degree = _out_degree_by_source(edges)
    outgoing = set(out_degree)
    unsafe_sources = _ground_truth_unsafe_sources(entities, edges)

    agents = [
        e.entity_id
        for e in entities
        if e.entity_type == EntityType.AGENT and e.entity_id in outgoing
    ]
    others = [
        e.entity_id
        for e in entities
        if e.entity_type != EntityType.AGENT and e.entity_id in outgoing
    ]

    ranked = _rank_by_outgoing(
        agents, out_degree, rng, unsafe_sources=unsafe_sources
    ) + _rank_by_outgoing(others, out_degree, rng, unsafe_sources=unsafe_sources)
    if len(ranked) < count:
        remainder = _rank_by_outgoing(
            [e.entity_id for e in entities if e.entity_id in outgoing],
            out_degree,
            rng,
            unsafe_sources=unsafe_sources,
        )
        for entity_id in remainder:
            if entity_id not in ranked:
                ranked.append(entity_id)
            if len(ranked) >= count:
                break
    return tuple(ranked[:count])
