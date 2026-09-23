"""Benchmark artifact persistence."""

from __future__ import annotations

import json
from pathlib import Path

from cirda_bench.experiment.aggregation import row_to_dict
from cirda_bench.experiment.runner import BenchmarkResult


def default_artifact_dir() -> Path:
    return Path("artifacts")


def save_table_ii(result: BenchmarkResult, path: Path | None = None) -> Path:
    """Save aggregated Table II rows."""
    out = path or default_artifact_dir() / "table_ii.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = [row_to_dict(row) for row in result.rows]
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def load_golden_table_ii(path: Path | None = None) -> list[dict[str, float | str]]:
    """Load golden Table II reference."""
    golden = path or Path(__file__).resolve().parents[3] / "tests" / "golden" / "table_ii.json"
    return json.loads(golden.read_text(encoding="utf-8"))


def save_json(data: object, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
