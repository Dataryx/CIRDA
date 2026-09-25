"""Decision evaluation service (immutable decisions, INV-013)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from cirda_core.analysis.critical_paths import enumerate_critical_paths
from cirda_core.decision.explanation import explain_decision
from cirda_core.decision.gate import evaluate_gate_from_layers
from cirda_core.decision.probe_planner import estimate_probe_delta_c, plan_probes
from cirda_core.domain.enums import EvidenceChannel, GraphLayer, Verdict
from cirda_core.version import ENGINE_VERSION

from cirda_api.db.repositories.decision import DecisionRepository
from cirda_api.db.repositories.evidence import EvidenceRepository
from cirda_api.services.coverage_service import CoverageService
from cirda_api.services.graph_service import GraphService
from cirda_api.services.policy import build_policy
from cirda_api.settings import Settings


class DecisionService:
    def __init__(
        self,
        decision_repo: DecisionRepository,
        graph_service: GraphService,
        coverage_service: CoverageService,
        evidence_repo: EvidenceRepository,
        settings: Settings,
    ) -> None:
        self.decision_repo = decision_repo
        self.graph_service = graph_service
        self.coverage_service = coverage_service
        self.evidence_repo = evidence_repo
        self.settings = settings

    async def evaluate(
        self,
        entity_id: str,
        *,
        as_of: datetime | None = None,
        change_type: str | None = None,
        created_by: str | None = None,
        supersedes_id: str | None = None,
    ) -> dict[str, Any]:
        as_of = as_of or datetime.now(timezone.utc)
        policy = build_policy(self.settings)
        g_c = await self.graph_service.build_digraph(GraphLayer.CONFIRMED, as_of=as_of)
        g_p = await self.graph_service.build_digraph(GraphLayer.POSSIBLE, as_of=as_of)
        coverage_est, coverage_inputs = await self.coverage_service.estimate_with_inputs(
            as_of=as_of,
            scope_entity_id=entity_id,
        )
        gate = evaluate_gate_from_layers(
            confirmed_graph=g_c,
            possible_graph=g_p,
            source_entity_id=entity_id,
            coverage=coverage_est["coverage"],
            policy=policy,
        )
        explanation = explain_decision(gate, entity_id)
        blast = await self._blast_summary(entity_id, as_of=as_of)
        rationale: dict[str, Any] = {
            "summary": explanation.summary,
            "details": list(explanation.details),
            "reason_codes": sorted(gate.reason_codes),
            "blast_radius": blast,
            "coverage_breakdown": coverage_est,
            "suggested_runbook": [
                {"stage": a.stage.value, "description": a.description, "entity_id": a.entity_id}
                for a in explanation.suggested_runbook
            ],
            "suggested_probes": [],
        }
        if gate.verdict == Verdict.INDETERMINATE:
            missing = self._missing_channels(coverage_est)
            rationale["suggested_probes"] = [
                {
                    "entity_id": plan.entity_id,
                    "channels": [ch.value for ch in plan.channels],
                    "rationale": plan.rationale,
                    "expected_delta_c": plan.expected_delta_c,
                }
                for plan in plan_probes(
                    entity_id,
                    missing,
                    policy,
                    coverage_inputs=coverage_inputs,
                )
            ]
        decision_id = str(uuid.uuid4())
        paths = [
            {
                "path_nodes": list(p.path_nodes),
                "path_confidence": p.path_confidence,
                "is_critical_path": p.is_critical_path,
            }
            for p in enumerate_critical_paths(
                g_p,
                entity_id,
                criticality_threshold=policy.critical_threshold,
            )
        ]
        record = {
            "decision_id": decision_id,
            "entity_id": entity_id,
            "verdict": gate.verdict.value,
            "coverage": gate.coverage,
            "truncated": gate.truncated,
            "reason_codes": sorted(gate.reason_codes),
            "rationale": rationale,
            "as_of": as_of,
            "engine_version": ENGINE_VERSION,
            "change_type": change_type,
            "supersedes_id": supersedes_id,
            "created_by": created_by,
            "paths": paths,
        }
        stored = await self.decision_repo.create(record)
        if supersedes_id:
            await self.decision_repo.mark_superseded(supersedes_id, decision_id)
        return self._to_response(stored)

    @staticmethod
    def _missing_channels(coverage_est: dict[str, Any]) -> list[EvidenceChannel]:
        raw = coverage_est.get("suppressed_channels") or []
        channels: list[EvidenceChannel] = []
        for item in raw:
            try:
                channels.append(EvidenceChannel(str(item)))
            except ValueError:
                continue
        return channels

    async def apply_probes(
        self,
        entity_id: str,
        channels: list[str],
        *,
        as_of: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Apply planned probes by lifting channel suppression (not live collectors).

        Requires probe_planning_enabled and probe_execution_enabled.
        """
        if not self.settings.probe_execution_enabled:
            raise PermissionError("probe execution is disabled")
        if not self.settings.probe_planning_enabled:
            raise PermissionError("probe planning must be enabled to apply probes")
        if not channels:
            raise ValueError("channels must be non-empty")

        parsed: list[EvidenceChannel] = []
        for raw in channels:
            try:
                parsed.append(EvidenceChannel(str(raw)))
            except ValueError as exc:
                raise ValueError(f"unknown evidence channel: {raw}") from exc

        as_of = as_of or datetime.now(timezone.utc)
        before, inputs = await self.coverage_service.estimate_with_inputs(
            as_of=as_of,
            scope_entity_id=entity_id,
        )
        expected = estimate_probe_delta_c(inputs, frozenset(parsed))
        await self.coverage_service.restore_channels_for_probe(entity_id, parsed)
        after, _ = await self.coverage_service.estimate_with_inputs(
            as_of=as_of,
            scope_entity_id=entity_id,
        )
        actual = float(after["coverage"]) - float(before["coverage"])
        return {
            "entity_id": entity_id,
            "channels": [ch.value for ch in parsed],
            "mode": "suppression_lift",
            "coverage_before": before["coverage"],
            "coverage_after": after["coverage"],
            "expected_delta_c": round(expected, 6),
            "actual_delta_c": round(actual, 6),
            "suppressed_channels_after": after["suppressed_channels"],
            "as_of": as_of,
        }

    async def rerun(self, decision_id: str, *, created_by: str | None = None) -> dict[str, Any]:
        prior = await self.decision_repo.get(decision_id)
        if not prior:
            raise KeyError(decision_id)
        return await self.evaluate(
            prior["entity_id"],
            as_of=datetime.now(timezone.utc),
            change_type=prior.get("change_type"),
            created_by=created_by,
            supersedes_id=decision_id,
        )

    async def get(self, decision_id: str) -> dict[str, Any] | None:
        row = await self.decision_repo.get(decision_id)
        return self._to_response(row) if row else None

    async def list_for_entity(self, entity_id: str, *, offset: int = 0, limit: int = 20) -> tuple[list[dict[str, Any]], int]:
        rows, total = await self.decision_repo.list_for_entity(entity_id, offset=offset, limit=limit)
        return [self._to_response(r) for r in rows if r], total

    async def _blast_summary(self, entity_id: str, *, as_of: datetime) -> dict[str, Any]:
        from cirda_core.analysis.blast_radius import compute_blast_radius

        g_p = await self.graph_service.build_digraph(GraphLayer.POSSIBLE, as_of=as_of)
        policy = build_policy(self.settings)
        br = compute_blast_radius(g_p, entity_id, criticality_threshold=policy.critical_threshold)
        return {
            "all_reachable_count": len(br.all_reachable),
            "critical_reachable_count": len(br.critical_reachable),
            "critical_reachable": sorted(br.critical_reachable),
            "truncated": br.truncated,
            "layer": GraphLayer.POSSIBLE.value,
        }

    def _to_response(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "decision_id": row["decision_id"],
            "entity_id": row["entity_id"],
            "verdict": row["verdict"],
            "coverage": row["coverage"],
            "truncated": row.get("truncated", False),
            "reason_codes": row.get("reason_codes", []),
            "rationale": row.get("rationale", {}),
            "limitations_footer": self.settings.decision_limitations_footer,
            "as_of": row["as_of"],
            "engine_version": row["engine_version"],
            "change_type": row.get("change_type"),
            "supersedes": row.get("supersedes_id"),
            "superseded_by": row.get("superseded_by_id"),
            "created_by": row.get("created_by"),
            "created_at": row.get("created_at"),
            "paths": row.get("paths", []),
        }
