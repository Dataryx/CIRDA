"""ASGI entrypoint for uvicorn/gunicorn."""

from cirda_api.main import app

__all__ = ["app"]
