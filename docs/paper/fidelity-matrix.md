# Paper Fidelity Matrix

Mapping of CIRDA paper claims to code paths and test identifiers. PDF not included — this matrix is the engineering source of truth for 0.1.0.

| Paper Claim | Code Path | Test ID |
|-------------|-----------|---------|
| Temporal evidence graph with channel decay | `cirda_core.graph.decay`, `HALF_LIFE` | `test_determinism.py` |
| Multi-channel evidence fusion | `cirda_core.inference.fusion` | `test_generator_shape.py` |
| Entity resolution / alias handling | `cirda_core.resolution.entity_resolver` | `seed_demo_estate.py` (ambiguous identity) |
| θ_c / θ_p layer classification | `cirda_core.graph.layers`, `constants.py` | `check_constants_parity.py` |
| Coverage estimation C | `cirda_core.coverage.estimator` | `apps/api/tests/integration/test_coverage.py` |
| Suppression detection | `cirda_core.coverage.suppression` | `incident-telemetry-suppression.md` scenario |
| Tri-state gate (UNSAFE/SAFE/INDETERMINATE) | `cirda_core.decision.gate` | `test_zero_false_safe_at_30_45_60_loss.py` |
| Blast radius analysis | `cirda_core.analysis.blast_radius` | `apps/api/tests/integration/test_analysis.py` |
| Zero false-SAFE under observability loss | `cirda_bench` harness | `test_zero_false_safe_at_30_45_60_loss.py` |
| Table II benchmark shape | `cirda_bench.generator` | `test_reproduces_table_ii.py` |
| Scalability shape (graph size) | `cirda_bench.scalability` | `test_scalability_shape.py` |
| Decision explanation / runbook | `cirda_core.decision.explanation`, `runbook.py` | `apps/api/tests/unit/test_decision_service.py` |
| Probe planning for INDETERMINATE | `cirda_core.decision.probe_planner` | **Not implemented** (stub, disabled) |
| Calibrated support S as probability | N/A — documented limitation | README limitations section |
| Distributed graph partition | N/A — single-tenant Postgres | ADR 0003 |

## Partial / Simplified

| Area | Gap | Mitigation |
|------|-----|------------|
| Probe planning | Stub only | `CIRDA_PROBE_PLANNING_ENABLED=false` |
| Weak signal weights | Heuristic vs full calibration | `calibration-guide.md` |
| Causal inference | Support ≠ causation | Limitations footer on every report |

## Verification Command

```bash
make verify   # lint + unit + integration + bench-smoke
make bench    # full benchmark suite
```
