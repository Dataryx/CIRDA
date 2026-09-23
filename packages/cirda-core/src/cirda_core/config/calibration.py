"""Calibration validation and tuning."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_core.config.constants import C_MIN, THETA_C, THETA_P
from cirda_core.domain.errors import CalibrationError


@dataclass(frozen=True, slots=True)
class CalibrationParams:
    """Calibrated threshold overrides."""

    theta_confirmed: float = THETA_C
    theta_possible: float = THETA_P
    c_min: float = C_MIN

    def validate(self) -> None:
        """Validate calibration ordering and bounds."""
        if not 0.0 < self.theta_possible < self.theta_confirmed <= 1.0:
            raise CalibrationError(
                "theta_possible must be < theta_confirmed and both in (0, 1]"
            )
        if not 0.0 < self.c_min <= 1.0:
            raise CalibrationError("c_min must be in (0, 1]")


def validate_calibration(
    theta_confirmed: float = THETA_C,
    theta_possible: float = THETA_P,
    c_min: float = C_MIN,
) -> CalibrationParams:
    """Build and validate calibration parameters."""
    params = CalibrationParams(
        theta_confirmed=theta_confirmed,
        theta_possible=theta_possible,
        c_min=c_min,
    )
    params.validate()
    return params
