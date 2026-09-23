# CIRDA monorepo Makefile
# Preferred on Windows: Git Bash or WSL. PowerShell alternatives noted inline.
# Native Windows: use `make` from Git for Windows, or run scripts/*.ps1 equivalents.

SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c

UV ?= uv
PNPM ?= pnpm
PYTHON ?= $(UV) run python
ROOT := $(CURDIR)
API_DIR := apps/api
WEB_DIR := apps/web
INGEST_DIR := apps/ingest-worker
CORE_DIR := packages/cirda-core
BENCH_DIR := packages/cirda-bench
CONTRACTS_DIR := packages/contracts
COMPOSE := docker compose -f deploy/docker/docker-compose.yml
COMPOSE_DEV := docker compose -f deploy/docker/docker-compose.dev.yml
COMPOSE_LITE := docker compose -f deploy/docker/docker-compose.lite.yml
DOCKER_AVAILABLE := $(shell command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1 && echo yes || echo no)

.PHONY: bootstrap dev dev-lite seed migrate lint test test-int e2e bench bench-smoke openapi verify build \
	help _check-docker _check-e2e-docker

help: ## Show targets
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Install Python (uv) and Node (pnpm) dependencies, pre-commit hooks
	@echo "==> Bootstrapping CIRDA monorepo"
	$(UV) sync --all-packages --group dev
	$(UV) run pre-commit install || true
	cd $(WEB_DIR) && $(PNPM) install
	@echo "==> Copy .env.example to .env if missing"
	@test -f .env || cp .env.example .env
	@echo "Bootstrap complete. Run: make dev"

bootstrap.ps1: ## Windows PowerShell bootstrap (no make required)
	powershell -ExecutionPolicy Bypass -File scripts/bootstrap.ps1

dev: ## Start API + web dev servers (requires bootstrap)
	@echo "==> Starting dev stack (API :8000, Web :5173)"
	$(MAKE) -j2 dev-api dev-web

dev-api:
	cd $(API_DIR) && $(UV) run uvicorn cirda_api.asgi:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd $(WEB_DIR) && $(PNPM) dev

dev-lite: ## Start API + web with in-memory store (no Postgres/Redis)
	@echo "==> dev-lite: in-memory store, inmemory event bus"
	CIRDA_MEMORY_STORE=true CIRDA_EVENT_BUS=inmemory CIRDA_SCHEDULER_ENABLED=false \
		$(MAKE) dev

dev-lite.ps1:
	$$env:CIRDA_MEMORY_STORE='true'; $$env:CIRDA_EVENT_BUS='inmemory'; $$env:CIRDA_SCHEDULER_ENABLED='false'; $(MAKE) dev

seed: ## Seed demo estate (requires CIRDA_ENV=local, API running or direct mode)
	$(PYTHON) scripts/seed_demo_estate.py

migrate: ## Run Alembic migrations (requires DATABASE_URL)
	cd $(API_DIR) && $(UV) run alembic upgrade head

lint: ## Ruff + ESLint + constants parity
	$(UV) run ruff check packages apps scripts
	$(UV) run ruff format --check packages apps scripts
	$(PYTHON) scripts/check_constants_parity.py
	cd $(WEB_DIR) && $(PNPM) lint

test: ## Unit tests (Python + frontend)
	$(UV) run pytest $(CORE_DIR)/tests $(BENCH_DIR)/tests $(API_DIR)/tests/unit -q --tb=short
	cd $(WEB_DIR) && $(PNPM) test

test-int: ## Integration tests (API)
	$(UV) run pytest $(API_DIR)/tests/integration -q --tb=short

e2e: _check-e2e-docker ## Playwright E2E (requires Docker for full stack)
	cd $(WEB_DIR) && $(PNPM) exec playwright install chromium
	cd $(WEB_DIR) && $(PNPM) e2e

bench: ## Full benchmark suite
	$(UV) run pytest $(BENCH_DIR)/tests -q --tb=short
	$(UV) run cirda-bench run --profile full || $(UV) run python -m cirda_bench.cli run --profile full || true

bench-smoke: ## Fast benchmark smoke (golden determinism + Table II shape)
	$(UV) run pytest $(BENCH_DIR)/tests/test_determinism.py $(BENCH_DIR)/tests/test_reproduces_table_ii.py -q --tb=short

openapi: ## Generate OpenAPI spec and frontend types
	$(PYTHON) scripts/generate_openapi.py
	bash scripts/generate_frontend_types.sh

verify: lint test test-int bench-smoke ## CI verification chain (skips e2e without Docker)
	@echo "==> verify: lint + test + test-int + bench-smoke OK"
ifeq ($(DOCKER_AVAILABLE),yes)
	@echo "==> Docker detected; run 'make e2e' separately for full browser tests"
else
	@echo "==> Skipping e2e: Docker not available. Install Docker or use WSL2 to run 'make e2e'"
endif

build: ## Build Python wheels and frontend production bundle
	$(UV) build --package cirda-core
	$(UV) build --package cirda-bench
	$(UV) build --package cirda-api
	$(UV) build --package cirda-ingest
	cd $(WEB_DIR) && $(PNPM) build
	$(COMPOSE) build || echo "Docker build skipped (docker unavailable)"

_check-docker:
ifeq ($(DOCKER_AVAILABLE),no)
	@echo "ERROR: Docker is required but not running."; exit 1
endif

_check-e2e-docker:
ifeq ($(DOCKER_AVAILABLE),no)
	@echo "WARNING: Skipping e2e — Docker not available."
	@echo "  On Windows: enable WSL2 + Docker Desktop, or use Git Bash with Docker."
	@exit 0
endif
