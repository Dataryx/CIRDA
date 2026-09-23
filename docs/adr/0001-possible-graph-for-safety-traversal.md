# ADR 0001: Possible Graph for Safety Traversal

## Status

Accepted

## Context

Retirement safety depends on **worst-case** dependency reachability: an operator
must not receive SAFE when an unobserved critical path might exist. Confirmed
edges alone under-estimate blast radius under telemetry loss.

## Decision

All safety traversal — blast radius and tri-state gate — uses **G_p (possible
layer) only** (INV-001). Confirmed edges are a subset of possible edges but never
the sole basis for reachability.

```python
# cirda_core.decision.gate.evaluate_gate
reach = critical_descendants(possible_graph, source_entity_id, ...)
if reach.reachable:
    return Verdict.UNSAFE  # coverage not consulted
```

## Consequences

- **Positive:** Aligns with paper; prevents optimistic SAFE under incomplete evidence
- **Negative:** Higher UNSAFE rate when G_p is dense; requires careful benchmark calibration
- **Testing:** `test_zero_false_safe_at_30_45_60_loss.py`; bench G_p must include confirmed edges
