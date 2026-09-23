"""Coverage estimation service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from cirda_core.coverage.estimator import estimate_coverage
from cirda_core.coverage.inputs import CoverageInputs
from cirda_core.domain.enums import EvidenceChannel

from cirda_api.db.repositories.coverage import CoverageRepository
from cirda_api.db.repositories.entity import EntityRepository
from cirda_api.db.repositories.evidence import EvidenceRepository
from cirda_api.services.policy import build_policy
from cirda_api.settings import Settings


class CoverageService:
    def __init__(
        self,
        entity_repo: EntityRepository,
        evidence_repo: EvidenceRepository,
        coverage_repo: CoverageRepository,
        settings: Settings,
    ) -> None:
        self.entity_repo = entity_repo
        self.evidence_repo = evidence_repo
        self.coverage_repo = coverage_repo
        self.settings = settings

    async def estimate(self, *, as_of: datetime | None = None) -> dict[str, Any]:
        as_of = as_of or datetime.now(timezone.utc)
        entities, _ = await self.entity_repo.list_entities(limit=10_000)
        total_ids = frozenset(e["entity_id"] for e in entities)
        events, _ = await self.evidence_repo.list_events(as_of=as_of, limit=100_000)
        observed: set[str] = set()
        for ev in events:
            observed.add(ev["source_id"])
            observed.add(ev["target_id"])
        inputs = CoverageInputs(
            total_entity_ids=total_ids,
            observed_entity_ids=frozenset(observed & set(total_ids)),
            suppressed_channels=frozenset(),
        )
        est = estimate_coverage(inputs)
        policy = build_policy(self.settings)
        return {
            "coverage": est.coverage,
            "observed_entities": est.observed_entities,
            "total_entities": est.total_entities,
            "suppressed_channels": sorted(est.suppressed_channels),
            "meets_threshold": est.coverage >= policy.c_min,
            "c_min": policy.c_min,
            "as_of": as_of,
        }

    async def snapshot(self, *, scope: str | None = None) -> dict[str, Any]:
        est = await self.estimate()
        record = {
            "snapshot_id": str(uuid.uuid4()),
            "coverage": est["coverage"],
            "observed_entities": est["observed_entities"],
            "total_entities": est["total_entities"],
            "suppressed_channels": est["suppressed_channels"],
            "scope": scope,
            "captured_at": datetime.now(timezone.utc),
        }
        return await self.coverage_repo.add_snapshot(record)

    async def latest(self) -> dict[str, Any] | None:
        return await self.coverage_repo.latest_snapshot()

    async def list_snapshots(self, *, offset: int = 0, limit: int = 20) -> tuple[list[dict[str, Any]], int]:
        return await self.coverage_repo.list_snapshots(offset=offset, limit=limit)

    async def channel_health(self) -> list[dict[str, Any]]:
        return await self.coverage_repo.list_channel_health()
