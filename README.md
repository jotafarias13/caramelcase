# CaramelCase

Five-minute practice sessions for computer science students, in the style of Duolingo: multiple-choice questions with code, adaptive difficulty, a short reason under every option, XP, a daily goal and a streak. Brazilian Portuguese first, English second.

A React single-page app (`web/`) on a FastAPI and Postgres backend (`api/`), with the question bank as files in `content/`. Everything runs locally with Docker; nothing needs an outside account.

**Where it stands.** V1 is built, and so are the production files. The bank holds 880 checked questions in the three launch subjects: Introdução à Programação, Estruturas de Dados and Banco de Dados. V2 and V3 features (review queue, leagues, paid plans, AI tutor...) come next, behind feature flags that are off by default. `docs/PLAN.md` has the full status.

## Run it on your computer

You need **Docker** (Docker Desktop on macOS or Windows, Docker Engine with the compose plugin on Linux), **git** and **make**. Nothing else: Python, Node and Postgres run inside containers. On Windows, use WSL 2 (not tried).

```sh
git clone <repository-url> caramelcase
cd caramelcase
make up      # starts Postgres, the API and the web app, and waits until they answer
make seed    # fills the database: questions, the three subjects, a demo user
```

Then open **http://localhost:5173**.

The first `make up` downloads three Docker images, which takes a few minutes. With the images on the machine, a fresh copy took 12 seconds for `make up` and 26 for `make seed`.

### What to show

- **The landing page** has a sample question to try without an account.
- **Play as a guest.** "Começar" (or "Start") creates a guest account silently. Onboarding asks for a language, a university and course (optional), a subject and a daily goal, then starts a session of 10 questions. Keys 1 to 4 pick an option and Enter confirms. After each answer every option shows why it is right or wrong.
- **After the session:** the summary (rating change, XP, streak), then Home, Profile and Settings. Settings switches language, theme (light or dark) and the per-option reasons.
- **The demo user** has three weeks of history and a 7-day streak, which makes Home and Profile look lived-in. `make seed` prints a sign-in link for it; the link works for 15 minutes, and `make demo-user` prints a new one. Open it in a private window: the guest in your normal window would otherwise be merged into the demo account.
- **"Continuar com Google"** works locally too: without Google keys, a stand-in signs you in as the demo user.
- **Sign-in by email** works with any address: no email is sent locally, and the link is in the API's log (`docker compose logs api`).
- **From a phone** on the same Wi-Fi: `http://<your computer's local IP address>:5173`.

### Stop, restart, start over

```sh
make down                  # stop; the database is kept
make up                    # start again
docker compose down -v     # stop and delete the database and installed dependencies
make up && make seed       # then start from scratch
```

If port 5173, 8000 or 5432 is taken, copy `.env.example` to `.env` and change `WEB_PORT`, `API_PORT` or `POSTGRES_PORT`. `docs/RUNBOOK.md` has a troubleshooting section at the end.

## Work on it

The checks run on your machine, outside Docker, and need [uv](https://docs.astral.sh/uv/), Node 24 and a C compiler as `cc` (the content tools compile the C in questions).

```sh
make install     # once: the API's and the web app's dependencies
make lint        # ruff, eslint, prettier
make typecheck   # mypy, tsc
make test        # pytest (starts its own Postgres in Docker) and vitest
make e2e         # a guest plays a whole session in Chromium, against make up and make seed
make help        # every other command
```

`make e2e` needs Playwright's browser once: `cd web && npx playwright install chromium`. GitHub Actions runs all of these on every push (`.github/workflows/ci.yaml`).

## Find your way around

| Folder | What is in it |
| --- | --- |
| `api/` | The FastAPI app: routes, services, business rules as pure functions, database models and migrations, tests |
| `web/` | The React app: one folder per screen, shared components, translations, the Playwright test |
| `content/` | The subject catalog, the question bank (one JSON question per line) and the tools that check it |
| `design/` | The finished design handoff: tokens, mockups of every screen, copy, assets |
| `deploy/` | Production: Dockerfiles, compose file, nginx, certificates, backups, deploy scripts |
| `docs/` | Spec, plan, decisions, architecture, runbook |

`docs/PROJECT-MAP.md` is a guided tour: what each folder holds and where to go for a given change.

## Documentation

| File | Read it for |
| --- | --- |
| `docs/PROJECT-MAP.md` | Finding your way around the code |
| `docs/ARCHITECTURE.md` | The request path, the data model, where each business rule lives |
| `docs/RUNBOOK.md` | Every procedure: local setup, migrations, importing questions, production, backups, troubleshooting |
| `docs/DEPLOY.md` | What to set up before the first deploy |
| `docs/initial-spec.md` | What the product is meant to be (V1 to V3) |
| `docs/PLAN.md` | Build order and status |
| `docs/DECISIONS.md` | Every choice made where the spec was silent, and why |
| `web/README.md`, `content/README.md`, `design/README.md`, `deploy/README.md` | The rules of each part |
