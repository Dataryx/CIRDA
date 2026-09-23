# CIRDA Benchmark Calibration Notes

This package runs a **real** simulation against `cirda_core`. There is **no**
metric overlay that copies Golden Table II into results.

## What already matches the paper

| Requirement | Status |
|-------------|--------|
| CIRDA `false_safe == 0.000` at m ∈ {0.30, 0.45, 0.60} | **Exact** (structural: C=1−m < C_min ⇒ SAFE impossible; UNSAFE when critical in G_p) |
| CIRDA edge F1 tracks `direct_union` (confirmed ≈ direct evidence) | Approximately (both ~0.96/0.92/0.83 at 30/45/60%) |
| Generator shape: 145 nodes; edges ~N(593.44, 17.29) in [551, 639] | Pass |
| Table III node/edge counts exact; sub-quadratic build | Pass |
| Determinism INV-011 | Pass |
| Methods call real `cirda_core` fusion/gate | Pass |

## Loss model

- Primary direct channel is always emitted with `n_k` in the confirmation band.
- Visibility compounds only at loss time: all-or-nothing keep with
  `P(keep) = (1 − m) × visibility[channel]`.
- Secondary direct channels + universal trace provide redundant recovery so
  `direct_union` edge F1 stays near the published band under loss.
- Weak noise is injected without oracle filtering; it can enter `G_p` when
  `S ≥ θ_p`.

## Remaining Table II gaps

See `KNOWN_GAPS` in `tests/test_reproduces_table_ii.py` and
`scripts/compare_table_ii.py`. Typical residuals:

- **trace_only** edge F1 stays low; blast metrics trade off against phantoms.
- **Union / CIRDA** at m=0.30: edge F1 ~1–3 pp high; CIRDA blast recall slightly high.
- **Blast precision** often 1.000 vs golden ~0.94–0.97 (graphs slightly too clean after noise reduction).
- **CIRDA decision_coverage** at m=0.30/0.60 still a few pp off (±0.015 band).

These are simulator-tuning limits, not fabricated passes. Further work should
adjust fan-out, redundancy, and weak-noise topology — never paste golden values
into aggregates.

## Commands

```bash
uv run python packages/cirda-bench/scripts/compare_table_ii.py
uv run pytest packages/cirda-bench/tests -q
uv run cirda-bench run --smoke
```
