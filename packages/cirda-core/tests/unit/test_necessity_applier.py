"""Necessity auto-mutate selection tests."""

from __future__ import annotations

from cirda_core.domain.enums import Necessity
from cirda_core.graph.necessity_applier import select_auto_mutations
from cirda_core.graph.necessity_suggester import NecessityHint


def test_auto_mutate_selects_required_above_threshold() -> None:
    hints = [
        NecessityHint(
            edge_id="a->b:calls",
            source_id="a",
            target_id="b",
            current_necessity="unknown",
            suggested_necessity="required",
            confidence=0.92,
            rationale="cut",
        ),
        NecessityHint(
            edge_id="a->c:calls",
            source_id="a",
            target_id="c",
            current_necessity="unknown",
            suggested_necessity="optional",
            confidence=0.95,
            rationale="optional",
        ),
    ]
    selected = select_auto_mutations(hints, min_confidence=0.85)
    assert len(selected) == 1
    assert selected[0].to_necessity == Necessity.REQUIRED.value


def test_auto_mutate_respects_allow_list() -> None:
    hints = [
        NecessityHint(
            edge_id="a->c:calls",
            source_id="a",
            target_id="c",
            current_necessity="unknown",
            suggested_necessity="optional",
            confidence=0.95,
            rationale="optional",
        ),
    ]
    selected = select_auto_mutations(
        hints,
        min_confidence=0.85,
        allowed_labels=frozenset({"optional"}),
    )
    assert len(selected) == 1
    assert selected[0].to_necessity == "optional"
