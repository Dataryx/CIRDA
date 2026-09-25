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
- Probe apply lifts channel suppression only (`CIRDA_PROBE_EXECUTION_ENABLED`); live collector execution is not implemented
- Necessity is operator-annotated (`PATCH /api/v1/edges/{id}`) with suggest-only heuristics (`GET /edges/necessity-suggestions`); auto-mutate inference is not implemented
- Kafka ingest path requires Redpanda/Kafka in full stack; lite mode uses in-memory bus
- E2E tests require Docker and Playwright browser install

[0.1.0]: https://github.com/cirda/cirda/releases/tag/v0.1.0
