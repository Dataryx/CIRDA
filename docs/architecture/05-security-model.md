# Security Model

## Authentication Modes

| Mode | Config | Behavior |
|------|--------|----------|
| dev | `CIRDA_AUTH_MODE=dev` | Bearer `dev` or `X-API-Key: dev` — **local only** |
| jwt | `CIRDA_AUTH_MODE=jwt` | HS256 JWT with roles claim |
| api_key | `CIRDA_AUTH_MODE=api_key` | `X-API-Key` header |

## RBAC Roles

| Role | Capabilities |
|------|--------------|
| viewer | Read graph, entities, decisions, coverage |
| analyst | Ingest, create entities, analysis |
| approver | Evaluate and rerun decisions |
| admin | Admin jobs (decay, snapshot, recalibration) |

Dev mode accepts `X-CIRDA-Role` header to simulate roles.

## Rate Limiting

`CIRDA_RATE_LIMIT_RPM` (default 600) applies per principal on API routes.

## Data Protection

- Payload hashing (`payload_hash`) for dedup without storing raw secrets
- Redaction hooks in normalizer for PII patterns
- Audit log for mutating operations (`entity.upsert`, `ingest.event`, `decision.evaluate`)

## Network Boundaries (Kubernetes)

Helm chart includes `NetworkPolicy` restricting:

- Ingress from ingress controller only (ports 8000, 80)
- Egress to Postgres, Redis, Kafka, OTel, DNS

## Production Checklist

- [ ] `CIRDA_AUTH_MODE=jwt` with rotated secret
- [ ] TLS on Ingress
- [ ] Restrict CORS origins
- [ ] Disable dev auth endpoints
- [ ] Enable audit log export
- [ ] Review [SECURITY.md](../../SECURITY.md)

See [diagrams/security-boundaries.mmd](diagrams/security-boundaries.mmd).
