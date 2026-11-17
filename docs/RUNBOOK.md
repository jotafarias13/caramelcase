# Runbook

An outline. Local development is written; the production sections are filled in by milestone 8.

## Local development

Needs Docker, and for the checks uv and Node 24.

```sh
docker compose up        # Postgres 16, the API with reload, the Vite dev server
```

- App: http://localhost:5173
- API: http://localhost:8000/api/v1/health, docs at http://localhost:8000/api/v1/docs
- Postgres: `localhost:5432`, user, password and database in `.env.example`

No `.env` is needed. To change a port or a setting, copy `.env.example` to `.env`.

The first start installs the API and web dependencies inside the containers, into volumes. After changing `api/pyproject.toml` or `web/package.json`, restart the service: `docker compose restart api` or `web`.

`docker compose down` stops everything and keeps the data; `docker compose down -v` also deletes the database and the dependency volumes.

## Checks

```sh
make install      # once: uv sync and npm ci on the host
make lint         # ruff, eslint, prettier
make typecheck    # mypy, tsc
make test         # pytest and vitest
```

The API tests start their own Postgres 16 container, so Docker must be running. To use a server that is already up instead, set `TEST_DATABASE_URL`.

CI (`.github/workflows/ci.yaml`) runs the same targets on every push.

## Seeding

To be written in milestone 5: `make seed`.

## Deploy

To be written in milestone 8: first deploy, later deploys, migrations as an explicit step, the workflows and their secrets.

## TLS certificates

To be written in milestone 8: first issue and renewal.

## Backup and restore

To be written in milestone 8: `deploy/backup.sh` and the restore procedure, tried locally.

## Feature flags and plans

To be written in milestones 9 and 10: switching a flag, `grant-plan`.

## Publishing a subject

To be written in milestone 5: the CLI command the owner runs after the hand check.

## Troubleshooting

- **API tests fail to start Postgres with a Docker socket mount error.** testcontainers mounts the Docker socket into its helper container. `api/tests/conftest.py` sets `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`, which is right for Docker Desktop; set the variable yourself if your Docker uses another path.
