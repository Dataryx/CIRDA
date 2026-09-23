#!/usr/bin/env bash
# CIRDA monorepo bootstrap — install Python (uv) and Node (pnpm) dependencies.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Checking prerequisites"
command -v uv >/dev/null 2>&1 || { echo "ERROR: uv not found. Install: https://docs.astral.sh/uv/"; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo "ERROR: pnpm not found. Install: npm i -g pnpm"; exit 1; }

echo "==> Syncing Python workspace"
uv sync --all-packages --group dev

echo "==> Installing pre-commit hooks"
uv run pre-commit install || true

echo "==> Installing frontend dependencies"
(cd apps/web && pnpm install)

if [[ ! -f .env ]]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
fi

echo ""
echo "Bootstrap complete."
echo "  make dev       — start API + web"
echo "  make dev-lite  — in-memory mode"
echo "  make seed      — demo estate (with API running)"
