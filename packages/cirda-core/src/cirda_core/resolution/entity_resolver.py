"""Entity resolver."""

from __future__ import annotations

from cirda_core.domain.entity import Entity
from cirda_core.resolution.alias_index import AliasIndex
from cirda_core.resolution.strategies import ExactMatchStrategy, FuzzyMatchStrategy, ResolutionMatch


class EntityResolver:
    """Resolve external identifiers to canonical entities."""

    def __init__(
        self,
        index: AliasIndex | None = None,
        fuzzy_threshold: float = 0.85,
    ) -> None:
        self._index = index or AliasIndex()
        self._strategies = [ExactMatchStrategy(), FuzzyMatchStrategy(fuzzy_threshold)]

    @property
    def index(self) -> AliasIndex:
        return self._index

    def register(self, entity: Entity) -> None:
        self._index.add(entity)

    def resolve(self, key: str) -> ResolutionMatch | None:
        for strategy in self._strategies:
            match = strategy.resolve(key, self._index)
            if match is not None:
                return match
        return None

    def resolve_or_passthrough(self, key: str) -> str:
        match = self.resolve(key)
        return match.entity_id if match else key
