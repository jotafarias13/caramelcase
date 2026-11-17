# Decisions

Every choice made where `docs/initial-spec.md` was silent, every conflict between the spec and the design, and every change agreed with the owner. Read it in full before any work, together with the spec and `docs/PLAN.md`.

Precedence: the spec wins on behaviour, the design wins on looks, and the first section below wins over both.

## Changes to the spec agreed with the owner

These override `docs/initial-spec.md` where they differ.

- **The design is finished.** `design/` is the UI handoff. There are no placeholder tokens and no later design pass. Use `design/tokens.css`, `design/tailwind.theme.js`, `design/assets/` and `design/copy.md` from milestone 1, and build each screen to match its file in `design/screens/`.
- **Precedence.** Where design and spec disagree, the spec wins on behaviour and the design wins on looks. Record each conflict in this file.
- **Tooling.** uv manages Python, with ruff and pytest.
- **Code language in questions.** C for Introdução à Programação (the syllabus covers pointers, structs, enums and unions). In Estruturas de Dados, C for the pointer and dynamic-allocation topics and Python elsewhere. SQL for Banco de Dados.
- **Estruturas de Dados scope.** The syllabus lists EDB I and EDB II; both merge into the single launch subject, about 16 topics.
- **nginx and certbot run as containers**, following the owner's examples in `../kai-app` and `../kai-api`, not on the host. Add the `/api` proxy, which neither example has.
- **Onboarding step 2.** University and course are stored as two optional text fields on `users`, included in export and delete.
- **Topic rows on Home.** Sessions stay per subject in V1. Tapping a topic starts a subject session.
- **Commits.** One commit per milestone, straight to `main`, message `feat:` / `fix:` / `chore:` plus a short imperative description. Push only when the owner asks.
- **Content pilot.** One topic per launch subject goes through the whole pipeline and the owner reviews it before the rest is generated.

## Defaults chosen where spec and design disagree or are silent

The owner saw these and did not object.

- Mockup sample content is not product behaviour: the landing page says five subjects and 8 to 12 questions per session; ship three subjects and 10 questions. XP, tutor allowance and similar numbers follow the spec.
- Difficulty badge: the design has three levels, the spec five. Prior 1–2 shows as Fácil, 3 as Médio, 4–5 as Difícil.
- Topic node states map from mastery: new is "available", learning and practiced are "in progress" with the accuracy percentage, mastered is "mastered". No locked topics in V1, since `topic_edges` is unused.
- Levels: the design shows them, the spec has none. 500 XP per level, as a setting.
- The "Lembrete diário" toggle in Settings is hidden until the `reminders` flag is on.
- Offline: the server still grades. The app keeps the selected option on the device and submits it on reconnect.
- The landing page's try-it question is a static sample embedded in the page; "Continuar praticando" creates the guest and goes to `/start`.
- Pix is offered for annual and semester passes only; the mockup shows it on a monthly plan.
- The streak counts a day with one finished session (spec), though the mockup caption mentions the goal.
- Navigation tabs follow flags: Início, Perfil, Ajustes in V1; Revisão appears with `review_queue`, Ligas with `leagues`, and Ajustes moves under Perfil once either is on.
- `/subjects` has no V1 mockup. Build it from the V2 catalog components without add, remove or course filter; those arrive in milestone 9.
- Tables the spec omits but its features need: lives, referrals, push subscriptions, a student's chosen subjects, and streak-repair state (the lost streak's length and time).
- Local `make seed` publishes the three launch subjects so a developer can play. In production, publishing is an explicit CLI command the owner runs after the hand check.
- Lives, leagues and push-notification rules come from "Decisions made by the designer" in `design/README.md`, as settings.
- Screens listed under "Not designed" in `design/README.md` are built from the existing components when a feature needs them.
- Stack, where the reference repos differ from the spec: the spec wins on Python 3.12, Alembic, opaque session tokens in Postgres and JSON logs. Taken from the reference repos: npm, Tailwind v4 (loading `design/tailwind.theme.js` unchanged through `@config`; fall back to Tailwind 3.4 if the theme does not carry over), gunicorn with Uvicorn workers, loguru with a request-id middleware, and manual build and deploy workflows. mypy is the type checker.
- `syllabus-v1.txt` stays out of the repo through `.git/info/exclude`.

## Milestone 1 · Scaffold

### Design and frontend

- **Tokens are read in place, not copied.** The spec's layout lists `web/src/styles/tokens.css`. That file does not exist: `web/src/main.tsx` imports `design/tokens.css` through the `@design` alias, and `web/tailwind.config.js` imports `design/tailwind.theme.js`. One copy cannot drift from the handoff. `web/src/styles/index.css` holds only Tailwind's entry and base rules that point at the tokens.
- **Tailwind v4 holds; no fallback to 3.4.** The theme file is Tailwind 3 syntax, loaded through `@config`. The built CSS of the sample page was checked: colours, font sizes with their line height and weight, radii, hard shadows, spacing names, durations, the `md` breakpoint at 768 px and the `dark:` variant on `[data-theme="dark"]` come out as the theme defines them. Theme keys the sample page does not use yet (outline, max-width, easing) are unchecked.
- **Token names that collide with Tailwind's own variables resolve to the design's values.** `tokens.css` and Tailwind v4 both define `--font-sans`, `--font-mono`, `--radius-xs` to `--radius-xl`, `--ease-in` and `--ease-out`. Tailwind's sit in a cascade layer and the tokens do not, so the tokens win, and `rounded-md` means the design's 10 px.
- **shadcn/ui is set up by hand.** `components.json`, `cn()`, class-variance-authority and Radix are in place, but `shadcn init` was not run because it writes its own colour palette into the CSS. Each component is written to its entry in `design/README.md`; `tokens.css` already carries the shadcn variable aliases.
- **`cn()` knows the design's scale names.** tailwind-merge reads an unknown `text-title` as a colour and drops it next to `text-fg`. `web/src/lib/utils.ts` lists the design's font-size, radius, shadow, spacing and easing names, and a test compares the lists with `design/tailwind.theme.js`.
- **The app always sets `data-theme`.** `tokens.css` follows the system when `<html>` has no attribute. The app resolves "system" itself and always writes `dark` or `light`, so the `dark:` variant and theme-specific assets (the wordmark) have one thing to test. The choice is kept in `localStorage` until user settings exist (milestone 5).
- **`web/public/favicon.svg` is a byte-for-byte copy of `design/assets/favicon.svg`**, the one design file that is copied: `index.html` needs a static URL for it. The icon export in milestone 6 supersedes it.
- **The sample page is temporary.** `web/src/features/sample/SamplePage.tsx` proves tokens, theme, components and the `/api` proxy. Its Portuguese copy is hardcoded; the landing page replaces it in milestone 6, when copy moves to the i18n files.
- **Frontend libraries arrive with their first use.** React Router, TanStack Query and react-i18next are not installed yet.
- **Tool versions.** Vite 7, TypeScript 5.9 and Vitest 4, the lines the owner's `kai-app` runs on, rather than the newest majors: typescript-eslint does not accept TypeScript 7 yet. ESLint is 10, because 9 is no longer supported. ESLint and Prettier use `kai-app`'s rules.
- **Open, not decided: web fonts.** `tokens.css` loads Geist and JetBrains Mono from Google Fonts, and it is consumed unchanged, so every visit makes a request to Google and the fonts are missing offline. Self-hosting them is a question for the PWA work in milestone 6.

### API

- **Settings come from the environment only.** `api/app/settings.py` reads no `.env` file; docker compose passes the values. Every field, tunables included, can be overridden by an environment variable of the same name.
- **The tunables are in `settings.py` from now on**, with the spec's numbers, including those V2 and V3 use (lives, leagues, streak freeze and repair, ad breaks). Numbers the spec does not give (rate limits, session lifetime, the tutor's token cap, the default daily goal) are added by the milestone that needs them, with an entry here.
- **Review intervals are stored as the list 1, 3, 7, 18, 45 days**, not as "multiply by 2.5". No single rounding rule turns ×2.5 into that list (3 × 2.5 = 7.5 must round down, 7 × 2.5 = 17.5 up). A correct review at the last step takes the item out of the queue, which matches "leave once the interval passes 60 days" (45 × 2.5 > 60).
- **`LOG_JSON` defaults to true**, so a production container that sets nothing logs JSON. Local compose and the tests turn it off for readable lines. Log timestamps are UTC.
- **The error shape is in place for every response**: `AppError` for routes, and handlers that convert unknown routes, invalid bodies and unexpected exceptions. The code of a framework error is its HTTP status name in snake case (`not_found`); an invalid body is `validation_error` with the first failing field in the message.
- **`GET /api/v1/health` answers 503 `database_unavailable`** when `SELECT 1` fails.
- **API docs are served at `/api/v1/docs`**, the schema at `/api/v1/openapi.json`, so everything sits behind the one `/api` proxy.
- **Lint and types.** ruff with `kai-api`'s rule set and 79-column lines, plus `UP` and `B`; mypy in strict mode with the pydantic plugin.
- **`api/app/cli.py` is not created yet.** It arrives with its first command in milestone 2.

### Tests, tooling, CI

- **API tests use a real Postgres 16 started by testcontainers**, once per run and only when a test asks for the `database` fixture, so unit tests need no Docker. `TEST_DATABASE_URL` points the tests at a server that is already running. This is `kai-api`'s approach; the rolled-back transaction per test arrives with the schema in milestone 2.
- **Local compose uses stock images and no development Dockerfiles.** The API runs in the uv image and the web app in the Node image, each with the source bind-mounted and its dependencies installed at start into a named volume, apart from the host's `.venv` and `node_modules`. Compose needs no `.env`: every value has a default.
- **`make lint`, `make typecheck` and `make test` run on the host** with uv and npm. CI calls the same targets, split into an API job and a web job, and also builds the web app.
- **CI runs on every push to any branch.** It could not be observed yet: nothing has been pushed.

## Milestone 2 · Schema

### Conventions of every table

- **An enum is stored as text in a `VARCHAR(32)`, with no database enum type and no CHECK.** The values are the `StrEnum` classes in `api/app/enums.py`; SQLAlchemy rejects an unknown value on write and on read. Adding a value needs no migration, and the models cannot drift from the database over it. The cost: a value written with plain SQL is not checked until the app reads it.
- **Keys that are data stay plain strings**: feature-flag keys, plan keys, league tiers, event names, the billing provider and a question's source. A row whose key the code no longer knows still loads, so removing a flag from the code cannot break `GET /config`.
- **The database enforces keys, uniqueness and NOT NULL; value rules live in Python.** There are no CHECK constraints: Alembic cannot see them change, so each one would be a place where models and migrations drift unnoticed.
- **`created_at` and `updated_at` are set in Python**, with `now()` as the database default for rows inserted with plain SQL. Each test runs in one transaction, where Postgres freezes `now()`, so database-side timestamps would all be equal in tests. `updated_at` equals `created_at` until the first update. An UPDATE written in plain SQL does not move `updated_at`: there is no trigger.
- **Business defaults are Python defaults on the model**, never database defaults, so no migration carries a business value. `user_settings.daily_goal` has no default at all: milestone 5 adds the number to settings.
- **A user's rows are deleted with the user** (`ON DELETE CASCADE`), attempts and question reports included; a question's own counts and rating stay. Milestone 7 builds `DELETE /me` on this and may choose to keep anonymous attempts instead.
- **No ORM relationships.** Queries join explicitly, which also avoids lazy loading under async.
- **Models are split by area** in `api/app/db/models/`: identity, content, practice, product (flags, events), retention (V2) and monetization (V3).

### Columns and tables beyond the spec's key columns

- **`subjects.short_pt` and `short_en`**: the badge the design puts next to a subject ("ed/", "ds/"). The design gives five; the labels of the other subjects in `content/catalog.yaml` are mine and are the owner's to change.
- **`users.current_subject_id`**: the subject Home shows. Onboarding step 3 picks one subject, and a switch on Home must survive a reload and a change of device. `user_subjects` is the list of chosen subjects that the V2 catalog adds to and removes from.
- **`users.referral_code`**: the code in the invite link. `referrals` records who invited whom, when the invited student finished a first session and when the reward was given.
- **Notification preferences are three columns** on `user_settings`: `daily_reminder`, `weekly_email` and `reminder_time` (local time; null means a default hour). Both switches default to off: opting in is the safe default under LGPD, and milestone 9 decides how the student is asked.
- **`question_reports.locale`**: the language the student was reading, without which a "typo" report points at two texts.
- **`attempts` stores both ratings after the answer as well as before.** The session summary shows a rating change that must read the same later, and K changes with the number of answers, so it cannot be recomputed. Before and after are equal when the attempt moved no rating.
- **An attempt is unique per session and question**, so a repeated request (the offline flow resubmits) cannot count twice.
- **`practice_sessions.subject_id` is nullable**: a review or an exam-track session can mix subjects. V1 sessions always have one.
- **`daily_activity.sessions_finished`**: the streak counts a day with one finished session, which the spec's `questions` and `goal_met` cannot tell.
- **Streak-repair state is two columns on `streaks`** (`lost_length`, `lost_at`), not a table: a user has at most one lost streak to repair.
- **`events.occurred_at`, and `events.user_id` nullable.** Events arrive in batches, so the time of arrival loses their order; and the landing page can send events before the visitor has a guest account.
- **Leagues:** `league_weeks` is one row per week. `league_memberships` holds the student's tier and `cohort` (which league of that tier, since a tier is split into leagues of ten), the week's XP, and `final_rank` and `outcome` once the week closes. A student has one membership per week.
- **`user_achievements.seen_at`**: the design marks an unseen badge "Nova!".
- **Mock exams:** `exam_templates` has a slug, names and an optional subject besides the spec's track, duration and composition. `exam_attempts` points at a practice session of mode `exam`, which holds the questions and answers, and adds the score and the results by topic.
- **`plans.price_semester_brl`**, for the semester pass the spec's billing section sells by Pix. The yearly and semester prices are null until the owner sets them.
- **`subscriptions` is unique per provider and provider reference**, so a repeated webhook finds and updates its own row. `plan_key` is a foreign key to `plans.key`.
- **`tutor_threads.topic_id`**: the design opens the tutor from a topic as well as from a question.
- **The four extra tables** agreed in milestone 1: `lives` (lives left, when the refill started), `referrals`, `push_subscriptions` (platform, endpoint or device token, Web Push keys) and `user_subjects`.
- **Left for the milestone that needs them:** whether a magic link remembers the guest who asked for it (5), which subjects belong to which course for the catalog's filter (9), and the name and date of an exam track (10).

### Migrations

- **One migration, `0001`, creates all 36 tables.** It was autogenerated from the models and then read and tidied. Enum columns appear in it as `sa.String(32)`; `env.py` writes them that way in future migrations too.
- **Migration files may be 120 columns wide** (`versions/ruff.toml`), so a table reads one column per line. The rest of the code stays at 79.
- **The drift test is `alembic check`**, run by pytest against the migrated test database. A second test removes a column and expects the check to fail, so a broken check cannot pass silently.
- **Tests run Alembic and the CLI as separate processes**, the way a deploy does, and build the test database with `alembic upgrade head`. Tests that migrate or commit for real get a scratch database of their own, created and dropped on the same server.
- **The per-test rollback from `kai-api` is in place**: a test's `session` and each request's session share one transaction that is never committed.
- **`make migrate`, `make seed` and `make migration` run inside the `api` container**, against the docker compose database, unlike the checks, which run on the host. They need no `DATABASE_URL` on the host and follow whatever ports `.env` sets.

### Seeds and the catalog

- **`python -m app.cli seed`** is the first CLI command. `make seed` runs the migrations and then it; milestone 5 extends the target with content import, publishing and the demo user.
- **Plans live in `settings.plans` and the `plans` table mirrors them.** The spec puts plan limits among the tunables of the settings module and also asks for a table. Seeding overwrites prices and limits from settings on every run, so a plan is changed in settings, never in the table.
- **Placeholder limits**, from the spec's plan table: `sessions_per_day` (3 on free, null for no limit), `ads`, `tutor_messages_per_day` (0, 0, 30, 200), `exam_mode`, `exam_tracks`.
- **Seeding never switches a flag and never changes a subject's status.** It creates missing flags as off and missing subjects as draft. A subject or plan that left its source is kept, not deleted.
- **`content/catalog.yaml` holds the 20 subjects in the spec's order**; the position in the file is the sort order. Slugs are the Portuguese names in lower-case ASCII (`estruturas-de-dados`), matching the spec's sample question id. `launch: true` marks the three launch subjects, and `typical_year` is kept in the file only.
- **The API finds `content/` through the `CONTENT_DIR` setting**, which defaults to the repository's directory; docker compose mounts it read-only at `/content`.
