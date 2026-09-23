# Contributing to CIRDA

Thank you for contributing! This guide covers local setup, conventions, and PR expectations.

## Getting Started

```bash
make bootstrap
make dev
make verify
```

See [README.md](../README.md) for Windows/Git Bash notes.

## Development Workflow

1. Create a feature branch from `main`
2. Make focused changes — prefer small PRs
3. Run `make verify` before pushing
4. Update contracts if API changes: `make openapi`
5. Update [fidelity-matrix.md](paper/fidelity-matrix.md) if inference/decision logic changes

## Code Conventions

### Python

- Python 3.12+, type hints required on public APIs
- `cirda-core` must stay I/O-free (ports pattern)
- Ruff for lint/format (`uv run ruff check`, `uv run ruff format`)
- pytest with `asyncio_mode = auto` for API tests

### TypeScript

- ESLint + Prettier in `apps/web`
- React Query for server state; Zustand for UI state
- Co-locate feature code under `src/features/`

### Commits

Use imperative mood: "Add coverage snapshot endpoint", "Fix decay half-life for IAM"

## Testing Expectations

| Change Type | Required Tests |
|-------------|----------------|
| cirda-core logic | Unit tests in `packages/cirda-core/tests` |
| API endpoint | Unit + integration in `apps/api/tests` |
| UI component | Vitest in `apps/web/src` |
| Benchmark- affecting | `make bench-smoke` minimum |

## ADRs

Significant architectural decisions require a new ADR in `docs/adr/` using the numbered format.

## Security

- Never commit `.env`, secrets, or credentials
- Report vulnerabilities per [SECURITY.md](../SECURITY.md)

## Code Review

All PRs need:

- Green CI (`ci-backend`, `ci-frontend`)
- Updated CHANGELOG for user-facing changes
- Paper fidelity note in PR template when touching engine logic
