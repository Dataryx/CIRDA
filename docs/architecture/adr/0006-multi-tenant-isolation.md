# ADR 0006: Multi-tenant logical isolation

- Status: Accepted
- Date: 2026-09-28

## Context

CIRDA 0.1.0 was single-tenant. Operators need isolation between estates without
immediately requiring physical DB partitioning.

## Decision

- Add `tenant_id` (default `default`) to primary data tables (migration 0007).
- Resolve tenant from `X-CIRDA-Tenant` when `CIRDA_MULTI_TENANT_ENABLED=true`.
- Scope entity repository reads/writes to the active tenant.
- Do not merge graphs across tenants for gate/blast decisions.

## Consequences

- Cross-tenant entity ID reuse is allowed (same `entity_id` in different tenants).
- Full edge/evidence/decision tenant scoping continues in follow-up; entity isolation
  is the load-bearing boundary for evaluate inputs via graph build from entities+edges.
- Postgres RLS may be added later as defense in depth.
