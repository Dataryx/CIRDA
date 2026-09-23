# ADR 0004: Tri-State Gate API Shape

## Status

Accepted

## Context

Binary safe/unsafe decisions fail when observability is incomplete. The paper
defines UNSAFE, SAFE, and INDETERMINATE outcomes with distinct operator workflows.

## Decision

Expose a **tri-state gate** via `cirda_core.decision.gate`:

1. **UNSAFE** — critical descendant reachable in G_p (coverage ignored)
2. **SAFE** — no critical descendant **and** C ≥ C_min
3. **INDETERMINATE** — no critical descendant **and** C < C_min (or truncated / hard block)

API returns `DecisionReport` with `verdict`, `coverage`, `reason_codes`, runbook,
and mandatory limitations footer.

## Consequences

- **Positive:** Prevents false confidence; matches benchmark Table II semantics
- **Negative:** Operators handle INDETERMINATE (probes, telemetry fixes)
- **Benchmark:** At m ≥ 0.30, C = 1−m < C_min so decision coverage ≈ UNSAFE rate; false-safe = 0

See [04-coverage-estimation.md](../architecture/04-coverage-estimation.md).
