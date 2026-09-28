# ADR 0006: Multi-tenant logical isolation

- Status: Accepted
- Date: 2026-09-28
- Updated: 2026-09-28 (Phase 2)

## Context

CIRDA 0.1.0 was single-tenant. Operators need isolation between estates without
immediately requiring physical DB partitioning.

## Decision

### Phase 1
- Add `tenant_id` (default `default`) to primary data tables (migration 0007).
- Resolve tenant from `X-CIRDA-Tenant` when `CIRDA_MULTI_TENANT_ENABLED=true`.
- Scope entity repository reads/writes to the active tenant.

### Phase 2 (complete)
- Composite entity PK `(tenant_id, entity_id)` and edge PK `(tenant_id, edge_id)`
  (migration 0008) so the same logical id can exist in multiple tenants.
- Composite FKs for aliases / edges / decisions → entities.
- Tenant-scoped queries for edges, evidence, decisions, coverage snapshots,
  and channel health (ORM + memory store).
- Idempotency uniqueness is `(tenant_id, idempotency_key)`.
- Channel health PK is `(tenant_id, channel)`.

## Consequences

- Cross-tenant entity ID reuse is supported.
- Graph / evaluate / blast / ingest inherit isolation via repository filters
  once request context sets the tenant.
- Postgres RLS may be added later as defense in depth.
- Child tables `decision_paths` / `runbook_executions` inherit isolation via
  parent `decision_id` (UUID) after tenant-scoped decision create/get.
