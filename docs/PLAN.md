# CaramelCase build plan

The build order for `docs/initial-spec.md`, as a checklist. Work top to bottom: the next task is the first unticked box. A milestone is done when every box under it is ticked, lint, type checks and tests pass, and it is committed.

Status on 2026-11-17: milestones 1 to 3 and 5 to 8 done. Milestone 4 is open but set aside: 34 of the 50 topics are in the bank (880 questions), imported as `verified`, and the owner decided that is enough to move on. Next: milestone 9, V2 behind flags. The other 16 topics of milestone 4 come later, when the owner says so, with subagents on Opus 5.5 at high effort (see milestone 4).

## Decisions

The changes to the spec agreed with the owner, and the defaults chosen where spec and design disagree or are silent, moved to `docs/DECISIONS.md` in milestone 1. Read that file in full before any work: its first section overrides `docs/initial-spec.md`.

## Reference material

- `syllabus-v1.txt` (repo root, never committed): syllabus for the three launch subjects.
- The owner's reference projects, a web app and an API in folders beside this repository: read-only. Take from them:
  - `nginx/default.conf.http`, `default.conf.https`, `default.conf.https.temp` in both: envsubst templates, JSON access log, 444 default servers, ACME webroot location. The API's adds the upstream, proxy headers and `limit_req`.
  - `certbot/certbot.sh`, `template.renew.sh`, `renew_cron` and the `certbot` compose profile with its two named volumes.
  - `.github/workflows/`: `ci.yaml` (the API's), `build_publish.yaml` and `deploy.yaml` (Docker Hub image, SSH deploy with health check and rollback), all manual except CI.
  - The API's `app/config/logger.py`, `request_info.py` and the middleware in `app/main.py` for logging; `tests/conftest.py` and `tests/support/` for the test-database approach (one outer transaction rolled back per test).
  - `Makefile` targets and `scripts/` in both.
- Known faults in the examples to fix, not copy: the unused `NGINX_CONF_FILE` export in `certbot.sh`, no `.dockerignore` in the web app's, no gzip, cache or security headers, no compose healthchecks.

## Environment

- Docker Desktop must be running for `docker compose up` and for the API tests, which start their own Postgres container.
- Installed: uv 0.8.5 with Python 3.12, Node 24, npm 11, Docker 27, gh, clang (for C snippets; `run-code` and its tests call it as `cc`).

## Milestones

### 1. Scaffold

- [x] Layout from the spec exists: `api/`, `web/`, `content/`, `deploy/`, `docs/`.
- [x] `docker compose up` starts Postgres 16, the API with reload and the Vite dev server; `GET /api/v1/health` returns 200 and checks the database.
- [x] `api` is a uv project on Python 3.12 with ruff, pytest and mypy; one typed settings module holds every tunable and env value.
- [x] `web` is React, TypeScript, Vite, Tailwind and shadcn/ui, styled only through `design/tokens.css` and `design/tailwind.theme.js`, both consumed unchanged; a sample page renders correctly with `data-theme` dark and light.
- [x] `make lint`, `make typecheck` and `make test` pass for `api` and `web`.
- [x] GitHub Actions runs lint, type checks and tests on every push. (The workflow is committed; its first run happens on the first push, which is the owner's call.)
- [x] `.env.example` is committed; `syllabus-v1.txt` is in `.git/info/exclude`.
- [x] `docs/DECISIONS.md` holds the two decision sections above; `docs/ARCHITECTURE.md` and `docs/RUNBOOK.md` exist as outlines.

### 2. Schema

- [x] Every table in the spec's data model exists as a typed SQLAlchemy model, plus `questions.external_id`, the university and course fields, and the extra tables listed above. UUID keys, `created_at` and `updated_at` everywhere, UTC.
- [x] `alembic upgrade head` on an empty database and `alembic downgrade base` both succeed; a test fails when models and migrations drift.
- [x] Idempotent seeds: plans (free 0, plus 15, pro 40, max 100, placeholder limits), every flag off, and the 20 subjects from `content/catalog.yaml` as draft.

### 3. Content tooling

- [x] `QuestionDoc` validates the spec's sample line; it is defined once and used by the tools and the importer.
- [x] `content/catalog.yaml` lists the topics of the three launch subjects, taken from the syllabus, each with its code language.
- [x] `content/tools/` has validate, strip-keys, run-code (Python, C and SQL, in a subprocess with a timeout), dedupe and report, each with unit tests. Two more, `check-blind` and `promote`, close the pipeline (see `docs/DECISIONS.md`).
- [x] `content/prompts/generate.md` and `blind-solve.md` carry the spec's writing rules.
- [x] `python -m app.cli import-content` upserts by `external_id`, bumps `version` on a changed `content_hash` and retires missing questions; tested.
- [x] A content test validates every line under `content/bank/` and runs in CI.

### 4. Launch content

Runs in subagents, in the background. The owner runs milestone 5 in a session of its own, not beside the content run. Per topic: one agent generates; the tools validate, run code and dedupe; a fresh agent that sees only the stripped file blind-solves; failures get one repair attempt, then are dropped. Waves of about six agents. `content/README.md` has the commands, step by step.

The 16 topics still to write are the ones with no questions in `content/REPORT.md`: 7 in Estruturas de Dados, 7 in Banco de Dados and 2 in Introdução à Programação. `arvores-binarias` is already written and waits in `content/work/` for its blind solve. Run them with one orchestrator agent per subject, so that the main session hears from each subject once and not four times per topic, and with at most three generators at a time. Every agent, the orchestrators included, is launched with model `opus` and effort `high`: the owner decided that. `content/work/fanout/brief.md` is the orchestrator's brief, with the task messages for generators, solvers and repairs, and `content/work/fanout/pipe.py` is the driver it calls. Both are local files, outside git. A topic costs about 260k tokens.

- [x] Pilot: one topic per launch subject through the full pipeline, with `content/REPORT.md` and samples shown to the owner. (`ponteiros` 32, `filas-e-deques` 22 and `sql-juncoes` 24: all 78 passed in the first round and are in `content/bank/`. What the pilot changed, and what it left open for the owner, is under "Milestone 4" in `docs/DECISIONS.md`.)
- [x] **Stop: the owner approves the pilot before the fan-out.** (Approved on 2026-11-17, with the decisions under "Milestone 4" in `docs/DECISIONS.md`.)
- [ ] About 400 questions per launch subject pass validation, blind solve, code runs and dedupe. (Per topic, as in the pilot: 32 in Introdução à Programação, 22 in Estruturas de Dados, 24 in Banco de Dados. On 2026-11-17: 352, 264 and 264, with 16 topics still to write.)
- [ ] Each topic's difficulty spread is near 25% level 1–2, 50% level 3, 25% level 4–5. (It holds for the 34 topics written; the box waits for the other 16.)
- [x] Every question is imported as `verified`. (880 questions on 2026-11-17, in the local database; run `make import-content` again after more topics.)
- [x] `content/REPORT.md` gives counts per subject, topic and difficulty, and the failure rate at each step.

### 5. V1 backend

- [x] `api/app/domain/` holds pure functions for rating, selection, XP, daily goal, streak, topic mastery and review schedule. Each has unit tests built on the spec's numbers, including streaks across timezones, and reads every number from settings.
- [x] Routes for auth, account, config, catalog, practice, stats, reports and events exist under `/api/v1` with Pydantic models; errors use the single shape.
- [x] API tests against a real Postgres cover: a guest playing a session of 10 through to finish; the answer response's fields; a session payload that never contains the correct key, reasons or explanation; a guest upgrade keeping its history; a merge into an existing account; a magic link working once and expiring after 15 minutes.
- [x] Session tokens are stored hashed and sent as an httpOnly, Secure, SameSite=Lax cookie or a bearer header; state-changing routes require the CSRF header; CORS reads its origins from settings.
- [x] A wrong answer writes a `review_items` row.
- [x] A flagged route returns 404 while its flag is off; the flag supports off, staff and on. (V1 has no flagged route: the test adds one. Milestone 9 is the first real use.)
- [x] `make seed` runs migrations, imports content, seeds plans and flags, publishes the launch subjects and creates a demo user with history. (Run on the local database: 880 questions published, `demo@example.com` with 18 sessions.)
- [x] The frontend's TypeScript types are generated from the OpenAPI schema. (`make types`; `web/src/api/schema.d.ts`.)

What milestone 6 builds on: `web/src/api/schema.d.ts` has every request and response; the API's description in `/api/v1/docs` says how the cookie and the `X-Requested-With` header work; "Signing in locally" in `docs/RUNBOOK.md` has the demo user. `GET /me/export` and `DELETE /me` already exist, with one test each, for milestone 7 to review.

### 6. V1 frontend

Read each screen's mockup files in full before building it.

- [x] Every V1 route in the spec exists: `/`, `/start`, `/home`, `/subjects`, `/session/:id`, `/session/:id/summary`, `/profile`, `/settings`, `/signin`, `/auth/callback`.
- [x] Each V1 screen matches its mockup at 360 px and 1280 px in both themes, checked by screenshots side by side with the mockup. (`npm run shots` in `web/`: 56 of the 57 V1 mockups have a scene, 112 comparisons, nearly all under 1% of pixels differing. The exceptions and their reasons are under "Milestone 6" in `docs/DECISIONS.md`. `/subjects` and `/auth/callback` have no mockup.)
- [x] All copy comes from `i18n/pt-BR.json` and `i18n/en.json`, built from `design/copy.md`; a check fails on hardcoded strings. Portuguese is the default and the browser language is detected on first visit. (The check is the lint rule `local/no-hardcoded-copy`, in `make lint`.)
- [x] Session screen: keys 1 to 4 select, Enter confirms, code scrolls sideways, reasons follow `show_option_reasons`, and an interrupted session resumes where it stopped.
- [x] The first visit creates a guest silently; the sign-in prompt appears after the first finished session.
- [x] `useFlag(key)` reads `/config`; flagged features are lazy-loaded and absent when off. (V1 has no flagged route: `<Flagged>` is tested on one of its own, and `useFlag("reminders")` hides the daily-reminder switch in Settings.)
- [x] Loading, empty, error, offline, 404 and maintenance states exist for every screen.
- [x] The landing page is pre-rendered to static HTML at build time.
- [x] PWA: manifest, icons exported from `design/assets/`, and a service worker caching the app shell only.
- [x] Nothing depends on hover; layouts respect safe areas.
- [x] Vitest component tests pass. (189 tests.)

What milestone 7 builds on: the whole flow was played against the real API by a throwaway Playwright script (a new guest through onboarding, ten questions by keyboard, the summary, Home, Profile and Settings), which is the path the Playwright test of milestone 7 makes permanent; `@playwright/test` is already a dev dependency of `web/`. The app has no links to privacy and terms pages yet. `web/README.md` has the frontend's rules.

### 7. V1 hardening

- [x] The Playwright test passes in CI: a guest opens the landing page, finishes a session and sees the summary. (`web/e2e/`, `make e2e`, in Portuguese at 360 px and English at 1280 px. The CI job `e2e` runs `make up`, `make seed`, `make e2e`; it passed locally run step by step, and its first run in CI happens on the first push, the owner's call.)
- [x] Rate limits on the auth, answer and report routes, with tests. (Four limits in settings, counted in memory per API process; a 429 with `Retry-After`.)
- [x] `GET /me/export` returns the user's data and `DELETE /me` erases it; both tested. (The export covers every table that points at `users`, guarded by a test; deleting erases the answers too, and the questions keep their counts. Settings has "Baixar meus dados".)
- [x] Privacy policy and terms pages exist in both languages with placeholder legal text. (`/privacy` and `/terms`, linked from the landing page, sign-in and Settings.)
- [x] `docs/ARCHITECTURE.md` explains the request path, the data model and where each business rule lives.
- [x] From a clean clone, two commands lead to a playable session. (`make up` and `make seed`: 12 and 26 seconds on a fresh copy with fresh volumes, then the Playwright test passed against it.)
- [x] V1 works end to end in both languages with every flag off. (The Playwright test, and a throwaway walk through sign-in, export, the legal pages, a rate limit and deletion in both languages. It found and fixed one bug: an account created by signing in before playing was always Portuguese.)

What milestone 8 builds on: the API trusts `X-Real-IP` for the rate limit per address, so nginx must set it (`proxy_set_header X-Real-IP $remote_addr`, as the reference API does) and the API container must publish no port. Rate-limit counts live in each gunicorn worker, so the number of workers multiplies the limits. The privacy policy promises backups kept 14 days. The Playwright test runs against the dev stack; it can be pointed at the production stack with `E2E_BASE_URL`.

### 8. Deployment files

- [x] Dockerfiles for the API (uv, gunicorn with Uvicorn workers) and for the web build served by nginx. (`deploy/api.Dockerfile`, `deploy/web.Dockerfile`, built from the repository root through an allowlist `.dockerignore`; the API's image carries the question bank.)
- [x] A production compose file with nginx and certbot containers adapted from the reference examples: envsubst templates for http, https and first-certificate, SPA fallback, `/api` proxied to the API container, 444 default servers. (`deploy/docker-compose.yml`, `deploy/nginx/`; the https template was tried with a self-signed certificate. `make check-deploy` runs `nginx -t` on all three in CI.)
- [x] Certificate issue and renew scripts adapted from the reference examples. (`deploy/certbot/`; the temporary configuration and `renew.sh` were tried, a real Let's Encrypt certificate was not: it needs a public domain.)
- [x] Migrations run as an explicit deploy step. (In `deploy/scripts/deploy.sh`, with the new API image, before it starts; never on the API's start.)
- [x] `deploy/backup.sh` keeps 14 nightly `pg_dump` files; the restore procedure in `docs/RUNBOOK.md` was tried locally. (`deploy/restore.sh` is the procedure; tried on 2026-11-17.)
- [x] Manual build-and-publish and deploy workflows modelled on the reference projects; `docs/RUNBOOK.md` names their secrets. (Not run yet: nothing has been pushed. `deploy.sh`, which the deploy workflow calls, was run against a local registry, rollback included.)
- [x] Logs are structured JSON; error tracking and external analytics switch on only when their keys are set. (gunicorn's and uvicorn's lines too, and nginx's access log; Better Stack error tracking, through the Sentry SDK, for the API and the web app; Plausible for the web app.)
- [x] The production stack boots locally with the http config. (The Playwright test passes against it in both languages: `docs/RUNBOOK.md`, "Trying the production stack on a laptop".)

What milestone 9 builds on: a new flagged route needs nothing in nginx, since everything under `/api/` is proxied. A migration must let the previous API image run on the new schema, because a rollback puts back images but not the schema. Anything the API should read in production is a setting, set in `deploy/.env`. The `reminders` feature's `send-reminders` command will need a cron line on the server, like `deploy/backup_cron`, running `docker compose run --rm --no-deps api python -m app.cli send-reminders`. Before Better Stack or Plausible is switched on, the privacy policy must name it.

### 9. V2 behind flags

For every feature: its routes return 404 with the flag off, it works locally with the flag on, its rules are pure functions with unit tests, and its screens match their `v2-*` mockups.

- [ ] `review_queue`: `GET /review/due`, review sessions, up to 3 due items in practice sessions.
- [ ] `question_types_v2`: true or false, predict the output, find the bug, fill in the blank, order the steps, with `QuestionDoc` payloads and a small verified set of each type.
- [ ] `exam_mode`: timed mock exam, navigator, results by topic.
- [ ] `lives`.
- [ ] `streak_freeze`, with each freeze earned and used recorded in `events`.
- [ ] `achievements`.
- [ ] `leagues`: weekly leaderboard with promotion and relegation.
- [ ] `reminders`: email and push, a `send-reminders` CLI command, the weekly email.
- [ ] `admin_console`: staff-only question list, edit, approve, retire, reports, flag switch.
- [ ] Subject catalog with add, remove, search and course filter.

### 10. V3 behind flags

Same four conditions as milestone 9, against the `v3-*` mockups. While `billing` is off, every user has no limits and no ads.

- [ ] Entitlements: `entitlements_for(user, subscription, flags)` is the only access decision; `usage_counters` enforces daily limits; `grant-plan <email> <plan> <days>` works.
- [ ] `billing`: `BillingProvider` with a mock that completes instantly and a Stripe adapter (card subscriptions, one-time Pix for annual and semester passes); webhooks are idempotent and write only to `subscriptions`; pricing, checkout, manage and cancel screens.
- [ ] `ads` and `beat_the_ad`: server-scheduled breaks, the challenge and double-or-nothing rules as pure functions, the mock `AdProvider` with a 5-second house ad, every step in `ad_events`.
- [ ] `streak_repair`: 48-hour window, rewarded ad for free users, one tap for paid plans, recorded in `events`.
- [ ] `ai_tutor`: `TutorProvider` with streaming, a mock and a real adapter set by environment variables; the daily limit is checked before the provider is called; tokens per reply are capped; rate limited.
- [ ] `exam_tracks`: track home with ranking.
- [ ] `write_code`: student code runs in the browser with Pyodide; the server never executes it.
- [ ] `referral`.

### 11. More content

- [ ] Subjects 4 onward, in catalog order, go through the milestone 4 pipeline and are imported as `draft`, as far as time allows; `content/REPORT.md` is updated after each run.

### 12. Capacitor shell

- [ ] An Android project loads the built app, with icons and splash from `design/`; it is not published.

## Still needed from the owner

None of these block the build; each has a mock or placeholder.

- Hosting choice (DigitalOcean or AWS) and the domain; then the server, the Docker Hub account and the workflows' secrets (`docs/RUNBOOK.md`, "Production")
- Where backups are copied off the server, if anywhere (they are kept 14 days on its own disk)
- Whether to switch on error tracking (Better Stack) and analytics (Plausible); each needs its key and a line in the privacy policy
- Whether to add Better Stack's uptime monitoring and log collection (`docs/RUNBOOK.md`, "Logs and monitoring"); log collection needs a line in the privacy policy too
- Google OAuth client id and secret (redirect URI to register: `<domain>/api/v1/auth/google/callback`)
- SMTP credentials for sign-in emails
- A hand check of about 50 questions per launch subject before it is published
- Final free-plan limits and ad frequency
- Legal text for the privacy policy and terms: the pages exist with placeholder text, and the gaps are in brackets (company, contact, data protection officer, legal basis, minimum age, retention, jurisdiction); also whether signing in needs a consent line
- Where a student types their name, if anywhere: only Google gives one (see "Open, not decided" under milestone 5 in `docs/DECISIONS.md`)
- Web fonts: served by Google Fonts as the design's token file asks, or self-hosted so they work offline (see "Landing page, PWA" under milestone 6 in `docs/DECISIONS.md`)
- A look at the screens no mockup covers: `/subjects`, `/auth/callback`, the subject switcher on Home, the streak moments on Home, a guest's Settings, a profile without a name
- The design's open placeholders: `[Benefício do plano]`, `[ANUAL]`, `[RECOMPENSA]`, `[nome da prova]`, `[seu-dominio]`
