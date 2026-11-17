# Runbook

An outline. Local development is written; the production sections are filled in by milestone 8.

## Local development

Needs Docker, and for the checks uv, Node 24 and a C compiler as `cc` (the content tools compile the C of questions).

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
- **Topics** follow the same file. A new one is created; an existing one gets its names and order updated. A topic that left the file stays in the database, because questions point at it.

Milestone 5 adds to `make seed`: importing the content, publishing the launch subjects and creating a demo user.

## Importing the question bank

```sh
make import-content                    # python -m app.cli import-content
make import-content args=--dry-run     # show the counts, save nothing
```

It reads `content/bank/` (the directory `CONTENT_DIR` points at) and brings the `questions` and `question_translations` tables in line with it. It is safe to run again, and it also writes the catalog's subjects and topics, so it works on a database that was only migrated.

| A question that is | Becomes |
| --- | --- |
| In the files, not in the database | A new row: `verified` in a launch subject, `draft` in any other; rating from its difficulty |
| In both, same content | Untouched |
| In both, content changed | New text, `version` plus 1. Status, counts and rating stay, except that the rating follows a new difficulty while nobody has answered the question |
| In the database, not in the files | `retired`. Nothing is deleted |
| Retired, back in the files with new content | Rewritten, and `verified` or `draft` again, as if new |
| Retired, in the files unchanged | Left retired, and listed in the command's output |

"Content" is everything in the line except `version` and `verification`: recording a hand check does not bump a version.

The whole bank is checked first. One invalid line, one question outside the catalog or one question that did not pass the pipeline, and the command prints the problems, exits with code 1 and imports nothing. An empty bank is refused too, since importing it would retire every question.

Before importing into production, run it with `--dry-run` and read the "retired" count: a file missing from the checkout retires its questions, and putting the file back does not bring them back (see the last row of the table). To undo that by hand, give them back the status they had (`published` if the subject is live): `UPDATE questions SET status = 'verified' WHERE external_id LIKE '<subject>.<topic>.%' AND status = 'retired';`.

Never reuse the id of a question that was removed: the database still has the old row under that id.

## Writing questions

`content/README.md` describes the pipeline and its tools. From the repository root:

```sh
uv run --project api python -m content.tools --help
uv run --project api python -m content.tools validate content/bank --verified
```

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

- **`run-code` or its tests fail with "cc is not installed".** Install a C compiler (Xcode command line tools on macOS, `gcc` on Linux), or name another one in `CODE_RUN_C_COMPILER`. The flags are `CODE_RUN_C_FLAGS`; the compiler must support `-fsanitize=address,undefined`.

- **API tests fail to start Postgres with a Docker socket mount error.** testcontainers mounts the Docker socket into its helper container. `api/tests/conftest.py` sets `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`, which is right for Docker Desktop; set the variable yourself if your Docker uses another path.
