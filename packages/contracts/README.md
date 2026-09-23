# CIRDA Contracts

Language-neutral API and payload contracts for CIRDA integrators.

## Contents

| Path | Description |
|------|-------------|
| `openapi/cirda-v1.yaml` | OpenAPI 3.1 REST spec (canonical) |
| `json-schema/canonical-event.schema.json` | Normalized evidence event |
| `json-schema/decision-report.schema.json` | Decision evaluation output |
| `json-schema/coverage-estimate.schema.json` | Coverage estimation output |
| `examples/events/` | Sample ingest payloads |
| `examples/decisions/` | Sample decision reports |

## Regeneration

```bash
make openapi
```

This runs `scripts/generate_openapi.py` (from FastAPI) and optionally `scripts/generate_frontend_types.sh`.

## Validation

Validate examples against JSON Schema:

```bash
# requires check-jsonschema or similar
check-jsonschema --schemafile json-schema/canonical-event.schema.json examples/events/trace-delegates.json
```

## Versioning

API version `v1` — breaking changes require a new major path (`/api/v2`) and spec file (`cirda-v2.yaml`).
