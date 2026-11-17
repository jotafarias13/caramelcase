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

## Milestone 3 · Content tooling

### The question format

- **`QuestionDoc` is in `api/app/domain/question_doc.py`, and the tools import it from there.** The API is the repository's one Python project; `content/tools/` is a package that runs in the API's environment and puts `api/` on its import path (three lines in `content/tools/__init__.py`). The other direction, the API importing from `content/`, would put the tools into the production image.
- **The spec's sample line is abbreviated, and as printed it is not a valid question**: its English text is `"..."` with an empty list of options, which breaks the spec's own rule of four options with reasons in both languages. The test validates the sample with the English written out (`api/tests/support/questions.py`).
- **`code_check` is a new field: `output`, `runs` or `skip`**, required when a question has code. The spec says to run code "with a deterministic output" and compare it "against the key", but nothing in its format says which questions those are. Guessing from the options would miss the case that matters: a wrong key whose real output is none of the options.
- **`verification.blind_agrees` is false with a null `blind_key`** when the blind solver found no option, or more than one, that it could defend. Null in both means not solved yet.
- **The file's `version` is where `questions.version` starts.** The spec has a `version` in the file and also says a changed hash bumps the version. The importer owns the number after the first import; nobody edits it in the files.
- **`content_hash` covers the whole line except `version` and `verification`**, so recording a blind solve or a hand check is not a change of content. Changing `difficulty_prior` or `source` is.
- **Limits.** The spec gives 160 characters for a reason and 15 lines of code. Mine, sized to keep a question on one phone screen: 400 characters for a stem, 140 for an option, 500 for an explanation, 80 for a line of code. All six are settings, like every other number, so a deployment that overrides one changes what a valid line is.
- **Rules the format enforces beyond the spec's list:** option keys are exactly a, b, c, d in that order; no two options of a question have the same text, ignoring case; an option cannot contain "todas as anteriores", "nenhuma das anteriores", "all of the above", "none of the above" or their variants; code is the same string in both languages, has no tab and no empty first or last line; the id is `<subject>.<topic>.<four digits>` and fits `questions.external_id`.
- **Only `mcq` is a valid type for now.** Milestone 9 extends `QuestionDoc` with the V2 types.
- **Text is plain text.** Nothing says how a stem or an option is rendered, so the prompts forbid Markdown. Milestone 6 may change that for inline code.
- **Spec against design: code has no comments.** The mockup `v1-flow-code-mobile.html` shows code with a Portuguese docstring and comments. The spec says code is identical across languages, and a comment cannot be translated, so `prompts/generate.md` asks for code without comments and with Portuguese identifiers without accents, as in the mockup.
- **The same mockup asks what a function returns without calling it.** That style is valid with `code_check: runs`, which checks that the code runs but not the answer. The prompt prefers a program that prints one line, with `output`, because then the key is checked by execution.

### The catalog

- **50 topics: 13 in Introdução à Programação, 19 in Estruturas de Dados, 18 in Banco de Dados**, about 22 to 31 questions each at 400 per subject. Syllabus items that hold several things are split (variables and operators; conditionals and loops; arrays, matrices and strings; structs, and enums with unions; SQL into DDL, DML, queries, joins, aggregation and subqueries).
- **Estruturas de Dados has 19 topics, not the "about 16" agreed.** EDB I and EDB II merged leave 19 sections that a student would name separately; merging further would join things like B-trees with balanced binary trees, or hashing with search. Three topics cover complexity (counting steps and cases, asymptotic notation, recursion and recurrences), since both syllabi give it the most space.
- **C in Estruturas de Dados is two topics**: `ponteiros-e-alocacao-dinamica` and `listas-encadeadas`. Every other topic is Python. Every Banco de Dados topic is SQL, including the conceptual ones, where most questions have no code.
- **A topic has `covers`**, a sentence of what it includes, written from the syllabus. It tells a question writer where the topic ends. `covers` and `code_language` stay in the file; the `topics` table is unchanged.
- **Seeding writes the topics too**, and a topic that leaves the catalog stays in the database.

### The tools

- **One command line, `python -m content.tools <command>`**, run from the repository root with `uv run --project api`. Exit code 0 means every question passed, 1 means some failed, 2 means the tool could not work.
- **Two tools beyond the plan's five: `check-blind` and `promote`.** Without the first, someone edits `blind_key` into 400 lines by hand; without the second, someone decides by hand which lines go to the bank. Both are places where a disagreement could be waved through.
- **Questions in the pipeline live in `content/work/`, which is not committed.** `content/bank/` holds only questions that passed everything, so the content test also requires `blind_agrees` true and, where code is run, `code_ran` true. Content generation in the background can never break `make test`.
- **`content/pipeline-log.jsonl` is committed.** A tool run with `--log` appends one line per question file: the step, how many questions it checked and the ids that failed. The report's failure rate is failed checks over checks, so a repaired question counts once per check. Without `--log` nothing is recorded: that is for trying things.
- **`run-code` runs everything more than once** and fails code whose output changes: that is the check for "deterministic", and it catches random numbers, clocks, printed addresses and the order of a Python set of strings. Twice at first; five times, each run with its own hash seed, since milestone 4 (below).
- **C is compiled as C11 with `-Wall -Werror` and the address and undefined-behaviour sanitizers.** A read out of bounds or a use after `free` would otherwise print an arbitrary value and pass. Leak detection is off, because it exists on Linux only and a question must pass or fail the same way on every machine. Both checked: clang on macOS and gcc 13 on Linux.
- **SQL runs on SQLite**, in memory, with foreign keys enforced, through Python's `sqlite3`. A row prints as its columns joined by `|`, NULL as `NULL`. A question about a feature SQLite lacks uses `skip`.
- **Python runs in the tools' own interpreter (3.12)** with `-I`; with `-s -P` since milestone 4 (below).
- **Each run has an empty temporary directory, no input, nothing of the user's environment but `PATH` and `TMPDIR`, a timeout of 10 seconds and 100 kB of output.** It is not a sandbox: generated code runs with the user's rights. The tests in CI run fixed snippets only; nothing in CI executes the bank's code.
- **Output is compared ignoring whitespace around it and at the end of each line.**
- **`dedupe` compares the Portuguese stem and the code.** Many questions share a stem such as "O que este programa imprime?", so two questions with code are duplicates only when the code is nearly the same too. Similarity is `difflib`'s ratio, at 0.85, a setting; stems are compared without case, accents or punctuation. The later question of a pair is the one flagged. Code has its own threshold, 0.92, since milestone 4 (below).
- **The blind solver sees both languages and answers once**, by reasoning, without running code or opening any other file. It answers null when the two languages differ in meaning.
- **The report adds one number to what the spec asks**: the share of questions whose correct option is the longest of the four, which should be near 25%. Since milestone 4 it is counted over the questions that have a longest option (below).

### The importer

- **A new question is `verified` in a launch subject and `draft` in any other**, read from `launch` in the catalog. That is the plan's rule for milestones 4 and 11 without an option someone could get wrong.
- **The importer sets a status in three cases only**: creating a question, retiring one that left the files, and bringing back a retired question whose content changed, which starts over as if created. A published question whose text changes stays published.
- **A retired question that is in the files unchanged stays retired** and is listed in the output. It was retired on purpose, or its file went missing for one import; the importer cannot tell which. The runbook has the SQL for the second case.
- **The rating follows a changed `difficulty_prior` only while nobody has answered the question.**
- **All or nothing**: one problem anywhere in the bank and nothing is imported. An empty bank is a problem, since it would retire everything. `--dry-run` shows the counts and rolls back.
- **`import-content` writes the catalog's subjects and topics itself**, so it does not depend on `seed` having run.
- **An id is never reused.** Nothing enforces it: the files cannot know which ids the database has seen. `content/README.md` and the runbook say so.

### Tests and tooling

- **The tools' tests are in `api/tests/content_tools/`**, and `make lint`, `make typecheck` and `make test` cover `content/tools/` with the API's rules (`content/ruff.toml` extends the API's; pytest gets the repository root on its path; mypy lists the directory).
- **The run-code tests need a C compiler as `cc`** and fail without one, rather than skip. GitHub's Ubuntu runners have gcc. The tool tests were run on Ubuntu's gcc 13 in a container, but CI itself is still unobserved: nothing has been pushed.
- **Typer options use `Annotated`**, in the tools and in `app/cli.py`: the default-value style fails ruff's B008 for a `Path`.

## Milestone 4 · Launch content

### The pilot

- **Pilot topics: `ponteiros`, `filas-e-deques` and `sql-juncoes`**, one per code language, so that the C, Python and SQL runners each met real questions. `pilhas` was left out on purpose: the example line of `prompts/generate.md` is a `pilhas` question, and a pilot on the prompt's own example would say little about the other 49 topics.
- **32, 22 and 24 questions**: each subject's 400 over its number of topics (31, 21 and 22), plus a small margin for drops. The pilot's questions count toward the 400, and the fan-out keeps these sizes per topic unless the owner changes them: 416, 418 and 432 questions before drops.
- **All 78 passed every step in the first round.** The repair round and the drop path have therefore not run on real questions; their tools are covered by unit tests only.
- **The blind solver was tested with a planted file**, because a clean sweep says little about a checker. Six pilot questions were mixed with six flawed ones: two right options (twice), no right option, Portuguese and English asking different things, output that depends on the order of a set, and undefined behaviour. A fresh solver gave the six sound questions their keys and answered `null` on the six flawed ones, each with the right reason. The file is not kept.
- **During a blind solve, no file with the keys can be opened**: `chmod 000` on the work file, and on whatever script the generator left in a scratch directory, until the answers are written. The solver's task message also says that the stripped file and the prompt are the only files it opens, the reading `CLAUDE.md` asks for before other work included: `CLAUDE.md`'s own rule, that a blind solver has seen only the stripped file, wins. `content/README.md` has both steps.
- **Milestone 4 is committed once per run**, not once for the milestone. `content/README.md` asks for `bank/`, the log and the report to be committed together after each run, and the content is generated in the background while later milestones are committed. The pilot is the first run.

### What the pilot changed in the tools

- **`run-code` runs code five times, each run with its own fixed hash seed** (`code_run_count`; run n has `PYTHONHASHSEED=n`). Two runs with random seeds printed a set of four strings in the same order 9 times in 200. That let such code pass, and it made a test of milestone 3 fail about one run in twenty on `main`. With a set of two strings it was every second time. Fixed seeds also make the check repeatable: a question passes or fails the same way on every run and machine. Python now runs with `-s -P`, because `-I` ignores the seed; the environment of a run was already empty. What is left: a set of two strings keeps its order under all five seeds for about 1 pair of strings in 16, and there the prompt's rule and the blind solver are the guard.
- **`dedupe` has a second threshold for code, 0.92** (`dedupe_code_similarity`); stems stay at 0.85. Short programs of one language share their frame: the include and `main` of C, the `CREATE TABLE` of SQL. In the pilot, unrelated C programs were as similar as 0.88, ten pairs in the `ponteiros` file alone were above 0.80, and the generator renamed variables in one program only to get under 0.85. A program with one number changed is at 0.98 or above and is still caught. With 13 C topics in one subject, the old number would have flagged sound questions in every run.
- **"Key is longest" in the report counts only the questions that have a longest option.** Two thirds of the pilot's questions have no single longest option, mostly because their options are numbers, which put the old figure at 5% and made its "near 25%" meaningless. Counted over the 25 questions with a longest option it is 16%.

### What the pilot changed in the prompt

`prompts/generate.md` now says what the three generators had to work out alone:

- the level split is as near to 25, 50 and 25% as the number allows, since 22 questions cannot meet it exactly;
- the file is built by a short script with `json.dumps`, kept outside the repository: all three did that to escape the code correctly;
- `strip-keys` gives the student's view for the self-solve;
- the English text names identifiers as the code does, and the code prints only values that read the same in both languages;
- code with undefined behaviour is asked as "which statement is correct", with `skip`, never as "what does it print", which the blind solver's rules fail;
- in SQL, a stem whose answer has more than one column says how the columns are separated, and an empty result cannot be the answer of an `output` question.

### Decided by the owner after the pilot

The owner approved the pilot on 2026-11-17 and settled what it had left open.

- **The fan-out keeps the pilot's sizes**: 32, 22 and 24 questions per topic.
- **A SQL query that returns several rows is asked through `SELECT COUNT(*)`.** `output` compares what the code prints with one option, and a join returns a table. The pilot's generator used COUNT(*) in 12 of its 17 code questions, with a sentence in the stem saying what it counts, although COUNT belongs to a later topic. Every key is checked by execution that way. The alternative, a fourth `code_check` that compares the number of rows, was not built. `prompts/generate.md` now states the convention.
- **Topological sort stays in `filas-e-deques`** (3 of 22 questions): the syllabus lists it among the uses of a queue, though it needs the vocabulary of directed graphs, which no topic of the subject teaches.
- **Content subagents keep reading the spec and the plan first**, as `CLAUDE.md` asks of any work: about 45 kB, some 5% of a generator's work. The owner keeps the line as it is. The blind solver stays the one exception, under `CLAUDE.md`'s own rule.
- **Milestone 5 runs in a session of its own**, started by the owner, not in the main session beside the content run as the plan first had it.

### Open, not decided

- **Overlap between neighbouring topics.** A generator reads the stems of its own topic in the bank, and `dedupe` compares text, not concepts. `ponteiros` used arrays in eight questions, which `vetores` may ask again in other words. Unknown until neighbouring topics exist.
- **No tool checks the level split or the balance of keys within a file.** The generators counted both with their own scripts and met them (each key correct 8, 8, 8, 8 times; 6, 6, 5, 5; 6, 6, 6, 6). The report shows the levels after the fact.

### The content run after the pilot

- **The run paused after 16 topics** (412 questions): it used up the owner's 5-hour usage limit, which cut six generators off in the middle of their topics; they went on after the limit reset. A topic costs about 260k tokens, some 200k for the generator and 57k for the blind solver. The other 34 topics wait for the owner's word.
- **Subagents run on Opus 5.5 at high effort from here on**, by the owner's decision, to spare the usage limit. The first 16 topics were written on Fable 5.2. Opus did the blind solves of the last two (`modelo-relacional` and `operadores-e-expressoes`) and agreed with every key. The planted-flaw test of the blind solver has not been repeated on Opus.
- **One orchestrator agent per subject runs the remaining topics**, not the main session. Run from the main session, every topic put two reports and two notifications into the main conversation, which is read again at each of them. The orchestrator's brief and the driver it calls are in `content/work/fanout/`, outside git; if more content is written in milestone 11, they are worth moving into `content/tools/` with tests.
- **All 412 questions passed every step in the first round.** The repair round and the drop path are still untested on real questions.
- **Relational algebra is written in plain text with brackets**: `σ[cond](R)`, `π[attrs](R)`, `ρ[X](R)` and `R ⋈[cond] S`, with the operators ∪ ∩ − × ⋈ ÷.
- **Options that differ only in case carry a label.** `validate` compares the texts of a question's options without case, so `O(g(n))` and `o(g(n))` count as one text. In `notacoes-assintoticas` such options say "com O maiúsculo" or "little-omega". The rule stays as it is.

