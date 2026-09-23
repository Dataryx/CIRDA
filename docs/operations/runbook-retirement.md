# Runbook: Agent Retirement

## Purpose

Safely retire an AI agent from the estate using CIRDA decision reports and staged runbooks.

## Prerequisites

- CIRDA API reachable with `approver` role
- Demo or production estate ingested with current telemetry
- Coverage snapshot within last 24h (or run `POST /api/v1/admin/coverage`)

## Procedure

### 1. Evaluate Decision

```bash
curl -X POST http://localhost:8000/api/v1/decisions/evaluate \
  -H "Authorization: Bearer dev" \
  -H "X-CIRDA-Role: approver" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "legacy-csv-export-agent", "change_type": "retirement"}'
```

### 2. Interpret Verdict

| Verdict | Action |
|---------|--------|
| SAFE | Proceed to staged runbook (step 3) |
| UNSAFE | Stop — remediate dependents listed in `rationale.blast_radius` |
| INDETERMINATE | Follow [runbook-coverage-gap.md](runbook-coverage-gap.md) |

### 3. Execute Runbook Stages

Follow `suggested_runbook` in order:

1. **report_and_remediate** — notify owning team
2. **disable_new_work** — drain queues, disable triggers
3. **observe_downstream** — monitor for 24–72h
4. **revoke_credentials** — IAM rotation
5. **delete_identity** — remove agent registration

### 4. Re-evaluate

```bash
curl -X POST http://localhost:8000/api/v1/decisions/evaluate/{decision_id}/rerun \
  -H "Authorization: Bearer dev" \
  -H "X-CIRDA-Role: approver"
```

### 5. Audit

Verify audit log entry: `GET /api/v1/audit?action=decision.evaluate`

## Demo Agents

| Entity | Expected Verdict |
|--------|------------------|
| `invoice-reconciler-agent` | UNSAFE |
| `legacy-csv-export-agent` | SAFE |
| `vendor-risk-agent` | INDETERMINATE |

## Escalation

If UNSAFE with disputed blast radius, export graph snapshot and open incident with graph `as_of` timestamp.
