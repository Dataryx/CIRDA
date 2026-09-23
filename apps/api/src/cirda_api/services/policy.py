"""Build PolicyConfig from settings."""

from __future__ import annotations

from cirda_core.config.policy import PolicyConfig
from cirda_api.settings import Settings


def build_policy(settings: Settings) -> PolicyConfig:
    return PolicyConfig(
        theta_confirmed=settings.theta_c,
        theta_possible=settings.theta_p,
        c_min=settings.c_min,
        confirmed_requires_direct_evidence=settings.confirmed_requires_direct_evidence,
        min_trace_observations_for_confirmed=settings.min_trace_observations_for_confirmed,
        max_ingest_lag_seconds=settings.max_ingest_lag_seconds,
        critical_threshold=settings.critical_threshold,
        probe_planning_enabled=settings.probe_planning_enabled,
        hard_blocks=settings.hard_block_set,
    )
