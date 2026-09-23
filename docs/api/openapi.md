# API Reference

CIRDA exposes a REST API at `/api/v1` plus WebSocket streaming and Prometheus metrics.

## Base URL

| Environment | URL |
|-------------|-----|
| Local dev | `http://localhost:8000` |
| Docker | `http://localhost:8000` |
| Production | `https://{host}/api/v1` via Ingress |

## Authentication

Dev mode (local only):

```http
Authorization: Bearer dev
X-CIRDA-Role: approver
```

Production: JWT bearer or `X-API-Key` per [security model](../architecture/05-security-model.md).

## OpenAPI Spec

Canonical spec: [`packages/contracts/openapi/cirda-v1.yaml`](../../packages/contracts/openapi/cirda-v1.yaml)

Regenerate:

```bash
make openapi
```

Interactive docs: `http://localhost:8000/docs` (when API running)

## Endpoint Summary

| Tag | Prefix | Key Operations |
|-----|--------|----------------|
| health | `/api/v1` | `GET /health`, `GET /health/ready` |
| ingest | `/api/v1/ingest` | `POST /events`, `POST /events/batch` |
| entities | `/api/v1/entities` | CRUD list/get/create |
| graph | `/api/v1/graph` | `GET /graph?layer=` |
| edges | `/api/v1/edges` | List, get, evidence |
| evidence | `/api/v1/evidence` | List, get by event_id |
| analysis | `/api/v1/analysis` | blast-radius, reachability, paths |
| decisions | `/api/v1/decisions` | evaluate, list, get, rerun |
| coverage | `/api/v1/coverage` | estimate, snapshots, channel-health |
| calibration | `/api/v1/calibration` | get/put profile |
| benchmarks | `/api/v1/benchmarks` | runs CRUD |
| audit | `/api/v1/audit` | audit log query |
| admin | `/api/v1/admin` | decay, coverage, snapshot jobs |
| stream | `/api/v1/stream` | WebSocket live updates |

## Metrics

`GET /metrics` — Prometheus exposition format (when `CIRDA_METRICS_ENABLED=true`)

## Contract Tests

```bash
uv run pytest apps/api/tests/contract -q
```

## JSON Schemas

Canonical payloads in `packages/contracts/json-schema/`:

- `canonical-event.schema.json`
- `decision-report.schema.json`
- `coverage-estimate.schema.json`

Example fixtures in `packages/contracts/examples/`.
