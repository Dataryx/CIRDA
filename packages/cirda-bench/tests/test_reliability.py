"""Tests for fused-support reliability metrics."""

from __future__ import annotations

import pytest
from cirda_bench.generator.ecosystem import generate_ecosystem
from cirda_bench.metrics.reliability import reliability_report, support_samples


def test_perfectly_calibrated_bins_have_zero_ece() -> None:
    samples = [(0.25, True)] + [(0.25, False)] * 3 + [(0.75, True)] * 3 + [(0.75, False)]
    report = reliability_report(samples, num_bins=4)
    assert report.samples == 8
    assert report.ece == pytest.approx(0.0)
    assert [b.count for b in report.bins] == [4, 4]
    assert report.brier == pytest.approx(0.1875)


def test_overconfident_support_yields_expected_ece() -> None:
    report = reliability_report([(0.9, False), (0.9, True)], num_bins=10)
    assert report.ece == pytest.approx(0.4)
    assert report.bins[0].lower == pytest.approx(0.9)


def test_support_of_one_lands_in_last_bin() -> None:
    report = reliability_report([(1.0, True)], num_bins=5)
    assert report.bins[0].upper == pytest.approx(1.0)


def test_empty_samples_and_invalid_inputs() -> None:
    assert reliability_report([]).samples == 0
    with pytest.raises(ValueError):
        reliability_report([(1.2, True)])
    with pytest.raises(ValueError):
        reliability_report([(0.5, True)], num_bins=0)


def test_support_samples_partition_by_confirming_evidence() -> None:
    bundle = generate_ecosystem(0, losses=(0.45,)).telemetry_by_loss[0.45]
    all_samples = support_samples(bundle)
    weak = support_samples(bundle, weak_only=True)
    confirmed = support_samples(bundle, weak_only=False)
    assert len(all_samples) == len(weak) + len(confirmed)
    assert weak and confirmed
    assert any(not real for _, real in weak)
    assert all(0.0 <= s <= 1.0 for s, _ in all_samples)
