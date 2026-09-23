"""Settings validation unit tests."""

from __future__ import annotations

import pytest

from cirda_api.settings import Settings


def test_theta_p_must_be_less_than_theta_c() -> None:
    with pytest.raises(ValueError, match="THETA_P"):
        Settings(THETA_C=0.5, THETA_P=0.6)
