"""Calibration validation tests."""

from __future__ import annotations

import pytest

from cirda_core.config.calibration import validate_calibration
from cirda_core.config.constants import C_MIN, THETA_C, THETA_P
from cirda_core.domain.errors import CalibrationError


def test_valid_defaults() -> None:
    params = validate_calibration()
    assert params.theta_confirmed == THETA_C
    assert params.theta_possible == THETA_P
    assert params.c_min == C_MIN


def test_invalid_ordering_raises() -> None:
    with pytest.raises(CalibrationError):
        validate_calibration(theta_confirmed=0.2, theta_possible=0.5)


def test_invalid_c_min_raises() -> None:
    with pytest.raises(CalibrationError):
        validate_calibration(c_min=0.0)
