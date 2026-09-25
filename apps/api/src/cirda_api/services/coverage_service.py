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

# Demo / ops narrative: vendor-risk depends on database audit that is silent.
_VENDOR_RISK_SUPPRESSED = frozenset(
    {EvidenceChannel.DATABASE, EvidenceChannel.MESSAGING}
)


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

    async def estimate(
        self,
        *,
        as_of: datetime | None = None,
        scope_entity_id: str | None = None,
    ) -> dict[str, Any]:
        payload, _inputs = await self._estimate(
            as_of=as_of,
            scope_entity_id=scope_entity_id,
        )
        return payload

    async def estimate_with_inputs(
        self,
        *,
        as_of: datetime | None = None,
        scope_entity_id: str | None = None,
    ) -> tuple[dict[str, Any], CoverageInputs]:
        """Estimate coverage and return the inputs used (for probe ΔC)."""
        return await self._estimate(as_of=as_of, scope_entity_id=scope_entity_id)

    async def _estimate(
        self,
        *,
        as_of: datetime | None = None,
        scope_entity_id: str | None = None,
    ) -> tuple[dict[str, Any], CoverageInputs]:
        as_of = as_of or datetime.now(timezone.utc)
        entities, _ = await self.entity_repo.list_entities(limit=10_000)
        total_ids = frozenset(e["entity_id"] for e in entities)
        events, _ = await self.evidence_repo.list_events(as_of=as_of, limit=100_000)
        observed: set[str] = set()
        for ev in events:
            observed.add(ev["source_id"])
            observed.add(ev["target_id"])

        suppressed = await self._suppressed_channels(scope_entity_id=scope_entity_id)
        inputs = CoverageInputs(
            total_entity_ids=total_ids,
            observed_entity_ids=frozenset(observed & set(total_ids)),
            suppressed_channels=suppressed,
        )
        est = estimate_coverage(inputs)
        policy = build_policy(self.settings)
        payload = {
            "coverage": est.coverage,
            "observed_entities": est.observed_entities,
            "total_entities": est.total_entities,
            "suppressed_channels": sorted(est.suppressed_channels),
            "meets_threshold": est.coverage >= policy.c_min,
            "c_min": policy.c_min,
            "as_of": as_of,
            "scope_entity_id": scope_entity_id,
            "estimator": "production",
            "label": "estimate",
        }
        return payload, inputs

    async def _suppressed_channels(
        self, *, scope_entity_id: str | None
    ) -> frozenset[EvidenceChannel]:
        # Target-scoped decision coverage: vendor-risk narrative only.
        # Do not apply estate-wide channel health penalties to unrelated targets —
        # that would incorrectly block SAFE when DB collectors are silent for a
        # different team's agent.
        if scope_entity_id and "vendor-risk" in scope_entity_id:
            restored = await self.coverage_repo.list_probe_restorations(scope_entity_id)
            return frozenset(
                channel
                for channel in _VENDOR_RISK_SUPPRESSED
                if channel.value not in restored
            )

        if scope_entity_id:
            return frozenset()

        # Estate-wide coverage panel: surface unhealthy / suppressed channels.
        health = await self.coverage_repo.list_channel_health()
        suppressed: set[EvidenceChannel] = set()
        for row in health:
            channel_raw = str(row.get("channel", ""))
            try:
                channel = EvidenceChannel(channel_raw)
            except ValueError:
                continue
            score = float(row.get("health_score", 1.0))
            details = row.get("details") or {}
            suspected = bool(
                row.get("suppression_suspected") or details.get("suppression_suspected")
            )
            if suspected or score < 0.4:
                suppressed.add(channel)
        return frozenset(suppressed)

    async def restore_channels_for_probe(
        self,
        entity_id: str,
        channels: list[EvidenceChannel],
    ) -> set[str]:
        """
        Apply a planned probe by lifting suppression for the given channels.

        Does not invent evidence edges — records a restoration and clears
        channel-health suppression flags for those channels.
        """
        channel_values = [ch.value for ch in channels]
        restored = await self.coverage_repo.record_probe_restorations(entity_id, channel_values)
        for channel in channels:
            await self.coverage_repo.upsert_channel_health(
                channel.value,
                health_score=1.0,
                lag_seconds=0.0,
                details={
                    "probe_restored_for": entity_id,
                    "mode": "suppression_lift",
                },
                suppression_suspected=False,
            )
        return restored

    async def snapshot(self, *, scope: str | None = None) -> dict[str, Any]:
        est = await self.estimate(scope_entity_id=scope)
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

    async def list_snapshots(
        self, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        return await self.coverage_repo.list_snapshots(offset=offset, limit=limit)

    async def channel_health(self) -> list[dict[str, Any]]:
        return await self.coverage_repo.list_channel_health()
