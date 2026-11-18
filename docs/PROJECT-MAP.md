# Project map

A tour of the repository: what each folder holds, and where to go for a given change. `docs/ARCHITECTURE.md` has the same ground in more depth (every module, table and business rule); this file is the way in.

## Reading order for someone new

1. `README.md`: what the app is and how to run it.
2. This file.
3. `docs/ARCHITECTURE.md`: how a request travels, the data model, where each rule lives.
4. The README of the part you will work in: `web/README.md`, `content/README.md`, `design/README.md` or `deploy/README.md`.
5. `docs/RUNBOOK.md` when you need a procedure (a migration, an import, a deploy).

`docs/initial-spec.md`, `docs/PLAN.md` and `docs/DECISIONS.md` are the project's history: what was asked, in what order it was built, and every choice made along the way. Read `DECISIONS.md` when you wonder why something is the way it is.

## The top level

```text
caramelcase/
  api/                  FastAPI backend (Python 3.12, uv)
  web/                  React frontend (TypeScript, Vite, Tailwind)
  content/              subject catalog, question bank, content tools
  design/               the design handoff: read-only source of truth for looks
  deploy/               production: Dockerfiles, compose, nginx, certbot, backups
  docs/                 spec, plan, decisions, architecture, runbook, this map
  .github/workflows/    CI on every push; build-and-publish and deploy, run by hand
  docker-compose.yml    local development stack (Postgres, API with reload, Vite)
  Makefile              every local command: make help
  .env.example          local settings you can override (none are required)
```

## api/

The backend. A request goes route → service → domain function → database.

```text
api/
  app/
    main.py             builds the app: middleware, error handlers, routers under /api/v1
    settings.py         every tunable number and environment value, in one place
    enums.py            fixed vocabularies: statuses, modes, flag keys, plan keys
    routes/             one module per API area (auth, account, practice, stats...)
    schemas/            Pydantic request and response models; the OpenAPI schema comes from them
    services/           reads and writes rows, calls domain functions; never commits
    domain/             business rules as pure functions: rating, selection, XP, streak...
    providers/          outside services behind an interface: email (console, SMTP), Google
    db/models/          every table as a SQLAlchemy model
    db/migrations/      Alembic migrations
    cli.py              commands: seed, import-content, publish-subjects, demo-user, openapi
    logger.py           JSON logs and the request log
  tests/
    domain/             unit tests of the business rules (no database)
    content_tools/      tests of content/tools
    test_*_api.py       API tests against a real Postgres, one rolled-back transaction each
  pyproject.toml        dependencies and the ruff, mypy and pytest settings
  gunicorn.conf.py      the production server
```

## web/

The frontend. One folder per screen; every text comes from the translation files and every colour from the design's tokens.

```text
web/
  src/
    app/                router (routes.tsx), providers, navigation shell, RequireUser, Flagged
    features/           one folder per screen: landing, onboarding, home, catalog, session,
                        summary, profile, settings, auth (sign-in), legal
    components/         shared pieces; ui/ holds the design's primitives (Button, Badge...)
    api/                typed API client, every call as a TanStack Query hook (queries.ts),
                        generated types (schema.d.ts, openapi.json: make types)
    i18n/               pt-BR.json and en.json: all interface text
    lib/                theme, language, flags, syntax highlighter, monitoring
    test/               mock API and sample data for the component tests
  e2e/                  the Playwright test: a guest plays a whole session
  shots/                screenshots of the app beside the design's mockups (npm run shots)
  eslint-rules/         the lint rule that fails on text written into a component
```

## content/

The question bank lives here as files; the database copies it.

```text
content/
  catalog.yaml          the 20 subjects and their topics
  bank/<subject>/<topic>.jsonl    the questions: one JSON object per line, both languages
  prompts/              instructions for the agents that write and blind-solve questions
  tools/                validate, run-code, dedupe, strip-keys, check-blind, promote, report
  REPORT.md             counts per subject, topic and difficulty
  work/                 questions still in the pipeline (not committed)
```

## design/

Finished, and read in place, never copied or edited: `tokens.css` and `tailwind.theme.js` feed the web app's styles, `screens/` has an HTML mockup of every screen (`v1-*` built, `v2-*` and `v3-*` to come), `copy.md` has the interface text, `assets/` the logo, icons and Mel, the mascot. `design/README.md` describes every component.

## deploy/

Production only; local development does not use it. `deploy/README.md` lists every file, and `docs/DEPLOY.md` says what to set up before the first deploy.

## Where to go when you want to…

| Change | Go to | Then |
| --- | --- | --- |
| A number: session length, XP, K-factors, rate limits | `api/app/settings.py` | Each is also an environment variable of the same name |
| A business rule | `api/app/domain/` | Its unit tests are in `api/tests/domain/` |
| What an API route accepts or returns | `api/app/schemas/`, then `api/app/routes/` | `make types`, so the web app's types follow |
| A table or a column | `api/app/db/models/` | `make migration m="..."`, read the new file, `make migrate` (`docs/RUNBOOK.md`, "Database migrations") |
| How a screen looks or behaves | `web/src/features/<screen>/` | Read its mockup in `design/screens/` first |
| Interface text | `web/src/i18n/pt-BR.json` and `en.json` | Both files need the same keys; a test checks |
| A shared component | `web/src/components/` | `ui/` follows `design/README.md` |
| A question | `content/bank/<subject>/<topic>.jsonl` | `content/README.md`; then `make import-content` |
| A subject or topic | `content/catalog.yaml` | `make seed` |
| A V2 or V3 feature switch | `feature_flags` table | `docs/ARCHITECTURE.md`, "Feature flags" |
| CI | `.github/workflows/ci.yaml` | It calls the same `make` targets you run |
| nginx, certificates, backups | `deploy/` | `docs/RUNBOOK.md`, "Production" |

## A change from end to end

Say a new field should appear on the profile:

1. Add the column to the model in `api/app/db/models/`, write the migration (`make migration m="add x"`) and apply it (`make migrate`).
2. Add the field to the response model in `api/app/schemas/`, and fill it in the service in `api/app/services/`. If it involves a rule, write the rule as a pure function in `api/app/domain/` with a unit test.
3. `make types`: the web app now knows the field, and `make typecheck` fails anywhere the types disagree.
4. Show it in `web/src/features/profile/`, with any new text added to both translation files.
5. `make lint`, `make typecheck`, `make test`; `make e2e` for a change to the main path.
