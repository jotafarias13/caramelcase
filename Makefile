# Checks run on the host with uv and npm; CI runs these same targets.
# Each recipe joins its commands with &&, so a failing step fails the target.

.PHONY: help install up down logs ps \
	lint lint-api lint-web typecheck typecheck-api typecheck-web \
	test test-api test-web format build-web

help:
	@echo "make install    install API and web dependencies on the host"
	@echo "make up         start Postgres, the API and the web app (docker compose)"
	@echo "make down       stop them"
	@echo "make logs       follow their logs"
	@echo "make lint       ruff, eslint and prettier"
	@echo "make typecheck  mypy and tsc"
	@echo "make test       pytest (needs Docker for Postgres) and vitest"
	@echo "make format     fix what the linters can fix"

install:
	cd api && uv sync --locked
	cd web && npm ci --no-audit --no-fund

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

lint: lint-api lint-web

lint-api:
	cd api && uv run ruff check && uv run ruff format --check

lint-web:
	cd web && npm run lint

typecheck: typecheck-api typecheck-web

typecheck-api:
	cd api && uv run mypy

typecheck-web:
	cd web && npm run typecheck

test: test-api test-web

test-api:
	cd api && uv run pytest

test-web:
	cd web && npm test

build-web:
	cd web && npm run build

format:
	cd api && uv run ruff check --fix && uv run ruff format
	cd web && npm run format
