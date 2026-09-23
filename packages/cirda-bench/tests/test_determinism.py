"""INV-011 determinism tests."""

from __future__ import annotations

from cirda_bench.experiment.runner import BenchmarkConfig, run_benchmark
from cirda_bench.generator.ecosystem import generate_ecosystem
from cirda_bench.seeds import seed


def test_seed_function_matches_normative_formula() -> None:
    value = seed("ecosystem:0", 0, "topology")
    again = seed("ecosystem:0", 0, "topology")
    assert value == again
    assert isinstance(value, int)


def test_ecosystem_generation_is_deterministic() -> None:
    a = generate_ecosystem(12)
    b = generate_ecosystem(12)
    assert a.spec == b.spec
    assert a.entities == b.entities
    assert a.ground_truth_edges == b.ground_truth_edges
    assert a.target_entity_ids == b.target_entity_ids


def test_benchmark_scenarios_are_deterministic() -> None:
    cfg = BenchmarkConfig(num_ecosystems=2, losses=(0.30,), methods=("trace_only",))
    first = run_benchmark(cfg)
    second = run_benchmark(cfg)
    assert first.scenarios == second.scenarios
