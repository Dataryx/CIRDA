# Calibration Guide

CIRDA uses three primary calibration parameters aligned with the paper:

| Parameter | Env Var | Default | Meaning |
|-----------|---------|---------|---------|
| θ_c | `CIRDA_THETA_C` | 0.62 | Confirmed edge threshold |
| θ_p | `CIRDA_THETA_P` | 0.28 | Possible edge floor |
| C_min | `CIRDA_C_MIN` | 0.85 | Minimum coverage for decisive verdict |

**Constraint:** `CIRDA_THETA_P` must be strictly less than `CIRDA_THETA_C`.

## When to Tune

- Too many INDETERMINATE → improve telemetry first; do not lower C_min without review
- Too many possible edges promoted → raise θ_c
- Missing weak dependencies → lower θ_p cautiously ( increases possible-layer noise)

## Procedure

1. Export benchmark baseline:
   ```bash
   make bench-smoke
   ```

2. Adjust calibration profile via API:
   ```bash
   curl -X PUT http://localhost:8000/api/v1/calibration \
     -H "Authorization: Bearer dev" \
     -H "X-CIRDA-Role: admin" \
     -H "Content-Type: application/json" \
     -d '{"theta_c": 0.62, "theta_p": 0.28, "c_min": 0.85}'
   ```

3. Re-run benchmarks:
   ```bash
   make bench
   ```

4. Verify constants parity:
   ```bash
   python scripts/check_constants_parity.py
   ```

## Validation Tests

| Test | File |
|------|------|
| Zero false-SAFE at 30/45/60% loss | `test_zero_false_safe_at_30_45_60_loss.py` |
| Table II shape reproduction | `test_reproduces_table_ii.py` |
| Determinism | `test_determinism.py` |

Do not merge calibration changes that regress golden benchmarks.

## Production

Store calibration in DB via calibration API; env vars serve as bootstrap defaults only.
