"""Coverage estimator tests."""

from __future__ import annotations

import pytest

from cirda_core.config.constants import C_MIN
from cirda_core.coverage.benchmark_estimator import benchmark_coverage
from cirda_core.coverage.estimator import estimate_coverage, meets_coverage_threshold
from cirda_core.coverage.inputs import CoverageInputs
from cirda_core.domain.enums import EvidenceChannel


def test_basic_coverage() -> None:
    inputs = CoverageInputs(
        observed_entity_ids=frozenset({"a", "b"}),
        total_entity_ids=frozenset({"a", "b", "c", "d"}),
    )
    result = estimate_coverage(inputs)
    assert result.coverage == pytest.approx(0.5)
    assert result.observed_entities == 2
    assert result.total_entities == 4


def test_empty_total_full_coverage() -> None:
    inputs = CoverageInputs(observed_entity_ids=frozenset(), total_entity_ids=frozenset())
    assert estimate_coverage(inputs).coverage == 1.0


def test_benchmark_coverage() -> None:
    inputs = CoverageInputs(
        observed_entity_ids=frozenset({"a", "b", "c"}),
        total_entity_ids=frozenset({"a", "b", "c", "d", "e"}),
    )
    result = benchmark_coverage(miss_rate=0.2, inputs=inputs)
    assert result.benchmark_adjusted
    assert result.coverage == pytest.approx(0.6)


def test_meets_threshold() -> None:
    assert meets_coverage_threshold(C_MIN)
    assert not meets_coverage_threshold(C_MIN - 0.01)
