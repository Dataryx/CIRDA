"""Policy builder unit tests."""

from __future__ import annotations

from cirda_api.services.policy import build_policy
from cirda_api.settings import Settings


def test_build_policy_from_settings() -> None:
    settings = Settings(THETA_C=0.62, THETA_P=0.28, C_MIN=0.85)
    policy = build_policy(settings)
    assert policy.theta_confirmed == 0.62
    assert policy.theta_possible == 0.28
    assert policy.c_min == 0.85
