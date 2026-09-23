# Coverage Estimation

Coverage C measures observability of the blast-radius scope for a proposed change.

## Production estimator

`cirda_core.coverage.estimator.estimate_coverage` computes:

```
C = |effective_observed| / |total_entities|
```

with channel suppression applied (`coverage.suppression`).

## Benchmark mode

For Table II isolation, the benchmark uses:

```
C = 1 − m
```

where m is the configured telemetry loss level. This isolates abstention behavior
from entity-discovery variance while still driving the real tri-state gate.

## Interaction with the gate

| Verdict | Coverage role |
|---------|-----------------|
| **UNSAFE** | Ignored — critical reachability in G_p is sufficient |
| **SAFE** | Requires C ≥ C_min (0.85) |
| **INDETERMINATE** | Returned when no critical descendant and C < C_min |

Therefore at m = 0.30 (C = 0.70), SAFE is impossible. **Decision coverage** at high
loss equals the fraction of targets classified **UNSAFE**, not SAFE. CIRDA
false-safe is structurally zero because the gate never returns SAFE when C < C_min.

At m ∈ {0.00, 0.15}, C ≥ 0.85 and small false-safe rates (~0.23%, ~0.75%) are
observable because SAFE is reachable when no critical descendants exist.
