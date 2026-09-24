"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from cirda_api.api.dependencies import set_app_container
from cirda_api.api.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from cirda_api.api.v1.router import api_router
from cirda_api.container import build_container
from cirda_api.db.session import create_all_tables, dispose_db, init_db
from cirda_api.jobs.scheduler import create_scheduler
from cirda_api.observability.logging import configure_logging
from cirda_api.observability.metrics import metrics_payload
from cirda_api.observability.tracing import configure_tracing
from cirda_api.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    configure_logging(cfg)
    configure_tracing(cfg)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        init_db(cfg)
        if cfg.use_memory_store or cfg.effective_database_url.startswith("sqlite"):
            await create_all_tables()
        container = None
        if cfg.use_memory_store:
            container = build_container(cfg)
            set_app_container(container)
            app.state.container = container
        scheduler = create_scheduler(cfg, container)
        if cfg.scheduler_enabled and container is not None:
            scheduler.start()
        yield
        if cfg.scheduler_enabled and container is not None:
            scheduler.shutdown(wait=False)
        await dispose_db()

    app = FastAPI(
        title="CIRDA Control Plane API",
        version="0.1.0",
        lifespan=lifespan,
        openapi_url="/openapi.json",
        docs_url="/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(api_router)

    @app.get("/metrics")
    async def metrics() -> Response:
        if not cfg.metrics_enabled:
            return Response(status_code=404)
        return Response(content=metrics_payload(), media_type="text/plain; version=0.0.4")

    return app


app = create_app()
