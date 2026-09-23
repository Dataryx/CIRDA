"""Benchmark inference methods."""

from cirda_bench.methods.base import InferenceResult, Method
from cirda_bench.methods.cirda_method import CirdaMethod
from cirda_bench.methods.direct_union import DirectUnionMethod
from cirda_bench.methods.trace_only import TraceOnlyMethod
from cirda_bench.methods.weak_union import WeakUnionMethod

METHODS: dict[str, Method] = {
    "trace_only": TraceOnlyMethod(),
    "direct_union": DirectUnionMethod(),
    "weak_union": WeakUnionMethod(),
    "cirda": CirdaMethod(),
}

__all__ = [
    "METHODS",
    "CirdaMethod",
    "DirectUnionMethod",
    "InferenceResult",
    "Method",
    "TraceOnlyMethod",
    "WeakUnionMethod",
]
