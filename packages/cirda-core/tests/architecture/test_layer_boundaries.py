"""Architecture boundary tests for INV-001 and INV-005."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from cirda_core.analysis.blast_radius import compute_blast_radius
from cirda_core.decision.gate import evaluate_gate
from cirda_core.inference.direction import translate_to_dependency_edge


SRC = Path(__file__).resolve().parents[2] / "src" / "cirda_core"


def test_INV_005_only_direction_constructs_edges() -> None:
    """DependencyEdge construction for inference should go through direction module."""
    direction_path = SRC / "inference" / "direction.py"
    source = direction_path.read_text(encoding="utf-8")
    assert "DependencyEdge(" in source

    candidate_path = SRC / "inference" / "candidate_generator.py"
    candidate_source = candidate_path.read_text(encoding="utf-8")
    assert "translate_to_dependency_edge" in candidate_source
    assert "DependencyEdge(" not in candidate_source.replace("from cirda_core.domain.edge import DependencyEdge", "")


def test_INV_001_gate_and_blast_use_possible_layer() -> None:
    gate_source = inspect.getsource(evaluate_gate)
    blast_source = inspect.getsource(compute_blast_radius)
    assert "possible_graph" in gate_source
    assert "G_p" in gate_source or "possible" in gate_source.lower()
    assert "GraphLayer.POSSIBLE" in blast_source or "possible" in blast_source.lower()


def test_no_datetime_now_in_domain() -> None:
    domain_dir = SRC / "domain"
    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "now":
                    if isinstance(func.value, ast.Name) and func.value.id == "datetime":
                        pytest.fail(f"datetime.now() found in {py_file}")
