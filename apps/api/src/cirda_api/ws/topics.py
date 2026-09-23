"""WebSocket topic constants."""

EVIDENCE = "evidence"
GRAPH = "graph"
DECISION = "decision"
COVERAGE = "coverage"
BENCHMARK = "benchmark"
AUDIT = "audit"

ALL_TOPICS = frozenset({EVIDENCE, GRAPH, DECISION, COVERAGE, BENCHMARK, AUDIT})
