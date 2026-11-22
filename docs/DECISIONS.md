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
- **nginx and certbot run as containers**, following the owner's two reference projects (a web app and an API), not on the host. Add the `/api` proxy, which neither example has.
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
- **Tool versions.** Vite 7, TypeScript 5.9 and Vitest 4, the lines the owner's reference web app runs on, rather than the newest majors: typescript-eslint does not accept TypeScript 7 yet. ESLint is 10, because 9 is no longer supported. ESLint and Prettier use the reference web app's rules.
- **Open, not decided: web fonts.** `tokens.css` loads Geist and JetBrains Mono from Google Fonts, and it is consumed unchanged, so every visit makes a request to Google and the fonts are missing offline. Self-hosting them is a question for the PWA work in milestone 6.

### API

- **Settings come from the environment only.** `api/app/settings.py` reads no `.env` file; docker compose passes the values. Every field, tunables included, can be overridden by an environment variable of the same name.
- **The tunables are in `settings.py` from now on**, with the spec's numbers, including those V2 and V3 use (lives, leagues, streak freeze and repair, ad breaks). Numbers the spec does not give (rate limits, session lifetime, the tutor's token cap, the default daily goal) are added by the milestone that needs them, with an entry here.
- **Review intervals are stored as the list 1, 3, 7, 18, 45 days**, not as "multiply by 2.5". No single rounding rule turns ×2.5 into that list (3 × 2.5 = 7.5 must round down, 7 × 2.5 = 17.5 up). A correct review at the last step takes the item out of the queue, which matches "leave once the interval passes 60 days" (45 × 2.5 > 60).
- **`LOG_JSON` defaults to true**, so a production container that sets nothing logs JSON. Local compose and the tests turn it off for readable lines. Log timestamps are UTC.
- **The error shape is in place for every response**: `AppError` for routes, and handlers that convert unknown routes, invalid bodies and unexpected exceptions. The code of a framework error is its HTTP status name in snake case (`not_found`); an invalid body is `validation_error` with the first failing field in the message.
- **`GET /api/v1/health` answers 503 `database_unavailable`** when `SELECT 1` fails.
- **API docs are served at `/api/v1/docs`**, the schema at `/api/v1/openapi.json`, so everything sits behind the one `/api` proxy.
- **Lint and types.** ruff with the reference API's rule set and 79-column lines, plus `UP` and `B`; mypy in strict mode with the pydantic plugin.
- **`api/app/cli.py` is not created yet.** It arrives with its first command in milestone 2.

### Tests, tooling, CI

- **API tests use a real Postgres 16 started by testcontainers**, once per run and only when a test asks for the `database` fixture, so unit tests need no Docker. `TEST_DATABASE_URL` points the tests at a server that is already running. This is the reference API's approach; the rolled-back transaction per test arrives with the schema in milestone 2.
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
- **The per-test rollback from the reference API is in place**: a test's `session` and each request's session share one transaction that is never committed.
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
- **The run stopped at 34 topics and 880 questions**, by the owner's decision on 2026-11-17: 352 in Introdução à Programação, 264 in Estruturas de Dados and 264 in Banco de Dados are enough to build and try the app, and the other 16 topics come later. Milestone 4 stays open with two boxes unticked, and milestone 5 starts without waiting for it.
- **The bank mixes two models.** The run went back to Fable 5.2 for a while and then to Opus 5.5 for the agents started last, so some of the later topics were written or blind-solved by Opus. The pipeline log does not record which model wrote a topic.
- **Still no failure at any step**: 880 of 880 questions passed validation, the code run, dedupe and the blind solve in the first round, so the repair round and the drop path remain untested on real questions.
- **The 880 questions were imported for real into the local database**, all as `verified`, with 1760 translations.

### The last 16 topics

- **The owner asked for the rest on 2026-11-22, and the bank now holds all 50 topics: 1266 questions**, 416 in Introdução à Programação, 418 in Estruturas de Dados and 432 in Banco de Dados. Both open boxes of the milestone hold.
- **The run took under an hour and did not reach the usage limit**: three orchestrators on Opus 5.5 at high effort, one per subject, each with one generator at a time. Fifteen topics were written and blind-solved by Opus; `arvores-binarias`, written on 2026-11-17, was only blind-solved.
- **It ran in a git worktree on the branch `feat/milestone-4`, and its commit is on that branch**, not on `main` as `CLAUDE.md` asks: the owner opened the session there, and `main` is checked out in the other folder, where it moved on in the meantime. Merging is the owner's step. The brief and the driver were copied from the main checkout's `content/work/fanout/` with the checkout's path changed, and the waiting `arvores-binarias` files with them; the originals were left where they were. Everything under `content/work/` in the worktree goes when the worktree is removed, and nothing in it is needed again: the keys a solver chose are in each question's `verification`, and the log is committed.
- **Still no failure at any step: 1266 of 1266 in the first round.** The repair round and the drop path have never run on a real question.
- **The planted-flaw test of the blind solver was repeated on Opus**, which milestone 4 had left undone, because of what the run's file times showed: every blind solve, in this run and on 2026-11-17, wrote its answers 20 to 75 seconds after the stripped file was made, 32 C questions in 24 seconds among them. That is fast enough to ask whether the solver reasons. A fresh Opus solver, with the pipeline's own task message, got a file of six `heaps` questions from the bank mixed with six flawed ones: two true statements; two expressions for a parent's index that are equal for every i > 0; a program whose output is no option; Portuguese asking the worst case and English the best; the first element of a set of strings; a C loop that reads past its array. It answered in 31 seconds, gave the six sound questions their keys and `null` to the six flawed ones, each with the right reason. The bank's file was unreadable during the solve, and the test file is not kept. What that does not show: how often a solver of the same model family shares a generator's mistake. The owner's hand check of about 50 questions per subject is the check that does not depend on the model.
- **The SQL runner no longer opens transactions of its own.** Python's `sqlite3` begins one before the first INSERT, so in `sql_runner.py` a `BEGIN` after an INSERT failed with "cannot start a transaction within a transaction", and a `ROLLBACK` without a `BEGIN` quietly undid every row written so far, where a database answers with an error. The generator of `transacoes-e-acid` met it and worked around it by putting every write after `BEGIN TRANSACTION`. The runner now connects in autocommit (`isolation_level=None`), which is how the sqlite3 shell and the databases of the course behave, with two tests. No key was verified under the wrong behaviour: the four bank questions with a ROLLBACK keep their writes inside the transaction, and all 132 Banco de Dados questions whose code is run pass under the new runner as they did under the old.
- **`serializacao-e-isolamento` and `controle-de-concorrencia` have no code that is run** (two `skip` fragments in the first, no code in the second). One SQLite connection in memory cannot show two transactions running at once, so their questions are schedules and rules in words. `transacoes-e-acid` has four run questions, `armazenamento-e-indices` two and `seguranca` three.
- **A C question whose answer depends on the platform says so in the stem or asks about the dependence.** In `enumeracoes-e-unioes`, the two `sizeof` questions begin with "Numa plataforma em que int ocupa 4 bytes e precisa ficar num endereço múltiplo de 4", and the one that reads an `int` through an array of bytes has as its key the option that says the result follows the machine's byte order, with `skip`. One question takes ASCII for granted (`'A' + 2` printed as a character). `prompts/generate.md` does not state this rule; the generator arrived at it.
- **The import was proved on a scratch database, not run on the local one.** `alembic upgrade head` and `import-content` against an empty Postgres 16: 1266 created, all `verified`, in 50 topics, with 2532 translations, and a second run changed nothing. The local database is shared with the `main` checkout through the compose project's name: imported from this branch, the 386 new questions would be retired by the next `make seed` or `make import-content` run from `main` before the merge, and a retired question that comes back unchanged stays retired (milestone 3). After the merge, `make import-content` on `main` brings them in and `make publish` shows them to students.
- **Stray files.** One generator ran a command from inside `content/` and wrote `content/content/work/`, which it removed; another found its build script changed on disk and rebuilt its file before the checks, cause unknown. Nothing of either is in git, and the files that were checked are the ones in the bank.
- **"Key is longest" is 29% in Banco de Dados**, up from 22%, and 24% over the whole bank. Near 25% still; the new conceptual topics pull it up.
- **Open, as before:** overlap between neighbouring topics is unmeasured, since `dedupe` compares text and not concepts; and no question is human-checked.


## Milestone 5 · V1 backend

### Routes and their shapes

- **`PATCH /me/settings` changes profile fields as well as settings.** Onboarding stores a language, a university, a course, a subject and a goal, and the spec has one route for all of it. So the route takes the fields of `user_settings` and, of `users`, the locale, timezone, display name, university, course and current subject. Only the fields sent change; null clears the name, the university or the course.
- **Names of subjects and topics are sent in both languages** (`name_pt`, `name_en`), so that switching language redraws without a request. A question's text is sent in one language, the user's.
- **`GET /config` is open to visitors** and adds to the spec's three things what the app needs before it draws: whether Google sign-in exists on this server, the session length, the goal options and the XP of a level.
- **`POST /sessions` gives back the session the student left unfinished in that subject**, if there is one, instead of a new one. That is how an interrupted session is found again from Home. Only `mode: "practice"` is accepted, and anything else is a 422, until milestone 9 adds review.
- **A session can be finished only when every question is answered** (409 `session_incomplete`). Otherwise one answer and a "finish" would keep a streak. Finishing twice counts once.
- **Answering a question of a session again changes nothing and returns the first result**, even with another key. The offline flow sends an answer again when it lost the response.
- **The summary is the response of `POST .../finish` and is also inside `GET /sessions/{id}`** once the session is finished, because the summary screen has its own address and can be reloaded. The session's own numbers are stored; the streak, goal and level in it are the student's at the moment of the request.
- **A session payload shows, for an answered question, the key the student chose, whether it was right and its XP**, and nothing else. `SessionQuestion` has no field for the correct key, the reasons or the explanation.
- **The order of a question's options is shuffled by a seed made of the session id and the question id**, so it differs between sessions and holds when a session is loaded again.
- **`GET /me/activity` returns the current month of the student's calendar** without arguments, which is what the profile shows, or the days from `start` to `end`, at most 366. Only days with activity are listed.
- **`GET /me/stats` carries what Home and the profile show**: level, streak with its state, today's goal, totals, the rating in every published subject (null before the first answer) and the rating change of the last finished session.
- **Only a question that was in one of the user's sessions can be reported.** Any other id is a 404, so reports do not tell which ids exist.
- **`POST /events` is open to visitors**, since the landing page has events before there is a guest. A batch has at most 50 events, an event's props at most 2000 bytes of JSON, a name is lower case with digits, dots and underscores, and a time in the future is stored as the time of arrival.
- **`GET /me/export` and `DELETE /me` exist already**, each with one test. The export is every column of the user's rows in twelve tables, without session tokens and sign-in links. Deleting removes the `users` row, which takes the rest with it, and the sign-in links sent to the address. Milestone 7 still owns their box.
- **Error codes**, beyond the framework's: `unauthenticated` (401), `csrf_header_missing` (403), `subject_not_found`, `session_not_found`, `question_not_in_session`, `question_not_found` (404), `no_questions`, `session_incomplete` (409), `invalid_magic_link` (400), `validation_error` (422).
- **An operation is named after its function** (`get_me`, `post_answer`), not FastAPI's long default, because the names appear in the web app's generated types.

### Rules where the spec is silent

- **"Answers" in the K rules are rated answers.** A student's count in a subject and a question's count go up only on a first attempt, the one that moves the ratings. Topic mastery, the daily goal and XP count every answer, repeats included.
- **A first attempt is the first time this student answers this question at all**, in any session.
- **A first session in a subject is one with no earlier session there.**
- **Selection, where the spec says "relax".** When fewer questions than a session needs were not answered in the last 14 days, all the recent ones come back at once. In a first session, levels 2 and 3 are used alone only if they fill the session. When the 30 closest cannot fill it under the limit of 3 per topic, the next closest are used, and after them the limit is dropped. Ties in closeness are broken at random: a fresh bank has five ratings, so most of it is tied.
- **Students are served `published` questions of `published` subjects.** `python -m app.cli publish-subjects` publishes a subject and its `verified` questions, and is run again after an import into a published subject. Nothing else publishes.
- **A subject's topics are listed only if they have a published question.** With 34 of 50 topics written, the other 16 would be rows that can never be practiced. `next_topic` is the first topic in catalog order that is not mastered.
- **85% or more with under 10 answers is "practiced"**, not mastered.
- **The 5 XP bonus is for a correct answer** to a question rated above the student, by the ratings from before the answer. Levels start at 1.
- **The daily goal defaults to 20**, the option the onboarding mockup has selected. A day that met its goal stays met if the goal is raised, and lowering the goal can meet today's.
- **A day is worked out with the timezone the user has at that moment.** Changing timezone does not rewrite earlier days.
- **The stored streak changes only when a session is finished.** "At risk" and "lost" are worked out when it is read, and a lost streak keeps its length in the row until the next session, which is what "Sua sequência de 7 dias terminou" needs. `streaks.lost_length` and `lost_at` stay empty until streak repair (milestone 10).
- **A review item is due 24 hours after the wrong answer**, not at the next local midnight. A wrong answer in practice to a question already in the queue starts it over; `lapses` counts wrong reviews only, so it stays 0 in V1.
- **`entitlements_for` is built now**, because `GET /config` returns entitlements: no limits while billing is off for the user; with billing on, the plan of a subscription that is active, or canceled with its period still running, and the free plan otherwise. A `past_due` subscription gives the free plan until milestone 10 decides otherwise. Its arguments are the flag, the subscription and the plans rather than the spec's `(user, subscription, flags)`: it needs nothing else of the user.
- **A flag without a row is off**, and a visitor sees only flags that are on for everyone.

### Auth

- **A session lasts 90 days and renews itself.** The spec gives no lifetime. A fixed one would sign a guest out for good, since a guest has no way back in, so a session past half of its lifetime gets the full lifetime again and the cookie is sent again.
- **The CSRF header is `X-Requested-With`, with any value, on every state-changing route**, the auth routes and bearer requests included. One rule with no exceptions; a billing webhook will be the first (milestone 10).
- **The token is never in a response body.** A native client can send it as a bearer header, as the spec says; how the Capacitor shell gets hold of it is milestone 12's question.
- **An email link does not remember who asked for it**, which milestone 2 left open. The guest that is upgraded is the one in the browser that opens the link, and the email says to open it on the same device. Opened elsewhere, the link signs in without the guest's history, and the guest is merged when that browser signs in too.
- **The link in the email is `<APP_BASE_URL>/auth/callback?token=...`**: the web app's page posts the token to `/auth/magic-link/verify`. `POST /auth/magic-link` answers 202 for any address.
- **Google and an email link with the same address are one account.** An identity is looked up first, then the address. Google must say the address is verified.
- **Merging a guest into an account.** Sessions, answers, reports and events change owner. Per subject, the rating built on more answers stays and the counts add up. Topic counts and days add up. The streak is rebuilt from the merged days. A question both have to review keeps the earlier date. The account keeps its settings and profile; the guest's university, course and current subject fill what is empty.
- **Signing in ends the token the request came with** and issues a new one.
- **A failed Google sign-in goes back to the app** at `/auth/callback?error=google_sign_in_failed` or `google_email_not_verified`, because the browser is on a page of ours, not in a fetch.
- **Outside production, a mock stands in for Google when no client id is set**, and signs in as the demo user. In production without the keys the Google routes are 404.
- **An email address is checked by its form only** (something, `@`, something with a dot), lower-cased. The link proves the rest.
- **Local docker compose sets `SESSION_COOKIE_SECURE=false`**, so sign-in works over http from a phone on the same network. The setting defaults to true.

### Code and tooling

- **`app/schemas/`** holds the request and response models, apart from routes and services, which both use them.
- **Services take `now` and `settings` as arguments and never commit**; a route commits once. That is what lets the demo user play sessions in the past and the tests move the clock.
- **An answer's `created_at` is the request's time**, not the time of the insert, for the same reason.
- **`ensure_row`** (`app/db/rows.py`) creates a missing row with `INSERT ... ON CONFLICT DO NOTHING` and returns it locked. With the lock on the session row, two requests cannot both add to a counter.
- **No ORM-level cascade: deleting a user relies on the database's `ON DELETE CASCADE`**, as milestone 2 set up.
- **`tzdata` is a dependency**: the slim Python image has no timezone database.
- **Authlib asks for the `httpx2` package and falls back to httpx**, with a deprecation warning at start. The API stays on httpx: adding `httpx2` is the owner's call, and it is one line in `pyproject.toml` when wanted.
- **`OPENSSL_armcap=0` in the local `api` container.** Authlib loads `cryptography`, whose OpenSSL dies with "Illegal instruction" while probing the CPU in Docker Desktop's VM on the owner's M4. Found when the container would not start; the runbook has the symptom.
- **TypeScript types.** `make types` writes `web/src/api/openapi.json` from the app and `web/src/api/schema.d.ts` from that file with openapi-typescript. Both are committed, so CI's two jobs can each check one: a pytest test compares the JSON with the app, and `npm run typecheck` runs openapi-typescript with `--check`.
- **The demo user** is `demo@example.com`, "Carol Demo". It plays real sessions on past dates through the practice service, with a fixed random seed: about three weeks, a streak of 7 days ending today, 78% of answers right. Its answers move question ratings like any student's. The command refuses to run in production.
- **`make seed`** runs the migrations, `seed`, `import-content`, `publish-subjects --launch` and `demo-user`. `make publish`, `make demo-user` and `make types` are new.
- **Tests.** The API's clock is a dependency the tests replace, and it moves a millisecond per request. The test client speaks https, because the cookie is Secure, and sends the CSRF header. The flag mechanism is tested on a route the test adds, since V1 has no flagged route.
- **The real Google provider is tested against a transport that answers in Google's place.** It has not met Google itself: that needs the owner's client id.

### Spec against design

- **XP.** The mockups show "+12 XP" for an answer and "+96" for a session. The spec's numbers hold: 10 or 15 for a correct answer, 10 for finishing.
- **Locked topics.** The profile and Home mockups show a locked topic; V1 has none, as decided in milestone 1.

### Open, not decided

- **Nobody is asked for a name.** The profile shows "Carol Nunes", but only Google gives a name; an account made by email link, and every guest, has none. `PATCH /me/settings` accepts `display_name`, so a field can be added wherever the owner wants it.
- **No "Difícil" in `design/copy.md`.** The badge has three levels by milestone 1's decision, and the copy has labels for two. Milestone 6 needs the third.
- **Guests are never cleaned up.** Every first visit makes a user row that stays, with its session, even if the visitor never returns.
- **No rate limits yet** (milestone 7). Until then `POST /auth/magic-link` sends an email to any address as often as it is asked.

## Milestone 6 · V1 frontend

### How it was built

- **The main session built the foundation and six subagents built the screens**, on Opus 5.5 at high effort, three at a time: session; Home and the catalog; onboarding and sign-in; then the summary; the profile and settings; the landing page. Each read its screen's mockups in full, as `CLAUDE.md` asks, and compared its screens with them by screenshot.
- **`web/README.md` holds the frontend's rules** (styling, copy, server state, states, tests, the screenshot check), so that they are in one place for whoever builds the next screen.

### Structure and libraries

- **React Router 8 in its plain form**: `<BrowserRouter>` with a `<Routes>` tree in `src/app/routes.tsx`, no data loaders. Every page but the landing page is a lazy import.
- **`openapi-fetch` is the API client**, typed by the generated `schema.d.ts`: a wrong path, parameter or body fails the type check. `src/api/queries.ts` wraps every call in a TanStack Query hook, and `unwrap()` turns every failure into one `ApiError` with the status and the API's error code. A request that never reached the server has status 0.
- **Queries and mutations run with `networkMode: "always"`.** TanStack Query's default pauses a request while the browser says it is offline, and the screen would wait without a word. Now the request fails at once and the screen shows the offline state with its retry.
- **One retry for a server error, none for a 4xx or a network failure.**
- **The syntax highlighter is 150 lines of our own** (`src/lib/highlight.ts`), not a library. The spec asks for "a light syntax highlighter", the bank has three languages, and the design colours five kinds of token: keyword, function, number, string, comment. It is tested, and an unknown language is shown as plain text.
- **Toasts are a small store and one component**, not Sonner, which the design names: the design's toast (icon, text, action, 44 px close button, four seconds) is 80 lines, and styling a library to it would be more. Modals and bottom sheets are built on Radix Dialog rather than a separate drawer library, so a sheet does not follow a dragging finger: `Sheet` serves the report form and the subject switcher, and the save-progress prompt and the delete confirmation (an alert dialog) are small components of their own, because their mockups lay the title out differently.
- **Not installed:** a global store, a form library, a date library.

### Guest first, language, theme, timezone

- **`RequireUser` wraps every route but `/`, `/signin` and `/auth/callback`.** With no session it creates a guest without asking, sending the language in use and the device's timezone. Two requests at the same moment share one call, so a first visit makes one guest.
- **Someone without a current subject has not been through onboarding** and is sent to `/start` from any other page. There is no separate "onboarded" field.
- **Language on a first visit:** English for a browser whose first language is English, Portuguese for any other. The choice is kept on the device and, once there is a user, on the account.
- **When account and device disagree on language or theme, the account wins**: that is a sign-in on a new device. A change in the app writes to both.
- **The device's timezone wins over the account's.** When they differ the app sends the device's to `PATCH /me/settings`: the API counts days in the user's timezone, and a student who travels should not lose a streak to the old one.
- **The theme is applied by a few lines in `index.html`** before the first paint, from the choice stored on the device, so a light-theme student never sees a dark flash.

### System states

- **Offline, error, 404 and maintenance cover the whole window**, navigation included, as their mockups draw them. Loading and empty stay inside the screen's frame.
- **Which state a failed request shows:** offline when the request did not reach the server; maintenance for a 502, 503 or 504 (the API's own 503 is "database unavailable", and the others are what nginx answers while the API restarts); 404 for a 404; the error screen for the rest.
- **Flagged routes:** `<Flagged flag="...">` shows the 404 screen while the flag is off and renders its child, a lazy component, only when it is on, so the feature's code is not requested. V1 has no flagged route; the test uses one of its own, as the API's does. The first real use of `useFlag` is the daily-reminder switch in Settings.
- **The navigation tabs are Início, Perfil and Ajustes.** Revisão and Ligas, and the move of Ajustes under Perfil, come with their routes in milestone 9.

### Copy

- **`i18n/pt-BR.json` and `en.json` are written by hand from `design/copy.md`**, with keys named after what the text is for (`states.offline_title`), not generated from the copy file's own keys, which are per mockup and repeat a text for every screen it appears on. Sample values in the copy became variables.
- **Three things enforce "no hardcoded strings":** the lint rule `local/no-hardcoded-copy` (`web/eslint-rules/`) fails on text in JSX and in the attributes people read or hear; `t()` checks its keys at compile time; and a test compares the keys and variables of the two files.
- **"Difícil" / "Hard"** is the third difficulty label, which the copy file lacks (left open in milestone 5).
- **The wordmark is drawn as text**, as the mockups do, not from the SVG files. It is the one place where text is written into a component: the name is the same in every language.

### Checking screens against mockups

- **`npm run shots`** (`web/shots/`) opens each mockup and the app in the same state, at the mockup's frame size and in both themes, and writes them side by side with the differing pixels marked and counted. The app runs against a mock API, the same one the component tests use, with the mockup's sample data. It is a tool for building and reviewing a screen, not a test: it is not part of `make test` or CI.
- **`-webkit-font-smoothing: antialiased` was removed** from the base styles. The mockups do not set it, and with it every letter differed by a pixel of weight.
- **A mockup may be read through `shots/print-mockup.mjs`**, which leaves out the coordinates of SVG shapes and nothing else. Icons are named by `data-lucide` and Mel by its label, so the coordinates are never built from. A first reading of a screen's mockups is still of the whole file.

### Landing page, PWA

- **The landing page is rendered at build time into `index.html`**, in Portuguese, with its title and description from the translation files. `npm run build` builds `src/prerender.tsx` for Node first and then the app, whose build calls it.
- **There is still one `index.html` for every address.** On any address but `/`, a two-line script empties the pre-rendered markup before it is painted. The alternative, a second HTML file for the app, would need its own rule in nginx and in the service worker.
- **The app renders over the static HTML rather than hydrating it.** The static page is Portuguese and follows the system theme; a visitor with English or a stored theme would not match it, and React would report the mismatch. The cost is that an English visitor sees Portuguese until the script has loaded.
- **The service worker precaches the build's files and nothing else**: no rule for `/api`, so questions and progress always come from the server. It updates itself when a new build is deployed. It is not registered by the dev server.
- **Icons are exported by `npm run icons`** from `design/assets/` at the web sizes of the design, drawn by Playwright's Chromium, and committed in `web/public/icons/`. The maskable icon is the two adaptive layers on top of each other.
- **Open, still: web fonts.** Geist and JetBrains Mono come from Google Fonts through `design/tokens.css`, which is consumed unchanged. Offline, or before they arrive, the app shows the system's fonts. Self-hosting them means either changing the tokens file or shipping the fonts twice.

### Onboarding and sign-in

- **"Bora praticar" at the end of onboarding saves and starts the first session.** One `PATCH /me/settings` stores university, course, subject and goal; then a session in the chosen subject opens. If the session cannot start the student lands on Home; if saving fails, a toast says so and step 4 stays.
- **Spec against design: "Pular" is on all four steps**, as the mockups draw it, though only step 2 is optional. On step 2 it stores nothing. On steps 1, 3 and 4, which always have an answer selected, it keeps that answer and goes on.
- **The step is in the address** (`/start?step=2`), so the browser's back button goes back a step. Someone who already has a subject and opens `/start` goes to Home.
- **What is selected at first:** the language in use, the first published subject, and the user's goal (20 for a new guest). An empty university or course is stored as null.
- **Sign-in never needs a user**: it works with no session at all. "Continuar com Google" is a plain link to the API and is shown only when `/config` says Google sign-in exists. "Continuar sem conta" goes to Home, where a guest is created if there is none. The close button goes back, or to Home when there is nothing to go back to.
- **The email address is checked by its form before sending**, like the API does. After "link sent", "Usar outro e-mail" returns to the form with the address still in it.
- **`/auth/callback`** verifies a token once (React's development double run is guarded against), and goes to Home. A 400 shows "this link no longer works" with the way back to sign-in; an `error` parameter shows that the Google sign-in failed; with no parameter, which is Google's successful return, it goes to Home.

### Home and the catalog

- **The greeting uses the first word of the name**, and "E aí!" when there is none.
- **The goal card's button** says "Começar" when nothing was answered today and "Continuar" otherwise. It starts a session, or resumes the one left unfinished: the API decides. "Próximo: …" is left out when every topic is mastered.
- **A button that starts practice is never a dead end.** When the subject has nothing to serve (409 `no_questions`), a toast says so and offers to switch subject. One hook, `src/lib/useStartPractice.ts`, does this for Home, the summary and the empty profile.
- **Streak moments on Home:** "started", "at risk" and "lost" get a card with Mel, the counter, a sentence and, for the last two, a button that starts a session; it is at the top on phones and under the goal card on desktop. An extended streak gets no card on phones, where the chip shows it, and the plain counter on desktop. "Restored" arrives with V2 and V3.
- **Spec against design, the streak's caption:** "Meta de hoje batida" is shown under the counter only when today's goal is met; otherwise it says "Praticou hoje". The streak counts a day with one finished session, so the mockup's caption would often be untrue.
- **The goal ring on the caramel card stays ink when the goal is met**, with a check in the centre. The design's green would vanish on caramel; green is used on a plain surface.
- **The rating card shows the last rating change**, on desktop only, as in the mockups. An unchanged rating has its own sentence.
- **The subject switcher** is a sheet with the published subjects as radio rows and a link to `/subjects`. It is listed under "Not designed" and was built from the components.
- **`/subjects`** takes from the V2 catalog mockups the row, the back arrow with the title and the 720 px column, and leaves out search, the course filter, the two headings and the add and remove buttons. A row shows the subject's rating or "Ainda não praticou"; the current one is marked. Choosing one makes it current and goes Home.
- **A current subject that is no longer published** leads to an empty state that points at `/subjects`.

### Session

- **The breadcrumb is the subject's short badge without its slash, a slash, and the topic** ("prog / ponteiros"). The mockups show the subject's full name; the short text is what fits beside the difficulty badge with real names.
- **Leaving a session asks nothing**: the close button goes Home and the session resumes from there.
- **Options are set in the code font** when the question has code and every option is short (30 characters at most) and does not end with a period. Statements about a program stay in the text font.
- **Keyboard:** 1 to 4 select, Enter checks and then continues. Enter keeps its own meaning on another control (the close link, "Reportar questão", a button), and the keys are off while the report form is open. After "Continuar", focus moves to the new question's title.
- **Offline.** The chosen option is kept on the device from the moment it is chosen, so it survives a reload. "Verificar" without a connection keeps the answer and its time, shows the banner, and sends it when the connection returns, with the "De volta online" toast. While it waits the student may change the option.
- **A session whose questions are all answered but that was never finished** (the student left on the last feedback) is finished when it is opened again.
- **The report form** needs a reason; details are optional, at most 1000 characters. It closes with a thank-you toast, and stays open with an error toast when sending fails.
- **An answer the server refuses** shows a toast and leaves the question as it was.

### Summary

- **Gain or loss is decided by the rating change alone.** An unchanged rating reads as a gain, with a grey "±0". A loss changes the words and Mel's pose and adds the reassuring line; colours and motion are those of a gain, and the change is grey with a down arrow.
- **Level up:** the bar is full, its label says "Subiu de nível!" and a chip names the new level.
- **The save-progress prompt is shown to a guest on the summary of their first finished session, and on no later one.** "Agora não" closes it; nothing is stored, so reloading that one summary shows it again. A guest who wants an account later finds "Entrar" in Settings.
- **"Topics to review" is left out when nothing was missed.**
- **Motion** follows the design's table for the rating, the XP bar and the level-up, with the duration tokens, so under reduced motion the final values are there from the first paint. The streak's five flame frames are not drawn: the design has one flame. The number ticks up when the session was the day's first.

### Profile and settings

- **A profile without a name** is titled "Perfil" with a user icon in place of the initial; the line with course and university shows what there is, or nothing.
- **A student who has answered nothing sees the empty state**, whose button starts a session.
- **"Domínio por tópico" lists the current subject's topics.** A bar is full when mastered, shows the accuracy while learning or practiced, and is empty while new.
- **The calendar** shows the month the API returns, weeks from Sunday in both languages as in the mockup, with month and weekday names from the browser's `Intl`.
- **Settings save at once**, with no save button. A failed save puts the control back, and for language and theme the device's value too, and a toast says so.
- **A guest's account section** says there is no account and offers "Entrar". "Excluir conta" is there for a guest too: a guest's data is erased the same way.
- **The delete confirmation** has "Cancelar" first and no close button; Esc closes it and a click outside does not. After deleting, and after "Sair", the app goes to the landing page.
- **Signing out does not create a new guest.** `RequireUser` sends someone who had a user and now has none to the landing page; a guest is made again only when they start to play.

### Landing page

- **Three subjects and ten questions**, by the decision of milestone 1: "Três matérias pra começar", with the launch subjects as static text from the catalog, and "10 questões por sessão" (the number comes from `/config` once it loads, and is 10 in the static HTML). On desktop the three cards fill the row the mockup gives to five.
- **The try-it question** behaves like a session's: "Verificar" needs a choice, then every option shows its reason and "Continuar praticando" leads to `/start`. The number keys are not bound on this page.
- **The language switch is a native select** under the mockup's "PT-BR" label, so a phone opens its own picker.
- **A visitor who has a session and has been through onboarding is sent to Home.** No other visitor gets a guest or a redirect.
- **Product events:** `landing.viewed` once per visit and `landing.sample_answered` with whether it was right. These are the only events the app sends so far.

### Spec against design, and mockups against the design's README

- **XP.** Mockups show "+12 XP" and "+96"; the app shows what the API returns under the spec's numbers.
- **Locked topics, five subjects, "8 a 12 questões", the subject's name in the breadcrumb, code with comments** in mockups are sample content; the decisions above and in earlier milestones say what is shown.
- **Button labels sit one pixel higher than in the mockups.** The README gives a button label a 20 px line; the mockups set none. The README wins by its own rule.
- **The toast has a close button and is 56 px tall**, as the README says; the one mockup with a toast draws neither.
- **Placeholders are in `--text-subtle`**, not the browser's default grey of the mockups, which fails the README's contrast rule on a white field.
- **Comparisons above 1% of pixels:** the landing page on phones (three subjects instead of five move everything below them up; each part matches when compared apart), Settings (the mockups select "Escuro" in both themes, and the comparison leaves the account on "Sistema" so that each theme can be photographed), and the toast above.
- **`v1-flow-streak-mobile` is a board of five cards, not a screen**: it has no comparison of its own. Its cards were compared one at a time while Home was built.
- **Not compared, for want of a mockup:** `/subjects`, `/auth/callback`, the subject switcher, the streak moments in place on Home, the guest's Settings, the level-up, English renders other than the session's, and every screen between 768 and 1279 px. The last was looked at on real data at 1024 px.

### Copy written for this milestone

`design/copy.md` has no text for the following, which were written in its voice in both languages. They are the owner's to change in `web/src/i18n/`.

- Failures: an answer, a report, a save or a session that could not be sent or started; a subject that could not be switched; a sign-out or a delete that failed; an invalid email address.
- Sign-in: the link that no longer works, the Google sign-in that failed, the link sent again.
- Home and catalog: the greeting without a name, the subject switcher's title and link, "Praticou hoje", the unchanged rating, a subject without questions or topics, "Atual", the empty catalog.
- Session and summary: the thank-you after a report, "Subiu de nível!" (from the design's README).
- Settings: the guest's line and "Entrar".
- Landing: "Três matérias pra começar", "10 questões por sessão…", and the page's title for search results.
- Labels for screen readers: the code block, the streak and rating chips.

### Open, not decided

- **Guests after sign-out.** Someone who signs out and plays again gets a new guest, apart from the account. That is the spec's guest-first rule applied again, but it means progress made after signing out is merged only on the next sign-in.
- **The profile has no way to enter a name** (carried from milestone 5).
- **Session-expired is not told apart from signed-out**: both end on the landing page without a word.


## Milestone 7 · V1 hardening

### Rate limits

- **Four limits, as settings**: guests, sign-in links and the Google flow together, per network address (300 in 10 minutes); sign-in links per email address (5 an hour); answers per user (60 a minute); reports per user (10 an hour). The spec names the routes and gives no numbers. Signing out is not limited. Every number is a placeholder to tune with real traffic, like the plan limits.
- **The limit per address is high on purpose.** A university can reach the API from one address for a whole campus, and the first visit of every student there creates a guest. The limit stops a script, not a classroom; the per-email limit is the one that protects an inbox.
- **Fixed windows from the Unix epoch**, the simplest count: a caller may make the limit's number of requests in a window. A burst across the end of one window and the start of the next can reach twice the limit, which is acceptable for these four.
- **Counts are kept in memory by each API process, not in Postgres.** No table, no migration and no clean-up job. The costs: under gunicorn each worker counts apart, and a restart clears the counts. nginx's limit per address (milestone 8) is the outer layer. If that proves too loose, the counter moves to a table without changing the routes.
- **A refused request is a 429 `rate_limited` with `Retry-After`**, in the single error shape, and it still counts. 429 is in the OpenAPI schema of every route.
- **The address is `X-Real-IP`, trusted as sent**, as the request log already did. nginx overwrites it with the real address, so in production the API must be reachable only through nginx (milestone 8). Locally, everything arrives from the Vite proxy's address.
- **The web app says "Muitas tentativas seguidas. Espera um pouquinho e tenta de novo."** where a student can meet a limit: sending a sign-in link, an answer, a report. The copy is new, in the voice of `design/copy.md`. A 429 while creating a guest shows the error screen, like any other failure there.
- **Product events are not limited.** `POST /events` is open to visitors and writes rows; the spec does not list it, and nginx's limit per address covers it. Left open below.

### Export and deletion

- **The export covers every table that points at `users`**, those of V2 and V3 included, as empty lists until their features exist: referrals on either side, and tutor messages through the user's threads. Session tokens and sign-in links are credentials and stay out. A test reads the database's foreign keys and fails when a new table is in neither the export nor the list of credentials, so a later milestone cannot forget one.
- **Deleting an account deletes its answers too; anonymous attempts are not kept.** Milestone 2 left this open. The questions keep the counts and ratings that the answers moved, which is all the statistics of a question need, and nothing of the person is left. Reports and events go with the account as well. A test checks that every foreign key to `users` cascades and that no row anywhere points at the deleted user afterwards.
- **Settings has "Baixar meus dados"** above "Excluir conta", for guests too: a plain download link to `GET /me/export`, saved as `caramelcase-data.json`. `design/README.md` lists data export under "Not designed"; the link is styled like "Excluir conta" in the text colour. The privacy policy points at it.

### Signing in before playing

- **An account created by a sign-in starts in the language and timezone of the device.** Found while checking V1 end to end in English: someone who signs in from the landing page, without playing first, has no guest, and the account was created in Portuguese with São Paulo's time. Since the account's language wins over the device's (milestone 6), the app then switched an English reader to Portuguese. The web app now sends its language and timezone in the body of `/auth/magic-link/verify` and in the query of `/auth/google/start`; the Google flow keeps them in a second short-lived cookie, `cc_oauth_device`, beside the state. A guest who signs in keeps their own, as before.

### Privacy policy and terms

- **`/privacy` and `/terms`, open to anyone**, lazy-loaded and not pre-rendered: only the landing page needs search visibility. Reading them creates no guest.
- **Built from existing pieces**, as `design/README.md` lists legal pages under "Not designed": the landing page's header (the wordmark, here a link to `/`, and the language switch) and footer around a 768 px reading column with the type sizes of the other screens.
- **The text is placeholder legal text in plain language, written from what the app does**: what is stored (the request log's IP address included), the one session cookie, Google Fonts, who receives data, the 14 days of backups milestone 8 sets up, and how to download and delete. What only the owner or a lawyer can say is in brackets: company, contact, data protection officer, legal basis, minimum age, retention of guests and logs, jurisdiction. A note at the top says the text is a draft.
- **The text lives in the translation files**, under `legal`, one title and one body per section, so the lint rule against hardcoded copy holds. A body is paragraphs apart by a blank line and lists as lines that start with "- ", which `LegalText` renders.
- **Links "Privacidade · Termos"** in the landing page's footer, under "Continuar sem conta" on sign-in, and under the cards in Settings. No consent wording at sign-in: what it should say is a legal decision.

### The end-to-end test

- **It runs against the docker compose stack seeded by `make seed`**, not against a production build: nginx and the production images are milestone 8's, and CI's web job already builds the app. The CI job runs `make up`, `make seed` and `make e2e` on a fresh runner, which is also the check that two commands lead to a playable session.
- **One test, two Playwright projects**: Portuguese on a 360 px phone and English on a 1280 px desktop, the language coming from the browser's as on a first visit. It finds everything by role and by the texts of the translation files, takes the first option of every question since it cannot know the keys, and first checks through `GET /config` that every flag is off. Past the summary it opens Home, Profile and Settings, so "works end to end in both languages" has a test.
- **No web server in the Playwright config.** The stack must be up; a global setup checks `/api/v1/health` first and says to run `make up && make seed`. One retry in CI, none locally. Each run leaves a guest in the database it ran against.
- **CI is still unobserved**: nothing has been pushed. The job was run locally step by step as it is written, against a stack on other ports.

### Two commands

- **`make up` waits until the app answers** (`docker compose up -d --wait`). The web service has a healthcheck now, so the wait covers its `npm install`. `make migrate`, and so `make seed`, starts the stack first if it is not up, because a command run in the API container while its first `uv sync` is still going would race it. Commands in the container run with `exec -T`, which CI needs.
- **Tried on a copy of the working tree with nothing installed**, as its own compose project on other ports and fresh volumes: `make up` took 12 seconds and `make seed` 26 (880 questions imported, three subjects published, the demo user created), with the Docker images already on the machine. The Playwright test then passed against it in both languages.
- **Checked by hand on that stack, in both languages**, with a throwaway browser script: signing in by email link from the landing page, the account in the device's language and timezone, onboarding to a session, the email in Settings, the data download, the privacy policy and the terms, the sixth link to one address in an hour refused with the new message, deleting the account, and a link sent before the deletion no longer working.

### Spec against design

- **The landing page's footer** now holds the two links beside the brand. On phones it takes two lines, with the languages on the second; the mockups draw one. The sign-in screen has a line of links under "Continuar sem conta", which its mockups do not have.

### Open, not decided

- **Product events have no rate limit** (above).
- **What the legal pages leave in brackets**, and whether signing in needs a consent line.
- **Guests are still never cleaned up**; the privacy policy has a bracket for how long they are kept, and for how long request logs are.
- **The local database collects a guest per end-to-end run.**


## Milestone 8 · Deployment files

### Layout and images

- **Everything for production is in `deploy/`, with its own `.env` and `Makefile`.** The root `Makefile` stays the developer's, plus `make check-deploy`; on the server every command is `make -C deploy <target>`. The reference projects keep one Makefile per repository, which here would mix two stacks.
- **Two images, `<user>/<repository>-api` and `-web`**, where each reference project has one. Both are built from the repository root through an allowlist `.dockerignore` (the reference web app has none), so nothing else reaches a build: no `.env`, no syllabus, no question still in `content/work/`.
- **The API's image holds `content/catalog.yaml` and `content/bank/`**, so `seed` and `import-content` on the server read the content of the commit that built the code. The tools and the tests stay out.
- **The API runs gunicorn from the virtualenv directly, as a user without rights.** The reference API's `uv run gunicorn` checks the lock at every start. `ENVIRONMENT=production` and `LOG_JSON=true` are set in the image.
- **The worker class is `uvicorn_worker.UvicornWorker`, from the `uvicorn-worker` package.** The reference API uses `uvicorn.workers.UvicornWorker`, which uvicorn 0.54 marks deprecated and points to that package.
- **gunicorn 27's control socket is off.** Nothing uses `gunicornc`, and the socket's default place is the home directory the image's user does not have: it logged an error at every start.
- **Two new settings: `gunicorn_workers` (2) and `gunicorn_timeout_seconds` (60).** The reference API runs 3 workers with a 6-minute timeout. Two, because each worker counts the rate limits apart and the server is small; no request here takes more than a second.
- **Base images.** The API on `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, as in development. The web app built on `node:24-slim`, as in development (glibc: Tailwind, Rollup and Lightning CSS ship native binaries, and musl builds of them are where npm's optional dependencies go wrong), and served by `nginx:1.30-alpine`, the stable line pinned to its minor version (the reference projects: `nginx:alpine` and `nginx:latest`). `postgres:16-alpine`; `certbot/certbot:latest` as in the reference projects.
- **The API's image is 107 MB compressed**, 345 MB unpacked, 43 of them uv itself. Not split into stages: not worth the extra file.

### The compose file

- **nginx is the web app's image** (the reference web app's pattern): nginx with `web/dist`, one container that serves the files and proxies `/api`. Its configuration is mounted from `deploy/nginx/` (the reference projects' pattern), so it comes from the clone, not the image; `deploy.sh` runs `nginx -t` on it before anything else.
- **`nginx.conf` is replaced whole.** The image's own writes every request in its "main" format to the container's output, and a second `access_log` at the same level would write each request twice. It holds what every mode shares (log format, gzip, the rate limit's zone, the cache rules, the resolver, a health server); `app.conf` holds the app's locations and is included by both the http and https templates, so the app's server block is written once. The three templates keep the reference projects' names and roles.
- **Postgres is a container of the same compose file**, in a named volume, which the spec allows. A managed database means editing the compose file: remove `db`, the API's `depends_on` and its `DATABASE_URL` line, and set `DATABASE_URL` in `deploy/.env`.
- **`DATABASE_URL` is built from the `POSTGRES_*` values**, so the password must be letters and digits; `.env.example` says so and suggests `openssl rand -hex 24`.
- **The API receives the whole `deploy/.env`** (`env_file`, as in the reference projects), so any tunable can be set there; nginx receives `DOMAIN` only.
- **The faults of the examples, fixed**: healthchecks on all three services (nginx's on a server that listens on the container's loopback only); `restart: unless-stopped`, without which a reboot of the server leaves the app down; Docker's logs rotated at 5 files of 10 MB per container, where the default keeps everything until the disk is full; gzip, cache rules and security headers; a `.dockerignore`; and `certbot.sh`'s `NGINX_CONF_FILE` override, now the variable compose reads.
- **The project is named `caramelcase-prod`**, so the stack tried on a laptop cannot use the development stack's database volume.
- **Both `image:` and `build:`** on `api` and `nginx`: a deploy pulls, `make -C deploy build` builds on a laptop. The reference projects keep a second compose file for that.
- **The published ports are settings** (`HTTP_PORT`, `HTTPS_PORT`), for a laptop where 80 is taken.

### nginx

- **The access log is JSON on the container's output**, where the reference projects write it to a file inside the container, which `docker compose logs` never shows and a new container loses. It adds `host`, `upstream_time` and `request_id` (the API's `X-Request-ID`, so nginx's line and the API's line of a request can be joined), writes the numbers as numbers and drops `remote_user`. The error log stays plain text, from warnings up: nginx cannot write it as JSON.
- **The limit per address covers `/api/` only: 30 requests a second with bursts of 60.** The reference projects limit everything at 10 a second with bursts of 10, which on static files would refuse part of a first visit (about 40 files). The numbers are in nginx's configuration, not in `settings.py`, which nginx cannot read; changing them is a commit and a deploy. Placeholders, like the API's limits.
- **nginx's own errors on `/api/` are JSON in the API's error shape**, as the spec asks of every error: its 429 as `rate_limited` with `Retry-After: 1`, and a 502 or 504 as 502 `api_unavailable`, a new code. The web app shows the maintenance screen for it, as for any 502.
- **The API's address is looked up through Docker's DNS on each request**, by putting it in a variable for `proxy_pass`. A deploy that changes only the API's image recreates only that container, and nginx would otherwise keep sending to the old address. Tried: a container took the API's old address and nginx found the new one.
- **Caching.** Vite's files in `/assets/` are cached for a year as immutable; everything else, `index.html`, the service worker, the manifest and the icons included, is `no-cache`, revalidated with its ETag. nginx adds nothing to the API's responses. A missing file under `/assets/` is a 404, not the app's HTML. The manifest gets `application/manifest+json`, which nginx's types lack.
- **Security headers:** `nosniff`, `X-Frame-Options: DENY`, `strict-origin-when-cross-origin`, a `Permissions-Policy` that turns off camera, microphone and location, a partial Content Security Policy (`frame-ancestors`, `base-uri`, `object-src`), and over https HSTS for a year, without subdomains or preload, which are hard to take back. No `script-src`: `index.html` has two inline scripts (the theme before the first paint, and the one that empties the pre-rendered page), whose hashes would have to follow every change of the file, and Google Fonts and the optional services would need listing. Left open below.
- **HTTP/2 over https**, and `server_tokens off`.
- **No `www.`**: the certificate and the server are for `DOMAIN` only, as in the reference API (the reference web app also serves `www.`). Adding it is a second `-d` in `certbot.sh` and a redirect server.
- **The http template also closes other names with 444**, which the reference projects' http files do not.

### Certificates

- **`certbot.sh`** starts nginx alone (`--no-deps`) with the temporary configuration through compose's own variable, and removes it with `docker compose rm --stop --force`. The reference web app's export of `NGINX_CONF_FILE` is never read, since its cert compose file names the template itself.
- **The renewal script needs no rendering**: it finds `deploy/` from its own path. Only the cron line is a template, filled with `PROJECT_ROOT`. The reference projects render the script into `~/.cron/` and the cron line says `~`, which cron reads as root's home whoever ran the script.
- **The renewal runs every day at 02:00**, not weekly as in the reference projects. certbot renews only a certificate near its expiry, and Let's Encrypt keeps shortening their lifetime.
- **Cron files are named with underscores** (`caramelcase_renew`, `caramelcase_backup`): Debian's cron skips a file in `/etc/cron.d` whose name has a dot.

### Deploys

- **`deploy/scripts/deploy.sh` keeps the reference projects' backup tag and rollback**, and the workflow calls it rather than holding a copy of it, as their `deploy.yaml` does. It waits for the healthchecks (`up --wait`) where they count running containers, which a container that restarts in a loop passes; checks nginx's configuration before anything; runs the migrations and `seed` with the new API image between the pull and the start, which is the explicit migration step the spec asks for; and removes dangling images after a deploy that worked. A failure before the start leaves the running containers alone and puts the old tags back.
- **`import-content` and `publish-subjects` are not part of a deploy.** Importing retires what left the files, and the runbook asks for a dry run first; publishing waits for the owner's hand check. Both are one command on the server.
- **A rollback does not undo migrations.** The runbook asks that each migration let the previous API run on the new schema.
- **The deploy workflow passes the Docker Hub token through the SSH action's `envs`** instead of writing the secret into the script, and pulls with `--ff-only`.
- **The build workflow runs CI first** (the reference API's pattern), builds on `main` only, both images as a matrix with a build cache each, tagged `main` and `main-<short sha>`. The reference projects' `develop` tags are left out: there is no `develop` branch. The web app's optional keys are passed as build arguments from secrets.
- **CI has a new job, "Deploy files"**: shellcheck on the scripts and `nginx -t` on the three configurations with a throwaway certificate (`make check-deploy`). The server reads nginx's configuration from git, so no image build would catch a mistake in it. CI builds no images: the build workflow does.
- **`install_server.sh` is the reference projects' three install scripts in one**, run as root rather than calling `sudo`, with git and envsubst added. Tried in an Ubuntu 24.04 container, without starting Docker there.

### Backups

- **`backup.sh` runs `pg_dump` inside the database container**, with that container's user and database, in the compressed custom format, into `BACKUP_DIR` on the host (`/var/backups/caramelcase`), readable by root only, and keeps the newest `BACKUP_KEEP` (14) by the date in the name. A failed dump leaves no partial file.
- **`restore.sh` goes beyond the plan's "procedure"**: one tested command rather than four typed during an incident. It asks for the database's name, and saves the current database as `before-restore-<time>.dump` first, a name the nightly pruning never deletes.
- **The backups stay on the server's disk.** Where to copy them is left open below.

### Logs, error tracking, analytics

- **The standard `logging` module goes through loguru** (`InterceptHandler` in `app/logger.py`): the lines of gunicorn, uvicorn and libraries, and Python's warnings, are JSON with a `logger` field. uvicorn's own line per request is silenced, since `log_request` writes a fuller one.
- **Error tracking is Sentry's SDK**, on with `SENTRY_DSN` for the API and `VITE_SENTRY_DSN` for the web app; GlitchTip accepts the same. (Replaced after milestone 8 by Better Stack, with new variable names: see "After milestone 8".) Nothing that identifies a student is sent: the API sends no personal data and no request bodies (a sign-in request holds an email address); the web app collects no user, cookies, headers, bodies or query strings, and strips queries itself as well, since a sign-in link carries its token in one. Sentry's browser SDK 11 has `dataCollection` where older versions had `sendDefaultPii`. Tracing is off (`sentry_traces_sample_rate` 0).
- **Analytics is Plausible**, on with `VITE_PLAUSIBLE_DOMAIN` (and `VITE_PLAUSIBLE_SCRIPT` for a self-hosted Plausible or a site's own script): no cookies, so no consent banner to design.
- **The web app's keys are read at build time**, as the reference web app does with its API address: an image is built for one set of keys, which are public anyway. While a key is empty the build holds none of that service's code; checked: a build without keys has no file that mentions either, and the service worker precaches nothing of Sentry.
- **The privacy policy does not name either service.** Switching one on means adding it there; the runbook says so.

### What was tried

On 2026-11-17, on an M4 with Docker Desktop 27.5, with both images built locally and pushed to a throwaway registry so that `deploy.sh` ran as it will on the server: a first deploy (18 seconds); import and publishing; the Playwright test in both languages through nginx and gunicorn, with the Secure cookie on `http://localhost`; static files, headers, gzip and 444 by `curl`; nginx's 429 and 502 in JSON; an `X-Real-IP` sent by the caller replaced by the real address; nginx finding a replaced API container; the https template with a self-signed certificate in the certbot volume (HTTP/2, HSTS, redirect, challenge); the temporary certificate configuration and `renew.sh`; a rollback from an API image that does not start (49 seconds, the previous images healthy again); a deploy stopped by a broken nginx configuration with nothing restarted; four backups with three kept; and a restore. Not tried: a real certificate from Let's Encrypt (it needs a public domain) and the two workflows (nothing has been pushed).

### Open, not decided

- **Where backups are copied off the server**, and whether the owner wants that.
- **A full Content Security Policy** with `script-src`.
- **Serving `www.`** as well as the domain.
- **The healthcheck's request every 30 seconds is in the API's log**: 2,880 lines a day.


## After milestone 8

- **CI's end-to-end job failed on the first two pushes**, at `npm ci` on the runner: `EACCES` creating a folder under `web/node_modules`. `make up` had run first, and the web container mounts a volume at `web/node_modules`; on Linux, Docker creates a missing mount point inside a bind mount as root, so the runner's user could not write into it. Docker Desktop on macOS gives the folder to the user, which is why the job passed when run locally. `make up` now creates `web/node_modules` before starting the stack. Moving `npm ci` before `make up` in the workflow would also have fixed CI, but not a Linux developer who runs `make up` and then `make install`. Not yet seen passing in CI: that needs a push.
- **The owner's reference projects are no longer named anywhere in the repository**, at the owner's request. `CLAUDE.md` describes them without names; the entries above say "the reference web app", "the reference API" or "the reference projects". Earlier commits still name them.
- **A root `README.md`, `docs/DEPLOY.md` and `docs/PROJECT-MAP.md`**: how to run the app and show it, what to set up before the first deploy, and a tour of the repository. `docs/DEPLOY.md` points at the runbook for every procedure rather than repeating it. Writing it showed that the runbook's first deploy needed the images published before the certificate step, not only before the deploy, since `certbot.sh` starts nginx from the web image; the runbook now says so.
- **Error tracking is Better Stack, not Sentry**, at the owner's request: they already use Better Stack and know it. Better Stack accepts what the Sentry SDK sends (its docs give JavaScript SDK 7 and Python SDK 2 as the minimum, and say JavaScript SDK 11 is supported), so the code keeps `sentry-sdk` and `@sentry/browser`, the same settings and the same privacy filters, and only the DSN changes. The variables are named after the service: `SENTRY_DSN` is now `BETTER_STACK_ERRORS_DSN`, `VITE_SENTRY_DSN` is now `VITE_BETTER_STACK_ERRORS_DSN` (also the build workflow's secret), and the setting `sentry_traces_sample_rate` is now `better_stack_traces_sample_rate`, still 0. Any service that accepts the Sentry SDK, Sentry and GlitchTip included, still works with the same variables. Nothing has been sent to Better Stack yet: that needs an account and a DSN.
- **Uptime monitoring and log collection are documented, not built.** `docs/RUNBOOK.md`, "Logs and monitoring", says how to do both with Better Stack: monitors on the health route and the home page, heartbeats from the backup and renewal cron jobs, and the containers' logs shipped by Better Stack's collector or by Vector. For this repository it recommends Vector as a container in the compose file, because then the setup is in git. Neither is in the code until the owner wants it, and log collection needs a line in the privacy policy first, since the logs hold IP addresses.


## Milestone 8.5 · Guidance

### Agreed with the owner on 2026-11-22

- **No guided tour.** The owner asked about a tour of the kind that dims the screen and points at one thing after another, because XP, the streak, the rating and "how to use the courses" confused even them. What was built instead, with their agreement, has three parts: the screen names what it shows, a tap on a number explains it at any time, and the same explanation opens once by itself when the number first matters. A tour would explain the streak, the rating and XP while they read 0, 1000 and nothing, and would stand between a new student and the first question, which the landing page and onboarding are built to reach quickly. No tour library was added.
- **Tapping a topic still starts a session of the whole subject**, as agreed in milestone 1. Home now says so ("Cada sessão mistura os tópicos da matéria."). Making a tap practise that one topic is a change of behaviour the owner may still want; it was offered and not chosen.
- **The look is derived from the design's tokens and components**, since `design/` has no mockup and no copy for any of this. `design/` itself is unchanged.
- **The milestone is numbered 8.5** and sits before milestone 9 in the plan, so that every reference to milestones 9 to 12 in this file still points at the right one.

### What changed on the screens

- **The streak and rating chips have their names on top** ("sequência", "rating", in the mono 11 px label the stat cards use), and each is a button. The mockups draw the two numbers with an icon and nothing else, and the words existed only for screen readers. On phones the greeting's row is 18 px taller for it.
- **Home's topic list has a line under its heading** saying that sessions mix topics, and an info button beside the heading. Neither is shown for a subject without topics.
- **The three cards of the summary are buttons.** Their labels are underlined with dots, which is the sign used here for "a tap explains this"; the cards are about 80 px wide inside on a phone, so there is no room for an icon.
- **The profile's level bar has an info button** after "Nível 4", for XP. The summary's level bar has none: the XP card above it explains the same thing.
- **An info button takes 16 px in the layout and 44 px under a finger**, by negative margins.
- **The topic's percentage is not itself a button**, though that was the first idea: it sits inside the row, which is already a button that starts a session. The info button beside the heading explains it.
- **Mel does not appear in the explanations.** A tooltip of 13 px text has no room for the sprite at a whole-number scale.

### The explanation

- **It is the "Tooltip" of `design/README.md`** (fill `--text`, text `--bg`, radius `tile`, 13/18, a 10 px arrow, at most 280 px wide), **plus an "Entendi" button**, on Radix Popover. The README says a tooltip opens on hover, focus and long-press; this one opens on a tap, because it must work on a phone and nothing may depend on hover.
- **It never blocks the screen.** It is not modal: a tap anywhere else closes it and still does what it was meant to do, and Esc closes it.
- **Five topics**: XP, rating, streak, topics, and the subject switcher. The last is a hint only, since the switcher is itself a button.
- **The numbers come from the API's settings.** `GET /config` has a new field, `rules`, with `xp_correct`, `xp_session_finished`, `user_rating_start`, `mastery_mastered_from` and `mastery_mastered_min_answers`; the XP of a level was already there. The copy holds `{{variables}}`, so a changed setting changes the sentence. The bonus for a harder question is mentioned without its number, to keep the sentence short; `xp_harder_question_bonus` is not in `rules`.
- **`UserChips` still holds its own 1000** for a subject without a rating, as before; the explanation's 1000 is the setting.

### The one-time hints

- **Where each shows:** XP and then the rating on a summary, on their cards; on Home the streak (on its chip: at the top on phones, in the sidebar from 1280 px), then the topics, then the subject switcher.
- **When:** the summary's two wait until the prompt to save progress is closed. The streak and the topics wait for a first finished session, since both read as nothing before it. The switcher's needs a second published subject. So a new student who lands on Home before playing sees only the switcher's hint.
- **One at a time.** "Entendi" lets the next hint of the screen show. Closing a hint any other way (a tap elsewhere, Esc) means the student is doing something else, and the next one waits until a screen with hints is opened again; otherwise a tap on "Mais uma" would flash the next hint while the session loads.
- **A hint that opens by itself does not take the focus** and does not close when the focus moves.
- **Shown hints are remembered on the device** (`localStorage`, `caramelcase.hints`), not on the account: no migration and no route. The cost is that a student sees them again on a new device or after clearing the browser. Signing out does not clear them.
- **Students who were using the app before this milestone get the hints too**, on their next summary and visit to Home.
- **Hints open only where they can be seen.** Both layouts' chips are in the page, one hidden by CSS, so `useIsDesktop()` (a media query at 1280 px) decides which one may open the streak's hint. It is the one place where JavaScript asks about the breakpoint.

### Tests and tools

- **jsdom gets a `ResizeObserver` that does nothing** (`web/src/test/setup.ts`): Radix's popover asks for one.
- **`npm run shots` starts with every hint already shown**, so the comparisons show the screens and not a hint over them; a scene can set `caramelcase.hints` to show one. Home now differs from its mockup by about 20% of pixels on phones, because everything under the greeting moved down 18 px, and by 2% on desktop.
- **The Playwright test closes each hint as it comes** and checks at the end that Home shows none a second time.

### Copy written for this milestone

In the voice of `design/copy.md`, in both languages, and the owner's to change in `web/src/i18n/`: the five explanations and their two buttons' labels under `explain`, "Entendi", and `home.topics_note`.

### Open, not decided

- **Whether a tap on a topic should practise that topic** (above).
- **Hints repeat on a new device.** Moving them to the account is a column on `user_settings` and a field in `PATCH /me/settings`.
- **V2 and V3 features have no explanations yet**: lives, streak freezes, leagues and achievements arrive with their own numbers. The plan's note under milestone 8.5 says how one is added.
