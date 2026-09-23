"""Change type analysis."""

from __future__ import annotations

from cirda_core.domain.enums import ChangeType, EntityType


_CHANGE_ENTITY_TYPES: dict[ChangeType, frozenset[EntityType]] = {
    ChangeType.RETIREMENT: frozenset(
        {EntityType.AGENT, EntityType.SERVICE, EntityType.TOOL}
    ),
    ChangeType.MODEL_UPGRADE: frozenset({EntityType.MODEL}),
    ChangeType.CREDENTIAL_ROTATION: frozenset({EntityType.CREDENTIAL}),
    ChangeType.TOOL_SCHEMA_CHANGE: frozenset({EntityType.TOOL}),
    ChangeType.DATA_CONTRACT_MIGRATION: frozenset({EntityType.DATA, EntityType.QUEUE}),
}


def applicable_change_types(entity_type: EntityType) -> list[ChangeType]:
    """Return change types applicable to an entity type."""
    return [
        change_type
        for change_type, types in _CHANGE_ENTITY_TYPES.items()
        if entity_type in types
    ]


def requires_blast_recheck(change_type: ChangeType) -> bool:
    """Return True if change type requires blast radius re-evaluation."""
    return change_type in {
        ChangeType.RETIREMENT,
        ChangeType.CREDENTIAL_ROTATION,
        ChangeType.DATA_CONTRACT_MIGRATION,
    }
