"""Authentication."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from jose import JWTError, jwt

from cirda_api.settings import Settings, get_settings


@dataclass(frozen=True, slots=True)
class PrincipalContext:
    principal_id: str
    subject: str
    roles: frozenset[str]


DEV_ROLES = frozenset({"admin", "approver", "analyst", "viewer"})


async def authenticate(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    settings: Settings = Depends(get_settings),
) -> PrincipalContext:
    if settings.auth_mode == "dev":
        token = None
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
        if token == "dev" or x_api_key == "dev":
            role_header = request.headers.get("X-CIRDA-Role", "admin")
            roles = frozenset({role_header} if role_header else {"viewer"})
            return PrincipalContext(principal_id="dev", subject="dev@local", roles=roles)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Dev auth requires Bearer dev or X-API-Key: dev")

    if settings.auth_mode == "api_key":
        if not x_api_key:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing X-API-Key")
        # Production would hash and lookup principal; dev fallback
        return PrincipalContext(principal_id="api-key", subject="api-key-user", roles=frozenset({"analyst"}))

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = authorization[7:].strip()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc
    roles = frozenset(payload.get("roles", ["viewer"]))
    return PrincipalContext(
        principal_id=str(payload.get("sub", "unknown")),
        subject=str(payload.get("sub", "unknown")),
        roles=roles,
    )


OptionalPrincipal = Annotated[PrincipalContext | None, Depends(lambda: None)]
