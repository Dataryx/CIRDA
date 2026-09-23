"""Synthetic ecosystem assembly."""

from __future__ import annotations

import random
from dataclasses import dataclass

from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import EntityType

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


def _select_targets(
    entities: list[Entity],
    edges: list,
    ecosystem_id: int,
    count: int,
) -> tuple[str, ...]:
    """Select 60 deterministic change targets with outgoing dependency paths."""
    rng = make_rng(seed_tag("ecosystem", ecosystem_id), 0, "targets")
    outgoing = {edge.source_id for edge in edges}

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
    rng.shuffle(agents)
    rng.shuffle(others)

    selected = agents[: min(len(agents), count)]
    if len(selected) < count:
        selected.extend(others[: count - len(selected)])
    if len(selected) < count:
        remainder = [e.entity_id for e in entities if e.entity_id in outgoing]
        rng.shuffle(remainder)
        for entity_id in remainder:
            if entity_id not in selected:
                selected.append(entity_id)
            if len(selected) >= count:
                break
    return tuple(selected[:count])
