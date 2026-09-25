# CIRDA

**Coverage-Informed Retirement Decision Analysis** — a monorepo implementing the CIRDA paper's dependency graph inference, observability coverage estimation, and tri-state safety gate for AI agent estate retirement.

CIRDA answers: *"Can we safely retire or decommission this agent given what we can observe?"* The engine produces **UNSAFE**, **SAFE**, or **INDETERMINATE** verdicts with explicit coverage and rationale — never a false sense of certainty.

## Quick Start

```bash
# 1. Bootstrap dependencies (uv + pnpm)
make bootstrap

# 2. Start API (:8000) and web UI (:5173)
make dev

# 3. Seed the demo estate (separate terminal, API must be running)
make seed
```

Open [http://localhost:5173](http://localhost:5173) and explore the demo agents.

### Windows Notes

- **Preferred:** Git Bash or WSL2 with `make`, `uv`, and `pnpm` on PATH.
- **PowerShell:** `.\scripts\bootstrap.ps1` then `.\scripts\verify.ps1` for the CI-mirror check.
- Docker Desktop with WSL2 backend is required for full `docker compose` and E2E stacks.

### Lite Mode (no Postgres/Redis)

```bash
make dev-lite
# Windows:
powershell -ExecutionPolicy Bypass -File scripts/dev-lite.ps1
```

Uses in-memory store and an in-memory event bus — ideal for first-time exploration.

### Docker Compose (Postgres)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/compose-up.ps1
# Web http://localhost:3000  API http://localhost:8000
```

Lite profile: Postgres + Redis + API + Web. Use `-Profile full` for Redpanda/ingest.

## Repository Layout

| Path | Description |
|------|-------------|
| `packages/cirda-core` | Domain engine: graph, inference, coverage, decision gate |
| `packages/cirda-bench` | Benchmark harness (Table II reproduction) |
| `packages/contracts` | OpenAPI 3.1, JSON Schemas, example payloads |
| `apps/api` | FastAPI control plane |
| `apps/ingest-worker` | Evidence ingest (Kafka/OTLP/file/in-memory) |
| `apps/web` | React dashboard (Vite + TanStack Query) |
| `deploy/` | Docker Compose, Helm, Grafana dashboards |
| `docs/` | Architecture, ADRs, runbooks, paper fidelity matrix |

## Make Targets

| Target | Purpose |
|--------|---------|
| `bootstrap` | Install deps, pre-commit, copy `.env.example` |
| `dev` | API + web hot reload |
| `dev-lite` | In-memory dev stack |
| `seed` | Demo estate (UNSAFE/SAFE/INDETERMINATE agents) |
| `migrate` | Alembic DB migrations |
| `lint` | Ruff, ESLint, constants parity |
| `test` | Unit tests (Python + Vitest) |
| `test-int` | API integration tests |
| `e2e` | Playwright browser tests (needs Docker) |
| `bench` | Full benchmark suite |
| `bench-smoke` | Fast golden + Table II smoke |
| `openapi` | Regenerate OpenAPI + frontend types |
| `verify` | `lint` + `test` + `test-int` + `bench-smoke` |
| `build` | Production builds |

Run `make help` for the full list.

## Paper Fidelity (Honest Summary)

CIRDA implements the **core architectural claims** of the paper:

- Temporal evidence graph with channel-specific decay half-lives
- Multi-channel evidence fusion and entity resolution
- Coverage estimation with suppression detection
- Tri-state gate with calibrated thresholds (θ_c, θ_p, C_min)
- Blast-radius and reachability analysis for retirement decisions
- **Zero false-SAFE at 30/45/60% telemetry loss** (structural gate property, tested)

**Benchmark Table II:** the harness runs a real simulation (no golden-value overlay).
CIRDA `false_safe=0` at high loss and several metric cells land within tolerance;
remaining cells are tracked as explicit `xfail` gaps in
[`packages/cirda-bench/CALIBRATION.md`](packages/cirda-bench/CALIBRATION.md).

**Roadmap hooks (flagged off by default):** probe planner execution/ΔC (coverage-gap probes are wired when `CIRDA_PROBE_PLANNING_ENABLED=true`), necessity models, multi-tenant aggregation.

See [docs/paper/fidelity-matrix.md](docs/paper/fidelity-matrix.md) for claim → code → test mapping.

## Known Limitations

1. **Absence of evidence ≠ evidence of absence.** Low coverage yields INDETERMINATE, not SAFE.
2. **Observability bias.** Suppressed telemetry channels reduce coverage and can block decisions.
3. **Identity ambiguity.** Alias collisions may merge or split entities incorrectly until resolved.
4. **Decay staleness.** Old edges remain as "possible" with decayed confidence — they do not auto-delete.
5. **Dev auth mode.** `CIRDA_AUTH_MODE=dev` bypasses real authentication — never use in production.

Every decision report includes a limitations footer (configurable via `CIRDA_DECISION_LIMITATIONS_FOOTER`).

## Demo Estate Scenarios

`make seed` creates:

| Agent | Expected Verdict | Scenario |
|-------|------------------|----------|
| `invoice-reconciler-agent` | UNSAFE | Critical downstream deps, high coverage |
| `legacy-csv-export-agent` | SAFE | Isolated, no critical reachability |
| `vendor-risk-agent` | INDETERMINATE | Ambiguous identity, insufficient coverage |

Plus: mediated dependency chain, decaying edge, and telemetry suppression on the messaging channel.

## Documentation

- [docs/README.md](docs/README.md) — documentation index
- [docs/architecture/00-overview.md](docs/architecture/00-overview.md) — system overview
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) — contribution guide
- [docs/api/openapi.md](docs/api/openapi.md) — API reference

## License

Apache-2.0 — see [LICENSE](LICENSE).
