"""Coverage domain model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CoverageEstimate:
    """Estimated observability coverage for a scope."""

    coverage: float
    observed_entities: int
    total_entities: int
    suppressed_channels: frozenset[str] = frozenset()
    benchmark_adjusted: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.coverage <= 1.0:
            raise ValueError("coverage must be in [0, 1]")
        if self.observed_entities < 0 or self.total_entities < 0:
            raise ValueError("entity counts must be non-negative")
        if self.total_entities > 0 and self.observed_entities > self.total_entities:
            raise ValueError("observed_entities cannot exceed total_entities")
