"""Report reliability of fused support S (all edges and weak-only) per loss level.

Usage: uv run python scripts/support_reliability.py [num_ecosystems]
"""

from __future__ import annotations

import sys

from cirda_bench.generator.ecosystem import generate_ecosystem
from cirda_bench.metrics.reliability import reliability_report, support_samples

LOSSES = (0.30, 0.45, 0.60)


def main() -> None:
    num_ecosystems = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    pooled: dict[tuple[float, str], list[tuple[float, bool]]] = {}
    for eco_id in range(num_ecosystems):
        ecosystem = generate_ecosystem(eco_id, losses=LOSSES)
        for loss in LOSSES:
            bundle = ecosystem.telemetry_by_loss[loss]
            for label, weak_only in (("all", None), ("weak_only", True)):
                pooled.setdefault((loss, label), []).extend(
                    support_samples(bundle, weak_only=weak_only)
                )

    for (loss, label), samples in sorted(pooled.items()):
        report = reliability_report(samples)
        print(
            f"=== m={loss} {label}: n={report.samples} "
            f"ECE={report.ece:.3f} Brier={report.brier:.3f}"
        )
        for b in report.bins:
            print(
                f"   [{b.lower:.1f},{b.upper:.1f}) n={b.count:5d} "
                f"mean_S={b.mean_support:.3f} real_rate={b.real_rate:.3f}"
            )


if __name__ == "__main__":
    main()
