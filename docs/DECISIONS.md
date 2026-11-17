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
