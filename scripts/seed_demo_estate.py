#!/usr/bin/env python3
"""
Seed a realistic demo agent estate for CIRDA local development.

Scenarios:
  - UNSAFE: invoice-reconciler-agent (critical downstream deps)
  - SAFE: legacy-csv-export-agent (isolated)
  - INDETERMINATE: vendor-risk-agent (ambiguous identity, low coverage)
  - Mediated dependency chain (orchestrator -> mediator -> payment-api)
  - Ambiguous identity (vendor-risk-agent / vendor_risk alias)
  - Decaying edge (old trace on legacy export path)
  - Suppression scenario (messaging channel gap)

Idempotent: uses deterministic event IDs and upsert-friendly entity creation.
Guard: requires CIRDA_ENV=local (or CIRDA_APP_ENV=development).
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

NOW = datetime.now(timezone.utc)
SEED_MARKER = "cirda-demo-estate-v1"
API_BASE = os.environ.get("CIRDA_API_URL", "http://localhost:8000")
AUTH_HEADERS = {"Authorization": "Bearer dev", "X-CIRDA-Role": "admin"}

DEMO_AGENT_IDS = (
    "invoice-reconciler-agent",
    "legacy-csv-export-agent",
    "vendor-risk-agent",
)

HEALTH_PATHS = ("/healthz", "/api/v1/health", "/health")


def _guard_local() -> None:
    env = os.environ.get("CIRDA_ENV", "").lower()
    app_env = os.environ.get("CIRDA_APP_ENV", "development").lower()
    if env != "local" and app_env not in ("development", "dev"):
        print("ERROR: seed_demo_estate.py requires CIRDA_ENV=local or CIRDA_APP_ENV=development")
        sys.exit(1)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _entities() -> list[dict[str, Any]]:
    return [
        {
            "entity_id": "invoice-reconciler-agent",
            "entity_type": "agent",
            "name": "Invoice Reconciler Agent",
            "criticality": "critical",
            "metadata": {"team": "finance", SEED_MARKER: True},
        },
        {
            "entity_id": "legacy-csv-export-agent",
            "entity_type": "agent",
            "name": "Legacy CSV Export Agent",
            "criticality": "low",
            "metadata": {"team": "ops", SEED_MARKER: True},
        },
        {
            "entity_id": "vendor-risk-agent",
            "entity_type": "agent",
            "name": "Vendor Risk Agent",
            "criticality": "high",
            "metadata": {"team": "risk", "aliases": ["vendor_risk"], SEED_MARKER: True},
        },
        {
            "entity_id": "payment-orchestrator-agent",
            "entity_type": "agent",
            "name": "Payment Orchestrator",
            "criticality": "critical",
            "metadata": {SEED_MARKER: True},
        },
        {
            "entity_id": "payment-mediator-service",
            "entity_type": "service",
            "name": "Payment Mediator",
            "criticality": "high",
            "metadata": {SEED_MARKER: True},
        },
        {
            "entity_id": "payment-api",
            "entity_type": "service",
            "name": "Payment API",
            "criticality": "critical",
            "metadata": {SEED_MARKER: True},
        },
        {
            "entity_id": "ledger-db",
            "entity_type": "data",
            "name": "Ledger Database",
            "criticality": "critical",
            "metadata": {SEED_MARKER: True},
        },
        {
            "entity_id": "invoice-queue",
            "entity_type": "queue",
            "name": "Invoice Events Queue",
            "criticality": "high",
            "metadata": {SEED_MARKER: True},
        },
        {
            "entity_id": "vendor-db",
            "entity_type": "data",
            "name": "Vendor Registry DB",
            "criticality": "medium",
            "metadata": {SEED_MARKER: True},
        },
        {
            "entity_id": "csv-export-bucket",
            "entity_type": "data",
            "name": "CSV Export Bucket",
            "criticality": "low",
            "metadata": {SEED_MARKER: True},
        },
    ]


def _events() -> list[dict[str, Any]]:
    """Deterministic evidence events covering all demo scenarios."""
    t_recent = NOW - timedelta(hours=2)
    t_old = NOW - timedelta(days=30)  # decaying edge

    return [
        # --- UNSAFE: invoice-reconciler-agent critical chain ---
        {
            "event_id": "seed-001-invoice-calls-ledger",
            "source": "trace",
            "source_id": "invoice-reconciler-agent",
            "target_id": "ledger-db",
            "relation": "writes",
            "observed_at": _iso(t_recent),
        },
        {
            "event_id": "seed-002-invoice-publishes-queue",
            "source": "trace",
            "source_id": "invoice-reconciler-agent",
            "target_id": "invoice-queue",
            "relation": "publishes",
            "observed_at": _iso(t_recent - timedelta(minutes=5)),
        },
        {
            "event_id": "seed-003-orchestrator-delegates-invoice",
            "source": "trace",
            "source_id": "payment-orchestrator-agent",
            "target_id": "invoice-reconciler-agent",
            "relation": "delegates",
            "observed_at": _iso(t_recent - timedelta(minutes=10)),
        },
        # --- Mediated dependency: orchestrator -> mediator -> payment-api ---
        {
            "event_id": "seed-004-orchestrator-calls-mediator",
            "source": "trace",
            "source_id": "payment-orchestrator-agent",
            "target_id": "payment-mediator-service",
            "relation": "calls",
            "observed_at": _iso(t_recent - timedelta(minutes=15)),
        },
        {
            "event_id": "seed-005-mediator-calls-payment-api",
            "source": "trace",
            "source_id": "payment-mediator-service",
            "target_id": "payment-api",
            "relation": "calls",
            "observed_at": _iso(t_recent - timedelta(minutes=14)),
        },
        {
            "event_id": "seed-006-invoice-reads-payment-api",
            "source": "trace",
            "source_id": "invoice-reconciler-agent",
            "target_id": "payment-api",
            "relation": "reads",
            "observed_at": _iso(t_recent - timedelta(minutes=12)),
        },
        # --- SAFE: legacy-csv-export-agent isolated (only weak old edge) ---
        {
            "event_id": "seed-007-legacy-writes-bucket-decaying",
            "source": "trace",
            "source_id": "legacy-csv-export-agent",
            "target_id": "csv-export-bucket",
            "relation": "writes",
            "observed_at": _iso(t_old),
        },
        # --- INDETERMINATE: vendor-risk-agent sparse + ambiguous identity ---
        {
            "event_id": "seed-008-vendor-risk-reads-vendor-db",
            "source": "trace",
            "source_id": "vendor-risk-agent",
            "target_id": "vendor-db",
            "relation": "reads",
            "observed_at": _iso(t_recent - timedelta(days=3)),
        },
        {
            "event_id": "seed-009-ambiguous-alias-vendor_risk",
            "source": "agent_framework",
            "channel": "agent_framework",
            "agent_id": "vendor_risk",
            "target_id": "vendor-db",
            "action": "call",
            "relation": "reads",
            "observed_at": _iso(t_recent - timedelta(days=2)),
        },
        # --- Suppression: messaging channel declared but no recent events ---
        {
            "event_id": "seed-010-static-invoice-queue-binding",
            "source": "static",
            "channel": "static_declared",
            "source_id": "invoice-reconciler-agent",
            "target_id": "invoice-queue",
            "relation": "publishes",
            "observed_at": _iso(NOW - timedelta(days=60)),
        },
        # Reinforce trace coverage for invoice-reconciler (UNSAFE path)
        *[
            {
                "event_id": f"seed-trace-reinf-{i:03d}",
                "source": "trace",
                "source_id": "invoice-reconciler-agent",
                "target_id": "ledger-db",
                "relation": "writes",
                "observed_at": _iso(t_recent - timedelta(minutes=i)),
            }
            for i in range(1, 6)
        ],
    ]


class HttpSeeder:
    def __init__(self, base_url: str) -> None:
        self.client = httpx.Client(base_url=base_url, headers=AUTH_HEADERS, timeout=30.0)

    def health(self) -> tuple[bool, str | None]:
        for path in HEALTH_PATHS:
            try:
                response = self.client.get(path)
                if response.status_code >= 500:
                    return False, f"{path} returned {response.status_code}"
                if response.status_code == 200:
                    return True, path
            except httpx.HTTPError:
                continue
        return False, None

    def list_entity_ids(self) -> set[str]:
        response = self.client.get("/api/v1/entities", params={"limit": 100})
        if response.status_code != 200:
            return set()
        payload = response.json()
        return {item["entity_id"] for item in payload.get("items", [])}

    def demo_estate_present(self) -> bool:
        return all(agent_id in self.list_entity_ids() for agent_id in DEMO_AGENT_IDS)

    def upsert_entity(self, entity: dict[str, Any]) -> None:
        response = self.client.post("/api/v1/entities", json=entity)
        if response.status_code not in (200, 201):
            print(f"  WARN entity {entity['entity_id']}: {response.status_code} {response.text[:120]}")

    def ingest_event(self, raw: dict[str, Any]) -> bool:
        response = self.client.post("/api/v1/ingest/events", json={"raw": raw})
        if response.status_code != 200:
            print(f"  WARN event {raw.get('event_id')}: {response.status_code}")
            return False
        return response.json().get("created", False)

    def upsert_channel_health(self, payload: dict[str, Any]) -> None:
        response = self.client.post("/api/v1/admin/channel-health", json=payload)
        if response.status_code not in (200, 201):
            print(f"  WARN channel-health {payload.get('channel')}: {response.status_code}")

    def patch_edge_necessity(self, edge_id: str, necessity: str) -> None:
        response = self.client.patch(f"/api/v1/edges/{edge_id}", json={"necessity": necessity})
        if response.status_code != 200:
            print(f"  WARN edge necessity {edge_id}: {response.status_code} {response.text[:120]}")
        else:
            print(f"  necessity: {edge_id} -> {necessity}")


def seed_entities_and_events(seeder: HttpSeeder) -> None:
    print("==> Seeding entities")
    for entity in _entities():
        seeder.upsert_entity(entity)
        print(f"  entity: {entity['entity_id']}")

    print("==> Ingesting evidence events")
    created = 0
    for raw in _events():
        if seeder.ingest_event(raw):
            created += 1
    print(f"==> Done. {created} new events ingested (duplicates skipped).")

    print("==> Seeding channel health (database/messaging suppression narrative)")
    seeder.upsert_channel_health(
        {
            "channel": "database",
            "health_score": 0.22,
            "lag_seconds": 14400,
            "suppression_suspected": True,
            "details": {
                "reporting_sources": 1,
                "expected_sources": 9,
                "notes": "6 of 9 expected audit sources silent for 4h",
            },
        }
    )
    seeder.upsert_channel_health(
        {
            "channel": "messaging",
            "health_score": 0.35,
            "lag_seconds": 3600,
            "suppression_suspected": True,
            "details": {"reporting_sources": 2, "expected_sources": 5},
        }
    )
    seeder.upsert_channel_health(
        {
            "channel": "trace",
            "health_score": 0.96,
            "lag_seconds": 12,
            "suppression_suspected": False,
            "details": {},
        }
    )
    print("==> Annotating optional necessity (demo load-bearing vs optional path)")
    # WRITES is retained: invoice→ledger stays load-bearing (UNSAFE).
    # Mark a secondary retained edge optional so critical blast skips it.
    seeder.patch_edge_necessity(
        "invoice-reconciler-agent->invoice-queue:publishes",
        "optional",
    )
    print("Evaluate decisions in the UI or via POST /api/v1/decisions/evaluate")


def seed_via_http(base_url: str, *, force_events: bool, skip_if_seeded: bool) -> None:
    seeder = HttpSeeder(base_url)
    ok, path = seeder.health()
    if not ok:
        print(f"ERROR: API not reachable at {base_url}. Start with: scripts/dev-lite.ps1 or make dev-lite")
        sys.exit(1)
    print(f"==> API healthy via {path}")

    if skip_if_seeded and seeder.demo_estate_present() and not force_events:
        print("==> Demo estate already seeded (all verdict-path agents present). Skipping.")
        print("    Use --force to re-ingest events anyway.")
        return

    seed_entities_and_events(seeder)


def seed_via_direct(*, force_events: bool) -> None:
    """Direct in-process seed using memory store (no running API)."""
    os.environ["CIRDA_MEMORY_STORE"] = "true"
    os.environ["CIRDA_EVENT_BUS"] = "inmemory"
    os.environ["CIRDA_AUTH_MODE"] = "dev"
    os.environ["CIRDA_SCHEDULER_ENABLED"] = "false"
    os.environ.setdefault("CIRDA_ENV", "local")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(root, "packages", "cirda-core", "src"))
    sys.path.insert(0, os.path.join(root, "apps", "api", "src"))

    import asyncio

    from cirda_api.container import build_container
    from cirda_api.settings import Settings, get_settings

    get_settings.cache_clear()
    cfg = Settings()

    async def _run() -> None:
        container = build_container(cfg)
        for entity in _entities():
            await container.entity_service.upsert_entity(
                entity_id=entity["entity_id"],
                entity_type=entity["entity_type"],
                name=entity["name"],
                criticality=entity["criticality"],
                metadata=entity["metadata"],
            )
            print(f"  entity: {entity['entity_id']}")

        created = 0
        for raw in _events():
            result = await container.ingest_service.ingest_raw(raw)
            if result["created"]:
                created += 1

        # Channel health: database/messaging silent → vendor-risk coverage gap at `now`.
        await container.coverage_service.coverage_repo.upsert_channel_health(
            "database",
            health_score=0.22,
            lag_seconds=14_400,
            suppression_suspected=True,
            details={
                "reporting_sources": 1,
                "expected_sources": 9,
                "notes": "6 of 9 expected audit sources silent for 4h",
            },
        )
        await container.coverage_service.coverage_repo.upsert_channel_health(
            "messaging",
            health_score=0.35,
            lag_seconds=3_600,
            suppression_suspected=True,
            details={"reporting_sources": 2, "expected_sources": 5},
        )
        await container.coverage_service.coverage_repo.upsert_channel_health(
            "trace",
            health_score=0.96,
            lag_seconds=12,
            suppression_suspected=False,
        )
        # Optional secondary path: critical blast still uses ledger; queue edge ignored.
        annotated = await container.edge_service.update_necessity(
            "invoice-reconciler-agent->invoice-queue:publishes",
            "optional",
        )
        if annotated:
            print("==> Necessity: invoice-reconciler-agent->invoice-queue:publishes -> optional")
        print(f"==> Direct seed complete. {created} new events.")
        print("==> Channel health: database+messaging suppression for vendor-risk narrative.")

    print("==> Seeding entities")
    asyncio.run(_run())
    if force_events:
        print("==> --force has no extra effect in direct mode (events are always upserted by event_id).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed CIRDA demo estate for local retirement workflow demos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  CIRDA_ENV=local uv run python scripts/seed_demo_estate.py
      Seed via HTTP against http://localhost:8000 (API must be running).

  CIRDA_ENV=local uv run python scripts/seed_demo_estate.py --direct
      Seed in-process with CIRDA_MEMORY_STORE (no API server required).

  uv run python scripts/seed_demo_estate.py --api-url http://127.0.0.1:8000 --force
      Re-upsert entities and attempt all event ingests even if agents exist.

Verdict-path agents created:
  invoice-reconciler-agent  -> UNSAFE (evaluate at as_of=now)
  legacy-csv-export-agent   -> SAFE (evaluate at as_of=now)
  vendor-risk-agent         -> INDETERMINATE (target-scoped silent DB/messaging
                              channels drop coverage below C_min=0.85 at `now`)
        """,
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Seed in-process with memory store (sets CIRDA_MEMORY_STORE=true; no HTTP API required).",
    )
    parser.add_argument(
        "--api-url",
        default=API_BASE,
        help=f"API base URL for HTTP mode (default: {API_BASE}, env CIRDA_API_URL).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Always upsert entities and ingest events (HTTP mode skips early exit when demo agents exist).",
    )
    parser.add_argument(
        "--no-skip-if-seeded",
        action="store_true",
        help="Do not skip HTTP seed when all demo agents are already present.",
    )
    args = parser.parse_args()

    _guard_local()
    print(f"==> CIRDA demo estate seeder ({SEED_MARKER})")

    if args.direct:
        print("==> Mode: direct (in-process memory store)")
        seed_via_direct(force_events=args.force)
    else:
        print(f"==> Mode: HTTP ({args.api_url.rstrip('/')})")
        seed_via_http(
            args.api_url.rstrip("/"),
            force_events=args.force,
            skip_if_seeded=not args.no_skip_if_seeded,
        )


if __name__ == "__main__":
    main()
