"""RFC 9457 Problem Details for HTTP APIs."""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException


class ProblemDetail(BaseModel):
    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    errors: list[dict[str, Any]] | None = None


def problem_response(
    *,
    status: int,
    title: str,
    detail: str | None = None,
    type_: str = "about:blank",
    instance: str | None = None,
    errors: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    body = ProblemDetail(
        type=type_,
        title=title,
        status=status,
        detail=detail,
        instance=instance,
        errors=errors,
    )
    return JSONResponse(status_code=status, content=body.model_dump(exclude_none=True), media_type="application/problem+json")


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return problem_response(
        status=exc.status_code,
        title=str(exc.detail) if isinstance(exc.detail, str) else "HTTP Error",
        detail=str(exc.detail) if not isinstance(exc.detail, str) else None,
        instance=str(request.url),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return problem_response(
        status=422,
        title="Validation Error",
        detail="Request validation failed",
        instance=str(request.url),
        errors=list(exc.errors()),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return problem_response(
        status=500,
        title="Internal Server Error",
        detail=str(exc),
        instance=str(request.url),
    )
