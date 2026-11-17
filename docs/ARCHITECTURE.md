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
| `app/enums.py` | The fixed vocabularies: statuses, modes, flag keys, plan keys |
| `app/db/` | Engine and session, `base.py` (table conventions), `models/` (every table), `migrations/` (Alembic) |
| `app/domain/` | Business rules as pure functions (milestone 5 onward) |
| `app/routes/` | One module per API area |
| `app/services/` | Orchestration between routes, database and domain |
| `app/providers/` | Email, billing, ads, tutor: interface, mock, real adapter |
| `app/cli.py` | Commands run by hand, make and cron: `python -m app.cli seed` so far |

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

Every table of V1, V2 and V3 exists since milestone 2: 36 tables, defined as SQLAlchemy models in `api/app/db/models/` and created by the Alembic migrations in `api/app/db/migrations/versions/`. Milestone 7 completes this section with how the tables are used.

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

### Migrations and seeds

- `alembic upgrade head` creates the schema; `alembic check` fails when a model and the migrations differ, and a test runs it. Both read the database URL from settings.
- `python -m app.cli seed` writes the rows every environment needs: the four plans from `settings.plans`, every feature flag switched off, and the 20 subjects of `content/catalog.yaml` as drafts. Running it again overwrites plans and subject names from their sources and never changes a flag's state or a subject's status.

## Where each business rule lives

To be written from milestone 5: one row per rule, naming its function in `app/domain/` and its settings.

## Feature flags

To be written in milestone 5.
