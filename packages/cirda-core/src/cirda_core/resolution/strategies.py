"""Entity resolution strategies."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_core.domain.entity import Entity
from cirda_core.resolution.similarity import similarity


@dataclass(frozen=True, slots=True)
class ResolutionMatch:
    """A candidate entity resolution match."""

    entity_id: str
    score: float
    strategy: str


class ExactMatchStrategy:
    """Exact key match via alias index."""

    name = "exact"

    def resolve(self, key: str, index: "AliasIndex") -> ResolutionMatch | None:
        from cirda_core.resolution.alias_index import AliasIndex

        entity_id = index.lookup(key)
        if entity_id is None:
            return None
        return ResolutionMatch(entity_id=entity_id, score=1.0, strategy=self.name)


class FuzzyMatchStrategy:
    """Fuzzy similarity match above threshold."""

    name = "fuzzy"

    def __init__(self, threshold: float = 0.85) -> None:
        self.threshold = threshold

    def resolve(self, key: str, index: "AliasIndex") -> ResolutionMatch | None:
        best: ResolutionMatch | None = None
        for entity in index.all_entities():
            candidates = [entity.entity_id, entity.name, *entity.aliases]
            for candidate in candidates:
                score = similarity(key, candidate)
                if score >= self.threshold and (best is None or score > best.score):
                    best = ResolutionMatch(entity_id=entity.entity_id, score=score, strategy=self.name)
        return best
