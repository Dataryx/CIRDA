#!/bin/sh
set -eu

cd /app/apps/api

if [ "${CIRDA_MEMORY_STORE:-false}" != "true" ] && [ -n "${CIRDA_DATABASE_URL:-}" ]; then
  echo "==> Running Alembic migrations"
  uv run alembic upgrade head
fi

exec "$@"
