"""CLI entrypoint: cirda-bench run|bench|bench-smoke|scale|report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cirda_bench.experiment.aggregation import row_to_dict
from cirda_bench.experiment.artifacts import default_artifact_dir, save_json, save_table_ii
from cirda_bench.experiment.runner import BenchmarkConfig, run_benchmark
from cirda_bench.scalability.kernel_benchmark import run_scaling_benchmark


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cirda-bench", description="CIRDA benchmark harness")
    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run", help="Run benchmark protocol (alias for bench)")
    run_cmd.add_argument("--smoke", action="store_true", help="Run smoke mode (3 ecosystems)")
    run_cmd.add_argument("--ecosystems", type=int, default=30)
    run_cmd.add_argument("--output", type=Path, default=default_artifact_dir())

    bench_cmd = sub.add_parser("bench", help="Full Table II benchmark (30 ecosystems)")
    bench_cmd.add_argument("--output", type=Path, default=default_artifact_dir())
    bench_cmd.add_argument("--ecosystems", type=int, default=30)

    smoke_cmd = sub.add_parser("bench-smoke", help="Smoke benchmark (3 ecosystems, real methods)")
    smoke_cmd.add_argument("--output", type=Path, default=default_artifact_dir())

    scale_cmd = sub.add_parser("scale", help="Run scalability benchmark")
    scale_cmd.add_argument("--output", type=Path, default=default_artifact_dir())

    report_cmd = sub.add_parser("report", help="Render benchmark report from artifacts")
    report_cmd.add_argument("--input", type=Path, default=default_artifact_dir())

    return parser


def _run_and_emit(config: BenchmarkConfig, out_dir: Path) -> int:
    result = run_benchmark(config)
    save_table_ii(result, out_dir / "table_ii.json")
    save_json(
        {
            "scenarios": len(result.scenarios),
            "smoke": config.smoke,
            "ecosystems": config.num_ecosystems,
        },
        out_dir / "run_meta.json",
    )
    print(json.dumps([row_to_dict(r) for r in result.rows], indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    config = BenchmarkConfig(num_ecosystems=args.ecosystems, smoke=args.smoke)
    return _run_and_emit(config, args.output)


def cmd_bench(args: argparse.Namespace) -> int:
    config = BenchmarkConfig(num_ecosystems=args.ecosystems, smoke=False)
    return _run_and_emit(config, args.output)


def cmd_bench_smoke(args: argparse.Namespace) -> int:
    config = BenchmarkConfig(smoke=True)
    return _run_and_emit(config, args.output)


def cmd_scale(args: argparse.Namespace) -> int:
    rows = run_scaling_benchmark()
    payload = [
        {
            "agents": r.agents,
            "nodes": r.nodes,
            "edges": r.edges,
            "build_ms": round(r.build_ms, 3),
            "p95_query_ms": round(r.p95_query_ms, 3),
            "complexity_proxy": round(r.complexity_proxy, 3),
        }
        for r in rows
    ]
    out = args.output / "table_iii.json"
    save_json(payload, out)
    print(json.dumps(payload, indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    in_dir: Path = args.input
    table_ii = json.loads((in_dir / "table_ii.json").read_text(encoding="utf-8"))
    narrative_path = Path(__file__).resolve().parents[2] / "tests" / "golden" / "narrative_values.json"
    narrative = json.loads(narrative_path.read_text(encoding="utf-8"))
    report = {"table_ii": table_ii, "narrative": narrative}
    print(json.dumps(report, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "bench":
        return cmd_bench(args)
    if args.command == "bench-smoke":
        return cmd_bench_smoke(args)
    if args.command == "scale":
        return cmd_scale(args)
    if args.command == "report":
        return cmd_report(args)
    parser.error(f"unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
