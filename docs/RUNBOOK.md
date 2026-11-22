# Runbook

How to run CaramelCase: on a laptop first, then in production (from "Production" on).

## Local development

Needs Docker, and for the checks uv, Node 24 and a C compiler as `cc` (the content tools compile the C of questions).

From a clean clone, two commands give a playable app:

```sh
make up          # Postgres 16, the API with reload, the Vite dev server; waits until they answer
make seed        # migrations, the question bank, the launch subjects published, the demo user
```

Then open http://localhost:5173. Tried on a fresh copy of the repository with fresh volumes: `make up` took 12 seconds and `make seed` 26, with the three images already pulled; the first pull adds a few minutes. `docker compose up` in the foreground works too; `make seed` starts the stack itself if it is not up.

- App: http://localhost:5173
- API: http://localhost:8000/api/v1/health, docs at http://localhost:8000/api/v1/docs
- Postgres: `localhost:5432`, user, password and database in `.env.example`

No `.env` is needed. To change a port or a setting, copy `.env.example` to `.env`.

The first start installs the API and web dependencies inside the containers, into volumes. After changing `api/pyproject.toml` or `web/package.json`, restart the service: `docker compose restart api` or `web`.

`docker compose down` stops everything and keeps the data; `docker compose down -v` also deletes the database and the dependency volumes.

A new database is empty. `make seed` makes it playable (see Seeding).

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

CI (`.github/workflows/ci.yaml`) runs the same targets on every push, and a third job runs the end-to-end test below.

### The end-to-end test

```sh
make up && make seed                          # once: the stack and its data
cd web && npx playwright install chromium     # once: the browser
make e2e
```

`web/e2e/guest-session.spec.ts` plays what the spec asks of it in a real Chromium against the running stack: a new guest opens the landing page, goes through onboarding, answers ten questions (always the first option: it does not know the keys), sees the summary, then opens Home, Profile and Settings. It runs twice, in Portuguese at 360 px and in English at 1280 px, and first checks with `GET /config` that every feature flag is off. Each run leaves a guest in the database.

`E2E_BASE_URL=http://localhost:55173 make e2e` runs it against a stack on other ports. When it fails, `web/test-results/` has a screenshot and a trace of each failed step: `npx playwright show-trace <file>`. In CI, the failed job keeps both as the `playwright-report` artifact and prints the stack's logs.

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

## Production

One Linux server runs everything with Docker Compose, from a clone of the repository: `deploy/docker-compose.yml` with its values in `deploy/.env`. Four services: `nginx` (the web app's image: nginx serving the built app and proxying `/api`), `api` (gunicorn with Uvicorn workers), `db` (Postgres 16 in the volume `caramelcase-prod_db_data`) and `certbot` (run only for certificates). The images are built by GitHub Actions and pulled from Docker Hub; nginx's configuration and the scripts come from the clone. `docs/ARCHITECTURE.md` has the request path.

Every production command is a target of `deploy/Makefile`: `make -C deploy help` lists them. They run on the server, from the repository's root.

### First deploy

Once, on a new server. `docs/DEPLOY.md` lists what to have ready first: accounts, secrets, the deploy user on the server.

1. **The server.** Ubuntu with ports 22, 80 and 443 open. `sudo deploy/scripts/install_server.sh` (after cloning, step 3) installs Docker with compose, git, make and envsubst.
2. **The domain.** An A record from `DOMAIN` to the server's address. Only `DOMAIN` gets a certificate; `www.` is not served.
3. **The clone.** `git clone <repository> /opt/caramelcase` (or another place: `PROJECT_ROOT` in `deploy/.env` must say where). A private repository needs a deploy key on the server.
4. **The settings.** `cp deploy/.env.example deploy/.env` and fill it in. At least: the two image names, `DOMAIN`, `CERTBOT_EMAIL`, `PROJECT_ROOT`, `POSTGRES_PASSWORD` (`openssl rand -hex 24`), `APP_BASE_URL` and `CORS_ORIGINS` (`https://<DOMAIN>`), and SMTP, without which nobody can sign in by email. Google sign-in is optional. Values with spaces go in double quotes: the scripts load the file with bash.
5. **Docker Hub.** `docker login`, if the images are private.
6. **The certificate.** The images must have been published first ("Build and publish images"), since this step runs nginx from the web image. `sudo make -C deploy certificate`: nginx answers Let's Encrypt's challenge, certbot gets the certificate, and a cron job to renew it is installed (see "TLS certificates").
7. **The deploy.** `make -C deploy deploy`, or the "Deploy to production" workflow once its secrets are set.
8. **The questions.** `make -C deploy import-content args=--dry-run`, then `make -C deploy import-content`. Students see nothing until a subject is published: after the hand check of about 50 questions, `make -C deploy publish s="introducao-a-programacao"` (see "Publishing a subject").
9. **Backups.** `sudo make -C deploy backup-cron` installs the nightly dump (see "Backup and restore").
10. **A look.** Open `https://<DOMAIN>`; `make -C deploy ps` shows three services healthy.

### Later deploys

1. Merge into `main`.
2. GitHub, Actions, **Build and publish images**, Run workflow on `main`. It runs CI first and builds only a commit that passes, then pushes `<user>/caramelcase-api` and `<user>/caramelcase-web`, each tagged `main` and `main-<short sha>`.
3. Actions, **Deploy to production**, Run workflow on `main`. On the server it runs `git pull` and `deploy/scripts/deploy.sh`.

Without GitHub, on the server: `git pull && make -C deploy deploy`.

`deploy/scripts/deploy.sh` does, in order:

1. Tags the images the server has as `<image>:main-bkp`.
2. Pulls the new images.
3. Runs `nginx -t` in the new web image with the configuration from the clone.
4. Migrates the database with the new API image (`alembic upgrade head`), then seeds plans, flags, subjects and topics. **This is the only place migrations run**: the API never migrates on start.
5. Starts the new images and waits up to 3 minutes for every service to be healthy.
6. If they are not: prints the last log lines, starts the `-bkp` images again and exits with 1. If a step before 5 fails, nothing running was touched.

A rollback puts back images, not the schema: migrations stay applied. Write each migration so that the API before it still runs on the schema after it (add a column before using it, drop it a release after the code stops using it).

**To go back to an older version on purpose:** set `DOCKER_TAG=main-<short sha>` in `deploy/.env` and `make -C deploy deploy`; set it back to `main` afterwards.

**After the question bank changed:** the content travels in the API's image, so after the deploy run `make -C deploy import-content args=--dry-run`, read the "retired" count, import, and run `make -C deploy publish s=...` again for a published subject.

### The workflows' secrets

GitHub, Settings, Secrets and variables, Actions. The names are those of the owner's reference projects.

| Secret | Used by | What it is |
| --- | --- | --- |
| `DOCKER_HUB_USERNAME` | both | The Docker Hub account the images are pushed to and pulled from |
| `DOCKER_HUB_TOKEN` | both | An access token of that account: read and write for the build, read for the deploy |
| `VM_HOST` | deploy | The server's address |
| `VM_USER` | deploy | The user the workflow signs in as over SSH; it must be able to run `docker` |
| `VM_SSH_PRIVATE_KEY` | deploy | The private key of that user's SSH key |
| `PROJECT_ROOT` | deploy | Where the repository is cloned on the server, as in `deploy/.env` |
| `VITE_BETTER_STACK_ERRORS_DSN` | build, optional | Better Stack error tracking for the web app (see "Logs and monitoring") |
| `VITE_PLAUSIBLE_DOMAIN` | build, optional | Plausible analytics: the site's domain as registered at Plausible |
| `VITE_PLAUSIBLE_SCRIPT` | build, optional | Another Plausible script address (self-hosted Plausible, or the site's own script) |

The image names come from the repository's name: a repository called `caramelcase` gives `<DOCKER_HUB_USERNAME>/caramelcase-api` and `-web`, which `deploy/.env` must name.

### Trying the production stack on a laptop

The same files with plain http, against images built on the laptop. In `deploy/.env` (from `.env.example`): `DOMAIN=localhost`, `NGINX_CONF_FILE=default.conf.http`, `HTTP_PORT=8080`, `HTTPS_PORT=8443`, `DOCKER_IMAGE_API=caramelcase-api`, `DOCKER_IMAGE_WEB=caramelcase-web`, `DOCKER_TAG=local`, a password, `APP_BASE_URL` and `CORS_ORIGINS` set to `http://localhost:8080`, and on an Apple M4 `OPENSSL_armcap=0` (see "Troubleshooting"). Then:

```sh
make -C deploy build          # both images, about 2 minutes the first time
make -C deploy migrate seed import-content
make -C deploy publish s="introducao-a-programacao estruturas-de-dados banco-de-dados"
make -C deploy up             # http://localhost:8080
E2E_BASE_URL=http://localhost:8080 make e2e
docker compose -f deploy/docker-compose.yml down -v    # stop, and delete its database
```

The compose project is `caramelcase-prod`, apart from the development stack's `caramelcase`, so the two never share a database. Chromium accepts the Secure cookie on `http://localhost`; another browser, or the laptop's address on a network, needs `SESSION_COOKIE_SECURE=false`. `make -C deploy deploy` pulls images, so it needs a registry: a throwaway one (`docker run -d -p 5001:5000 registry:2`, images named `localhost:5001/caramelcase-api`, `make -C deploy build`, then `docker push` both) runs the script as on the server.

Milestone 8 tried all of this on 2026-11-17, on an M4 with Docker Desktop 27.5: the first deploy (18 seconds), the Playwright test in both languages through nginx and gunicorn, the https configuration with a self-signed certificate in the certbot volume, a rollback from an API image that does not start, a deploy stopped by a broken nginx configuration, backups and a restore. The one thing not tried is a real certificate from Let's Encrypt, which needs a public domain.

## TLS certificates

- **First certificate:** `sudo make -C deploy certificate` (`deploy/certbot/certbot.sh`), before the first deploy. It starts nginx alone with `default.conf.https.temp`, which serves only `/.well-known/acme-challenge/`; certbot writes its challenge into the shared volume and Let's Encrypt fetches it over port 80; then the temporary nginx is removed and `/etc/cron.d/caramelcase_renew` installed. To try it without spending Let's Encrypt's weekly limit, add `--staging` to the certbot command in the script first.
- **Renewal:** every day at 02:00, cron runs `deploy/certbot/renew.sh`: `certbot renew` renews a certificate close to expiry, and nginx reloads it. Its log is `/var/log/caramelcase-renew.log`. By hand: `sudo deploy/certbot/renew.sh`.
- **When it expires:** `docker compose -f deploy/docker-compose.yml run --rm certbot certificates` shows the date.
- The certificate lives in the volume `caramelcase-prod_certbot`, which nginx mounts at `/etc/nginx/ssl`. Deleting that volume means issuing again.

## Backup and restore

- **Every night at 03:00**, cron runs `deploy/backup.sh` (installed once by `sudo make -C deploy backup-cron` as `/etc/cron.d/caramelcase_backup`; its log is `/var/log/caramelcase-backup.log`). It writes `caramelcase-<UTC time>.dump`, a compressed `pg_dump`, to `BACKUP_DIR` (`/var/backups/caramelcase`) and deletes all but the newest `BACKUP_KEEP` (14). The files are readable by root only: they hold students' data. One now: `sudo make -C deploy backup`.
- **They are on the server's own disk.** A lost server loses them too. Copying them elsewhere (a bucket, another machine) is still to be decided.
- **A deleted account stays in the backups** for 14 days, as the privacy policy says.

**Restoring** replaces the whole database:

```sh
sudo deploy/restore.sh /var/backups/caramelcase/caramelcase-20261118T030000Z.dump
```

It asks for the database's name to go on, stops nginx and the API (the app is down meanwhile), saves the current database as `before-restore-<time>.dump` beside the backups (which `backup.sh` never deletes), drops and recreates the database, restores the dump with `pg_restore`, and starts everything again. After a restore, check the deployed code's migrations against the dump's: a dump older than a migration needs `make -C deploy migrate`.

Tried on the laptop stack on 2026-11-17: four backups with `BACKUP_KEEP=3` left the newest three; after deleting every user and unpublishing every question, a restore brought back the 2 users, 20 answers and 880 published questions of the dump, and the app answered again. A wrong name at the prompt changed nothing.

**Reading one table out of a dump** without touching production:

```sh
cd deploy
docker compose exec -T db sh -c 'createdb -U "$POSTGRES_USER" scratch'
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d scratch --no-owner' \
    < /var/backups/caramelcase/caramelcase-20261118T030000Z.dump
make psql      # then \c scratch; drop it afterwards with dropdb
```

## Logs and monitoring

- **Logs:** `make -C deploy logs`, or one service: `docker compose -f deploy/docker-compose.yml logs api`. The API writes one JSON object per line (`time` in UTC, `level`, `message`, then fields such as `request_id`, `path`, `status`, `duration_ms`, or `logger` for a line of gunicorn or a library). nginx writes one per request, with `request_id` set to the API's for `/api` requests, so `grep <request_id>` finds both lines. nginx's error log stays plain text. Docker keeps 5 files of 10 MB per container.
- **Health:** `https://<DOMAIN>/api/v1/health` answers 200 when the API reaches the database. That is the address for an uptime monitor ("Uptime monitoring with Better Stack", below).
- **Error tracking (Better Stack):** for the API, `BETTER_STACK_ERRORS_DSN` in `deploy/.env` and `make -C deploy up`; for the web app, the `VITE_BETTER_STACK_ERRORS_DSN` secret and a new build. Without them nothing is sent. Each DSN comes from the Ingest tab of an application in Better Stack's error tracking, and looks like `https://<token>@<host>/<id>`; one application for the API and one for the web app keeps their errors apart. Better Stack accepts what the Sentry SDK sends, so the code uses `sentry-sdk` and `@sentry/browser` and only the DSN points at Better Stack. Neither sends cookies, request bodies or a user's identity, and the web app strips query strings, where a sign-in link carries its token.
- **Analytics (Plausible):** the `VITE_PLAUSIBLE_DOMAIN` secret and a new build. Plausible sets no cookies. Without the secret the build has no script.
- **Before switching on either:** add the service to the privacy policy's list of who receives data (`legal` in `web/src/i18n/`).

### Uptime monitoring with Better Stack

Not set up yet. It needs a Better Stack account and nothing in the repository.

- **The app:** a monitor on `https://<DOMAIN>/api/v1/health`. A 200 means nginx, the API and the database all answer. nginx answers 502 `api_unavailable` when the API is down, and the API answers 503 `database_unavailable` when the database is, so either opens an incident. For a stricter check, make it a keyword monitor that expects `"database":"ok"` in the body.
- **The site:** a second monitor on `https://<DOMAIN>/`, which nginx serves without the API. With both monitors you can tell "nginx is down" from "the API is down".
- **The certificate:** Better Stack's monitors can warn before a certificate expires, which catches a renewal that has stopped working.
- **The cron jobs:** a heartbeat for the backup and one for the certificate renewal. Each heartbeat is a URL (`https://uptime.betterstack.com/api/v1/heartbeat/<token>`) that expects a request on schedule, and opens an incident when none arrives. Ping it only when the job succeeds, by adding to the line in `deploy/backup_cron` or `deploy/certbot/renew_cron`:

  ```sh
  0 3 * * * root ${PROJECT_ROOT}/deploy/backup.sh >> /var/log/caramelcase-backup.log 2>&1 && curl -fsS -m 10 --retry 3 https://uptime.betterstack.com/api/v1/heartbeat/<token> > /dev/null
  ```

  The tidier way is a code change: an optional `BACKUP_HEARTBEAT_URL` in `deploy/.env` that `backup.sh` calls at the end, and `<url>/fail` when the dump fails, so the token stays out of the cron file. The same goes for `send-reminders` when the `reminders` cron line arrives in milestone 9.

Uptime checks send no student's data, so the privacy policy needs no change for them.

### Log collection with Better Stack

Not set up yet. Today the logs stay on the server: Docker keeps 5 files of 10 MB per container, and losing the server loses them. Shipping them to Better Stack makes them searchable, kept for longer, and able to raise an alert. There are two ways, and both keep Docker's `json-file` driver, so `make -C deploy logs` still works:

- **Better Stack's collector** (the `betterstack/collector` image): Better Stack's recommended way. It is installed on the server with one command from the source's page in Better Stack, and reads every container's logs. It also sends the host's metrics. This is the least work, but its setup lives on the server and not in git.
- **Vector**, with Better Stack's HTTP sink and the source's token. Better Stack's Docker guide installs it on the host as a service, and the `vector` user must be in the `docker` group. To fit this repository better, run it as a container in `deploy/docker-compose.yml` instead, under a `logs` profile. It would mount `/var/run/docker.sock` read-only, with a `docker_logs` source and its configuration in `deploy/`, and take the token from `deploy/.env`. Then it lives in git and is deployed with the rest. This is the way to choose for this repository.

What Better Stack would receive: the API's lines are already JSON, so their fields (`request_id`, `path`, `status`, `duration_ms`, `logger`) can be searched as they are. nginx's access lines are JSON too, and share `request_id` with the API's. Two things to do before switching it on:

- **The privacy policy.** nginx's access log and the API's request log hold IP addresses, so the policy must name Better Stack among those who receive data, and say how long it keeps logs.
- **The volume.** Drop the healthcheck's line every 30 seconds (2,880 a day) with a filter in Vector or in Better Stack, so it does not count against the plan.

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

## Rate limits

The auth routes, sign-in links, answers and reports are limited (the table is in `docs/ARCHITECTURE.md`). Over a limit, the API answers 429 `rate_limited` with `Retry-After`; the app says "Muitas tentativas seguidas…" on sign-in, an answer and a report.

- **Change a limit** with an environment variable holding JSON, then restart the API: `RATE_LIMIT_AUTH='{"requests": 600, "seconds": 600}'`. The four are `RATE_LIMIT_AUTH`, `RATE_LIMIT_SIGN_IN_EMAIL`, `RATE_LIMIT_ANSWERS` and `RATE_LIMIT_REPORTS`.
- **Lift a limit for someone now:** restart the API. The counts live in the API's memory and start again from zero.
- **Under gunicorn**, each worker counts apart, so a caller can reach the number of workers times a limit before every worker refuses.
- **A whole campus may share one address.** The limit per address (300 in 10 minutes) is set high for that; if students behind one network see "Muitas tentativas seguidas" on their first visit, raise `RATE_LIMIT_AUTH`.
- **In production nginx limits `/api/` too**, per address: 30 requests a second with bursts of 60 (`limit_req_zone` in `deploy/nginx/nginx.conf`, `limit_req` in `app.conf`). Over it, nginx answers the same 429 `rate_limited`. To change it, edit both lines, `make -C deploy check-nginx`, commit, and deploy.

## A student's data

A student downloads everything the app keeps about them in Settings, "Baixar meus dados" (`GET /me/export`, a JSON file), and erases it with "Excluir conta" (`DELETE /me`). Both work for a guest too.

When someone asks by email instead, for an account they can no longer open:

```sql
-- What the account holds: the user's id, then the same tables as the export.
SELECT id, email, created_at FROM users WHERE email = '<address>';
-- Erase it: every row of the user goes with it, and the sign-in links sent to the address.
DELETE FROM users WHERE email = '<address>';
DELETE FROM magic_links WHERE email = '<address>';
```

Backups keep a deleted account for as long as they are kept (14 days, milestone 8); the privacy policy says so.

## Privacy policy and terms

`/privacy` and `/terms` hold placeholder text written in plain language from what the app does. Their text is under `legal` in `web/src/i18n/pt-BR.json` and `en.json`: one title and one body per section, paragraphs apart by a blank line, a list as lines that start with `- `. Gaps are in brackets (`[nome da empresa]`, `[e-mail de contato]`, `[data]`).

When the final text arrives: replace the bodies in both files, fill or remove every bracket, set `legal.updated`, and remove the draft note (`legal.draft`, the `role="note"` paragraph in `web/src/features/legal/LegalDocument.tsx`, and its check in `legal.test.tsx`). A section is added or removed in the list at the top of `PrivacyPage.tsx` or `TermsPage.tsx` and in both files.

## Troubleshooting

- **The `api` container never becomes healthy, and its log stops after "Started reloader process".** On an Apple M4 with Docker Desktop 27.5, OpenSSL's CPU probe dies with "Illegal instruction" when the `cryptography` package loads (`docker compose exec api /opt/venv/bin/python -X faulthandler -c "import cryptography.hazmat.bindings._rust"` shows it). `docker-compose.yml` sets `OPENSSL_armcap=0` for the container, which skips the probe; check that the line is still there. A newer Docker Desktop may not need it.

- **The production stack on an Apple M4: the `api` container restarts with no log, or a `make -C deploy` command dies at once.** The same OpenSSL probe as above. Put `OPENSSL_armcap=0` in `deploy/.env`, which the API's container reads. A real server does not need it.

- **A deploy ends "The new images are not healthy".** It has already started the previous images again. `docker compose -f deploy/docker-compose.yml logs api` (or `nginx`) has the reason; the script prints the last 40 lines of both.

- **The app shows its maintenance screen and `/api/` answers 502 `api_unavailable`.** nginx cannot reach the API: `make -C deploy ps`, then the API's log.

- **`run-code` or its tests fail with "cc is not installed".** Install a C compiler (Xcode command line tools on macOS, `gcc` on Linux), or name another one in `CODE_RUN_C_COMPILER`. The flags are `CODE_RUN_C_FLAGS`; the compiler must support `-fsanitize=address,undefined`.

- **On Linux, `npm ci` or `make install` fails with `EACCES` under `web/node_modules`.** The stack was started with `docker compose up` before that folder existed, so Docker created it as root to mount the web container's volume there. `make down`, `sudo rm -rf web/node_modules`, then start the stack again with `make up`, which creates the folder as you first. CI's end-to-end job failed this way until `make up` did that.

- **API tests fail to start Postgres with a Docker socket mount error.** testcontainers mounts the Docker socket into its helper container. `api/tests/conftest.py` sets `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`, which is right for Docker Desktop; set the variable yourself if your Docker uses another path.
