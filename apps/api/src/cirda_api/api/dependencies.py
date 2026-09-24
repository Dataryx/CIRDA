"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from cirda_api.container import Container, build_container
from cirda_api.db.session import get_session
from cirda_api.settings import Settings, get_settings
from sqlalchemy.ext.asyncio import AsyncSession

_app_container: Container | None = None


def get_app_container() -> Container:
    global _app_container
    if _app_container is None:
        settings = get_settings()
        _app_container = build_container(settings)
    return _app_container


def set_app_container(container: Container) -> None:
    global _app_container
    _app_container = container


async def get_container(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Container:
    if hasattr(request.app.state, "container"):
        return request.app.state.container
    return get_app_container()


async def get_request_container(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Container:
    if settings.use_memory_store:
        if hasattr(request.app.state, "container"):
            return request.app.state.container
        return get_app_container()
    return build_container(settings, session=session)


ContainerDep = Annotated[Container, Depends(get_request_container)]
