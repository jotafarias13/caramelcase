# Architecture

An outline. Each section says what exists today; milestone 7 completes it with the request path, the data model and where each business rule lives.

## Repository

| Path | What it is |
| --- | --- |
| `api/` | FastAPI app on Postgres. uv project, Python 3.12 |
| `web/` | React single-page app. Vite, TypeScript, Tailwind, shadcn/ui |
| `content/` | Question bank (JSONL) and the tools that check it |
| `design/` | The UI handoff: tokens, Tailwind theme, mockups, assets, copy. Read-only for the build |
| `deploy/` | Production Dockerfiles, compose file, nginx, certbot, backup |
| `docs/` | The spec, the plan, decisions, this file, the runbook |

## Request path

Today, in development: browser → Vite dev server (`:5173`) → `/api` proxied to Uvicorn (`:8000`) → FastAPI → Postgres.

Inside the API a request passes through, in order:

1. `app/logger.py` `log_request`: gives the request an id, logs one line when it ends, returns the id in `X-Request-ID`.
2. CORS, with origins from settings.
3. The route in `app/routes/`, which gets a database session from `app/db/session.py`.
4. `app/errors.py`: any error leaves as `{"error": {"code": "...", "message": "..."}}`.

To be written: production path through nginx, authentication, CSRF, rate limits, feature flags.

## API layout

| Module | Role |
| --- | --- |
| `app/main.py` | Builds the app: middleware, error handlers, routers under `/api/v1` |
| `app/settings.py` | Every environment value and tunable number |
| `app/db/` | Engine and session; models and migrations from milestone 2 |
| `app/domain/` | Business rules as pure functions (milestone 5 onward) |
| `app/routes/` | One module per API area |
| `app/services/` | Orchestration between routes, database and domain |
| `app/providers/` | Email, billing, ads, tutor: interface, mock, real adapter |

## Web layout

| Path | Role |
| --- | --- |
| `src/main.tsx` | Entry: loads `design/tokens.css`, then Tailwind, applies the theme |
| `src/app/` | App shell; router and providers from milestone 6 |
| `src/features/` | One folder per feature |
| `src/components/` | Shared components; `ui/` holds the shadcn-style primitives |
| `src/lib/` | `cn()` and the theme helper |
| `src/styles/index.css` | Tailwind entry and base rules. No token is defined here |

## Data model

To be written in milestone 2 and completed in milestone 7.

## Where each business rule lives

To be written from milestone 5: one row per rule, naming its function in `app/domain/` and its settings.

## Feature flags

To be written in milestone 5.
