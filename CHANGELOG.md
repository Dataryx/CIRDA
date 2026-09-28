# Changelog

All notable changes to CIRDA are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-23

### Added

- Monorepo scaffold: `cirda-core`, `cirda-bench`, `cirda-api`, `cirda-ingest`, `@cirda/web`
- Coverage-informed tri-state decision gate (UNSAFE / SAFE / INDETERMINATE)
- Temporal dependency graph with evidence decay and entity resolution
- FastAPI control plane with ingest, graph, decision, coverage, and benchmark endpoints
- React dashboard with topology, entity, evidence, and calibration views
- Benchmark harness reproducing paper Table II shape constraints
- Docker Compose stacks (full, dev hot-reload, lite in-memory)
- Helm chart, Grafana dashboards, and GitHub Actions CI pipelines
- Contract package: OpenAPI 3.1 spec, JSON Schemas, and example payloads
- Demo estate seeder with UNSAFE/SAFE/INDETERMINATE scenarios

### Known Limitations

- Paper fidelity is partial; see [docs/paper/fidelity-matrix.md](docs/paper/fidelity-matrix.md)
- Probe planning (coverage-gap + expected ΔC) is flag-gated (`CIRDA_PROBE_PLANNING_ENABLED=false` by default)
- Probe apply lifts suppression (`CIRDA_PROBE_EXECUTION_ENABLED`); live HTTP collectors need `CIRDA_PROBE_COLLECTOR_ENABLED` + `metadata.probe_url`
- Necessity auto-mutate is flag-gated (`CIRDA_NECESSITY_AUTO_MUTATE_ENABLED`; default required-only at high confidence)
- Multi-tenant logical isolation is flag-gated (`CIRDA_MULTI_TENANT_ENABLED` + `X-CIRDA-Tenant`; ADR 0006 Phase 2: composite PKs + scoped edges/evidence/decisions/coverage)
- Decision reports include load-bearing critical paths (`paths`) when critical dependents exist
- Runbook executions are seeded on evaluate and advanced via `PATCH /decisions/{id}/runbook/{execution_id}`
- Channel health `lag_seconds` feeds INV-002 (`ingest_lag_exceeded` blocks SAFE when lag exceeds `max_ingest_lag_seconds`)
- Entity aliases persist on create; orphan alias nodes / collisions emit `ambiguous_identity` and block SAFE
- Ingest resolves unique aliases to canonical entity ids (collision aliases passthrough)
- Worker loads DB aliases into EntityResolver and preserves operator necessity on re-ingest
- Static DECLARED channels can confirm edges (`has_confirming_evidence`)
- Analysis UI at `/analysis` (blast / reachability / paths)
- Table II: 40/60 cells in tolerance, all 15 CIRDA cells pass; 20 residual `xfail` cells are structural baseline gaps (trace_only shape, union false_safe / recall overshoot); CIRDA false_safe=0 is exact — see `CALIBRATION.md`
- Simulator models spurious direct evidence (`DIRECT_NOISE_RATE_BY_LOSS`, separate RNG stream) so union baselines no longer score blast precision = 1.000 by construction; regression-aware sweep in `scripts/sweep_direct_noise.py`
- Fused-support reliability report (`cirda_bench.metrics.reliability`, `scripts/support_reliability.py`): S is conservative on simulator truth; weak-signal weights stay heuristic
- Support S is calibrated support, not causal probability (limitations footer on every decision)
- Kafka ingest path requires Redpanda/Kafka in full stack; lite mode uses in-memory bus
- Topology viz styles load-bearing vs optional/redundant necessity; coverage page surfaces INV-002 lag
- Entity create UI accepts aliases; edge evidence page supports manual necessity PATCH
- E2E tests require Docker and Playwright browser install (11/11 green against the lite stack with the demo seed)
- Alembic chain 0001→0008 applies cleanly on Postgres (fixed 0007/0008 revision ids); multi-tenant isolation verified on Postgres via `test_multi_tenant_postgres.py`
- Entity upsert no longer lazy-loads aliases in async context (MissingGreenlet fix)
- Demo seed keeps database/messaging suppression but lag within `max_ingest_lag_seconds`, so the SAFE scenario is not blocked by INV-002
- Safety-critical flags (`CIRDA_PROBE_*`, `CIRDA_NECESSITY_AUTO_*`, `CIRDA_MULTI_TENANT_*`) default off

[0.1.0]: https://github.com/cirda/cirda/releases/tag/v0.1.0
