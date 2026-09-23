"""Simple in-memory rate limiter."""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

from cirda_api.settings import Settings, get_settings


class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str, rpm: int) -> None:
        now = time.time()
        window_start = now - 60.0
        hits = [t for t in self._hits[key] if t >= window_start]
        if len(hits) >= rpm:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded")
        hits.append(now)
        self._hits[key] = hits


_limiter = RateLimiter()


async def rate_limit_middleware(request: Request) -> None:
    settings = get_settings()
    client = request.client.host if request.client else "unknown"
    _limiter.check(client, settings.rate_limit_rpm)
