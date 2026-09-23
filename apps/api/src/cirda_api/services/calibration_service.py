"""Calibration profile service."""

from __future__ import annotations

from typing import Any

from cirda_api.db.repositories.calibration import CalibrationRepository
from cirda_api.settings import Settings


class CalibrationService:
    def __init__(self, repo: CalibrationRepository, settings: Settings) -> None:
        self.repo = repo
        self.settings = settings

    async def get_active(self) -> dict[str, Any]:
        active = await self.repo.get_active()
        if active:
            return active
        return {
            "profile_id": "default",
            "name": "default",
            "theta_c": self.settings.theta_c,
            "theta_p": self.settings.theta_p,
            "c_min": self.settings.c_min,
            "is_active": True,
        }

    async def update(self, *, theta_c: float, theta_p: float, c_min: float) -> dict[str, Any]:
        if theta_p >= theta_c:
            raise ValueError("theta_p must be less than theta_c")
        return await self.repo.upsert_active(theta_c=theta_c, theta_p=theta_p, c_min=c_min)
