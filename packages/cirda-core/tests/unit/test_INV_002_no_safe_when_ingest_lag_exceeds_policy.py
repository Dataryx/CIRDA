"""INV-002: no SAFE when ingest lag exceeds policy."""

from __future__ import annotations

import networkx as nx

from cirda_core.config.policy import PolicyConfig
from cirda_core.decision.gate import evaluate_gate
from cirda_core.domain.enums import Criticality, Verdict


def test_INV_002_no_safe_when_ingest_lag_exceeds_policy() -> None:
    g: nx.DiGraph = nx.DiGraph()
    g.add_node("source", criticality=Criticality.LOW.value)
    policy = PolicyConfig(max_ingest_lag_seconds=60.0)
    decision = evaluate_gate(
        possible_graph=g,
        source_entity_id="source",
        coverage=1.0,
        policy=policy,
        ingest_lag_seconds=120.0,
    )
    assert decision.verdict != Verdict.SAFE
    assert decision.verdict == Verdict.INDETERMINATE
