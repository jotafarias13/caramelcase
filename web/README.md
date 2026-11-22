# web

The React app. Read `../design/README.md` before touching a screen: the design handoff in `../design/` is the source of truth for looks, and it is consumed in place, never copied.

## Layout

```text
src/
  api/          client.ts (fetch, ApiError), queries.ts (every call, as hooks), types.ts,
                schema.d.ts and openapi.json (generated: make types)
  app/          App, providers, routes, the navigation shell, RequireUser, Flagged
  components/   shared pieces: ui/ (design/README.md's components), StateScreen, Mel, Wordmark,
                Explain (what a number means)
  features/     one directory per screen: landing, auth, onboarding, home, catalog,
                session, summary, profile, settings, legal
  i18n/         pt-BR.json, en.json and the setup
  lib/          theme, preferences, flags, highlight, analytics, monitoring, online,
                hints (the one-time hints)
  test/         fixtures.ts (sample API data), mock-api.ts, render.tsx
shots/          screenshots of the app next to the mockups
e2e/            the Playwright test against the real stack
eslint-rules/   no-hardcoded-copy
```

## Rules

- **Styling** is Tailwind classes that resolve to the design's tokens (`bg-surface`, `text-fg-muted`, `rounded-lg`, `shadow-step-md`; the names are in `../design/tailwind.theme.js`). Pixel values the mockups write inline become arbitrary values: `text-[15px] leading-[22px]`. Never a hex colour. Breakpoints: `md:` is 768 px and `lg:` is 1280 px; build the phone layout first.
- **Copy** comes from `src/i18n/pt-BR.json` and `en.json`, through `t("section.key")`. The texts are those of `../design/copy.md`; sample values in them (names, numbers) become `{{variables}}`. Keys are checked at compile time, both files must have the same keys (a test), and `local/no-hardcoded-copy` fails the lint on text written into a component. Names of subjects and topics come from the API in both languages: `localName(subject)`.
- **Server state** goes through the hooks of `src/api/queries.ts`; add a hook there for a new call. Components keep only UI state. There is no global store.
- **Every screen has its states.** While its data loads: `<LoadingState />`. When a request failed: `<FailureScreen error={query.error} onRetry={query.refetch} />`, which picks offline, maintenance, 404 or error. Nothing to show yet: `<EmptyState>`.
- **Nothing depends on hover**, touch targets are at least 44 px, and anything at a screen edge adds `env(safe-area-inset-*)`.
- **Icons** are `lucide-react`, by the name in the mockup's `data-lucide`. **Mel** is `<Mel pose="wave" scale={6} />`, or `head` for the head crop.
- **Flags:** `useFlag("reminders")` for a piece of a screen, `<Flagged flag="...">` around a lazy route.
- **A number a student may not understand explains itself.** Wrap its button in `<Explain topic="xp">`, with the dotted `explainedLabel` on its label, or put an `<ExplainButton>` beside it where there is no button. `hint` also opens it once without being asked: set it in one place per topic, with the condition under which it makes sense. A new topic is an id in `HINTS` (`src/lib/hints.ts`), a text under `explain` in both translation files and a case in `useExplanation`; a number it quotes comes from `rules` in `/config`, never from the copy. In a test, a hint is a `dialog` named "Explicação": name the dialog you mean (`{ name: "Trocar matéria" }`) rather than asking for any.

## Tests

`npm test` runs Vitest. `renderApp("/home", { routes })` renders the whole app at an address against a mock API whose answers are the "world" of `src/test/fixtures.ts`; `routes` replaces answers (`"GET /me": guest`, `"POST /sessions": apiError(409, "no_questions")`). `api.callsTo("PATCH /me/settings")` lists what the app sent. Look things up the way a student would: by role and name.

## The end-to-end test

`e2e/guest-session.spec.ts` is the one Playwright test: a new guest goes from the landing page through onboarding and ten questions to the summary, then Home, Profile and Settings, against the real API and database. It runs in Portuguese at 360 px and in English at 1280 px, and finds everything by role and by the texts of the translation files, so a change of copy does not break it.

```bash
make up && make seed      # from the repository root, once
npx playwright install chromium
npm run e2e               # or make e2e from the root
```

It is part of CI, not of `npm test`.

## Checking a screen against its mockup

```bash
npm run dev -- --port 5180 --strictPort    # once, in another terminal
npm run shots                              # every scene
npm run shots -- -g v1-home                # the scenes whose name contains v1-home
```

A scene (`shots/scenes/<feature>.ts`) names a mockup, an address, the API's answers and, if needed, a few clicks. For each scene and theme, `shots/out/` gets four files: `<mockup>-<theme>.mockup.png`, `.app.png`, `.side.png` (mockup left, app right) and `.diff.png` (the app, with the pixels that differ in magenta), and the run prints the share of pixels that differ. Text placed one pixel off shows as a magenta outline; a wrong size or colour shows as a block. `node shots/print-mockup.mjs v1-home-mobile` prints a mockup one element per line without the icons' path data, to look values up.
