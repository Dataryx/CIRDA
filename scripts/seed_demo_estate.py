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

    def health(self) -> bool:
        try:
            r = self.client.get("/api/v1/health")
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    def upsert_entity(self, entity: dict[str, Any]) -> None:
        r = self.client.post("/api/v1/entities", json=entity)
        if r.status_code not in (200, 201):
            print(f"  WARN entity {entity['entity_id']}: {r.status_code} {r.text[:120]}")

    def ingest_event(self, raw: dict[str, Any]) -> bool:
        r = self.client.post("/api/v1/ingest/events", json={"raw": raw})
        if r.status_code != 200:
            print(f"  WARN event {raw.get('event_id')}: {r.status_code}")
            return False
        return r.json().get("created", False)


def seed_via_http(base_url: str) -> None:
    seeder = HttpSeeder(base_url)
    if not seeder.health():
        print(f"ERROR: API not reachable at {base_url}. Start with: make dev")
        sys.exit(1)

    print(f"==> Seeding entities via {base_url}")
    for entity in _entities():
        seeder.upsert_entity(entity)
        print(f"  entity: {entity['entity_id']}")

    print("==> Ingesting evidence events")
    created = 0
    for raw in _events():
        if seeder.ingest_event(raw):
            created += 1
    print(f"==> Done. {created} new events ingested (duplicates skipped).")
    print("Evaluate decisions in the UI or via POST /api/v1/decisions/evaluate")


def seed_via_direct() -> None:
    """Direct in-process seed using memory store (no running API)."""
    os.environ.setdefault("CIRDA_MEMORY_STORE", "true")
    os.environ.setdefault("CIRDA_EVENT_BUS", "inmemory")
    os.environ.setdefault("CIRDA_AUTH_MODE", "dev")
    os.environ.setdefault("CIRDA_SCHEDULER_ENABLED", "false")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(root, "packages", "cirda-core", "src"))
    sys.path.insert(0, os.path.join(root, "apps", "api", "src"))

    import asyncio

    from cirda_api.container import build_container
    from cirda_api.db.session import create_all_tables, init_db
    from cirda_api.settings import Settings

    async def _run() -> None:
        cfg = Settings()
        init_db(cfg)
        await create_all_tables()
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
        print(f"==> Direct seed complete. {created} new events.")

    asyncio.run(_run())


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed CIRDA demo estate")
    parser.add_argument("--direct", action="store_true", help="Seed in-process without HTTP API")
    parser.add_argument("--api-url", default=API_BASE, help="API base URL")
    args = parser.parse_args()

    _guard_local()
    print(f"==> CIRDA demo estate seeder ({SEED_MARKER})")

    if args.direct:
        print("==> Mode: direct (in-process memory store)")
        seed_via_direct()
    else:
        print(f"==> Mode: HTTP ({args.api_url})")
        seed_via_http(args.api_url.rstrip("/"))


if __name__ == "__main__":
    main()
