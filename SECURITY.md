# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in CIRDA, please report it responsibly.

1. **Do not** open a public GitHub issue for security-sensitive findings.
2. Email the maintainers with:
   - A description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested remediation (if any)
3. Allow up to **5 business days** for an initial response.

We will acknowledge receipt, investigate, and coordinate disclosure. Critical issues affecting authentication, authorization, or data exfiltration via ingest paths receive highest priority.

## Scope

In scope:

- `apps/api` — REST/WebSocket control plane, RBAC, rate limiting
- `apps/ingest-worker` — evidence ingestion pipelines
- `packages/cirda-core` — inference and decision engine
- Deployment manifests under `deploy/`

Out of scope:

- Third-party dependencies (report upstream; we will track CVEs via Dependabot)
- Denial-of-service against dev-mode defaults without production hardening

## Secure Deployment Guidance

- Set `CIRDA_AUTH_MODE=jwt` or `api_key` in production; never use `dev` auth.
- Rotate `CIRDA_JWT_SECRET` and database credentials regularly.
- Restrict network access to PostgreSQL, Redis, and Kafka via NetworkPolicies (see Helm templates).
- Enable TLS on Ingress and restrict CORS origins.
- Treat ingest endpoints as **trusted writer** surfaces — authenticate all producers.

## Security Updates

Security fixes are released as patch versions and documented in [CHANGELOG.md](CHANGELOG.md).
