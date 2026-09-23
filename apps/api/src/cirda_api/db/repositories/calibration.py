"""Calibration profile repository."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.models.calibration import CalibrationProfile
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore


class CalibrationRepository(RepositoryBase):
    async def get_active(self) -> dict[str, Any] | None:
        if self.memory:
            for p in self.memory.calibration_profiles.values():
                if p.get("is_active"):
                    return p
            return None

        assert self.session is not None
        result = await self.session.execute(
            select(CalibrationProfile).where(CalibrationProfile.is_active.is_(True)).limit(1)
        )
        row = result.scalar_one_or_none()
        return self._dict(row) if row else None

    async def upsert_active(self, *, theta_c: float, theta_p: float, c_min: float) -> dict[str, Any]:
        now = utcnow()
        record = {
            "profile_id": "default",
            "name": "default",
            "theta_c": theta_c,
            "theta_p": theta_p,
            "c_min": c_min,
            "is_active": True,
            "updated_at": now,
            "created_at": now,
        }
        if self.memory:
            self.memory.calibration_profiles["default"] = record
            return record

        assert self.session is not None
        for row in (await self.session.execute(select(CalibrationProfile))).scalars().all():
            row.is_active = False
        existing = await self.session.get(CalibrationProfile, "default")
        if existing:
            existing.theta_c = theta_c
            existing.theta_p = theta_p
            existing.c_min = c_min
            existing.is_active = True
            existing.updated_at = now
        else:
            self.session.add(
                CalibrationProfile(
                    profile_id="default",
                    name="default",
                    theta_c=theta_c,
                    theta_p=theta_p,
                    c_min=c_min,
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                )
            )
        await self.session.commit()
        return record

    @staticmethod
    def _dict(row: CalibrationProfile) -> dict[str, Any]:
        return {
            "profile_id": row.profile_id,
            "name": row.name,
            "theta_c": row.theta_c,
            "theta_p": row.theta_p,
            "c_min": row.c_min,
            "is_active": row.is_active,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
