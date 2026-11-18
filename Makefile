# Checks run on the host with uv and npm; CI runs these same targets.
# Each recipe joins its commands with &&, so a failing step fails the target.

.PHONY: help install up down logs ps migrate migration seed import-content \
	publish demo-user types lint lint-api lint-web typecheck typecheck-api \
	typecheck-web test test-api test-web e2e format build-web

help:
	@echo "make install    install API and web dependencies on the host"
	@echo "make up         start Postgres, the API and the web app (docker compose)"
	@echo "                and wait until they answer"
	@echo "make down       stop them"
	@echo "make logs       follow their logs"
	@echo "make migrate    apply the database migrations (starts the stack if needed)"
	@echo "make seed       migrate, seed, import the content, publish the launch"
	@echo "                subjects and create the demo user: a playable database"
	@echo "make import-content   bring the questions in line with content/bank"
	@echo "make publish s=\"slug\"   publish a subject and its verified questions"
	@echo "make demo-user  print a new sign-in link for the demo user"
	@echo "make types      regenerate the web app's types from the API's schema"
	@echo "make migration m=\"add x\"   write a migration from the models"
	@echo "make lint       ruff, eslint and prettier"
	@echo "make typecheck  mypy and tsc"
	@echo "make test       pytest (needs Docker for Postgres, and cc) and vitest"
	@echo "make e2e        the Playwright test, against make up and make seed"
	@echo "make format     fix what the linters can fix"

install:
	cd api && uv sync --locked
	cd web && npm ci --no-audit --no-fund

# Returns once every service is healthy: the first start installs the
# API's and the web app's dependencies, which takes a minute or two.
up:
	docker compose up -d --wait
	@echo "The app is at http://localhost:5173 (WEB_PORT in .env changes it)."

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

# The ones below run inside the api container, against the database of
# docker compose. -T: no terminal is needed, so they also run in CI.
API_RUN = docker compose exec -T api uv run --frozen

# Starts the stack first if it is not up: the api container must have
# finished installing its dependencies before a command runs in it.
migrate: up
	$(API_RUN) alembic upgrade head

# Everything a development database needs to be played on. Every step is
# safe to run again. Publishing the launch subjects here is for
# development only: in production a subject is published by hand, after
# its questions were checked (docs/RUNBOOK.md).
seed: migrate
	$(API_RUN) python -m app.cli seed
	$(API_RUN) python -m app.cli import-content
	$(API_RUN) python -m app.cli publish-subjects --launch
	$(API_RUN) python -m app.cli demo-user

publish:
	@test -n "$(s)" || { echo 'usage: make publish s="estruturas-de-dados"'; exit 1; }
	$(API_RUN) python -m app.cli publish-subjects $(s)

# The demo user's sign-in link is valid for 15 minutes; this prints a new one.
demo-user:
	$(API_RUN) python -m app.cli demo-user

# Add args=--dry-run to see what would change.
import-content:
	$(API_RUN) python -m app.cli import-content $(args)

migration:
	@test -n "$(m)" || { echo 'usage: make migration m="add a column"'; exit 1; }
	$(API_RUN) alembic revision --autogenerate -m "$(m)"

# The web app's types come from the API's OpenAPI schema. Both files are
# committed; a test on each side fails when one is out of date.
types:
	cd api && uv run python -m app.cli openapi > ../web/src/api/openapi.json
	cd web && npm run types

lint: lint-api lint-web

# The API and the content tools, which run in the API's environment.
lint-api:
	cd api && uv run ruff check . ../content && uv run ruff format --check . ../content

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

# Plays a whole session in a browser against the running stack (make up,
# make seed). Needs Playwright's Chromium once: cd web && npx playwright
# install chromium.
e2e:
	cd web && npm run e2e

build-web:
	cd web && npm run build

format:
	cd api && uv run ruff check --fix . ../content && uv run ruff format . ../content
	cd web && npm run format
