"""Report Table II metrics within tolerance."""
from __future__ import annotations

import json
from pathlib import Path

from cirda_bench.experiment.aggregation import row_to_dict
from cirda_bench.experiment.runner import BenchmarkConfig, run_benchmark

TOLS = {
    "edge_f1": 0.01,
    "blast_recall": 0.02,
    "blast_precision": 0.02,
    "decision_coverage": 0.015,
    "false_safe": 0.03,
}

golden = json.loads(
    (Path(__file__).resolve().parents[1] / "tests" / "golden" / "table_ii.json").read_text()
)
result = run_benchmark(BenchmarkConfig(num_ecosystems=30))
rows = [row_to_dict(r) for r in result.rows]

passes = 0
fails: list[str] = []
for gr in golden:
    actual = next(r for r in rows if r["loss"] == gr["loss"] and r["method"] == gr["method"])
    for metric in ("edge_f1", "blast_recall", "blast_precision", "decision_coverage", "false_safe"):
        if gr["method"] == "cirda" and metric == "false_safe" and gr["loss"] in {0.30, 0.45, 0.60}:
            ok = actual[metric] == 0.0
        else:
            ok = abs(float(actual[metric]) - float(gr[metric])) <= TOLS[metric]
        if ok:
            passes += 1
        else:
            fails.append(
                f"({gr['loss']}, {gr['method']!r}, {metric!r}),  "
                f"{actual[metric]:.3f} vs {gr[metric]:.3f}"
            )

print(f"passing metrics: {passes}/60")
for line in fails:
    print(line)
