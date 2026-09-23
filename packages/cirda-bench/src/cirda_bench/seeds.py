"""Deterministic seed derivation (INV-011)."""

from __future__ import annotations

import hashlib
import random
from typing import Any

BASE_SEED = 20260921


def seed(condition: str | int, replicate: int, purpose: str) -> int:
    """Derive a deterministic 64-bit seed from benchmark inputs."""
    payload = f"{BASE_SEED}:{condition}:{replicate}:{purpose}"
    digest = hashlib.blake2b(payload.encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def make_rng(condition: str | int, replicate: int, purpose: str) -> random.Random:
    """Return a seeded ``random.Random`` instance."""
    return random.Random(seed(condition, replicate, purpose))


def numpy_seed(condition: str | int, replicate: int, purpose: str) -> int:
    """Return a seed suitable for ``random.Random`` / reproducible draws."""
    return seed(condition, replicate, purpose) % (2**32)


def seed_tag(*parts: Any) -> str:
    """Build a stable condition tag from heterogeneous parts."""
    return ":".join(str(part) for part in parts)
