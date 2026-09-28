"""Reliability of fused support S against simulator ground truth.

Measures how well S tracks the empirical rate of real edges. It does not change
channel weights; S is documented as support, not a calibrated probability.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from cirda_core.inference.fusion import fuse_channels, has_confirming_evidence

from cirda_bench.generator.telemetry import TelemetryBundle, to_channel_observations


@dataclass(frozen=True, slots=True)
class ReliabilityBin:
    lower: float
    upper: float
    count: int
    mean_support: float
    real_rate: float


@dataclass(frozen=True, slots=True)
class ReliabilityReport:
    samples: int
    bins: tuple[ReliabilityBin, ...]
    ece: float
    brier: float


def support_samples(
    bundle: TelemetryBundle,
    *,
    weak_only: bool | None = None,
) -> list[tuple[float, bool]]:
    """Return ``(S, is_real_edge)`` for every observed edge in the bundle.

    ``weak_only=True`` keeps edges without confirming evidence, ``False`` keeps
    edges with it, ``None`` keeps all.
    """
    samples: list[tuple[float, bool]] = []
    for record in bundle.edge_telemetry:
        obs = to_channel_observations(record.observations)
        if not obs:
            continue
        if weak_only is not None and has_confirming_evidence(obs) == weak_only:
            continue
        samples.append((fuse_channels(obs), not record.is_spurious))
    return samples


def reliability_report(
    samples: Iterable[tuple[float, bool]],
    *,
    num_bins: int = 10,
) -> ReliabilityReport:
    """Equal-width reliability bins, expected calibration error and Brier score."""
    if num_bins < 1:
        raise ValueError("num_bins must be >= 1")
    items = list(samples)
    for support, _ in items:
        if not 0.0 <= support <= 1.0:
            raise ValueError(f"support {support} outside [0, 1]")

    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(num_bins)]
    for support, real in items:
        buckets[min(int(support * num_bins), num_bins - 1)].append((support, real))

    total = len(items)
    bins: list[ReliabilityBin] = []
    ece = 0.0
    for i, bucket in enumerate(buckets):
        if not bucket:
            continue
        mean_support = sum(s for s, _ in bucket) / len(bucket)
        real_rate = sum(1 for _, r in bucket if r) / len(bucket)
        ece += len(bucket) / total * abs(mean_support - real_rate)
        bins.append(
            ReliabilityBin(
                lower=i / num_bins,
                upper=(i + 1) / num_bins,
                count=len(bucket),
                mean_support=mean_support,
                real_rate=real_rate,
            )
        )

    brier = sum((s - (1.0 if r else 0.0)) ** 2 for s, r in items) / total if total else 0.0
    return ReliabilityReport(samples=total, bins=tuple(bins), ece=ece, brier=brier)
