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

A new database is empty. `make seed` makes it playable (see Seeding): from a clean clone, `docker compose up` and `make seed` are the two commands.

### Signing in locally

Nothing is needed to play: the app creates a guest on the first visit. To sign in:

- **As the demo user.** `make seed` creates `demo@example.com` with three weeks of history and prints a link that signs in as it. The link is valid for 15 minutes; `make demo-user` prints a new one.
- **With "Continue with Google".** Without `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`, a mock stands in for Google and signs in as the demo user at once. With both set, the real flow runs; register `http://localhost:5173/api/v1/auth/google/callback` as a redirect URI at Google.
- **With an email link.** Without `SMTP_HOST`, the email is written to the API's log: `docker compose logs api` shows the link. Any address works.

The guest playing in the browser is merged into the account that signs in, so sign in from a private window to keep the demo user's history as it is.

## Checks

```sh
make install      # once: uv sync and npm ci on the host
make lint         # ruff, eslint, prettier
make typecheck    # mypy, tsc, and that the web app's API types are current
make test         # pytest and vitest
make types        # after changing a route or a model in api/app/schemas/
```

`make types` writes the API's OpenAPI schema to `web/src/api/openapi.json` and the TypeScript types to `web/src/api/schema.d.ts`. Both are committed. A pytest test fails when the first is out of date and `make typecheck` fails when the second is.

The API tests start their own Postgres 16 container, so Docker must be running. To use a server that is already up instead, set `TEST_DATABASE_URL`: the tests drop everything in that database, and create and drop other databases on that server, so its user needs `CREATEDB`.

CI (`.github/workflows/ci.yaml`) runs the same targets on every push.

### The web app

```sh
make build-web                          # what a deploy serves: web/dist
cd web && npx vite preview              # serves web/dist on :4173, with /api proxied to :8000
cd web && npm run shots -- -g v1-home   # a screen beside its mockup: web/README.md
cd web && npm run icons                 # after the design's app icon changes
```

- **The build has two steps**, both inside `npm run build`: the landing page is built for Node into `web/dist-ssr/`, then the app is built into `web/dist/` with the landing page's HTML written into `index.html`. `dist-ssr/` is not deployed.
- **The service worker exists only in a build.** `npm run dev` and docker compose do not register one. After trying a build with `vite preview`, the browser keeps that origin's service worker: remove it in the browser's developer tools (Application, Service workers, Unregister) before using the same port for something else.
- **`npm run shots` and `npm run icons` need Playwright's Chromium once**: `cd web && npx playwright install chromium`. CI does not need it.

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
make seed        # everything a development database needs to be played on
```

`make seed` runs, in the `api` container, the migrations and then four commands. Each is safe to run again:

| Command | What it does |
| --- | --- |
| `python -m app.cli seed` | Plans, feature flags, subjects and topics (below) |
| `python -m app.cli import-content` | The question bank (next section) |
| `python -m app.cli publish-subjects --launch` | Publishes the three launch subjects and their verified questions (see Publishing a subject) |
| `python -m app.cli demo-user` | Creates `demo@example.com` with three weeks of sessions and a streak of 7 days, and prints a sign-in link. If the demo user exists, only the link is new |

The last two are for development. In production, run `seed` and `import-content` at a deploy, publish a subject by hand after its questions were checked, and never run `demo-user`: it refuses when `ENVIRONMENT=production`.

The demo user's history is not written by hand: it plays real sessions on past dates, so its answers move the ratings of the questions it answered, as any student's do. To start it over, delete it and run `make demo-user`: `DELETE FROM users WHERE email = 'demo@example.com';`.

`python -m app.cli seed` writes the rows every environment needs:

- **Plans** follow `plans` in `api/app/settings.py`. Prices and limits are overwritten on every run, so change a plan there, not in the table.
- **Feature flags** are created switched off. A flag that exists keeps its state.
- **Subjects** follow `content/catalog.yaml`. A new one is created as a draft; an existing one gets its names, badge and order updated and keeps its status.
- **Topics** follow the same file. A new one is created; an existing one gets its names and order updated. A topic that left the file stays in the database, because questions point at it.

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

Students see only published subjects, and are served only published questions. Importing never publishes: a question enters as `verified` (launch subjects) or `draft`.

```sh
make publish s="estruturas-de-dados"                        # docker compose
uv run python -m app.cli publish-subjects estruturas-de-dados banco-de-dados   # from api/, anywhere
```

The command sets the subject's status to `published` and turns each of its `verified` questions into `published`. Drafts and retired questions are left alone. It prints how many questions it published.

- **Before the first time:** check a sample of the subject's questions by hand (about 50).
- **After importing more questions** into a published subject, run it again: the new ones wait as `verified` until then.
- **To take one question out of play:** `UPDATE questions SET status = 'retired' WHERE external_id = '<id>';`. If the question is still in the files unchanged, the importer leaves it retired.
- **To hide a whole subject again:** `UPDATE subjects SET status = 'draft' WHERE slug = '<slug>';`. Its questions keep their status and come back with the subject.

A topic shows in the app once it has a published question.

## Sign-in settings

All from the environment (`.env.example` lists them):

| Variable | Meaning |
| --- | --- |
| `APP_BASE_URL` | The web app's public address. Sign-in links in emails start with it, and Google sends the student back to `<APP_BASE_URL>/api/v1/auth/google/callback`, which must be registered at Google |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Google sign-in. Without them, production has no Google sign-in (the routes answer 404 and `GET /config` says `google_sign_in: false`); development uses the mock |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM` | Where sign-in links are sent from (STARTTLS). Without `SMTP_HOST` the email goes to the log, which in production means nobody can sign in by email |
| `SESSION_COOKIE_SECURE` | Leave it `true`. Local docker compose sets `false`, because it serves plain http |
| `CORS_ORIGINS` | The origins allowed to call the API with the cookie: the app's own |

A session lasts 90 days from its last renewal (`SESSION_LIFETIME_DAYS`) and is renewed while the student keeps coming back. To sign a user out everywhere: `DELETE FROM sessions_auth WHERE user_id = '<id>';`.

## Troubleshooting

- **The `api` container never becomes healthy, and its log stops after "Started reloader process".** On an Apple M4 with Docker Desktop 27.5, OpenSSL's CPU probe dies with "Illegal instruction" when the `cryptography` package loads (`docker compose exec api /opt/venv/bin/python -X faulthandler -c "import cryptography.hazmat.bindings._rust"` shows it). `docker-compose.yml` sets `OPENSSL_armcap=0` for the container, which skips the probe; check that the line is still there. A newer Docker Desktop may not need it.

- **`run-code` or its tests fail with "cc is not installed".** Install a C compiler (Xcode command line tools on macOS, `gcc` on Linux), or name another one in `CODE_RUN_C_COMPILER`. The flags are `CODE_RUN_C_FLAGS`; the compiler must support `-fsanitize=address,undefined`.

- **API tests fail to start Postgres with a Docker socket mount error.** testcontainers mounts the Docker socket into its helper container. `api/tests/conftest.py` sets `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`, which is right for Docker Desktop; set the variable yourself if your Docker uses another path.
