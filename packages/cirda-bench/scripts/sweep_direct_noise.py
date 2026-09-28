"""Sweep DIRECT_NOISE_RATE_BY_LOSS and score against golden Table II."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from cirda_bench import calibration as cal
from cirda_bench.experiment.aggregation import row_to_dict
from cirda_bench.experiment.runner import BenchmarkConfig, run_benchmark

TOLS = {
    "edge_f1": 0.01,
    "blast_recall": 0.02,
    "blast_precision": 0.02,
    "decision_coverage": 0.015,
    "false_safe": 0.03,
}
METRICS = tuple(TOLS)
GOLDEN = json.loads(
    (Path(__file__).resolve().parents[1] / "tests" / "golden" / "table_ii.json").read_text()
)


def _load_known_gaps() -> set[tuple[float, str, str]]:
    """Read KNOWN_GAPS from the Table II test without importing pytest."""
    test_file = Path(__file__).resolve().parents[1] / "tests" / "test_reproduces_table_ii.py"
    for node in ast.parse(test_file.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == "KNOWN_GAPS":
            return set(ast.literal_eval(node.value))
    raise RuntimeError("KNOWN_GAPS not found")


KNOWN_GAPS = _load_known_gaps()


def score(rows: list[dict]) -> tuple[int, bool, list[str], list[str]]:
    """Return (passes, cirda_fs_zero, regressions outside KNOWN_GAPS, all fails)."""
    passes = 0
    cirda_zero_fs = True
    fails: list[str] = []
    regressions: list[str] = []
    for gr in GOLDEN:
        actual = next(r for r in rows if r["loss"] == gr["loss"] and r["method"] == gr["method"])
        for metric in METRICS:
            if gr["method"] == "cirda" and metric == "false_safe":
                ok = actual[metric] == 0.0
                cirda_zero_fs = cirda_zero_fs and ok
            else:
                ok = abs(float(actual[metric]) - float(gr[metric])) <= TOLS[metric]
            if ok:
                passes += 1
            else:
                label = (
                    f"{gr['loss']} {gr['method']} {metric} "
                    f"{actual[metric]:.3f}/{gr[metric]:.3f}"
                )
                fails.append(label)
                if (float(gr["loss"]), gr["method"], metric) not in KNOWN_GAPS:
                    regressions.append(label)
    return passes, cirda_zero_fs, regressions, fails


def _loss_map(raw: dict[str, float]) -> dict[float, float]:
    return {float(k): float(v) for k, v in raw.items()}


def main() -> None:
    """argv[1]: JSON file with a list of ``{"direct": {loss: rate}, "weak": {loss: rate}}``."""
    configs = (
        json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")) if len(sys.argv) > 1 else [{}]
    )
    weak_default = dict(cal.WEAK_NOISE_RATE_BY_LOSS)
    for cfg in configs:
        cal.DIRECT_NOISE_RATE_BY_LOSS.clear()
        cal.DIRECT_NOISE_RATE_BY_LOSS.update(_loss_map(cfg.get("direct", {})))
        cal.WEAK_NOISE_RATE_BY_LOSS.clear()
        cal.WEAK_NOISE_RATE_BY_LOSS.update({**weak_default, **_loss_map(cfg.get("weak", {}))})
        rows = [row_to_dict(r) for r in run_benchmark(BenchmarkConfig(num_ecosystems=30)).rows]
        passes, zero_fs, regressions, _fails = score(rows)
        print(f"=== {cfg} -> {passes}/60 cirda_fs0={zero_fs} regressions={regressions}", flush=True)
        if "--rows" not in sys.argv:
            continue
        for r in rows:
            if r["method"] != "trace_only":
                print(
                    f"   {r['method']:12} m={r['loss']} f1={r['edge_f1']:.3f} "
                    f"br={r['blast_recall']:.3f} bp={r['blast_precision']:.3f} "
                    f"fs={r['false_safe']:.3f} dc={r['decision_coverage']:.3f}",
                    flush=True,
                )


if __name__ == "__main__":
    main()
