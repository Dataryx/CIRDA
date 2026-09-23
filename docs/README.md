# CIRDA Documentation

Welcome to the CIRDA documentation index.

## Architecture

| Document | Description |
|----------|-------------|
| [00-overview](architecture/00-overview.md) | System context and goals |
| [01-pipeline](architecture/01-pipeline.md) | Ingest, fusion, gate pipeline |
| [02-data-model](architecture/02-data-model.md) | Entities, edges, layers |
| [03-confidence-model](architecture/03-confidence-model.md) | Fusion, θ_c / θ_p |
| [04-coverage-estimation](architecture/04-coverage-estimation.md) | Coverage C and gate interaction |
| [05-security-model](architecture/05-security-model.md) | Auth, RBAC, network boundaries |

Diagrams live in [architecture/diagrams/](architecture/diagrams/).

## ADRs

| ADR | Title |
|-----|-------|
| [0001](adr/0001-possible-graph-for-safety-traversal.md) | G_p for safety traversal |
| [0002](adr/0002-postgres-as-graph-system-of-record.md) | Postgres system of record |
| [0003](adr/0003-at-least-once-idempotent-ingestion.md) | At-least-once idempotent ingest |
| [0004](adr/0004-tri-state-gate-api-shape.md) | Tri-state gate API shape |
| [0005](adr/0005-cytoscape-for-topology-rendering.md) | Cytoscape topology rendering |

## Operations

| Runbook | Purpose |
|---------|---------|
| [runbook-retirement](operations/runbook-retirement.md) | Agent retirement workflow |
| [runbook-coverage-gap](operations/runbook-coverage-gap.md) | Coverage below C_min |
| [calibration-guide](operations/calibration-guide.md) | θ_c, θ_p tuning |
| [incident-telemetry-suppression](operations/incident-telemetry-suppression.md) | Suppressed channel response |

## Paper & API

- [Paper fidelity matrix](paper/fidelity-matrix.md)
- [API reference](api/openapi.md)
- [Contributing](../docs/CONTRIBUTING.md)
