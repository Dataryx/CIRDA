"""Entity resolution layer tests."""

from __future__ import annotations

from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import EntityType
from cirda_core.resolution.entity_resolver import EntityResolver


def test_exact_alias_resolution() -> None:
    resolver = EntityResolver()
    entity = Entity(
        entity_id="svc-payment",
        entity_type=EntityType.SERVICE,
        name="Payment Service",
        aliases=frozenset({"payments", "payment-svc"}),
    )
    resolver.register(entity)
    match = resolver.resolve("payment-svc")
    assert match is not None
    assert match.entity_id == "svc-payment"
    assert match.score == 1.0


def test_fuzzy_resolution() -> None:
    resolver = EntityResolver(fuzzy_threshold=0.8)
    entity = Entity(
        entity_id="agent-alpha",
        entity_type=EntityType.AGENT,
        name="Alpha Agent",
    )
    resolver.register(entity)
    match = resolver.resolve("alpha-agent")
    assert match is not None
    assert match.entity_id == "agent-alpha"
    assert match.score >= 0.8


def test_passthrough_unknown() -> None:
    resolver = EntityResolver()
    assert resolver.resolve_or_passthrough("unknown-id") == "unknown-id"
