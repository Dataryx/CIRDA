"""Multi-tenant request context (logical isolation)."""

from __future__ import annotations

from contextvars import ContextVar

from fastapi import Header, HTTPException, status

from cirda_api.settings import Settings

_tenant_id: ContextVar[str] = ContextVar("cirda_tenant_id", default="default")


def get_current_tenant_id() -> str:
    return _tenant_id.get()


def set_current_tenant_id(tenant_id: str) -> None:
    _tenant_id.set(tenant_id)


async def resolve_tenant(
    settings: Settings,
    x_cirda_tenant: str | None = Header(default=None, alias="X-CIRDA-Tenant"),
) -> str:
    """
    Resolve tenant for the request.

    When multi-tenant is disabled, always use ``default_tenant_id``.
    When enabled, require ``X-CIRDA-Tenant`` (or fall back to default only in
    development).
    """
    if not settings.multi_tenant_enabled:
        tenant = settings.default_tenant_id
        set_current_tenant_id(tenant)
        return tenant

    tenant = (x_cirda_tenant or "").strip() or settings.default_tenant_id
    if settings.app_env == "production" and not (x_cirda_tenant or "").strip():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "X-CIRDA-Tenant header required when multi-tenant mode is enabled",
        )
    set_current_tenant_id(tenant)
    return tenant
