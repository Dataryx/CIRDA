"""Verify cirda_method uses real cirda_core primitives."""

from __future__ import annotations

import inspect

from cirda_bench.methods.cirda_method import CirdaMethod
from cirda_core.decision.gate import evaluate_gate_from_layers
from cirda_core.inference.fusion import fuse_channels


def test_cirda_method_imports_core_gate_and_fusion() -> None:
    source = inspect.getsource(CirdaMethod.infer)
    assert "evaluate_gate_from_layers" in source
    assert "fuse_channels" in source
    assert "benchmark_coverage" in source


def test_core_symbols_are_real() -> None:
    assert fuse_channels.__module__.startswith("cirda_core")
    assert evaluate_gate_from_layers.__module__.startswith("cirda_core")
