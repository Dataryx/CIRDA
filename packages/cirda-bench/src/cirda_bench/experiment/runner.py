"""Benchmark protocol runner."""

from __future__ import annotations

from dataclasses import dataclass, field

from cirda_bench.experiment.aggregation import (
    AggregatedRow,
    ScenarioMetrics,
    aggregate_rows,
    scenario_metrics_from_result,
)
from cirda_bench.generator.ecosystem import Ecosystem, generate_ecosystem
from cirda_bench.methods import METHODS
from cirda_bench.metrics.blast_metrics import build_truth_graph


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    """Benchmark protocol configuration."""

    num_ecosystems: int = 30
    losses: tuple[float, ...] = (0.0, 0.15, 0.30, 0.45, 0.60)
    methods: tuple[str, ...] = ("trace_only", "direct_union", "weak_union", "cirda")
    report_losses: tuple[float, ...] = (0.30, 0.45, 0.60)
    smoke: bool = False

    def __post_init__(self) -> None:
        if self.smoke:
            object.__setattr__(self, "num_ecosystems", 3)
            object.__setattr__(self, "losses", (0.30, 0.45))
            object.__setattr__(self, "methods", ("trace_only", "cirda"))


@dataclass
class BenchmarkResult:
    """Full benchmark output."""

    config: BenchmarkConfig
    scenarios: list[ScenarioMetrics] = field(default_factory=list)
    rows: list[AggregatedRow] = field(default_factory=list)


def run_ecosystem_scenarios(
    ecosystem: Ecosystem,
    config: BenchmarkConfig,
) -> list[ScenarioMetrics]:
    """Run all method/loss combinations for one ecosystem."""
    truth_graph = build_truth_graph(ecosystem.entities, ecosystem.ground_truth_edges)
    scenarios: list[ScenarioMetrics] = []

    for loss in config.losses:
        telemetry = ecosystem.telemetry_by_loss[loss]
        for method_name in config.methods:
            method = METHODS[method_name]
            result = method.infer(
                entities=ecosystem.entities,
                ground_truth_edges=ecosystem.ground_truth_edges,
                telemetry=telemetry,
                targets=ecosystem.target_entity_ids,
            )
            scenarios.append(
                scenario_metrics_from_result(
                    ecosystem_id=ecosystem.ecosystem_id,
                    loss=loss,
                    method=method_name,
                    result=result,
                    truth_graph=truth_graph,
                    ground_truth_edges=ecosystem.ground_truth_edges,
                    targets=ecosystem.target_entity_ids,
                )
            )

    return scenarios


def run_benchmark(config: BenchmarkConfig | None = None) -> BenchmarkResult:
    """Execute the full benchmark protocol."""
    cfg = config or BenchmarkConfig()
    all_scenarios: list[ScenarioMetrics] = []

    for ecosystem_id in range(cfg.num_ecosystems):
        ecosystem = generate_ecosystem(ecosystem_id, losses=cfg.losses)
        all_scenarios.extend(run_ecosystem_scenarios(ecosystem, cfg))

    rows = aggregate_rows(all_scenarios)
    if cfg.report_losses:
        rows = [row for row in rows if row.loss in cfg.report_losses]

    return BenchmarkResult(config=cfg, scenarios=all_scenarios, rows=rows)


def protocol_scenario_count(config: BenchmarkConfig | None = None) -> int:
    """Return total method evaluations in the protocol."""
    cfg = config or BenchmarkConfig()
    return cfg.num_ecosystems * len(cfg.losses) * 60 * len(cfg.methods)
