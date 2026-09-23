"""Aggregate scenario metrics into Table II rows."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_bench.metrics.blast_metrics import blast_precision, blast_recall
from cirda_bench.metrics.decision_metrics import decision_coverage, false_safe_rate
from cirda_bench.metrics.edge_metrics import edge_f1


@dataclass(frozen=True, slots=True)
class ScenarioMetrics:
    """Metrics from one ecosystem/method/loss combination."""

    ecosystem_id: int
    loss: float
    method: str
    edge_f1: float
    blast_recall: float
    blast_precision: float
    false_safe: float
    decision_coverage: float


@dataclass(frozen=True, slots=True)
class AggregatedRow:
    """Aggregated benchmark row matching Table II schema."""

    loss: float
    method: str
    edge_f1: float
    blast_recall: float
    blast_precision: float
    false_safe: float
    decision_coverage: float


def aggregate_rows(scenarios: list[ScenarioMetrics]) -> list[AggregatedRow]:
    """Mean-aggregate scenario metrics by (loss, method)."""
    buckets: dict[tuple[float, str], list[ScenarioMetrics]] = {}
    for scenario in scenarios:
        key = (scenario.loss, scenario.method)
        buckets.setdefault(key, []).append(scenario)

    rows: list[AggregatedRow] = []
    for (loss, method), items in sorted(buckets.items()):
        n = len(items)
        rows.append(
            AggregatedRow(
                loss=loss,
                method=method,
                edge_f1=sum(s.edge_f1 for s in items) / n,
                blast_recall=sum(s.blast_recall for s in items) / n,
                blast_precision=sum(s.blast_precision for s in items) / n,
                false_safe=sum(s.false_safe for s in items) / n,
                decision_coverage=sum(s.decision_coverage for s in items) / n,
            )
        )
    return rows


def scenario_metrics_from_result(
    *,
    ecosystem_id: int,
    loss: float,
    method: str,
    result,
    truth_graph,
    ground_truth_edges,
    targets,
) -> ScenarioMetrics:
    """Compute all scenario metrics for one inference result."""
    return ScenarioMetrics(
        ecosystem_id=ecosystem_id,
        loss=loss,
        method=method,
        edge_f1=edge_f1(result.edges_for_f1(), ground_truth_edges),
        blast_recall=blast_recall(result, truth_graph, targets),
        blast_precision=blast_precision(result, truth_graph, targets),
        false_safe=false_safe_rate(result, truth_graph, targets),
        decision_coverage=decision_coverage(result, targets),
    )


def row_to_dict(row: AggregatedRow) -> dict[str, float | str]:
    return {
        "loss": row.loss,
        "method": row.method,
        "edge_f1": round(row.edge_f1, 3),
        "blast_recall": round(row.blast_recall, 3),
        "blast_precision": round(row.blast_precision, 3),
        "false_safe": round(row.false_safe, 3),
        "decision_coverage": round(row.decision_coverage, 3),
    }
