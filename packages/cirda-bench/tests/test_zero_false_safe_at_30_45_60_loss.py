"""CIRDA zero false-safe invariant at high loss (structural, no overlay)."""

from __future__ import annotations

import pytest

from cirda_core.config.constants import C_MIN

from cirda_bench.experiment.runner import BenchmarkConfig, run_benchmark


@pytest.mark.parametrize("loss", [0.30, 0.45, 0.60])
def test_cirda_false_safe_is_zero(loss: float) -> None:
    assert (1.0 - loss) < C_MIN
    result = run_benchmark(
        BenchmarkConfig(
            num_ecosystems=30,
            losses=(loss,),
            methods=("cirda",),
            report_losses=(loss,),
        )
    )
    row = result.rows[0]
    assert row.method == "cirda"
    assert row.loss == loss
    assert row.false_safe == 0.0
