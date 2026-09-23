"""Scalability shape tests (Table III)."""

from __future__ import annotations

import json
from pathlib import Path

from cirda_bench.generator.topology import TABLE_III_COUNTS, expected_build_complexity
from cirda_bench.scalability.kernel_benchmark import run_scaling_benchmark

GOLDEN = json.loads(
    (Path(__file__).parent / "golden" / "table_iii.json").read_text(encoding="utf-8")
)


def test_table_iii_exact_counts() -> None:
    rows = run_scaling_benchmark()
    for golden, actual in zip(GOLDEN, rows, strict=True):
        assert actual.agents == golden["agents"]
        assert actual.nodes == golden["nodes"]
        assert actual.edges == golden["edges"]


def test_sub_quadratic_build_shape() -> None:
    rows = run_scaling_benchmark()
    ratios = []
    for left, right in zip(rows, rows[1:], strict=False):
        node_ratio = right.nodes / left.nodes
        build_ratio = right.build_ms / max(left.build_ms, 1e-6)
        ratios.append(build_ratio / node_ratio)
    # Build time should grow slower than quadratic in node count.
    assert max(ratios) < rows[-1].nodes / rows[0].nodes


def test_p95_query_shape_at_1000_agents() -> None:
    rows = run_scaling_benchmark()
    largest = rows[-1]
    assert largest.agents == 1000
    assert largest.p95_query_ms < 5.0 or largest.p95_query_ms / largest.complexity_proxy < 0.01


def test_complexity_proxy_monotonic() -> None:
    proxies = [expected_build_complexity(r.nodes, r.edges) for r in run_scaling_benchmark()]
    assert proxies == sorted(proxies)
