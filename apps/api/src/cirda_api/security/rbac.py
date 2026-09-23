"""Role-based access control."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from cirda_api.security.auth import PrincipalContext, authenticate

ROLE_ORDER = {"viewer": 0, "analyst": 1, "approver": 2, "admin": 3}


def require_role(min_role: str) -> Callable[..., PrincipalContext]:
    async def _dep(principal: Annotated[PrincipalContext, Depends(authenticate)]) -> PrincipalContext:
        min_level = ROLE_ORDER[min_role]
        if not any(ROLE_ORDER.get(r, -1) >= min_level for r in principal.roles):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Requires role {min_role} or higher")
        return principal

    return _dep


RequireViewer = Annotated[PrincipalContext, Depends(require_role("viewer"))]
RequireAnalyst = Annotated[PrincipalContext, Depends(require_role("analyst"))]
RequireApprover = Annotated[PrincipalContext, Depends(require_role("approver"))]
RequireAdmin = Annotated[PrincipalContext, Depends(require_role("admin"))]
