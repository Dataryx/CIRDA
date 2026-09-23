"""Pytest fixtures."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from cirda_api.api.dependencies import set_app_container
from cirda_api.container import build_container
from cirda_api.main import create_app
from cirda_api.settings import Settings, get_settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    os.environ["CIRDA_MEMORY_STORE"] = "true"
    os.environ["CIRDA_EVENT_BUS"] = "inmemory"
    os.environ["CIRDA_AUTH_MODE"] = "dev"
    os.environ["CIRDA_SCHEDULER_ENABLED"] = "false"
    os.environ.pop("CIRDA_DATABASE_URL", None)
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture
async def client(test_settings: Settings) -> AsyncIterator[AsyncClient]:
    get_settings.cache_clear()
    container = build_container(test_settings)
    set_app_container(container)
    app = create_app(test_settings)
    app.state.container = container
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer dev", "X-CIRDA-Role": "admin"}


@pytest.fixture
def viewer_headers() -> dict[str, str]:
    return {"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer"}


def pytest_configure(config: object) -> None:
    config.addinivalue_line("markers", "integration: integration tests requiring DATABASE_URL")  # type: ignore[attr-defined]
