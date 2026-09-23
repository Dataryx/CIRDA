"""Async database session factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cirda_api.db.base import Base
from cirda_api.settings import Settings, get_settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _normalize_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def init_db(settings: Settings | None = None) -> None:
    global _engine, _session_factory
    cfg = settings or get_settings()
    url = _normalize_url(cfg.effective_database_url)
    connect_args: dict[str, object] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    _engine = create_async_engine(url, echo=cfg.app_env == "development", connect_args=connect_args)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)


async def create_all_tables() -> None:
    if _engine is None:
        init_db()
    assert _engine is not None
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        init_db()
    assert _session_factory is not None
    async with _session_factory() as session:
        yield session
