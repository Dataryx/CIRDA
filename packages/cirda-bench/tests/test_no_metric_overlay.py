"""Ensure calibration module does not fabricate Table II metrics."""

from __future__ import annotations

import inspect

import cirda_bench.calibration as calibration
from cirda_bench.experiment import runner as runner_mod


def test_calibration_has_no_golden_overlay() -> None:
    source = inspect.getsource(calibration)
    assert "GOLDEN_TABLE" not in source
    assert "calibrated_scenario_metrics" not in source


def test_runner_has_no_overlay_hook() -> None:
    source = inspect.getsource(runner_mod)
    assert "calibrated_scenario_metrics" not in source
    assert "use_calibration" not in source
