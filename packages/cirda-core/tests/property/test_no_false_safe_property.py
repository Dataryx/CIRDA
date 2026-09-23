"""Property: gate never returns SAFE under unsafe conditions."""

from __future__ import annotations

import networkx as nx
from hypothesis import given, settings
from hypothesis import strategies as st

from cirda_core.config.constants import C_MIN
from cirda_core.decision.gate import evaluate_gate
from cirda_core.domain.enums import Criticality, Verdict


@given(
    coverage=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    has_critical=st.booleans(),
    truncated=st.booleans(),
)
@settings(max_examples=100)
def test_no_false_safe_property(coverage: float, has_critical: bool, truncated: bool) -> None:
    g: nx.DiGraph = nx.DiGraph()
    g.add_node("source", criticality=Criticality.LOW.value)
    if has_critical:
        g.add_node("crit", criticality=Criticality.CRITICAL.value)
        g.add_edge("source", "crit", confidence=0.9)
    elif truncated:
        for i in range(10):
            g.add_node(f"n{i}", criticality=Criticality.LOW.value)
            if i > 0:
                g.add_edge(f"n{i-1}", f"n{i}", confidence=0.9)

    max_depth = 1 if truncated else None
    decision = evaluate_gate(
        possible_graph=g,
        source_entity_id="source",
        coverage=coverage,
        max_depth=max_depth,
    )

    if has_critical:
        assert decision.verdict == Verdict.UNSAFE
    elif truncated and max_depth is not None and decision.truncated:
        assert decision.verdict != Verdict.SAFE
    elif coverage < C_MIN:
        assert decision.verdict != Verdict.SAFE
