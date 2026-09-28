"""Recompute Table II artifact with current calibration."""

from __future__ import annotations

import json
from pathlib import Path

from cirda_bench.experiment.aggregation import row_to_dict
from cirda_bench.experiment.runner import BenchmarkConfig, run_benchmark

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "artifacts" / "table_ii_computed.json"


def main() -> None:
    result = run_benchmark(BenchmarkConfig(num_ecosystems=30))
    rows = [row_to_dict(r) for r in result.rows]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    for r in rows:
        if r["method"] in {"cirda", "weak_union", "direct_union"}:
            print(
                f"{r['method']:12} m={r['loss']} "
                f"f1={r['edge_f1']:.3f} br={r['blast_recall']:.3f} "
                f"bp={r['blast_precision']:.3f} fs={r['false_safe']:.3f} "
                f"dc={r['decision_coverage']:.3f}"
            )


if __name__ == "__main__":
    main()
