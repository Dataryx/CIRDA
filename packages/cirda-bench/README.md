# cirda-bench

Benchmark harness for evaluating CIRDA dependency-analysis methods against synthetic ecosystems.

## Commands

```bash
cirda-bench bench              # full Table II (30 ecosystems, real methods)
cirda-bench bench-smoke        # smoke (3 ecosystems)
cirda-bench run [--smoke]      # alias for bench / bench-smoke
cirda-bench scale
cirda-bench report
python scripts/compare_table_ii.py
```

See `CALIBRATION.md` for tuning knobs and known simulation gaps vs golden Table II.

## Protocol

30 ecosystems × 5 loss levels × 60 targets × 4 methods (36,000 evaluations).

Golden reference tables live in `tests/golden/`.
