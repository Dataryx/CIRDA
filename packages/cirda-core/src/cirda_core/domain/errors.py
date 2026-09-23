"""Domain errors."""

from __future__ import annotations


class CirdaError(Exception):
    """Base error for CIRDA domain."""


class NaiveDatetimeError(CirdaError):
    """Raised when a naive datetime is supplied at a boundary."""


class InvalidEntityError(CirdaError):
    """Raised when entity data is invalid."""


class InvalidEdgeError(CirdaError):
    """Raised when edge construction violates invariants."""


class CalibrationError(CirdaError):
    """Raised when calibration parameters are invalid."""


class CoverageError(CirdaError):
    """Raised when coverage inputs are invalid."""
