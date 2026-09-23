# Confidence Model

Edge confidence comes from **multi-channel evidence fusion** in `cirda_core.inference.fusion`.

## Per-channel strength

For channel k with observation count n_k and age Δt:

```
s_k = r_k · (1 − exp(−n_k / τ_k)) · exp(−Δt / h_k)
```

- r_k — channel reliability (from `CHANNEL_PROFILES`)
- τ_k — saturation parameter
- h_k — half-life in seconds

## Fusion

Combined strength across channels:

```
S = 1 − Π_k (1 − s_k)
```

## Layer classification

`classify_layer(S, has_direct_evidence)` assigns:

- **None** — S < θ_p
- **Possible** — θ_p ≤ S < θ_c, or S ≥ θ_c without direct evidence when policy requires it
- **Confirmed** — S ≥ θ_c with direct evidence (when `confirmed_requires_direct_evidence`)

Weak channels alone cannot confirm an edge (`can_confirm_layer`).

## Benchmark note

The benchmark harness uses the same fusion and thresholds; it does not substitute
golden metrics for computed ones. See `packages/cirda-bench/CALIBRATION.md`.
