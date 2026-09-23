"""Graph topology generation with calibrated edge counts."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import EntityType, GraphLayer, Necessity, Relation
from cirda_core.inference.direction import translate_to_dependency_edge

# Normative scaling counts for Table III (agents, nodes, edges).
TABLE_III_COUNTS: dict[int, tuple[int, int]] = {
    50: (145, 592),
    100: (293, 1210),
    250: (731, 3025),
    500: (1465, 6093),
    1000: (2930, 12263),
}

# Non-agent entity mix for the reference 95-node remainder at 50 agents.
_NON_AGENT_MIX: list[tuple[EntityType, int]] = [
    (EntityType.TOOL, 20),
    (EntityType.SERVICE, 15),
    (EntityType.DATA, 20),
    (EntityType.QUEUE, 15),
    (EntityType.CREDENTIAL, 10),
    (EntityType.MODEL, 15),
]

# Typed operations with valid source/target semantics.
_RELATION_RULES: list[tuple[Relation, EntityType, EntityType, float]] = [
    (Relation.DELEGATES, EntityType.AGENT, EntityType.AGENT, 0.10),
    (Relation.CALLS, EntityType.AGENT, EntityType.TOOL, 0.18),
    (Relation.CALLS, EntityType.AGENT, EntityType.SERVICE, 0.14),
    (Relation.READS, EntityType.AGENT, EntityType.DATA, 0.12),
    (Relation.WRITES, EntityType.AGENT, EntityType.DATA, 0.08),
    (Relation.PUBLISHES, EntityType.SERVICE, EntityType.QUEUE, 0.10),
    (Relation.CONSUMES, EntityType.AGENT, EntityType.QUEUE, 0.10),
    (Relation.AUTHENTICATES, EntityType.AGENT, EntityType.CREDENTIAL, 0.08),
    (Relation.USES_MODEL, EntityType.AGENT, EntityType.MODEL, 0.10),
    (Relation.CALLS, EntityType.SERVICE, EntityType.SERVICE, 0.10),
]

EDGE_COUNT_MEAN = 593.44
EDGE_COUNT_SD = 17.29
EDGE_COUNT_MIN = 551
EDGE_COUNT_MAX = 639

_EDGE_COUNT_MEAN = EDGE_COUNT_MEAN
_EDGE_COUNT_SD = EDGE_COUNT_SD
_EDGE_COUNT_MIN = EDGE_COUNT_MIN
_EDGE_COUNT_MAX = EDGE_COUNT_MAX


@dataclass(frozen=True, slots=True)
class TopologySpec:
    """Resolved topology dimensions."""

    num_agents: int
    num_nodes: int
    target_edges: int


def resolve_topology(
    num_agents: int,
    ecosystem_id: int,
    rng: random.Random,
    *,
    exact_scaling: bool = False,
) -> TopologySpec:
    """Resolve node and edge counts for an ecosystem."""
    if exact_scaling and num_agents in TABLE_III_COUNTS:
        num_nodes, target_edges = TABLE_III_COUNTS[num_agents]
        return TopologySpec(num_agents, num_nodes, target_edges)

    if num_agents == 50:
        sampled = _sample_reference_edge_count(rng)
        return TopologySpec(num_agents, 145, sampled)

    num_nodes = round(num_agents * 2.93)
    target_edges = round(num_agents * 12.1)
    return TopologySpec(num_agents, num_nodes, target_edges)


def _sample_reference_edge_count(rng: random.Random) -> int:
    """Sample edge count for the 145-node reference ecosystem."""
    value = rng.gauss(_EDGE_COUNT_MEAN, _EDGE_COUNT_SD)
    return int(max(_EDGE_COUNT_MIN, min(_EDGE_COUNT_MAX, round(value))))


def non_agent_counts(num_agents: int, num_nodes: int) -> dict[EntityType, int]:
    """Scale non-agent entity counts to fill ``num_nodes - num_agents`` slots."""
    remainder = num_nodes - num_agents
    if remainder <= 0:
        return {}

    if num_agents == 50 and num_nodes == 145:
        return {entity_type: count for entity_type, count in _NON_AGENT_MIX}

    base_total = sum(count for _, count in _NON_AGENT_MIX)
    scale = remainder / base_total
    counts: dict[EntityType, int] = {}
    allocated = 0
    for entity_type, count in _NON_AGENT_MIX[:-1]:
        scaled = max(1, round(count * scale))
        counts[entity_type] = scaled
        allocated += scaled
    last_type = _NON_AGENT_MIX[-1][0]
    counts[last_type] = max(1, remainder - allocated)
    return counts


def generate_edges(
    entity_ids_by_type: dict[EntityType, list[str]],
    target_edges: int,
    rng: random.Random,
) -> list[DependencyEdge]:
    """Generate typed dependency edges until ``target_edges`` is reached."""
    edges: list[DependencyEdge] = []
    seen: set[tuple[str, str, Relation]] = set()

    weights = [rule[3] for rule in _RELATION_RULES]
    attempts = 0
    max_attempts = target_edges * 40

    while len(edges) < target_edges and attempts < max_attempts:
        attempts += 1
        relation, src_type, dst_type, _ = rng.choices(_RELATION_RULES, weights=weights, k=1)[0]
        sources = entity_ids_by_type.get(src_type, [])
        targets = entity_ids_by_type.get(dst_type, [])
        if not sources or not targets:
            continue

        actor_id = rng.choice(sources)
        counterpart_id = rng.choice(targets)
        if actor_id == counterpart_id:
            continue

        key = (actor_id, counterpart_id, relation)
        if key in seen:
            continue
        seen.add(key)

        dep = translate_to_dependency_edge(
            actor_id=actor_id,
            counterpart_id=counterpart_id,
            relation=relation,
            layer=GraphLayer.CONFIRMED,
            confidence=1.0,
            evidence_count=rng.randint(3, 12),
        )
        edges.append(
            DependencyEdge(
                source_id=dep.source_id,
                target_id=dep.target_id,
                relation=dep.relation,
                layer=GraphLayer.CONFIRMED,
                confidence=1.0,
                necessity=Necessity.UNKNOWN,
                evidence_count=dep.evidence_count,
                edge_id=dep.edge_id,
            )
        )

    # Fill any shortfall with agent->service calls to guarantee exact count.
    agents = entity_ids_by_type.get(EntityType.AGENT, [])
    services = entity_ids_by_type.get(EntityType.SERVICE, [])
    idx = 0
    while len(edges) < target_edges and agents and services:
        actor = agents[idx % len(agents)]
        counterpart = services[idx % len(services)]
        idx += 1
        relation = Relation.CALLS
        key = (actor, counterpart, relation)
        if key in seen:
            continue
        seen.add(key)
        dep = translate_to_dependency_edge(
            actor_id=actor,
            counterpart_id=counterpart,
            relation=relation,
            layer=GraphLayer.CONFIRMED,
            confidence=1.0,
            evidence_count=4,
        )
        edges.append(
            DependencyEdge(
                source_id=dep.source_id,
                target_id=dep.target_id,
                relation=dep.relation,
                layer=GraphLayer.CONFIRMED,
                confidence=1.0,
                necessity=Necessity.UNKNOWN,
                evidence_count=4,
                edge_id=dep.edge_id,
            )
        )

    edges = ensure_agent_outgoing_edges(edges, entity_ids_by_type, rng)
    return edges


def ensure_agent_outgoing_edges(
    edges: list[DependencyEdge],
    entity_ids_by_type: dict[EntityType, list[str]],
    rng: random.Random,
) -> list[DependencyEdge]:
    """Ensure every agent has at least one outgoing dependency (agent -> X).

    Replaces random non-backbone edges to preserve the target edge count.
    """
    agents = entity_ids_by_type.get(EntityType.AGENT, [])
    data_nodes = entity_ids_by_type.get(EntityType.DATA, [])
    if not agents or not data_nodes:
        return edges

    augmented = list(edges)
    outgoing_sources = {edge.source_id for edge in augmented}
    seen = {(edge.source_id, edge.target_id, edge.relation) for edge in augmented}
    replaceable = list(range(len(augmented)))

    for agent in agents:
        if agent in outgoing_sources:
            continue
        for _ in range(24):
            target = rng.choice(data_nodes)
            relation = Relation.WRITES
            key = (agent, target, relation)
            if key in seen:
                continue

            if not replaceable:
                break
            victim_idx = rng.choice(replaceable)
            victim = augmented[victim_idx]
            if victim.source_id == agent:
                continue

            dep = translate_to_dependency_edge(
                actor_id=agent,
                counterpart_id=target,
                relation=relation,
                layer=GraphLayer.CONFIRMED,
                confidence=1.0,
                evidence_count=rng.randint(8, 14),
            )
            new_edge = DependencyEdge(
                source_id=dep.source_id,
                target_id=dep.target_id,
                relation=dep.relation,
                layer=GraphLayer.CONFIRMED,
                confidence=1.0,
                necessity=Necessity.UNKNOWN,
                evidence_count=dep.evidence_count,
                edge_id=dep.edge_id,
            )

            seen.discard((victim.source_id, victim.target_id, victim.relation))
            seen.add(key)
            if victim.source_id in outgoing_sources:
                if not any(e.source_id == victim.source_id for i, e in enumerate(augmented) if i != victim_idx):
                    outgoing_sources.discard(victim.source_id)
            augmented[victim_idx] = new_edge
            outgoing_sources.add(agent)
            break

    return augmented


def expected_build_complexity(num_nodes: int, num_edges: int) -> float:
    """Return n log n style complexity proxy for scalability shape tests."""
    if num_nodes <= 0:
        return 0.0
    return num_edges * math.log2(num_nodes + 1)
