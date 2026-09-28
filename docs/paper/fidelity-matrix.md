# Paper Fidelity Matrix

Mapping of CIRDA paper claims to code paths and test identifiers. PDF not included — this matrix is the engineering source of truth for 0.1.0.

| Paper Claim | Code Path | Test ID |
|-------------|-----------|---------|
| Temporal evidence graph with channel decay | `cirda_core.graph.decay`, `HALF_LIFE` | `test_determinism.py` |
| Multi-channel evidence fusion | `cirda_core.inference.fusion` | `test_generator_shape.py` |
| Entity resolution / alias handling | `ambiguity.py`; API + worker ingest alias resolve; gate `ambiguous_identity` | `test_ambiguous_identity.py`, `test_ingest_alias_resolve.py`, `test_pipeline_stages.py` |
| θ_c / θ_p layer classification | `cirda_core.graph.layers`, `constants.py` | `check_constants_parity.py` |
| Static DECLARED can confirm | `has_confirming_evidence` (DIRECT ∪ DECLARED) | `test_static_declared_can_confirm.py` |
| Coverage estimation C | `cirda_core.coverage.estimator` | `apps/api/tests/integration/test_coverage.py` |
| Suppression detection | `cirda_core.coverage.suppression` | `incident-telemetry-suppression.md` scenario |
| Tri-state gate (UNSAFE/SAFE/INDETERMINATE) | `cirda_core.decision.gate` | `test_zero_false_safe_at_30_45_60_loss.py` |
| INV-002 ingest lag blocks SAFE | `CoverageService` → `CoverageInputs.ingest_lag_seconds` → gate | `test_INV_002_no_safe_when_ingest_lag_exceeds_policy.py`, `test_decision_flow.py` |
| Blast radius analysis | `cirda_core.analysis.blast_radius` | `apps/api/tests/integration/test_analysis.py` |
| Critical path enumeration | `critical_paths.py`; decision `paths`; `GET /analysis/paths` | `test_critical_paths.py`, `test_decision_flow.py` |
| Zero false-SAFE under observability loss | `cirda_bench` harness | `test_zero_false_safe_at_30_45_60_loss.py` |
| Table II benchmark shape | `cirda_bench.generator` (incl. spurious direct evidence) | `test_reproduces_table_ii.py` (40/60 in tolerance, 20 structural xfails) |
| Fused support reliability | `cirda_bench.metrics.reliability` (ECE / Brier vs simulator truth) | `test_reliability.py`; `scripts/support_reliability.py` |
| Scalability shape (graph size) | `cirda_bench.scalability` | `test_scalability_shape.py` |
| Decision explanation / runbook | `cirda_core.decision.explanation`, `runbook.py` | `apps/api/tests/unit/test_decision_service.py` |
| Runbook execution tracking | Seed on evaluate; `GET/PATCH …/runbook` | `test_runbook.py`, `test_runbook_execution.py` |
| Probe planning for INDETERMINATE | `cirda_core.decision.probe_planner`, wired in `decision_service.py` | `test_probe_planner.py`, `test_decision_flow.py` |
| Probe expected ΔC | `estimate_probe_delta_c` (restore suppressed channel → re-estimate C) | `test_probe_planner.py` |
| Probe apply (suppression lift) | `POST /decisions/probes/apply`; `CoverageService.restore_channels_for_probe` | `test_decision_flow.py` |
| Live collector probes | HTTP probe via `metadata.probe_url` when `CIRDA_PROBE_COLLECTOR_ENABLED` | `probe_collectors.py` |
| Necessity auto-mutate | `necessity_applier.py`; `POST /edges/necessity-auto-mutate` (flag-gated) | `test_necessity_applier.py`, `test_necessity_auto_mutate.py` |
| Multi-tenant isolation | Composite PKs + tenant-scoped edges/evidence/decisions/coverage; ADR 0006 Phase 2 (migrations 0007–0008) | `test_multi_tenant.py`, `test_multi_tenant_postgres.py` (needs `CIRDA_TEST_DATABASE_URL`) |
| Analysis UI | Web `/analysis` over blast/reachability/paths APIs | `test_analysis.py` |
| Necessity-aware critical traversal | `reachability.py` load-bearing filter; gate/blast | `test_necessity_load_bearing.py` |
| Operator necessity annotation | `PATCH /api/v1/edges/{edge_id}`; preserved on re-ingest | `test_edge_necessity.py` |
| Necessity suggestions (suggest-only) | `necessity_suggester.py`; `GET /edges/necessity-suggestions` | `test_necessity_suggester.py`, `test_necessity_suggestions.py` |
| Calibrated support S as probability | N/A — documented product limitation (support ≠ causation) | README limitations section |
| Distributed graph partition | Logical tenants with composite PKs; not physical shard | ADR 0006, `test_multi_tenant.py` |

## Partial / Simplified

| Area | Gap | Mitigation |
|------|-----|------------|
| Probe planning | Apply lifts suppression; optional live HTTP collector probe when flagged | `CIRDA_PROBE_*` flags; requires `metadata.probe_url` for collector mode |
| Necessity models | Suggest-only by default; optional auto-mutate of high-confidence `required` | `CIRDA_NECESSITY_AUTO_MUTATE_ENABLED` (off); UNKNOWN ≡ load-bearing |
| Multi-tenant | Logical isolation: composite PKs + scoped edges/evidence/decisions/coverage | `CIRDA_MULTI_TENANT_ENABLED`; ADR 0006 Phase 2 |
| Weak signal weights | Heuristic `r_k`/`τ_k`, measured not fitted: S is conservative on simulator truth (real rate ≥ S for S ≥ 0.2) | Reliability report in `CALIBRATION.md`; `calibration-guide.md` |
| Causal inference | Support ≠ causation — by design, not a gap | Limitations footer on every report |
| Table II residuals | 20 structural baseline gaps (trace_only shape, union false_safe / recall overshoot); all CIRDA cells pass | `KNOWN_GAPS` / `CALIBRATION.md`; CIRDA false_safe=0 exact |

## Verification Command

```bash
make verify   # lint + unit + integration + bench-smoke
make bench    # full benchmark suite
```
