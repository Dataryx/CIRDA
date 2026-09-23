# ADR 0002: Postgres as Graph System of Record

## Status

Accepted

## Context

CIRDA needs durable entity/edge storage, transactional ingest, and snapshot queries
for the API and dashboard. Alternatives included pure in-memory graphs and dedicated
graph databases.

## Decision

Use **PostgreSQL** as the system of record for entities, edges, evidence events,
and decision snapshots. NetworkX (`cirda_core.graph.kernel`) builds in-memory
DiGraphs for analysis; Postgres holds authoritative state.

## Consequences

- **Positive:** ACID ingest, familiar ops tooling, joins with audit tables
- **Negative:** Large blast-radius queries require bounded traversal caps
- **Neutral:** `cirda-core` remains storage-agnostic; adapters live in `apps/api`
