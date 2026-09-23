"""Structured logging setup."""

from __future__ import annotations

import logging

import structlog

from cirda_api.settings import Settings


def configure_logging(settings: Settings) -> None:
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    if settings.log_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(processors=processors)
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
