"""Coverage repository."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.models.channel_health import ChannelHealth as ChannelHealthModel
from cirda_api.db.models.coverage import CoverageSnapshot
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore

PROBE_RESTORE_PREFIX = "__probe_restore__:"


class CoverageRepository(RepositoryBase):
    async def latest_snapshot(self) -> dict[str, Any] | None:
        if self.memory:
            if not self.memory.coverage_snapshots:
                return None
            return sorted(self.memory.coverage_snapshots, key=lambda s: s["captured_at"], reverse=True)[0]

        assert self.session is not None
        result = await self.session.execute(
            select(CoverageSnapshot).order_by(CoverageSnapshot.captured_at.desc()).limit(1)
        )
        row = result.scalar_one_or_none()
        return self._snapshot_dict(row) if row else None

    async def add_snapshot(self, record: dict[str, Any]) -> dict[str, Any]:
        if self.memory:
            self.memory.coverage_snapshots.append(record)
            return record

        assert self.session is not None
        row = CoverageSnapshot(
            snapshot_id=record["snapshot_id"],
            coverage=record["coverage"],
            observed_entities=record["observed_entities"],
            total_entities=record["total_entities"],
            suppressed_channels=record.get("suppressed_channels", []),
            scope=record.get("scope"),
            captured_at=record["captured_at"],
        )
        self.session.add(row)
        await self.session.commit()
        return record

    async def list_snapshots(self, *, offset: int = 0, limit: int = 20) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            rows = sorted(self.memory.coverage_snapshots, key=lambda s: s["captured_at"], reverse=True)
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        q = select(CoverageSnapshot).order_by(CoverageSnapshot.captured_at.desc())
        result = await self.session.execute(q.offset(offset).limit(limit))
        items = [self._snapshot_dict(r) for r in result.scalars().all()]
        total = len((await self.session.execute(select(CoverageSnapshot))).scalars().all())
        return items, total

    async def list_channel_health(self) -> list[dict[str, Any]]:
        if self.memory:
            return [
                row
                for row in self.memory.channel_health.values()
                if not str(row.get("channel", "")).startswith(PROBE_RESTORE_PREFIX)
            ]

        assert self.session is not None
        result = await self.session.execute(select(ChannelHealthModel))
        rows: list[dict[str, Any]] = []
        for r in result.scalars().all():
            if str(r.channel).startswith(PROBE_RESTORE_PREFIX):
                continue
            details: dict[str, Any] = {}
            if r.details:
                try:
                    import json

                    parsed = json.loads(r.details)
                    if isinstance(parsed, dict):
                        details = parsed
                except (json.JSONDecodeError, TypeError):
                    details = {"note": r.details}
            rows.append(
                {
                    "channel": r.channel,
                    "health_score": r.health_score,
                    "lag_seconds": r.lag_seconds,
                    "last_checked_at": r.last_checked_at,
                    "details": details,
                    "suppression_suspected": bool(details.get("suppression_suspected")),
                }
            )
        return rows

    async def list_probe_restorations(self, entity_id: str) -> set[str]:
        if self.memory:
            return set(self.memory.probe_restorations.get(entity_id, set()))

        assert self.session is not None
        row = await self.session.get(ChannelHealthModel, f"{PROBE_RESTORE_PREFIX}{entity_id}")
        if not row or not row.details:
            return set()
        try:
            import json

            parsed = json.loads(row.details)
        except (json.JSONDecodeError, TypeError):
            return set()
        channels = parsed.get("channels") if isinstance(parsed, dict) else None
        if not isinstance(channels, list):
            return set()
        return {str(c) for c in channels}

    async def record_probe_restorations(self, entity_id: str, channels: list[str]) -> set[str]:
        existing = await self.list_probe_restorations(entity_id)
        merged = sorted(existing | {str(c) for c in channels})
        if self.memory:
            self.memory.probe_restorations[entity_id] = set(merged)
            return set(merged)

        await self.upsert_channel_health(
            f"{PROBE_RESTORE_PREFIX}{entity_id}",
            health_score=1.0,
            details={"kind": "probe_restoration", "channels": merged, "entity_id": entity_id},
            suppression_suspected=False,
        )
        return set(merged)

    async def upsert_channel_health(
        self,
        channel: str,
        health_score: float,
        lag_seconds: float = 0.0,
        *,
        details: dict[str, Any] | None = None,
        suppression_suspected: bool = False,
    ) -> None:
        import json

        now = utcnow()
        detail_payload = {
            **(details or {}),
            "suppression_suspected": suppression_suspected,
        }
        payload = {
            "channel": channel,
            "health_score": health_score,
            "lag_seconds": lag_seconds,
            "last_checked_at": now,
            "suppression_suspected": suppression_suspected,
            "details": detail_payload,
        }
        if self.memory:
            self.memory.channel_health[channel] = payload
            return

        assert self.session is not None
        detail_str = json.dumps(detail_payload)
        row = await self.session.get(ChannelHealthModel, channel)
        if row:
            row.health_score = health_score
            row.lag_seconds = lag_seconds
            row.last_checked_at = now
            row.details = detail_str
        else:
            self.session.add(
                ChannelHealthModel(
                    channel=channel,
                    health_score=health_score,
                    lag_seconds=lag_seconds,
                    last_checked_at=now,
                    details=detail_str,
                )
            )
        await self.session.commit()

    @staticmethod
    def _snapshot_dict(row: CoverageSnapshot) -> dict[str, Any]:
        return {
            "snapshot_id": row.snapshot_id,
            "coverage": row.coverage,
            "observed_entities": row.observed_entities,
            "total_entities": row.total_entities,
            "suppressed_channels": row.suppressed_channels,
            "scope": row.scope,
            "captured_at": row.captured_at,
        }
