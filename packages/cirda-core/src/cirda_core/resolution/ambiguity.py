"""Identity ambiguity detection for retirement safety."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_core.domain.entity import Entity
from cirda_core.resolution.similarity import normalized_key


@dataclass(frozen=True, slots=True)
class IdentityAmbiguity:
    """Result of checking whether an entity has unresolved identity conflicts."""

    is_ambiguous: bool
    conflicting_ids: frozenset[str]
    detail: str = ""


def detect_identity_ambiguity(
    *,
    entity_id: str,
    entities: list[Entity],
) -> IdentityAmbiguity:
    """
    Detect unresolved identity for ``entity_id``.

    Ambiguous when:
    - Another registered entity ID matches one of this entity's aliases (split identity).
    - Another entity claims the same alias string (collision).
    - Another entity lists this entity's ID as an alias.
    """
    by_id = {e.entity_id: e for e in entities}
    target = by_id.get(entity_id)
    if target is None:
        return IdentityAmbiguity(is_ambiguous=False, conflicting_ids=frozenset())

    target_alias_keys = {normalized_key(a) for a in target.aliases}

    # Map normalized alias → owning entity ids.
    alias_owners: dict[str, set[str]] = {}
    for entity in entities:
        for alias in entity.aliases:
            key = normalized_key(alias)
            alias_owners.setdefault(key, set()).add(entity.entity_id)

    conflicts: set[str] = set()

    # Split identity: orphan node whose id equals a declared alias of the target.
    for other in entities:
        if other.entity_id == entity_id:
            continue
        other_id_key = normalized_key(other.entity_id)
        if other_id_key in target_alias_keys:
            conflicts.add(other.entity_id)

    # Collision: same alias claimed by multiple entities, involving the target.
    for key, owners in alias_owners.items():
        if entity_id in owners and len(owners) > 1:
            conflicts.update(owners - {entity_id})
        if key in target_alias_keys and any(o != entity_id for o in owners):
            conflicts.update(o for o in owners if o != entity_id)

    # Cross-claim: another entity lists this entity_id as an alias.
    for entity in entities:
        if entity.entity_id == entity_id:
            continue
        for alias in entity.aliases:
            if normalized_key(alias) == normalized_key(entity_id):
                conflicts.add(entity.entity_id)

    # Shared surface form: another entity's name/id collides with target aliases.
    for entity in entities:
        if entity.entity_id == entity_id:
            continue
        other_keys = {normalized_key(entity.entity_id), normalized_key(entity.name)}
        if other_keys & target_alias_keys:
            conflicts.add(entity.entity_id)

    if not conflicts:
        return IdentityAmbiguity(is_ambiguous=False, conflicting_ids=frozenset())

    conflict_list = ", ".join(sorted(conflicts))
    return IdentityAmbiguity(
        is_ambiguous=True,
        conflicting_ids=frozenset(conflicts),
        detail=(
            f"Entity {entity_id} has unresolved identity conflict with: {conflict_list}"
        ),
    )
