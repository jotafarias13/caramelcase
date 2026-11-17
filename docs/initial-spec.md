# CaramelCase — Build Spec for Claude Code

Nov 16, 2026 · @João Lucas Farias

Build CaramelCase, a Duolingo-style practice app for computer science students, as a React single-page app on a FastAPI and Postgres backend. V1 ships; V2 and V3 are built now behind feature flags.

## Mission and ground rules

The product is five-minute practice sessions of multiple-choice CS questions with adaptive difficulty, explanations, and a streak. Brazilian Portuguese first, English second.

**Priorities, in order.**

1. A correct, verified question bank for the three launch subjects.
2. A complete data model and backend for all three versions.
3. A working V1 web app a student can use end to end.
4. V2 and V3 features, built behind feature flags that are off by default.

**How to work.**

- The owner reviews and debugs the backend himself and is strongest in Python. Favor plain, readable code over clever abstractions. Type everything. Keep functions short and name things literally.
- Do not block on external accounts. Everything must run locally with `docker compose up`, using mock providers for email, ads, billing, and the AI tutor.
- Every milestone ends with passing tests and a commit. Never leave the main branch broken.
- Put business rules (rating, selection, streak, entitlements) in pure functions with unit tests, separate from routes and database code.
- All tunable numbers (session length, K-factors, plan limits, ad frequency) live in one typed settings module, not scattered through the code.
- Run the content pipeline in parallel with application work, using subagents.
- The UI design arrives later as tokens and mockups. Until then, build against placeholder design tokens so the real ones drop in without code changes.
- When the spec is silent, choose the simplest option, record it in `docs/DECISIONS.md`, and continue.

## Stack and repository layout

This project is a monorepo: frontend, backend, content, deployment files, and docs all live in a single GitHub repository, and nothing is split into separate repos. It has three top-level packages: `web`, `api`, `content`.

| Layer | Choice |
| --- | --- |
| Frontend | React, TypeScript, Vite, Tailwind CSS. Client-side rendered single-page app |
| Frontend libraries | React Router, TanStack Query, react-i18next, shadcn/ui (Radix) primitives, Lucide icons, a light syntax highlighter |
| Backend | Python 3.12, FastAPI, Pydantic v2, pydantic-settings |
| Database | PostgreSQL 16, SQLAlchemy 2 (async, asyncpg), Alembic migrations |
| Auth | Implemented in the API: guest accounts, Google sign-in (Authlib), email magic links. No third-party auth service |
| Background work | A Typer CLI (`python -m app.cli ...`) run by cron. No Celery or Redis in V1 |
| Email | An `EmailSender` interface with a console implementation for development and an SMTP implementation for production |
| Web server | nginx serves the built frontend and proxies `/api` to Uvicorn. TLS by certbot. The owner supplies working config examples |
| Hosting | A single Linux server on DigitalOcean or AWS, Docker Compose |
| Mobile (V2) | Capacitor wrapping the same built frontend |
| Tests | pytest and httpx for the API; Vitest and Testing Library for components; Playwright for one end-to-end path |

```text
caramelcase/
  api/
    app/
      main.py            # FastAPI app, router registration
      settings.py        # all tunables and env config
      db/                # models, session, migrations (alembic)
      domain/            # pure logic: rating, selection, streak, review, entitlements
      routes/            # one module per API area
      services/          # orchestration: sessions, auth, billing, ads, tutor
      providers/         # email, billing, ads, tutor: interface + mock + real
      cli.py             # import-content, grant-plan, send-reminders, ...
    tests/
  web/
    src/
      app/               # router, providers, layout shell
      features/          # auth, catalog, session, stats, settings, review, exam, ...
      components/        # shared UI components
      styles/tokens.css  # design tokens as CSS variables
      i18n/              # pt-BR.json, en.json
  content/
    catalog.yaml         # subjects and topics
    prompts/             # generation and blind-solve instructions
    bank/<subject>/<topic>.jsonl
    tools/               # validate, strip-keys, run-code, dedupe, report
  deploy/                # Dockerfiles, compose files, nginx drafts, backup script
  docs/                  # ARCHITECTURE.md, DECISIONS.md, RUNBOOK.md
```

## Release scope and feature flags

V1 has no flags: it is the app. Every V2 and V3 feature sits behind a flag stored in the `feature_flags` table, off by default, readable by the frontend through `GET /config`.

**V1, always on**

- Guest play, then optional sign-in with Google or an email magic link
- Subject and topic catalog, with three published subjects
- Practice sessions of 10 multiple-choice questions, graded on the server
- After each answer: correct or wrong, and a short reason under every option. A user setting turns the per-option reasons off
- Adaptive rating per subject, XP, daily goal, streak
- Profile and stats, question reports, settings, account deletion
- Portuguese and English interface; installable as a PWA

| Flag | Feature | Release |
| --- | --- | --- |
| `review_queue` | Spaced-repetition review of missed questions | V2 |
| `question_types_v2` | True or false, predict the output, find the bug, fill in the blank, order the steps | V2 |
| `exam_mode` | Timed mock exam with results by topic | V2 |
| `leagues` | Weekly leaderboard with promotion and relegation | V2 |
| `achievements` | Badges | V2 |
| `lives` | Lives that drop on wrong answers and refill over time. Separate flag \`streak\_freeze\` (V2): earned freezes that protect a missed day | V2 |
| `reminders` | Email and push reminders | V2 |
| `admin_console` | Question review tool for staff | V2 |
| `billing` | Paid plans, limits, checkout | V3 |
| `ads` | Ad breaks for free users | V3 |
| `beat_the_ad` | Challenge question and double or nothing before an ad break. Separate flag \`streak\_repair\` (V3): restore a lost streak within 48 hours | V3 |
| `ai_tutor` | Chat about a wrong answer or a topic | V3 |
| `exam_tracks` | Exam-specific tracks with ranking | V3 |
| `write_code` | Write-code questions, executed in the browser | V3 |
| `referral` | Invite a classmate | V3 |

A flag has three states: off, on for staff only, on for everyone.

## Data model

Create every table below in the first migrations, including those only V2 and V3 use. UUID primary keys, `created_at` and `updated_at` everywhere, timestamps in UTC.

**Identity**

| Table | Key columns | Notes |
| --- | --- | --- |
| `users` | email (nullable), display\_name, locale, timezone, is\_guest, role | A guest is a real row; signing in upgrades it and keeps its history |
| `auth_identities` | user\_id, provider, provider\_subject | Providers: google, email |
| `sessions_auth` | user\_id, token\_hash, expires\_at | Opaque tokens, stored hashed |
| `magic_links` | email, token\_hash, expires\_at, used\_at | Single use, 15-minute expiry |
| `user_settings` | daily\_goal, theme, show\_option\_reasons (default true), notification prefs | One row per user |

**Content**

| Table | Key columns | Notes |
| --- | --- | --- |
| `subjects` | slug, name\_pt, name\_en, status, sort\_order | Status: draft, published |
| `topics` | subject\_id, slug, name\_pt, name\_en, sort\_order |  |
| `topic_edges` | from\_topic, to\_topic, kind, weight | Prerequisite and related links. Seeded later; not used by selection in V1 |
| `questions` | subject\_id, topic\_id, type, status, difficulty\_prior, rating, answers\_count, correct\_count, content\_hash, version, source | Status: draft, verified, published, retired. Never deleted |
| `question_translations` | question\_id, locale, stem, code, code\_language, payload (JSONB), explanation | `payload` holds the options, each with key, text, is\_correct, and reason |
| `question_reports` | question\_id, user\_id, reason, comment, status |  |

**Practice**

| Table | Key columns | Notes |
| --- | --- | --- |
| `practice_sessions` | user\_id, subject\_id, mode, question\_ids, started\_at, finished\_at, correct\_count, xp\_earned | Modes: practice, review, exam, challenge |
| `attempts` | user\_id, question\_id, session\_id, answer (JSONB), is\_correct, time\_ms, user\_rating\_before, question\_rating\_before, locale | The raw history; everything else can be rebuilt from it |
| `user_subject_ratings` | user\_id, subject\_id, rating, answers\_count |  |
| `user_topic_mastery` | user\_id, topic\_id, correct, total, last\_seen\_at |  |
| `daily_activity` | user\_id, local\_date, xp, questions, goal\_met | Drives streak and calendar |
| `streaks` | user\_id, current, longest, last\_active\_date, freezes |  |
| `review_items` | user\_id, question\_id, due\_at, interval\_days, lapses | Written from V1 on every wrong answer, so V2 starts with data |

**V2 and V3**

| Table | Key columns | Notes |
| --- | --- | --- |
| `feature_flags` | key, state | Off, staff, on |
| `league_weeks`, `league_memberships` | week\_start, tier, user\_id, xp |  |
| `achievements`, `user_achievements` | key, unlocked\_at |  |
| `exam_templates`, `exam_attempts` | track, duration\_min, composition (JSONB), score, per-topic results |  |
| `plans` | key, price\_month\_brl, price\_year\_brl, limits (JSONB) | Seed: free 0, plus 15, pro 40, max 100 |
| `subscriptions` | user\_id, plan\_key, status, provider, provider\_ref, current\_period\_end | The only source of truth for what a user has paid for |
| `usage_counters` | user\_id, local\_date, questions\_answered, tutor\_messages | Enforces daily limits |
| `ad_events` | user\_id, kind, meta (JSONB) | Break due, challenge offered, won, lost, double accepted, ad shown, rewarded completed |
| `tutor_threads`, `tutor_messages` | user\_id, question\_id (nullable), role, content |  |
| `events` | user\_id, name, props (JSONB) | First-party product analytics |

## Question format and content pipeline

Questions are authored as JSONL files in `content/bank/`, one question per line, and imported into Postgres. The files are the source of truth for question text; the database is the source of truth for everything live (rating, statistics, status, reports).

**Format.** One Pydantic model, `QuestionDoc`, validates every line.

```json
{
  "id": "estruturas-de-dados.pilhas.0001",
  "subject": "estruturas-de-dados",
  "topic": "pilhas",
  "type": "mcq",
  "difficulty_prior": 1,
  "correct_key": "b",
  "code_language": null,
  "source": "generated",
  "version": 1,
  "locales": {
    "pt-BR": {
      "stem": "Qual estrutura de dados segue a política LIFO?",
      "code": null,
      "options": [
        {"key": "a", "text": "Fila", "reason": "A fila é FIFO: quem entra primeiro sai primeiro."},
        {"key": "b", "text": "Pilha", "reason": "Na pilha, o último elemento inserido é o primeiro a sair."},
        {"key": "c", "text": "Lista ligada", "reason": "A lista ligada não impõe ordem de remoção."},
        {"key": "d", "text": "Árvore binária", "reason": "A árvore organiza hierarquia, não ordem de chegada."}
      ],
      "explanation": "LIFO significa que o último a entrar é o primeiro a sair, como uma pilha de pratos."
    },
    "en": {"stem": "...", "code": null, "options": [], "explanation": "..."}
  },
  "verification": {"blind_key": "b", "blind_agrees": true, "code_ran": null, "human_checked": false}
}
```

- `id` is a stable slug, stored in a unique `questions.external_id` column.
- Every option carries a `reason` in both languages: one sentence, at most 160 characters, saying why that option is right or wrong.
- `difficulty_prior` runs from 1 to 5 and only seeds the starting rating.
- Option order is shuffled when served; keys stay stable.

**Writing rules.**

- Exactly one defensible answer. No "all of the above", no "none of the above", no trick wording.
- Distractors come from real misconceptions, and are similar in length and form to the correct option.
- Test understanding over recall where the topic allows it.
- Code is at most 15 lines, runs as written, and is deterministic. Python by default; C or SQL where the subject calls for it.
- Spread each topic across difficulties: roughly 25% level 1 to 2, 50% level 3, 25% level 4 to 5.
- Portuguese is written natively, not translated word for word. Keep code and identifiers identical across languages.

**Pipeline.** Generation and blind solving are done by Claude Code subagents writing files. The other steps are Python tools in `content/tools/`.

1. **Outline.** For each subject, write its topics into `content/catalog.yaml` from the syllabus the owner supplies.
2. **Generate.** One subagent per topic writes `bank/<subject>/<topic>.jsonl`, following `prompts/generate.md`.
3. **Validate.** Schema, four unique options, one correct key, reasons present in both languages, length limits.
4. **Blind solve.** `strip-keys` exports the questions without answers or reasons. A fresh subagent that has never seen the keys answers them. Any disagreement marks the question as failed.
5. **Run code.** For questions with code and a deterministic output, execute the snippet in a subprocess with a timeout and compare against the key.
6. **Dedupe.** Flag near-duplicate stems within a subject.
7. **Repair or drop.** Failed questions get one regeneration attempt, then are dropped. Never hand-wave a disagreement.
8. **Import.** `python -m app.cli import-content` upserts by `external_id`. A changed `content_hash` bumps `version`. Missing questions are retired, never deleted.

**Targets.** About 400 questions for each of the three launch subjects, imported as `verified`. A subject becomes `published` only after the owner has checked a sample by hand and set the flag. Then generate further subjects from the catalog as `draft`, as far as time allows.

Write `content/REPORT.md` after each run: counts per subject, topic, and difficulty, plus failure rates at each step.

## Core logic

All of this lives in `api/app/domain/` as pure functions with unit tests. Every number below is a default in `settings.py`.

**Grading.** The server grades. A session is created with a fixed list of question ids. The client receives stems and options only; the correct key, the per-option reasons, and the explanation are returned by the answer endpoint after the student commits.

**Rating.** Each student has a rating per subject and each question has its own rating, updated together after every first attempt.

```latex
E = \frac{1}{1 + 10^{(R_q - R_u)/400}} \qquad P = 0.25 + 0.75\,E
```

```latex
R_u' = R_u + K_u\,(S - P) \qquad R_q' = R_q - K_q\,(S - P)
```

- S is 1 for a correct answer and 0 otherwise. P adjusts for the 25% chance of guessing among four options.
- A student starts at 1000. A question starts from its prior: levels 1 to 5 map to 700, 850, 1000, 1150, 1300.
- K for the student is 32 for the first 30 answers in a subject, then 16.
- K for the question is 16 for its first 50 answers, then 4.
- Only a student's first attempt at a question moves either rating. Review attempts never do.

**Question selection.** Aim for a predicted success of about 80%.

1. Candidates: published questions in the subject, available in the student's language, not answered by them in the last 14 days. Relax the 14 days if too few remain.
2. Score each candidate by the distance between its P and 0.80. Keep the 30 closest.
3. Sample 10 at random from those, with at most 3 from any one topic.
4. When `review_queue` is on, up to 3 of the 10 slots go to due review items first.
5. A student's first session in a subject uses prior levels 2 and 3 only, to calibrate quickly.

**XP, goal, streak.**

- 10 XP per correct answer, 5 more when the question's rating is above the student's, and 10 for finishing a session.
- The daily goal counts questions answered: 10, 20, or 30 a day (one, two, or three sessions). XP stays a separate score, shown in the session summary and profile.
- A day counts toward the streak when the student finishes at least one session, by local date in their timezone. When \`streak\_freeze\` is on: meeting the daily goal 7 days in a row earns a freeze, a student holds at most 2, and a freeze is spent automatically on a missed day so the streak survives. When \`streak\_repair\` is on: for 48 hours after a streak is lost, the student can restore it; free users by completing an opt-in rewarded ad, paid plans with one tap. Record each freeze earned, freeze used, and repair in \`events\`.

**Topic mastery.** From correct and total answers per topic: new (under 5 answers), learning (under 60%), practiced (60 to 85%), mastered (85% or more with at least 10 answers).

**Review schedule.** A wrong answer creates a review item due the next day. A correct review multiplies the interval by 2.5 (1, 3, 7, 18, 45 days); a wrong one resets it to 1. Items leave the queue once the interval passes 60 days.

## API

All routes are under `/api/v1`, return JSON, and are described by Pydantic models so the OpenAPI schema is accurate. Generate the frontend's TypeScript types from that schema.

| Area | Routes | Release |
| --- | --- | --- |
| Auth | `POST /auth/guest` · `GET /auth/google/start` · `GET /auth/google/callback` · `POST /auth/magic-link` · `POST /auth/magic-link/verify` · `POST /auth/logout` | V1 |
| Account | `GET /me` · `PATCH /me/settings` · `GET /me/export` · `DELETE /me` | V1 |
| Config | `GET /config` (flags, plan limits, the user's entitlements) | V1 |
| Catalog | `GET /subjects` · `GET /subjects/{slug}` (topics with the user's mastery) | V1 |
| Practice | `POST /sessions` · `POST /sessions/{id}/answers` · `POST /sessions/{id}/finish` · `GET /sessions/{id}` | V1 |
| Stats | `GET /me/stats` · `GET /me/activity` | V1 |
| Reports | `POST /questions/{id}/report` | V1 |
| Events | `POST /events` (batched product analytics) | V1 |
| Review | `GET /review/due` (then `POST /sessions` with mode `review`) | V2 |
| Exams | `GET /exams` · `POST /exams/{id}/attempts` · `POST /exam-attempts/{id}/submit` | V2 |
| Leagues, achievements | `GET /leagues/current` · `GET /achievements` | V2 |
| Admin | `GET /admin/questions` · `PATCH /admin/questions/{id}` · `GET /admin/reports` · `PUT /admin/flags/{key}` | V2 |
| Billing | `GET /plans` · `POST /billing/checkout` · `POST /billing/webhook/{provider}` · `POST /billing/cancel` | V3 |
| Ads | `GET /ads/next-break` · `POST /ads/challenge` · `POST /ads/events` | V3 |
| Tutor | `POST /tutor/threads` · `POST /tutor/threads/{id}/messages` (streamed) | V3 |

**Answer response.** `POST /sessions/{id}/answers` returns: is\_correct, correct\_key, the reason for every option, the explanation, the rating change, XP earned, and whether the session is complete. The frontend decides whether to show the per-option reasons from the user's setting; the API always sends them.

**Rules for every route.**

- A flagged route returns 404 while its flag is off.
- Entitlements are checked on the server. The frontend only mirrors them.
- No route returns questions in bulk with their answers.
- Errors use one shape: `{"error": {"code": "...", "message": "..."}}`.

## Frontend

A client-side rendered React app organized by feature, where every color, size, and string comes from tokens or translation files.

- **Routes:** `/` (landing), `/start` (onboarding), `/home`, `/subjects`, `/session/:id`, `/session/:id/summary`, `/profile`, `/settings`, `/signin`, `/auth/callback`. Flagged: `/review`, `/exam`, `/leagues`, `/pricing`, `/tutor`, `/admin`.
- **Landing page:** the only page that needs search visibility. Pre-render it to static HTML at build time; everything else is client-rendered.
- **Design tokens:** `styles/tokens.css` defines CSS variables for color, type, spacing, radius, and shadow in light and dark. Tailwind reads those variables. Ship neutral placeholder values now; the design handoff replaces the file.
- **No hardcoded strings.** All copy lives in `i18n/pt-BR.json` and `i18n/en.json`. Default to Portuguese; detect the browser language on first visit.
- **Server state** through TanStack Query; local UI state in components. No global store unless a real need appears.
- **Session screen:** keys 1 to 4 select an option and Enter confirms. Code blocks scroll horizontally. The answer panel shows the result, then a reason under each option when `show_option_reasons` is on, then the continue button.
- **Guest first:** the first visit creates a guest account silently. Prompt to sign in after the first finished session.
- **Flags:** a `useFlag(key)` hook reads `/config`. Flagged features do not render or load their code when off.
- **Resilience:** loading, empty, error, and offline states for every screen. An interrupted session resumes where it stopped.
- **PWA:** manifest, icons, and a service worker that caches the app shell only.
- **Native later:** nothing may depend on hover, and layouts must respect safe areas, because the same build runs inside Capacitor in V2.

## Monetization structure

None of this is visible in V1, but the tables, interfaces, and logic are built and tested now. While `billing` is off, every user is treated as having no limits and no ads.

**Plans.** Seeded in the `plans` table. Prices are set; the limits are placeholders to tune later.

| Plan | Price per month | Practice | Ads | AI tutor | Exam mode and tracks |
| --- | --- | --- | --- | --- | --- |
| Free | R$0 | 3 sessions a day | Yes | No | No |
| Plus | R$15 | Unlimited | No | No | Exam mode |
| Pro | R$40 | Unlimited | No | 30 messages a day | Exam mode |
| Max | R$100 | Unlimited | No | 200 messages a day | Exam mode and tracks |

**Entitlements.** One pure function, `entitlements_for(user, subscription, flags)`, returns what the user may do. Routes call it; nothing else decides access. `usage_counters` enforces the daily numbers. A CLI command, `grant-plan <email> <plan> <days>`, grants a plan by hand for testing.

**Billing.** A `BillingProvider` interface with `create_checkout`, `handle_webhook`, and `cancel`. Build a mock provider that completes instantly, and a Stripe adapter with card subscriptions and one-time Pix for annual and semester passes. Webhooks are idempotent and only ever write to `subscriptions`. Store purchases (Google Play, Apple) are later adapters on the same interface.

**Ads.** The server schedules breaks; the client only displays them.

- A free user is due an ad break every 2 sessions.
- When `beat_the_ad` is on, the break is preceded by a challenge question slightly above the student's level.
- Correct: the ad is skipped. Wrong: the ad plays.
- After a correct challenge the student may go double or nothing on a second, harder question. Win: the next break is pushed back by 2 further sessions. Lose: the ad plays and the next break arrives 1 session sooner.
- Opt-in offers (for example, watch an ad to restore a life) always include a decline option that costs nothing.
- An `AdProvider` interface on the frontend has a mock implementation showing a 5-second house ad. The AdMob implementation comes with the Capacitor build.
- Every step is recorded in `ad_events`.

**AI tutor.** A `TutorProvider` interface with a streaming `reply` method, a mock implementation returning canned text, and a real adapter configured by environment variables. The prompt includes the question, the options with their reasons, and the student's answer. Enforce the daily message limit before calling the provider, and cap tokens per reply.

**Write-code questions.** Student code runs in the browser (Pyodide for Python). The server never executes student code.

## Auth, security, privacy

Auth is implemented in the API with opaque session tokens, so there is no third-party auth service to learn or depend on.

- **Session tokens:** random 256-bit values, stored hashed in `sessions_auth`. The web app receives them as an httpOnly, Secure, SameSite=Lax cookie. The native wrapper sends the same token as a bearer header.
- **Guests:** `POST /auth/guest` creates a user with `is_guest` true. Signing in attaches an identity to that same user. If the email already belongs to another user, merge the guest's history into it.
- **Google:** standard authorization-code flow with Authlib. **Magic link:** a single-use token emailed to the user, valid for 15 minutes.
- **No passwords** are stored anywhere.
- **Rate limits** on auth routes, the answer route, reports, and the tutor.
- **CSRF:** state-changing routes require a custom header that browsers will not send cross-site.
- **CORS** is limited to the app's own origins, read from settings.
- **Roles:** user, staff. Admin routes require staff.
- **Privacy (LGPD):** store only email, display name, locale, and timezone. `GET /me/export` returns the user's data and `DELETE /me` erases it. Keep a plain-language privacy policy and terms page in both languages, with placeholder legal text for the owner to complete.
- **Secrets** come from environment variables only. Commit a `.env.example`, never a real `.env`.
- **Content protection:** questions are served only inside sessions, a few at a time.

## Deployment, testing, definition of done

**Local development.** `docker compose up` starts Postgres, the API with reload, and the Vite dev server. `make seed` runs migrations, imports the content, seeds plans and flags, and creates a demo user with history.

**Production.** One Linux server running Docker Compose.

- nginx on the host serves `web/dist` and proxies `/api` to the API container. TLS by certbot.
- The owner will supply nginx and certbot configs he has used before. Adapt those; do not invent a different setup. Until they arrive, leave a clearly marked draft in `deploy/`.
- Postgres runs either as a container with a named volume or as a managed database; the API only needs `DATABASE_URL`.
- Provide `deploy/backup.sh` (nightly `pg_dump`, 14 days kept) and a restore procedure in `docs/RUNBOOK.md`.
- Migrations run as an explicit deploy step, never automatically on start.
- A `/api/v1/health` route checks the database.
- Structured JSON logs. Error tracking and external analytics are optional and enabled only when their keys are set.

**Tests.**

- Unit tests for every function in `domain/`: rating, selection, XP, streak across timezones, review schedule, entitlements, ad scheduling.
- API tests against a real test database for auth flows, a full practice session, limits, and flags returning 404 when off.
- Content tests: every line in `content/bank/` validates.
- One Playwright test: a guest opens the landing page, finishes a session, and sees the summary.
- GitHub Actions runs lint, type checks, and all tests on every push.

**Done means.**

- A new developer can clone, run two commands, and play a session locally.
- V1 works end to end in both languages with all flags off.
- Each V2 and V3 feature works locally with its flag on and its mock provider.
- `docs/ARCHITECTURE.md` explains the request path, the data model, and where each business rule lives.
- `docs/DECISIONS.md` lists every choice made where this spec was silent.

## Work order

Steps 3 and 4 onward run in parallel: content generation in subagents, application work in the main session.

1. **Scaffold.** Repository layout, tooling, Docker Compose, CI, placeholder design tokens.
2. **Schema.** All models and migrations for V1 to V3. Seed plans, flags, and the subject catalog.
3. **Content, launch subjects.** Outlines, generation, validation, blind solve, code runs, import, report.
4. **V1 backend.** Auth, catalog, sessions and grading, rating, XP and streak, stats, reports, config, events.
5. **V1 frontend.** Landing, onboarding, home, session, feedback, summary, profile, settings, sign-in, system states, both languages, PWA.
6. **V1 hardening.** Tests, the Playwright path, rate limits, export and delete, docs.
7. **Deployment files.** Dockerfiles, production compose, env template, backup script, nginx draft.
8. **V2 behind flags.** Review queue, new question types, exam mode, lives, achievements, leagues, reminders, admin console.
9. **V3 behind flags.** Entitlements and limits, billing with mock and Stripe adapters, ad scheduling and Beat the ad, AI tutor, exam tracks, write-code questions, referral.
10. **Design pass.** When the design handoff arrives, replace the tokens and align components and screens to the mockups.
11. **More content.** Further subjects from the catalog as drafts, in catalog order.
12. **Capacitor shell.** Android project that loads the built app. Not published.

## Subject catalog

Seed all 20 subjects in `content/catalog.yaml` as drafts; generate questions for the three launch subjects first, then continue in this order. "Typical year" is a general guide for Brazilian computing degrees, to be matched against the real curriculum by the owner.

| # | Subject | English name | Typical year | Launch |
| --- | --- | --- | --- | --- |
| 1 | Introdução à Programação | Introduction to Programming | 1 | Yes |
| 2 | Estruturas de Dados | Data Structures | 1 to 2 | Yes |
| 3 | Banco de Dados | Databases | 2 | Yes |
| 4 | Programação Orientada a Objetos | Object-Oriented Programming | 1 to 2 |  |
| 5 | Matemática Discreta | Discrete Mathematics | 1 |  |
| 6 | Lógica para Computação | Logic for Computing | 1 |  |
| 7 | Análise e Projeto de Algoritmos | Algorithm Design and Analysis | 2 |  |
| 8 | Circuitos Digitais | Digital Circuits | 1 to 2 |  |
| 9 | Arquitetura e Organização de Computadores | Computer Architecture | 2 |  |
| 10 | Sistemas Operacionais | Operating Systems | 2 to 3 |  |
| 11 | Redes de Computadores | Computer Networks | 3 |  |
| 12 | Engenharia de Software | Software Engineering | 2 to 3 |  |
| 13 | Teoria dos Grafos | Graph Theory | 2 to 3 |  |
| 14 | Probabilidade e Estatística | Probability and Statistics | 2 |  |
| 15 | Linguagens Formais e Autômatos | Formal Languages and Automata | 3 |  |
| 16 | Teoria da Computação | Theory of Computation | 3 |  |
| 17 | Paradigmas de Linguagens de Programação | Programming Language Paradigms | 2 to 3 |  |
| 18 | Compiladores | Compilers | 3 to 4 |  |
| 19 | Inteligência Artificial e Aprendizado de Máquina | AI and Machine Learning | 3 to 4 |  |
| 20 | Sistemas Distribuídos | Distributed Systems | 3 to 4 |  |

Later candidates: Segurança da Informação, Computação Gráfica, Interação Humano-Computador, Cálculo, Álgebra Linear.

## What the owner provides

None of these block the build; each has a mock or placeholder until it arrives.

- [ ] Syllabus text for the three launch subjects, to shape the topic outlines
- [ ] nginx and certbot configuration examples from earlier deployments
- [ ] The design handoff: tokens, mockups, SVG assets
- [ ] Hosting choice (DigitalOcean or AWS) and the domain
- [ ] Google OAuth client id and secret
- [ ] SMTP credentials for sign-in emails
- [ ] A hand check of about 50 questions per launch subject before it is published
- [ ] Final free-plan limits and ad frequency (placeholders are in the monetization section)
- [ ] Legal text for the privacy policy and terms
