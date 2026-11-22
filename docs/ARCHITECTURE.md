# Architecture

Each section says what exists today: V1, reviewed against the finished app in milestone 7, and its production setup from milestone 8.

## Repository

| Path | What it is |
| --- | --- |
| `api/` | FastAPI app on Postgres. uv project, Python 3.12 |
| `web/` | React single-page app. Vite, TypeScript, Tailwind, shadcn/ui |
| `content/` | The catalog, the question bank (JSONL), the prompts and the tools of the content pipeline |
| `design/` | The UI handoff: tokens, Tailwind theme, mockups, assets, copy. Read-only for the build |
| `deploy/` | Production Dockerfiles, compose file, nginx, certbot, backup |
| `docs/` | The spec, the plan, decisions, this file, the runbook, the deploy checklist (`DEPLOY.md`) and a tour of the repository (`PROJECT-MAP.md`) |

## Request path

In development: browser → Vite dev server (`:5173`) → `/api` proxied to Uvicorn (`:8000`) → FastAPI → Postgres.

In production (`deploy/docker-compose.yml`), four containers on one server: browser → `nginx` (`:443`, `:80` only redirects and answers certbot's challenge) → the built web app from its own files, or `/api/` proxied to `api` (gunicorn with two Uvicorn workers on `:8000`, no published port) → `db` (Postgres 16, a named volume). `certbot` runs only to issue or renew the certificate. The `nginx` container is the web app's image: nginx with `web/dist`, and its configuration mounted from `deploy/nginx/`.

Either way the browser only ever talks to one origin, so the session cookie is a first-party cookie.

What nginx adds in front of the API (`deploy/nginx/app.conf`):

- It overwrites `X-Real-IP` with the caller's address, which the API's rate limits trust; the API is reachable only through it.
- A limit on `/api/` per address (30 requests a second, bursts of 60), above the API's own per route. Its 429, and its 502 when the API is down, are JSON in the API's error shape.
- The API is looked up through Docker's DNS on each request (a variable in `proxy_pass`), so a replaced API container is found at its new address.
- Static files: any address that is not a file gets `index.html`, a missing file under `/assets/` is a 404, Vite's hashed files are cached for a year and everything else is revalidated on each use; gzip; security headers (`nosniff`, `DENY` framing, a referrer policy, a partial CSP, HSTS over https).
- Hosts other than `DOMAIN` get their connection closed (444).

Logs: the API writes one JSON line per request and per event, gunicorn's and uvicorn's own lines included (`app/logger.py` routes the standard `logging` module into loguru). nginx writes one JSON line per request, with the API's `X-Request-ID` as `request_id`, so the two lines of a request can be joined. `docker compose logs` reads both; Docker keeps 5 files of 10 MB per container.

In the web app, a screen never calls `fetch` itself:

1. A component calls a hook of `web/src/api/queries.ts` (`useMe`, `useCreateSession`, `useAnswer`...), which is TanStack Query around one call.
2. The call goes through `openapi-fetch` (`web/src/api/client.ts`), typed by `schema.d.ts`, which the API's OpenAPI schema generates. Every request carries the `X-Requested-With` header and the cookie.
3. `unwrap()` turns any failure into one `ApiError` with the HTTP status and the API's error code; status 0 means the request never reached the server. `errorKind()` picks the full-screen state a failed screen shows (offline, maintenance, 404, error), and `isRateLimited()` the "too many tries" message.

Inside the API a request passes through, in order:

1. `app/logger.py` `log_request`: gives the request an id, logs one line when it ends with the caller's address (`app/client_ip.py`), returns the id in `X-Request-ID`.
2. CORS, with origins from settings.
3. `require_csrf_header` (`app/routes/dependencies.py`), on every route: a POST, PATCH, PUT or DELETE without the `X-Requested-With` header is a 403.
4. The route's own dependencies: `CurrentUser` (401 without a valid session), `OptionalUser`, `require_flag(key)` on a flagged route (404 while the flag is off for whoever asks), and a rate limit on the routes that have one (429, see below).
5. The route in `app/routes/`: it reads the input, calls one or two functions of `app/services/`, commits, and returns a model from `app/schemas/`.
6. The service: reads and writes rows, and calls the pure functions of `app/domain/` for every decision. It takes `now` and `settings` as arguments and never commits.
7. `app/errors.py`: any error leaves as `{"error": {"code": "...", "message": "..."}}`.

### Rate limits

| Rule | Counted per | Routes | Setting (default) |
| --- | --- | --- | --- |
| `auth` | Network address | `POST /auth/guest`, `POST /auth/magic-link`, `POST /auth/magic-link/verify`, `GET /auth/google/start`, `GET /auth/google/callback` (not logout) | `rate_limit_auth` (300 in 10 minutes) |
| `sign_in_email` | Email address | `POST /auth/magic-link` | `rate_limit_sign_in_email` (5 an hour) |
| `answers` | User | `POST /sessions/{id}/answers` | `rate_limit_answers` (60 a minute) |
| `reports` | User | `POST /questions/{id}/report` | `rate_limit_reports` (10 an hour) |

- Time is cut into fixed windows from the Unix epoch (`domain/rate_limit.py`); a caller may make the limit's number of requests in a window. The next one is a 429 `rate_limited` with `Retry-After`, the seconds left in the window.
- The counts are kept in memory by each API process (`services/rate_limits.py`), one window per rule: when a new window starts, the old counts are dropped. Each gunicorn worker counts on its own, and a restart clears every count.
- The network address is `X-Real-IP`, which nginx sets, else the connection's (`app/client_ip.py`).
- The routes declare it: `dependencies=[Depends(limit_answers)]`; `enforce_rate_limit` in `routes/dependencies.py` counts and refuses.

### Authentication

- A session token is 256 random bits. The client holds it; `sessions_auth` holds its SHA-256 hash (`app/services/auth_sessions.py`).
- The web app gets it as an httpOnly, Secure, SameSite=Lax cookie (`cc_session`); a native client sends the same token as `Authorization: Bearer`. `session_token` in `app/routes/dependencies.py` reads either.
- A session lasts 90 days and is renewed, with the cookie sent again, once less than half of that is left.
- `POST /auth/guest` creates a guest: a real `users` row with `is_guest` true and a `user_settings` row.
- Signing in (`app/services/sign_in.py`) is the same for Google and for an email link. If nobody has the identity or the email, the guest in that browser becomes the account. If an account has it, the student is signed in to that account and the guest's history is merged into it (`merge_guest`), then the guest is deleted. Either way the old token is ended and a new one issued.
- An email link (`app/services/magic_links.py`) is a random token stored hashed, spent by one UPDATE that also checks the 15 minutes.
- Google (`app/providers/google.py`) is the authorization-code flow through Authlib. The `state` goes to Google and into a short-lived httpOnly cookie, and the callback compares the two.
- An account that a sign-in creates, with no guest behind it, starts in the language and timezone of the device: the web app sends them in the body of `/auth/magic-link/verify` and in the query of `/auth/google/start`, which keeps them in a second short-lived cookie for the callback. A guest who signs in keeps their own.

### What a session never sends

`POST /sessions` and `GET /sessions/{id}` return `SessionQuestion`: stem, code and options with key and text only. That model has no field for the correct key, the reasons or the explanation, and `app/services/session_views.py` reads them in one function, `answer_feedback`, which runs after the answer is recorded. Tests check both the responses and the OpenAPI schema.

### A user's data: export and deletion

- `GET /me/export` (`services/account.export_user`) returns the `users` row and, table by table, every row about the user: the tables in `EXPORTED_BY_USER_ID`, the referrals on either side, and the tutor messages of the user's threads. A table of V2 or V3 is there as an empty list. Session tokens (`sessions_auth`) and sign-in links are credentials and are left out. A test fails when a table that points at `users` is in neither the export nor the list of credentials. Settings offers it as "Baixar meus dados", a plain download.
- `DELETE /me` (`services/account.delete_user`) deletes the `users` row; every foreign key to `users` is `ON DELETE CASCADE`, which a test checks, so every other row of the user goes with it, answers included. The sign-in links sent to the address are deleted by address. The questions keep the counts and ratings the answers moved, which say nothing about who answered.

## API layout

| Module | Role |
| --- | --- |
| `app/main.py` | Builds the app: middleware, error handlers, routers under `/api/v1` |
| `app/settings.py` | Every environment value and tunable number |
| `app/enums.py` | The fixed vocabularies: statuses, modes, flag keys, plan keys |
| `app/db/` | Engine and session, `base.py` (table conventions), `models/` (every table), `migrations/` (Alembic) |
| `app/domain/` | Business rules as pure functions: no database, no HTTP, no clock. See "Where each business rule lives" |
| `app/schemas/` | The Pydantic models of requests and responses, one module per area. The OpenAPI schema comes from them |
| `app/routes/` | One module per API area: `auth`, `account`, `config`, `catalog`, `practice`, `stats`, `feedback` (reports and events), `health`. `dependencies.py` has the signed-in user, the CSRF header and feature flags |
| `app/services/` | Reading and writing rows around the domain functions: `practice`, `session_views`, `progress`, `catalog`, `stats`, `account`, `sign_in`, `auth_sessions`, `magic_links`, `users`, `flags`, `config`, `feedback`, `publishing`, `demo`, and the content ones (`seed`, `content_import`, `catalog_file`, `question_files`) |
| `app/providers/` | Outside services behind an interface with a stand-in: `email` (console, SMTP) and `google` (mock, OAuth). Billing, ads and the tutor arrive in milestone 10 |
| `app/db/rows.py` | `ensure_row`: get-or-create with a row lock, for the one-row-per-user-and-something tables |
| `app/cli.py` | Commands run by hand, make and cron: `seed`, `import-content`, `publish-subjects`, `demo-user`, `openapi` |
| `app/logger.py` | JSON or readable log lines, the request log, and the standard `logging` module routed into the same sink |
| `app/error_tracking.py` | Better Stack error tracking through the Sentry SDK, started only when `BETTER_STACK_ERRORS_DSN` is set, without personal data or request bodies |
| `gunicorn.conf.py` | The production server: Uvicorn workers, their number and timeout from settings, gunicorn's lines through `app/logger.py` |

## Web layout

`web/README.md` has the rules for working in it.

| Path | Role |
| --- | --- |
| `index.html` | The one HTML file, served for every address. The build writes the landing page into it as static HTML |
| `src/main.tsx` | Entry: loads `design/tokens.css`, then Tailwind, applies the theme |
| `src/app/` | `App` and its providers, the route table (`routes.tsx`), the navigation shell (`AppShell`), `RequireUser` (creates the guest, sends a new user to onboarding) and `Flagged` (a route behind a feature flag) |
| `src/features/` | One folder per screen: `landing`, `auth` (sign-in and the link's landing page), `onboarding`, `home`, `catalog`, `session`, `summary`, `profile`, `settings`, `legal` (the privacy policy and the terms). Rules a screen decides by are pure functions in a `rules.ts` beside it |
| `src/components/` | Shared components (`AnswerOption`, `CodeBlock`, `TopicNode`, `StreakCard`, `StateScreen` and others); `ui/` holds the primitives of `design/README.md` |
| `src/api/` | `client.ts` (the typed fetch client and `ApiError`), `queries.ts` (every API call as a TanStack Query hook), `types.ts`; `openapi.json` and `schema.d.ts` are written by `make types` and committed |
| `src/i18n/` | `pt-BR.json`, `en.json` and the setup. All interface text is here |
| `src/lib/` | Theme, language and timezone preferences, flags, the syntax highlighter, product events, the one-time hints (`hints.ts`, kept on the device), `cn()`, and `monitoring.ts`: Better Stack error tracking (through the Sentry SDK) and Plausible, built in only when their keys are set at build time |
| `src/test/` | Sample API data (`fixtures.ts`), the mock API and the render helpers of the component tests |
| `src/prerender.tsx` | Build-time entry that renders the landing page to HTML |
| `src/styles/index.css` | Tailwind entry and base rules. No token is defined here |
| `shots/` | Screenshots of the app beside the mockups (`npm run shots`) |
| `e2e/` | The Playwright test: a guest plays a whole session against the real stack (`make e2e`) |
| `eslint-rules/` | `no-hardcoded-copy`: fails the lint on interface text outside the translation files |

## Data model

Every table of V1, V2 and V3 exists since milestone 2: 36 tables, defined as SQLAlchemy models in `api/app/db/models/` and created by the Alembic migrations in `api/app/db/migrations/versions/`. V1 writes 21 of them; the rest wait, empty, for their features (see "How V1 uses the tables").

### Conventions

`api/app/db/base.py` holds them; every model inherits from its `Base`.

- Every table has a UUID `id`, `created_at` and `updated_at`. The timestamps are set in Python, are equal until the row is first updated, and have `now()` as a database default for rows inserted with plain SQL.
- Every timestamp is `TIMESTAMP WITH TIME ZONE` and holds UTC. A student's own calendar day is a `DATE` named `local_date`, worked out from `users.timezone`.
- A value from an enum in `api/app/enums.py` is stored as text in a `VARCHAR(32)`. The database does not list the allowed values, so a new one needs no migration; SQLAlchemy rejects an unknown value on write and on read.
- The database enforces keys, uniqueness and NOT NULL. Value rules such as ranges live in Python.
- A row that belongs to a user is deleted with the user (`ON DELETE CASCADE`). Subjects, topics and questions are never deleted.
- Models have no ORM relationships: queries join explicitly.
- Keys, constraints and indexes are named by one convention (`pk_`, `fk_`, `uq_`, `ix_` plus table and columns), so a migration can refer to each.

### Tables

| Module | Table | What a row is |
| --- | --- | --- |
| `identity.py` | `users` | A student or staff member; a guest is a real row. Holds email, name, locale, timezone, university, course, the subject Home shows, the referral code |
| | `auth_identities` | One way a user signs in: Google or email |
| | `sessions_auth` | A signed-in browser or device, by the hash of its token |
| | `magic_links` | A single-use sign-in link, by the hash of its token |
| | `user_settings` | Daily goal, theme, per-option reasons, notification preferences. One per user |
| | `user_subjects` | A subject the student chose |
| | `push_subscriptions` | Where to send a user's push notifications (V2) |
| `content.py` | `subjects` | A subject: slug, names, badge label, status, order |
| | `topics` | A topic of a subject |
| | `topic_edges` | A prerequisite or related link between topics; unused in V1 |
| | `questions` | A question's identity (`external_id`) and live numbers: status, rating, counts, version |
| | `question_translations` | A question's text in one language: stem, code, options with reasons (`payload`), explanation |
| | `question_reports` | A student's report about a question |
| `practice.py` | `practice_sessions` | One run of a fixed list of questions, in a mode: practice, review, exam, challenge |
| | `attempts` | One answer, with both ratings before and after it. The raw history |
| | `user_subject_ratings` | A student's rating in a subject |
| | `user_topic_mastery` | A student's correct and total answers in a topic |
| | `daily_activity` | XP, questions, finished sessions and goal met on one local day |
| | `streaks` | Current and longest streak, freezes held, the lost streak that can still be repaired |
| | `review_items` | A missed question and when it is due for review; written from V1 |
| | `lives` | Lives left and when the refill started (V2) |
| `product.py` | `feature_flags` | A V2 or V3 feature's switch: off, staff, on |
| | `events` | First-party analytics, and the record of freezes and repairs |
| `retention.py` (V2) | `league_weeks` | One week of the leagues |
| | `league_memberships` | A student's tier, league and XP in one week |
| | `achievements`, `user_achievements` | A badge, and a student unlocking it |
| | `exam_templates` | The recipe of a mock exam: duration, composition, optional track |
| | `exam_attempts` | One sitting of a mock exam; its questions are a practice session of mode exam |
| `monetization.py` (V3) | `plans` | A plan's prices and limits; mirrors `settings.plans` |
| | `subscriptions` | What a user has paid for; the only source of truth for it |
| | `usage_counters` | Questions answered and tutor messages on one local day |
| | `ad_events` | One step of an ad break or a Beat the ad challenge |
| | `tutor_threads`, `tutor_messages` | A conversation with the tutor |
| | `referrals` | One student invited by another |

### How V1 uses the tables

What each thing a student does writes. Everything happens in the request's one transaction.

| A student... | Route | Rows written |
| --- | --- | --- |
| Opens the app for the first time | `POST /auth/guest` | `users` (a guest), `user_settings`, `sessions_auth` |
| Goes through onboarding, changes a setting | `PATCH /me/settings` | `users` (language, timezone, university, course, current subject), `user_settings`, `user_subjects` |
| Starts a session | `POST /sessions` | `practice_sessions`, with its fixed list of question ids |
| Answers | `POST /sessions/{id}/answers` | `attempts`; on a first attempt, `questions` (rating and counts) and `user_subject_ratings`; `user_topic_mastery`, `daily_activity`, the session's counts; `review_items` when wrong |
| Finishes | `POST /sessions/{id}/finish` | the session's end and XP, `daily_activity`, `streaks` |
| Asks for an email link | `POST /auth/magic-link` | `magic_links` |
| Signs in | `/auth/magic-link/verify`, `/auth/google/callback` | `users` (the guest becomes the account, or is merged into it and deleted), `auth_identities`, `sessions_auth` (the old token ended, a new one) |
| Reports a question | `POST /questions/{id}/report` | `question_reports` |
| Uses the app | `POST /events` | `events` (the landing page's two events, in V1) |
| Deletes the account | `DELETE /me` | everything of the user is deleted |

Home, the profile and the catalog read `daily_activity`, `streaks`, `user_subject_ratings`, `user_topic_mastery`, `subjects` and `topics`. Questions reach students only inside a session, from `questions` and `question_translations`.

Written by commands, never by a student: `subjects`, `topics`, `questions` and `question_translations` (`import-content`, `publish-subjects`), `plans` and `feature_flags` (`seed`).

Empty in V1, for V2 and V3: `topic_edges`, `push_subscriptions`, `lives`, `league_weeks`, `league_memberships`, `achievements`, `user_achievements`, `exam_templates`, `exam_attempts`, `subscriptions`, `usage_counters`, `ad_events`, `tutor_threads`, `tutor_messages`, `referrals`. The columns of V1 tables that only those features use (`streaks.freezes`, `lost_length`, `lost_at`; `user_settings.daily_reminder`, `weekly_email`, `reminder_time`; `users.referral_code`) keep their defaults.

### Migrations and seeds

- `alembic upgrade head` creates the schema; `alembic check` fails when a model and the migrations differ, and a test runs it. Both read the database URL from settings.
- `python -m app.cli seed` writes the rows every environment needs: the four plans from `settings.plans`, every feature flag switched off, and the 20 subjects of `content/catalog.yaml` as drafts, with their topics. Running it again overwrites plans and the names of subjects and topics from their sources, and never changes a flag's state or a subject's status.

## Content

Questions are written as files and imported; `content/README.md` describes the files, the tools and the pipeline step by step.

| Piece | Where | Role |
| --- | --- | --- |
| The format | `api/app/domain/question_doc.py` | `QuestionDoc`, the one definition of a line of the bank, with every format rule; `content_hash`, which says whether a question's content changed |
| The catalog | `content/catalog.yaml`, read by `api/app/services/catalog_file.py` | Subjects and their topics; each topic has the language of its code |
| Reading files | `api/app/services/question_files.py` | Reads question files and checks them against the catalog. `load_bank` adds what the bank promises: every question passed the pipeline |
| The tools | `content/tools/` | `python -m content.tools`: validate, run-code, dedupe, strip-keys, check-blind, promote, report. They import the three modules above from `api/`, so the tools and the importer cannot disagree about a file |
| The importer | `api/app/services/content_import.py` | `python -m app.cli import-content`: creates, rewrites and retires rows of `questions` and `question_translations` |

The flow: a subagent writes `content/work/<subject>/<topic>.jsonl`; the tools validate it, run its code and look for near-duplicates; a second subagent, which sees only the stripped file, answers it blind; `promote` moves the questions that passed everything into `content/bank/`; `import-content` copies the bank into the database. A test loads the bank with `load_bank` in CI.

What the importer may change is narrow, because the database owns everything live. It writes a question's text, type, difficulty, source, hash and version. It sets the status when it creates a question (`verified` in a launch subject, `draft` elsewhere), when a question leaves the files (`retired`) and when a retired question comes back with new content. It sets the rating from the difficulty while nobody has answered the question. It never touches the counts.

The tests of `content/tools/` are in `api/tests/content_tools/`: the API is the repository's one Python project, and `make lint`, `make typecheck` and `make test` cover both.

## Where each business rule lives

Every rule is a pure function in `api/app/domain/`, with unit tests in `api/tests/domain/`, and every number it uses is a field of `api/app/settings.py`. The services call them; no route or query decides anything.

| Rule | Function | Settings | Called from |
| --- | --- | --- | --- |
| Chance of a correct answer, P | `rating.predicted_success` | `rating_guess_chance`, `rating_scale` | selection, rating |
| Both ratings after a first attempt | `rating.rate_answer`, with `user_k` and `question_k` | `user_k_early`, `user_k_early_answers`, `user_k`, `question_k_early`, `question_k_early_answers`, `question_k`, `user_rating_start` | `services/practice.answer_question` |
| A question's starting rating | `rating.question_starting_rating` | `question_rating_by_prior` | `services/content_import` |
| Which questions a session gets | `selection.select_questions` | `session_length`, `selection_target_success`, `selection_pool_size`, `selection_max_per_topic`, `selection_recent_days`, `first_session_prior_levels` | `services/practice.start_session` |
| The order of a question's options | `selection.shuffled_option_keys` | none | `services/session_views` |
| XP for an answer and for finishing | `xp.xp_for_answer`, `xp.xp_for_finishing` | `xp_correct`, `xp_harder_question_bonus`, `xp_session_finished` | `services/practice` |
| Levels | `xp.level_progress` | `xp_per_level` | `services/progress` |
| Daily goal | `daily_goal.goal_progress`, `is_goal_option` | `daily_goal_options`, `daily_goal_default` | `services/progress`, `services/account` |
| The student's own day | `local_time.local_date` | `default_timezone` | wherever a day is counted |
| Streak after a finished session | `streak.streak_after_session` | none | `services/practice.finish_session` |
| Streak as shown today: active, at risk, lost | `streak.streak_today` | none | `services/progress.streak_of` |
| Streak rebuilt from days | `streak.streak_from_days` | none | `services/sign_in.merge_guest` |
| Topic mastery | `mastery.mastery_level` | `mastery_new_below_answers`, `mastery_learning_below`, `mastery_mastered_from`, `mastery_mastered_min_answers` | `services/catalog` |
| Review schedule | `review.first_review`, `review.after_correct_review` | `review_intervals_days` | `services/practice` (a wrong answer); the rest from milestone 9 |
| Is a flag on for this user | `flags.flag_is_on` | none | `services/flags` |
| Rate limits: the window, the limit, Retry-After | `rate_limit.window_start`, `is_over_limit`, `retry_after_seconds` | `rate_limit_auth`, `rate_limit_sign_in_email`, `rate_limit_answers`, `rate_limit_reports` | `routes/dependencies.enforce_rate_limit` |
| What a user may do | `entitlements.entitlements_for` | `plans` | `services/config`; enforced from milestone 10 |
| The format of a question | `question_doc.QuestionDoc` | the `question_*` limits | the content tools and the importer |

What one answer writes, all in one transaction (`services/practice.answer_question`): the `attempts` row with both ratings before and after; the question's rating and counts and the student's subject rating, on a first attempt only; the topic's `user_topic_mastery`; the day's `daily_activity`; the session's counts; and a `review_items` row when the answer is wrong. Finishing adds the finishing XP, the day's finished session and the `streaks` row. The session row is locked for the length of the request, so a repeated or simultaneous answer is counted once.

## Feature flags

A flag is a row of `feature_flags` with a state: `off`, `staff` or `on`. Every key is in `FlagKey` (`app/enums.py`); seeding creates each one off, and a flag without a row is off.

- **Routes.** A flagged route has `dependencies=[Depends(require_flag(FlagKey.X))]`. While the flag is off for whoever asks, it answers the same 404 as a route that does not exist. `staff` opens it to users with the staff role.
- **The web app.** `GET /config` returns each flag as a boolean for the user who asks, with the plans and the user's entitlements. It also carries `rules`, the settings the app quotes when it explains XP, the rating and topic mastery to a student.
- **V1 has no flagged route.** The mechanism is tested with a route the test adds; milestone 9 is its first real use.

Switching a flag has no command yet (the admin console is milestone 9): `UPDATE feature_flags SET state = 'on' WHERE key = '<key>';`.

## Tests

| Kind | Where | Runs against | Command |
| --- | --- | --- | --- |
| Business rules | `api/tests/domain/` | Pure functions, no database | `make test-api` |
| API | `api/tests/test_*_api.py` and the others | A real Postgres 16 that testcontainers starts; each test in one transaction, rolled back | `make test-api` |
| Content | `api/tests/test_content_bank.py`, `api/tests/content_tools/` | Every line of `content/bank/`; the tools on fixed samples | `make test-api` |
| Components | `web/src/**/*.test.tsx` | The whole app in jsdom against a mock API (`web/src/test/`) | `make test-web` |
| End to end | `web/e2e/` | Chromium against the docker compose stack, seeded by `make seed`, in Portuguese at 360 px and in English at 1280 px | `make e2e` |

CI (`.github/workflows/ci.yaml`) runs lint, type checks and the first four on every push, and builds the web app. A third job does what a new developer does, `make up` and `make seed`, and then `make e2e`.
