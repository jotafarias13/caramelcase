# CaramelCase

A Duolingo-style practice app for computer science students: React SPA in `web/`, FastAPI and Postgres in `api/`, question bank in `content/`.

## Before any work

Read `docs/initial-spec.md` and `docs/PLAN.md` in full. The spec says what to build; the plan says in what order, what is already done, and which decisions override the spec. Resume at the first unticked box in the plan.

## Finishing a milestone

A milestone is done when every acceptance box under it holds and lint, type checks and tests pass. Then, in this order:

1. Tick its boxes in `docs/PLAN.md`.
2. Add to `docs/DECISIONS.md` every choice made where the spec was silent and every conflict between spec and design.
3. Commit to `main` with a `feat:`, `fix:` or `chore:` message and a body saying what changed and why.

Push only when the owner asks. `main` always passes its tests.

## Rules that outlast any one task

- **Spec against design:** the spec wins on behaviour, the design wins on looks. `docs/PLAN.md` wins over both where it records an agreed change.
- **Design:** `design/` is the finished handoff and the source of truth for the UI. Consume `design/tokens.css` and `design/tailwind.theme.js` unchanged, take copy from `design/copy.md`, and read a screen's mockup files in `design/screens/` in full before building that screen.
- **When the spec is silent:** choose the simplest option, record it in `docs/DECISIONS.md`, and continue.
- **Python:** uv runs everything, with ruff, pytest and mypy.
- **Business rules** live as pure, unit-tested functions in `api/app/domain/`; every tunable number lives in `api/app/settings.py`.
- **Content generation and blind solving** run in subagents. A blind solver is a fresh agent that has seen only the stripped file.
- **`../kai-app` and `../kai-api`** are the owner's reference projects for nginx, certbot, deploy workflows and logging. Read them, leave them unchanged.
- **`syllabus-v1.txt`** stays out of the repo.
