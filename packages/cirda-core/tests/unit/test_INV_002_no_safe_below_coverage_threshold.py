"""INV-002: no SAFE below coverage threshold."""

from __future__ import annotations

import networkx as nx
import pytest

from cirda_core.config.constants import C_MIN
from cirda_core.decision.gate import evaluate_gate
from cirda_core.domain.enums import Criticality, Verdict


def _safe_graph() -> nx.DiGraph:
    g: nx.DiGraph = nx.DiGraph()
    g.add_node("source", criticality=Criticality.LOW.value)
    return g


@pytest.mark.parametrize("coverage", [round(x * 0.01, 2) for x in range(0, 101)])
def test_INV_002_no_safe_below_coverage_threshold(coverage: float) -> None:
    decision = evaluate_gate(
        possible_graph=_safe_graph(),
        source_entity_id="source",
        coverage=coverage,
    )
    if coverage < C_MIN:
        assert decision.verdict != Verdict.SAFE
    else:
        assert decision.verdict == Verdict.SAFE
