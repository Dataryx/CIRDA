"""Compare benchmark output to golden Table II."""
from __future__ import annotations

import json
from pathlib import Path

from cirda_bench.experiment.aggregation import row_to_dict
from cirda_bench.experiment.runner import BenchmarkConfig, run_benchmark

golden = json.loads(
    (Path(__file__).resolve().parents[1] / "tests" / "golden" / "table_ii.json").read_text()
)
result = run_benchmark(BenchmarkConfig(num_ecosystems=30))
rows = [row_to_dict(r) for r in result.rows]
for gr in golden:
    actual = next(
        r for r in rows if r["loss"] == gr["loss"] and r["method"] == gr["method"]
    )
    print(
        f"{gr['method']:12} m={gr['loss']:.2f}  "
        f"f1 {actual['edge_f1']:.3f}/{gr['edge_f1']:.3f}  "
        f"br {actual['blast_recall']:.3f}/{gr['blast_recall']:.3f}  "
        f"bp {actual['blast_precision']:.3f}/{gr['blast_precision']:.3f}  "
        f"fs {actual['false_safe']:.3f}/{gr['false_safe']:.3f}  "
        f"dc {actual['decision_coverage']:.3f}/{gr['decision_coverage']:.3f}"
    )
