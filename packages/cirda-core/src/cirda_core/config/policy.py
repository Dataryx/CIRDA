"""Policy configuration."""

from __future__ import annotations

from dataclasses import dataclass, field

from cirda_core.config.constants import C_MIN, THETA_C, THETA_P
from cirda_core.domain.enums import Criticality


@dataclass(frozen=True, slots=True)
class PolicyConfig:
    """Runtime policy knobs for inference and gating."""

    theta_confirmed: float = THETA_C
    theta_possible: float = THETA_P
    c_min: float = C_MIN
    confirmed_requires_direct_evidence: bool = True
    min_trace_observations_for_confirmed: int = 3
    max_ingest_lag_seconds: float = 3600.0
    critical_threshold: Criticality = Criticality.HIGH
    probe_planning_enabled: bool = False
    hard_blocks: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not 0.0 < self.theta_confirmed <= 1.0:
            raise ValueError("theta_confirmed must be in (0, 1]")
        if not 0.0 < self.theta_possible <= 1.0:
            raise ValueError("theta_possible must be in (0, 1]")
        if not 0.0 < self.c_min <= 1.0:
            raise ValueError("c_min must be in (0, 1]")
        if self.min_trace_observations_for_confirmed < 1:
            raise ValueError("min_trace_observations_for_confirmed must be >= 1")


DEFAULT_POLICY = PolicyConfig()
