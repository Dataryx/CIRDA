#!/usr/bin/env bash
# Generate TypeScript types from OpenAPI spec (optional — requires openapi-typescript).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC="$ROOT/packages/contracts/openapi/cirda-v1.yaml"
OUT="$ROOT/apps/web/src/types/api.generated.ts"

if [[ ! -f "$SPEC" ]]; then
  echo "OpenAPI spec not found at $SPEC — run: make openapi"
  exit 1
fi

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm not found; skipping frontend type generation"
  exit 0
fi

cd "$ROOT/apps/web"
if pnpm exec openapi-typescript --version >/dev/null 2>&1; then
  pnpm exec openapi-typescript "$SPEC" -o "$OUT"
  echo "Generated $OUT"
else
  echo "openapi-typescript not installed; add as devDependency to enable type gen"
  echo "  pnpm add -D openapi-typescript"
  exit 0
fi
