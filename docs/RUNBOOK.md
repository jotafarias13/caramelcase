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

A new database is empty. `make seed` creates the tables and the starting rows (see Seeding).

## Checks

```sh
make install      # once: uv sync and npm ci on the host
make lint         # ruff, eslint, prettier
make typecheck    # mypy, tsc
make test         # pytest and vitest
```

The API tests start their own Postgres 16 container, so Docker must be running. To use a server that is already up instead, set `TEST_DATABASE_URL`: the tests drop everything in that database, and create and drop other databases on that server, so its user needs `CREATEDB`.

CI (`.github/workflows/ci.yaml`) runs the same targets on every push.

## Database migrations

The schema is managed by Alembic. Its files are in `api/app/db/migrations/versions/`, one per change, and `api/alembic.ini` lists the commands. The database URL comes from `DATABASE_URL`.

```sh
make migrate                         # apply every migration to the docker compose database
make migration m="add a column"      # write a new migration from the models
```

Both run inside the `api` container, so `make up` comes first.

To change the schema: edit the model in `api/app/db/models/`, run `make migrate` so the database is at the latest migration, run `make migration m="..."`, read the new file, then `make migrate` again. `make test` fails while a model and the migrations differ.

A new value in an enum of `api/app/enums.py` needs no migration: enum columns are plain `VARCHAR(32)`.

Outside docker compose, from `api/`: `uv run alembic upgrade head`, `uv run alembic downgrade -1` to undo the last migration, `uv run alembic upgrade head --sql` to print the SQL without running it.

## Seeding

```sh
make seed        # make migrate, then python -m app.cli seed
```

`python -m app.cli seed` writes the rows every environment needs, and is safe to run again:

- **Plans** follow `plans` in `api/app/settings.py`. Prices and limits are overwritten on every run, so change a plan there, not in the table.
- **Feature flags** are created switched off. A flag that exists keeps its state.
- **Subjects** follow `content/catalog.yaml`. A new one is created as a draft; an existing one gets its names, badge and order updated and keeps its status.

Milestone 5 adds to `make seed`: importing the content, publishing the launch subjects and creating a demo user.

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
