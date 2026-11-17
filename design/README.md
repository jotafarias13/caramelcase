# caramelCase design handoff

Direction A2, "Terminal + caramel". This folder is the source of truth for building the UI. Everything is code: read exact values from the files, not from this page.

| Path | Contents |
| --- | --- |
| `README.md` | This document: tokens, components and states, motion, screens by release, open decisions |
| `tokens.css` | Every token as a CSS custom property, dark and light, plus shadcn/ui aliases |
| `tailwind.theme.js` | Tailwind theme extension that points at those variables |
| `screens/` | 139 HTML mockups, one per screen and device, styled only through `tokens.css` |
| `assets/` | 25 SVG files: wordmark, app icon, favicon, Mel sprites |
| `copy.md` | All interface text in PT-BR and EN, keyed by screen |

## How to read the screens

- Each file is a static mockup of one state, at a fixed frame: 360 px wide for phones, 1280 px for desktop. Frame heights are in the screen tables below.
- Colours, font families, radii and shadows are always `var(--token)`. Spacing and font sizes are written as pixel values inline; they sit on the spacing and type scales listed here, and Tailwind's default 4 px spacing scale matches.
- Open a file and change `data-theme="dark"` to `"light"` on `<html>` to see the other theme. The same markup serves both.
- Icons are inline Lucide SVGs. The Lucide name is in each icon's `data-lucide` attribute; use `lucide-react` in the build.
- Mel sprites are inline pixel SVGs copied from `assets/`. In the build, load the asset files and render them with `image-rendering: pixelated` at whole-number scales.
- Code blocks carry `data-code`. Each screen root carries `data-screen` and `data-device`.
- The mockups are not responsive. Build mobile-first and use the desktop file for the layout from 1280 px; between 768 and 1279 px use the mobile layout with 24 px gutters and a centred column of at most 640 px.
- About 20 of the mockups were rendered in Chrome with the real fonts and checked by eye, in both themes; the rest come from the same code but were not looked at one by one. If a mockup and this README disagree, the token values and component rules in this README win; report the mismatch.

## Brand

- **Name:** caramelCase, written in camelCase. The capital C sits in an inverted block: a caramel block with an ink letter on dark and light grounds, an ink block with a caramel letter on caramel.
- **Mascot:** Mel, a caramel street dog drawn as a 22 × 23 px pixel sprite on a 26 × 27 px canvas. Seven expressions, each with a head-only crop of 21 × 14 px.
- **Voice:** a sharp classmate, not a teacher. Informal "você". Wrong answers get encouragement, never sarcasm.
- **Colour idea:** caramel is a surface (question header, goal card, active navigation), cyan is the one primary action, and pink, violet and lime belong to streak, XP and rating.

## Tokens

### Theme colours

| Token | Dark | Light | Use |
| --- | --- | --- | --- |
| `--bg` | `#1B2140` | `#F4F5FB` | App background |
| `--bg-well` | `#141833` | `#FFFFFF` | Inputs, bar tracks, wells |
| `--surface` | `#252C52` | `#FFFFFF` | Cards, options, sheets |
| `--surface-raised` | `#313966` | `#E9ECF7` | Hover fill, raised tiles |
| `--border` | `#4A5488` | `#D3D8EC` | Dividers, card outlines (decorative) |
| `--border-strong` | `#6876A6` | `#7C86AE` | Control boundaries (3:1 on background) |
| `--text` | `#F4F5FB` | `#141833` | Primary text |
| `--text-muted` | `#B4BCDA` | `#4A5380` | Secondary text |
| `--text-subtle` | `#8F99BD` | `#5F6993` | Tertiary text, icons |
| `--brand` | `#F6A93B` | `#F6A93B` | Caramel fills: question header, goal card, active nav |
| `--brand-text` | `#F6A93B` | `#8F5300` | Caramel text on the theme background |
| `--brand-deep` | `#C47A17` | `#C47A17` | Hard shadow under caramel, progress borders |
| `--brand-cream` | `#FFE6B8` | `#FFE6B8` | Light text on ink, current progress segment |
| `--brand-pale` | `#FFF1D6` | `#FFF1D6` | Pale caramel wash |
| `--on-brand` | `#141833` | `#141833` | Text and icons on caramel |
| `--action` | `#40DDE6` | `#40DDE6` | Primary button fill, selection fill |
| `--action-hover` | `#74E8EF` | `#74E8EF` | Primary hover |
| `--action-pressed` | `#22BFC8` | `#22BFC8` | Primary pressed |
| `--action-shadow` | `#17868D` | `#141833` | Hard shadow under primary |
| `--on-action` | `#062329` | `#062329` | Text on primary |
| `--action-text` | `#40DDE6` | `#0A6F78` | Links, ghost buttons, selected icons |
| `--action-tint` | `#1C3D55` | `#DDF8FA` | Selected surface |
| `--action-border` | `#40DDE6` | `#0B8791` | Selected border (3:1) |
| `--correct` | `#3EE0A1` | `#3EE0A1` | Correct fill |
| `--correct-text` | `#3EE0A1` | `#08704A` | Correct text and icons |
| `--correct-tint` | `#1B4347` | `#DDF8EC` | Correct surface |
| `--correct-border` | `#3EE0A1` | `#0C8A5A` | Correct border |
| `--wrong` | `#FF6470` | `#FF6470` | Wrong fill, danger button |
| `--wrong-text` | `#FF8A93` | `#C21F33` | Wrong text and icons |
| `--wrong-tint` | `#472748` | `#FFE8EA` | Wrong surface |
| `--wrong-border` | `#FF6470` | `#D93445` | Wrong border |
| `--wrong-shadow` | `#A8303E` | `#141833` | Hard shadow under danger |
| `--warning` | `#FFD84A` | `#FFD84A` | Warning fill |
| `--warning-text` | `#FFD84A` | `#7A5600` | Warning text |
| `--warning-tint` | `#454030` | `#FFF6D1` | Warning surface |
| `--warning-border` | `#FFD84A` | `#9A6E00` | Warning border |
| `--info` | `#8DB4FF` | `#8DB4FF` | Info fill, streak-freeze chip |
| `--info-text` | `#8DB4FF` | `#2450C4` | Info text |
| `--info-tint` | `#26375F` | `#E6EEFF` | Info surface |
| `--info-border` | `#8DB4FF` | `#3B67D8` | Info border |
| `--streak` | `#FF5CB8` | `#FF5CB8` | Streak fill (pink, never orange) |
| `--streak-text` | `#FF7CC6` | `#C2187A` | Streak text |
| `--xp` | `#A58BFF` | `#A58BFF` | XP fill (violet) |
| `--xp-text` | `#B7A2FF` | `#5B3BD1` | XP text |
| `--rating` | `#B8F25A` | `#B8F25A` | Rating fill (lime) |
| `--rating-text` | `#B8F25A` | `#456F00` | Rating gain text |
| `--focus-ring` | `#FFFFFF` | `#141833` | Focus ring |
| `--shadow-hard` | `#141833` | `#BFC6E0` | Neutral hard shadow |
| `--overlay` | `rgba(10, 12, 32, 0.66)` | `rgba(20, 24, 51, 0.5)` | Backdrop behind modals and sheets |
| `--disabled-bg` | `#2B3157` | `#E4E7F3` | Disabled fill |
| `--disabled-text` | `#7781A8` | `#8B93B5` | Disabled text |
| `--btn-border` | `1.5px solid transparent` | `1.5px solid #141833` | Outline on filled buttons (visible in light only) |
| `--code-bg` | `#141833` | `#141833` | Code block background (dark in both themes) |
| `--code-border` | `#4A5488` | `#141833` | Code block outline |
| `--shadow-overlay` | `0 16px 40px rgba(6, 8, 24, 0.5)` | `0 16px 40px rgba(20, 24, 51, 0.22)` | Soft shadow for overlays and toasts |

### Fixed palette

These do not change with the theme.

| Token | Value | Use |
| --- | --- | --- |
| `--ink` | `#141833` | Always-dark navy: text on caramel, code background |
| `--ink-raised` | `#252C52` | Hover row inside code, key caps |
| `--ink-line` | `#4A5488` | Rules inside code blocks |
| `--ink-selected` | `#1C3D55` | Selected code line, filled blank |
| `--ink-text` | `#F4F5FB` | Text on ink |
| `--ink-muted` | `#B4BCDA` | Secondary text on ink |
| `--ink-subtle` | `#8F99BD` | Line numbers, comments |
| `--ink-24` | `rgba(20, 24, 51, 0.24)` | To-do progress segments on caramel |
| `--white` | `#FFFFFF` | QR code ground |
| `--on-correct` | `#06281C` | Text on the correct fill |
| `--on-wrong` | `#3A0A12` | Text on the wrong fill |
| `--on-xp` | `#1C1147` | Text on the XP fill |
| `--on-streak` | `#3A0A28` | Text on the streak fill |
| `--on-rating` | `#1F2E00` | Text on the rating fill |
| `--on-info` | `#0D1B45` | Text on the info fill |
| `--wrong-hover` | `#FF8088` | Danger hover |
| `--wrong-pressed` | `#F04C5A` | Danger pressed |
| `--xp-gain` | `#D9CDFF` | Fresh XP segment |
| `--syn-keyword` | `#A58BFF` | Keywords |
| `--syn-function` | `#F6A93B` | Function names |
| `--syn-number` | `#B8F25A` | Numbers |
| `--syn-string` | `#3EE0A1` | Strings |
| `--syn-comment` | `#8F99BD` | Comments |

Text on a tinted surface uses the matching `-text` token. Computed contrast: every text token is at least 4.78:1 on the background, the surface and its own tint in both themes, and `--border-strong` and the state borders are at least 3.28:1 against the background. Disabled text is exempt.

### Type

Two families, both SIL Open Font License on Google Fonts: **Geist** for UI and **JetBrains Mono** for code, labels and numbers. Never below 12 px, except 11 px mono labels and tab-bar labels. Inputs stay at 16 px so phones do not zoom. Numbers that change use `font-variant-numeric: tabular-nums`.

| Token | Size / line / weight | Family | Use |
| --- | --- | --- | --- |
| `--text-display` | 32 / 40 / 700 | Geist | Big moments: Mandou bem!, level up |
| `--text-title` | 24 / 32 / 700 | Geist | Screen titles |
| `--text-question` | 22 / 28 / 700 | Geist | Question text on phones (26/34 from 1280) |
| `--text-heading` | 18 / 24 / 700 | Geist | Section and card headings |
| `--text-body` | 16 / 24 / 400 | Geist | Default text, option labels, inputs |
| `--text-body-sm` | 14 / 20 / 400 | Geist | Secondary text, helper copy |
| `--text-caption` | 12 / 16 / 500 | Geist | Captions, meta |
| `--text-button` | 16 / 20 / 700 | Geist | Button labels (15 at md, 14 at sm) |
| `--text-label-mono` | 12 / 16 / 500 | JetBrains Mono | Lowercase labels, breadcrumbs, badges |
| `--text-code` | 13 / 21 / 400 | JetBrains Mono | Code on phones |
| `--text-code-lg` | 14 / 22 / 400 | JetBrains Mono | Code from 1280 |
| `--text-stat-mono` | 28 / 32 / 800 | JetBrains Mono | Rating and score numbers, tabular |

### Spacing

4 px base: 0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64 px (`--space-0` to `--space-10`). Screen gutter is 16 px on phones, 24 px from 768, 32 px from 1280. Content column is at most 1040 px; the sidebar is 248 px. Touch targets are at least 44 × 44 px with 8 px between them.

### Radius

| Token | Value | Use |
| --- | --- | --- |
| `--radius-px` | 2px | progress segments, tiny bars |
| `--radius-xs` | 4px | pixel chips, toggle knob, code slot |
| `--radius-sm` | 6px | badges, key caps |
| `--radius-tile` | 8px | chips, icon tiles, toggles, segmented items |
| `--radius-md` | 10px | inputs, tabs, icon buttons, sidebar items |
| `--radius-lg` | 12px | buttons, options, rows, code blocks |
| `--radius-bubble` | 14px | chat bubbles |
| `--radius-card` | 16px | cards, banners, achievement tiles |
| `--radius-xl` | 20px | panels, sheets, modals |
| `--radius-full` | 999px | pills, handles |

### Shadows

Hard, unblurred offsets down and to the right. The colour follows the element.

| Token | Value | Use |
| --- | --- | --- |
| `--shadow-step-sm` | `2px 2px 0 var(--shadow-hard)` | Pressed state |
| `--shadow-step-md` | `3px 3px 0 var(--shadow-hard)` | Options, secondary buttons, tiles |
| `--shadow-step-lg` | `4px 4px 0 var(--action-shadow)` | Primary buttons |
| `--shadow-step-xl` | `6px 6px 0 var(--brand-deep)` | Caramel cards and panels |
| `--shadow-selected` | `3px 3px 0 var(--action-border)` | Selected options and rows |
| `--shadow-brand` | `3px 3px 0 var(--brand-deep)` | Active sidebar item, mastered topic |
| `--shadow-overlay` | soft, see `tokens.css` | Modals, sheets, toasts only |

Leave 4 to 6 px of room on the right and bottom of anything with a hard shadow so it is not clipped.

### Breakpoints and layout

360 px (primary), 768 px, 1280 px. Phones use a bottom tab bar; from 1280 px a 248 px sidebar. Sessions hide navigation on every size. The app runs inside Capacitor with `viewport-fit=cover`: headers add `env(safe-area-inset-top)` to their padding, the tab bar and bottom actions add `env(safe-area-inset-bottom)`. No hover-only interactions.

## Components

Each entry gives the anatomy, the exact state rules and where to see it. shadcn/ui (Radix) primitive in brackets. Unless stated, focus is the standard ring and disabled uses `--disabled-bg` with `--disabled-text`, no shadow, `cursor: not-allowed`.

### Button [Button]

Height 52 (lg, main action on phones), 44 (md), 36 (sm, desktop only). Horizontal padding 22 / 18 / 14. Label 16 / 15 / 14 px, weight 700. Radius `lg`. Icon 18 px, gap 8. One primary per screen.

| Variant | Default | Hover | Pressed | Disabled | Loading |
| --- | --- | --- | --- | --- | --- |
| primary | fill `--action`, text `--on-action`, border `--btn-border`, shadow `step-lg` | fill `--action-hover` | fill `--action-pressed`, `translate(2px, 2px)`, shadow `2px 2px 0 var(--action-shadow)` | disabled tokens | `loader-circle` spinner before the label, `aria-busy="true"`, label changes (Verificando…) |
| secondary | fill `--surface`, text `--text`, border 1.5 px `--border-strong`, shadow `step-md` | fill `--surface-raised` | same shift, shadow `1px 1px 0` | disabled tokens | spinner |
| ghost | transparent, text `--action-text`, no shadow | fill `--surface-raised` | fill `--border` | text `--disabled-text` | spinner |
| danger | fill `--wrong`, text `--on-wrong`, shadow `4px 4px 0 var(--wrong-shadow)` | fill `--wrong-hover` | fill `--wrong-pressed`, same shift | disabled tokens | spinner |
| on caramel | fill `--ink`, text `--brand-cream`, shadow `4px 4px 0 var(--brand-deep)` | fill `--ink-raised` | same shift | n/a | n/a |

Icon button: 44 × 44, radius `md`, transparent; hover `--surface-raised`, pressed `--border`; always has an `aria-label`. See: every screen; all states in `v1-session-0-default`, `v1-session-2-checking`.

### Input, textarea, search [Input, Textarea]

Label 13/18 weight 600 above, gap 6. Field height 48 (textarea 96, padding 12 14, line 22), radius `md`, fill `--bg-well`, border 1.5 px `--border-strong`, padding 0 14, text 16 px. Helper 12/16 `--text-muted` below.
States: hover border `--text`; focus border `--action-border` plus ring at 2 px offset; filled; error border 2 px `--wrong-border` with a `triangle-alert` icon and message in `--wrong-text`; disabled. Search adds a 20 px `search` icon at left 14 and left padding 44. See: `v1-signin`, `v1-report`, `v2-catalog`, `v3-checkout-card`.

### Toggle [Switch]

52 × 30, radius `tile`, border 1.5 px. Off: fill `--surface-raised`, border `--border-strong`, knob 22 × 22 radius `xs` in `--text-muted` at left 2.5. On: fill `--action`, border `--action-border`, knob `--on-action` at left 24.5 with a 14 px `check`. Hover: off `--border`, on `--action-hover`. The row around it is at least 44 px tall and the label is clickable. See: `v1-settings`.

### Tabs [Tabs]

Tab height 44, padding 0 16, 15 px. Active: `--text`, weight 700, 3 px bottom bar `--brand`. Default: `--text-muted`, weight 500. Hover: fill `--surface-raised`. Disabled: `--disabled-text`. The list has a 1 px `--border` bottom rule.

### Segmented control [ToggleGroup, single]

Container fill `--bg-well`, border 1.5 px `--border-strong`, radius `lg`, padding 4, gap 4. Items min-height 44, radius `tile`, 14/18. Active: fill `--brand`, text `--on-brand`, weight 700. See: `v1-settings`, `v3-pricing`, `v3-checkout-card`.

### Chip [Toggle]

Height 36, radius `tile`, padding 0 12, 14 px weight 500, 8 px apart. Default: fill `--surface`, border 1.5 px `--border-strong`. Hover: `--surface-raised`. Selected: fill `--action-tint`, border `--action-border`, 14 px `check` in `--action-text`, `aria-pressed="true"`. Disabled. Code chips (fill-in-the-blank) are 44 tall, radius `md`, mono 14, with hard shadow `step-md`; used shows the selected style. See: `v2-catalog`, `v2-type-4-blank`, `v3-tutor-chat`.

### Badge [Badge]

Padding 2 8, radius `sm`, mono 11/16 weight 700, optional 12 px icon. Colour pairs: count and tier `--brand` / `--on-brand`; new `--info-tint` / `--info-text`; approved `--correct-tint` / `--correct-text`; pending `--warning-tint` / `--warning-text`; neutral `--surface-raised` / `--text-muted`.
Difficulty badge: padding 3 9, mono 12 lowercase, three 6 × 10 bars (radius `px`). Level 1 one bar `--correct` (Fácil), level 2 two bars `--warning` (Médio), level 3 three bars `--wrong` (Difícil); empty bars `--border`. On caramel: fill `--ink`, text `--brand-cream`, empty bars `--ink-line`. Always bars plus a word.

### Tooltip [Tooltip]

Fill `--text`, text `--bg`, padding 8 12, radius `tile`, 13/18 weight 500, 10 px arrow. Opens on hover, keyboard focus and long-press; never hover alone.

### Toast [Sonner]

Up to 360 wide, min-height 56, fill `--surface`, border 1.5 px `--border-strong`, radius `lg`, shadow `overlay`. 20 px icon in the semantic text colour (`circle-check`, `circle-x`, `wifi-off`, `info`), text 14/20 weight 500, optional text action in `--action-text`, 44 px close button. `role="status"`. Stacks above the tab bar; leaves after 4 s. See: `v1-flow-offline-2`.

### Modal [Dialog, AlertDialog]

Width 400 to 480 (full width minus 32 on phones), padding 24, radius `xl`, fill `--surface`, border 1.5 px `--border-strong`, shadow `overlay`, backdrop `--overlay`. Title 20/26 weight 700, body 15/22 `--text-muted`, actions right-aligned with the safe choice first. Close button top right except on destructive confirmations. See: `v1-settings-delete`, `v3-account-cancel`, `v2-achievements-unlock`, `v1-report` (desktop).

### Bottom sheet [Drawer]

Full width, radius `xl xl 0 0`, top border 1.5 px `--border-strong`, padding 16 to 20 top, 16 sides, 24 plus safe-area bottom. Optional 40 × 4 handle. Primary action at the bottom, within thumb reach. See: `v1-report` (mobile), `v1-summary-save`, `v2-exam-2-navigator`, `v3-paywall-2-locked`, `v3-adoffer-life`, `v3-tutor-entry-2-topic`.

### Radio row [RadioGroup]

Min-height 56, padding 8 14, radius `lg`, title 16/22, optional sub-line 13/18. Default: fill `--surface`, border 1.5 px `--border-strong`, shadow `step-md`, empty 20 px ring. Selected: fill `--action-tint`, border 2 px `--action-border`, shadow `selected`, weight 700, filled ring. See: `v1-onboarding-1` to `-4`, `v1-report`.

### Answer option [RadioGroup item]

Min-height 56, padding 12 14, radius `lg`. Key badge 28 × 28, radius `sm`, mono 13. Label 16/22 Geist, or 15/22 JetBrains Mono when the answer is code or output. Optional reason line 13/19 `--text-muted`, indented 40.

| State | Fill | Border | Shadow | Key badge | Right side |
| --- | --- | --- | --- | --- | --- |
| default | `--surface` | 1.5 px `--border-strong` | `step-md` | outlined, number in `--text-muted` | nothing |
| hover | `--surface-raised` | same | same | same | nothing |
| pressed | `--surface-raised`, shifted 2 px | same | `1px 1px 0` | same | nothing |
| focus | default plus focus ring | | | | |
| selected | `--action-tint` | 2 px `--action-border` | `selected` | fill `--action`, text `--on-action`, weight 700 | radio mark in `--action-text` |
| correct | `--correct-tint` | 2 px `--correct-border` | `3px 3px 0 var(--correct-border)` | fill `--correct` with `check` | "Correta" plus `circle-check` in `--correct-text` |
| wrong | `--wrong-tint` | 2 px `--wrong-border` | none | fill `--wrong` with `x` | "Sua resposta" plus `circle-x` in `--wrong-text` |
| revealed as correct | `--surface` | 2 px dashed `--correct-border` | none | outlined in `--correct-border` with `check` | "Resposta certa" plus `circle-check` |
| disabled | `--bg` | 1.5 px `--border` | none | outlined `--border` | nothing |

After the answer, every option shows its reason line when "Explicar cada alternativa" is on. Keys 1 to 4 select on desktop. See: `v1-session-*`.

### Code block

Always dark, in both themes. Fill `--code-bg`, border 1 px `--code-border`, radius `lg`. Header strip: padding 7 12, mono 11/16 `--ink-muted`, language left and line count right, bottom rule `--ink-line`. Body padding 12 0. Line-number gutter 34 px, right-aligned, `--ink-subtle`. Code mono 13/21 on phones, 14/22 from 1280, `white-space: pre`, text `--ink-text`. Long lines scroll sideways inside the block; a 32 px fade to `--ink` on the right marks the cut. Syntax: `--syn-keyword`, `--syn-function`, `--syn-number`, `--syn-string`, `--syn-comment`. No ligatures.
- **Selectable lines** (find the bug): each line is a button at least 44 px tall. Hover fill `--ink-raised`. Selected fill `--ink-selected` with an inset 2 px `--action` outline, line number in `--action` weight 700, and a `circle-check` at the right.
- **Blank slot** (fill in the blank): padding 2 8, fill `--ink-selected`, border 1.5 px `--action`, radius `xs`, text `--action`.
- **Editor** (write code): border 2 px `--action-border`, caret 2 px `--action`, status text "linha, coluna" in the header; on phones a key row (tab, brackets, colon, equals, quotes, hash) with 36 px keys in `--ink-raised`.
See: `v1-flow-code`, `v2-type-3-bug`, `v2-type-4-blank`, `v3-writecode`.

### Question header

Caramel in both themes: fill `--brand`, text `--on-brand`. Padding 12 16 20 on phones; on desktop a full-width band with a 1040 px inner column, padding 14 40 26.
- Row 1: 44 px close button, progress, count in mono 13 weight 700. Progress is ten segments, 10 px tall, 3 px apart, radius `px`: done `--ink`, current `--brand-cream` with an inset 2 px `--ink` outline, to do `--ink-24`. Exams with other totals use one continuous bar.
- From V2: three 16 px hearts after the count (filled or outlined). In exam mode: a timer chip (fill `--ink`, text `--brand-cream`, `clock` icon).
- Row 2: breadcrumb in mono 12 lowercase, subject weight 800, slash, topic weight 500; difficulty badge; from V2 a question-type tag with a 1.5 px `--ink` outline.
- Title: `h1`, 22/28 weight 700 on phones, 26/34 on desktop, balanced wrapping.
See: `v1-session-1-selected`, `v2-lives-session`, `v2-exam-1-question`.

### Feedback panel

Rises from the bottom after Verificar. Fill `--correct-tint` or `--wrong-tint`, top border 2 px in the matching `-border`, radius `xl xl 0 0` on phones, padding 16 16 22, gap 8.
- Title row: Mel head at ×3 (celebrating or encouraging), `circle-check` or `circle-x` in the semantic text colour, title 18/24 weight 700 ("Mandou bem!" or "Quase. Olha só o porquê:"), and on correct a "+12 XP" chip (fill `--xp`, text `--on-xp`, `zap` icon).
- Explanation paragraph 15/22: shown only when per-option reasons are off.
- "Reportar questão" link with a `flag` icon, 44 px tall.
- From V3, on wrong: a secondary button "Por que eu errei?" with a `message-circle` icon.
- "Continuar" primary button, lg, full width. On desktop the panel is a full-width band with title left, link and button right, and an Enter key hint.
See: `v1-session-3-correct`, `v1-session-4-wrong`, `v1-session-5-reasons-off`, `v3-tutor-entry-1-wrong`.

### Streak counter

Card 248 × 64, radius `lg`, fill `--surface`, border 1.5 px `--border-strong`. Icon tile 40 × 40 radius `tile`; title 15/20 weight 700; sub-line 12/16.

| State | Tile | Title | Sub-line |
| --- | --- | --- | --- |
| started | fill `--streak`, filled `flame` in `--on-streak` | 1 dia | Começou hoje |
| extended | same | 7 dias seguidos | Meta de hoje batida |
| at risk | fill `--warning-tint`, dashed `--warning-border`, outlined flame | 7 dias seguidos | `triangle-alert` plus "Pratique hoje pra não perder" in `--warning-text` |
| lost | fill `--bg`, dashed `--border-strong`, flame in `--text-subtle` | Sequência perdida, in `--text-muted` | Bora começar outra? |
| restored | as extended | 7 dias seguidos | `check` plus "Sequência recuperada" in `--correct-text` |

Header chip: height 32, radius `tile`, fill `--streak`, text `--on-streak`, mono 14 weight 800, 15 px flame. Streak-freeze chip (V2): same shape, fill `--info`, text `--on-info`, `snowflake` icon, count 0 to 2. See: `v1-flow-streak`, `v2-freeze`, `v3-repair-*`.

### XP bar [Progress]

Label row: "Nível 4" 13/18 weight 700 left, "320 / 500 XP" mono 12 right. Bar 12 px tall, radius `xs`, fill `--bg-well`, border 1 px `--border-strong`, progress `--xp`. After a correct answer: a `--xp-gain` segment at the end and a "+12 XP" chip. Level up: full bar, "Subiu de nível!" and a "Nível 5" chip. See: `v1-summary-gain`, `v1-profile`.

### Rating badge

Chip: height 32, radius `tile`, fill `--rating`, text `--on-rating`, mono 14 weight 800, `trending-up` icon. Delta: mono 13 weight 700 with an arrow icon; up in `--rating-text`, down and unchanged in `--text-muted`. Summary card: label mono 11, number in `stat-mono`, delta, and one line of text. A loss is never red and never animates differently from a gain. See: `v1-summary-gain`, `v1-summary-loss`.

### Daily-goal ring

80 × 80, stroke 8, radius 32, starting at 12 o'clock. Track `--border`, arc `--brand`; centre shows done over goal in mono. Done: arc `--correct`, centre `check`, label "Meta batida!". On the caramel goal card: track `--ink-24`, arc `--ink`. See: `v1-home`.

### Topic node

A row, min-height 76, padding 10 12, radius `lg`: a 52 × 52 node (radius `lg`), the topic name 16/22 weight 600, a status line, and a chevron. Rows stack vertically on a 2 px `--border` rail.

| State | Node | Status line |
| --- | --- | --- |
| locked | fill `--bg`, dashed 1.5 px `--border-strong`, `lock` in `--text-subtle`; row is disabled | Bloqueado |
| available | fill `--surface`, 2 px `--action-border`, shadow `selected`, filled `play` | Começar, in `--action-text` |
| in progress | fill `--surface`, 2 px `--brand-deep`, shadow `brand`, percentage in mono | 96 × 6 bar in `--brand` plus "Em andamento" |
| mastered | fill `--brand`, 2 px `--brand-deep`, shadow `brand`, filled `star` in `--on-brand` | `check` plus "Dominado" in `--correct-text` |

Hover fills the row with `--surface-raised`; pressed shifts it 2 px. See: `v1-home`.

### Leaderboard row

Height 56, padding 0 14, radius `lg`, fill `--surface`, border 1 px `--border`. Rank in mono 14 weight 700 (20 px wide, right-aligned), 16 px zone icon (`trending-up` in `--correct-text`, `minus` in `--text-subtle`, `trending-down` in `--warning-text`), 36 px avatar tile with an initial, name 15/20 weight 600, score in mono 13 weight 700. Own row: fill `--action-tint`, border 2 px `--action-border`, caramel avatar and a "Você" badge. Zones are labelled with a mono line above their first row. See: `v2-leagues`, `v3-tracks`.

### Achievement badge

Tile 68 to 72 px square, radius `card`, name 13/17 weight 600 below. Unlocked: coloured fill (streak, XP, action or brand), ink icon, shadow `step-md`. Locked: fill `--bg`, dashed border, `lock`. Just unlocked: 2 px `--brand` outline at 4 px offset and a "Nova!" badge. See: `v2-achievements`, `v2-achievements-unlock`.

### Stat card and card

Card: fill `--surface`, border 1 px `--border`, radius `card`, padding 16, gap 12. Stat card: radius `lg`, padding 12, a 24 px coloured icon tile, mono label 11, value in mono 20 weight 800.

### Caramel card

Fill `--brand`, text `--on-brand`, radius `card`, shadow `step-xl`. Used for the goal card, the review hero, the exam countdown, the paywall banner and upsell. Its button is the "on caramel" variant. Dismissible versions have a 44 px close button top right. See: `v1-home`, `v2-review`, `v3-paywall-3-upsell`.

### Pricing card

Padding 20, radius `card`, fill `--surface`, border 1.5 px `--border-strong`. Tier name mono 14 weight 800 lowercase; price in mono 40 weight 800 with "R$" before and "/mês" after; billing line 13/18; benefit rows with a `check` in `--correct-text`; full-width button. Featured: border 2 px `--brand-deep`, shadow `step-xl`, "Recomendado" badge, primary button. Current plan: disabled button "Plano atual". Tier name, price and benefits are separate text nodes, so renaming or repricing touches no layout. See: `v3-pricing`.

### Usage meter [Progress]

Label 13/18 weight 600 and count in mono 12 on one row; bar 10 px, radius `px`, fill `--bg-well`, border 1 px `--border-strong`. Normal: `--action`. Low: `--warning` with a `triangle-alert` line in `--warning-text`. Empty: `--text-subtle` with a "Ver planos" link. See: `v3-tutor-chat`, `v3-tutor-out`.

### Ad containers

Sizes are reserved before the ad loads, so nothing shifts. Always labelled "Anúncio". Never beside answer options.
- Banner slot: 320 × 50, fill `--surface-raised`, dashed 1 px `--border-strong`, radius `xs`; loading shows a skeleton of the same size.
- Break frame: full screen; label badge and countdown on top, a fixed-size slot in the middle, a reassurance line, and a "Voltar pra sessão" button that is disabled until the countdown ends.
See: `v3-beat-6-adbreak`.

### Chat

User bubble: right-aligned, up to 250 wide, fill `--action`, text `--on-action`, radius `14 14 4 14`, padding 10 14, 15/21. Tutor bubble: left, up to 262 wide, fill `--surface`, border 1 px `--border-strong`, radius `14 14 14 4`, with a 36 px caramel avatar tile holding Mel's head. Code inside a message: fill `--ink`, radius `tile`, mono 13/20. Typing: thinking Mel plus three 6 px squares. Suggestions are chips. Composer: 44 px input plus a 44 px send button in `--action`; both disabled when the allowance is used up. See: `v3-tutor-chat`, `v3-tutor-out`.

### Navigation

- **Bottom tab bar (phones):** fill `--surface`, top border 1 px `--border`, padding 6 8 and 20 plus safe-area at the bottom. Items at least 52 px tall: a 48 × 28 icon tile (radius `tile`) over an 11/14 label. Active: tile fill `--brand`, icon `--on-brand`, label `--text` weight 700, `aria-current="page"`. Inactive: `--text-muted`. Pressed: tile `--surface-raised`. Count badge: 18 px, fill `--action`, text `--on-action`.
- **Sidebar (from 1280):** 248 wide, fill `--surface`, right border. Wordmark at 20 px, items 44 tall, radius `md`, 20 px icon and 15 px label. Active: fill `--brand`, text `--on-brand`, shadow `brand`. Hover: `--surface-raised`. Streak and rating chips and Ajustes sit at the bottom.
See: `v1-home`, `v2-review`.

### Mel

Seven sprites (`assets/mel-*.svg`) and seven head crops (`assets/mel-head-*.svg`). Use: wave for greeting and empty states; celebrate for correct answers, milestones and level up; encourage for wrong answers; think for loading and tutor typing; sleep for a lost streak, no lives and the daily limit; mischief for the ad challenge and 404; study for exam mode and maintenance. Full sprites at ×4 to ×6 on screens, heads at ×2 to ×4 in panels and avatars.


## Motion

Short and purposeful. Pixel things move in steps; panels and numbers ease. Nothing loops while a question is on screen. Durations and easings are tokens (`--dur-*`, `--ease-*`) and switch off under `prefers-reduced-motion`.

| Name | Trigger | Duration | Easing | What moves | Reduced motion |
| --- | --- | --- | --- | --- | --- |
| `press` | Pointer down on any button, option or node | 80ms | `linear` | Element moves 2 px into its shadow; shadow shrinks to step-sm | Same (travel is only 2 px) |
| `option-select` | Tap or key 1 to 4 on an option | 120ms | `ease-out` | Border thickens, tint fades in, key badge fills | Instant state change |
| `answer-reveal` | Tap Verificar or press Enter | 480ms total (120 + 240 + 120) | `cubic-bezier(.2,.8,.2,1)` | 120 ms button spinner, 240 ms result colours sweep the options, 120 ms feedback panel rises 16 px | Cross-fade in 120 ms, no movement |
| `xp-gain` | Feedback panel shown after a correct answer | 600ms | `ease-out` | +XP chip counts up and lifts 12 px; XP bar fills | Number and bar jump to the final value |
| `rating-delta` | Session summary opens | 700ms | `ease-out` | Rating counts to the new value, delta chip fades in. A loss uses the same calm motion, no shake | Final value shown at once |
| `streak-increment` | First session of the day is completed | 500ms | `steps(5)` | Flame plays 5 pixel frames and the number ticks up | Number swaps, static flame |
| `level-up` | XP crosses a level | 900ms | `steps(6), then ease-out` | Mel celebrate sprite plays 6 frames, 24 confetti pixels fall and fade | Static celebrate sprite, no confetti |
| `overlay` | Modal or bottom sheet opens and closes | 200ms in, 150ms out | `cubic-bezier(.2,.8,.2,1) in, ease-in out` | Rises 24 px and fades; backdrop fades | Fade only, 100 ms |
| `toast` | Appears; leaves after 4 s or on dismiss | 160ms in, 120ms out | `ease-out in, ease-in out` | Slides 12 px from the bottom edge | Fade only |

## Accessibility

- WCAG AA contrast in both themes.
- Correct and wrong never rely on colour: each has an icon and a word. Selected has a thicker border, a filled key badge and a radio mark.
- Every control is a real `button`, `a`, `input` or `textarea`; icon-only buttons have an `aria-label`.
- Focus ring: 2 px `--focus-ring`, 3 px offset, on every control.
- Desktop sessions are fully keyboard-driven: 1 to 4 select, Enter confirms, Esc closes overlays, Tab reaches everything.
- Modals and sheets trap focus and return it on close. Toasts use `role="status"`.

## Screens

### V1 · practice loop (launches)

| Screen | Group | File | Frame (px) |
| --- | --- | --- | --- |
| Session · option selected | Session · multiple choice and answer reveal | `screens/v1-session-1-selected-mobile.html`<br>`screens/v1-session-1-selected-desktop.html` | 360 × 800<br>1280 × 800 |
| Feedback · correct | Session · multiple choice and answer reveal | `screens/v1-session-3-correct-mobile.html`<br>`screens/v1-session-3-correct-desktop.html` | 360 × 1040<br>1280 × 800 |
| Feedback · wrong | Session · multiple choice and answer reveal | `screens/v1-session-4-wrong-mobile.html`<br>`screens/v1-session-4-wrong-desktop.html` | 360 × 1040<br>1280 × 800 |
| Summary · rating gain | Session summary and rating change | `screens/v1-summary-gain-mobile.html`<br>`screens/v1-summary-gain-desktop.html` | 360 × 940<br>1280 × 900 |
| Report a question | Report a question | `screens/v1-report-mobile.html`<br>`screens/v1-report-desktop.html` | 360 × 1040<br>1280 × 800 |
| Session · nothing selected | Session · multiple choice and answer reveal | `screens/v1-session-0-default-mobile.html` | 360 × 800 |
| Answer reveal · checking | Session · multiple choice and answer reveal | `screens/v1-session-2-checking-mobile.html` | 360 × 800 |
| Feedback · reasons off | Session · multiple choice and answer reveal | `screens/v1-session-5-reasons-off-mobile.html` | 360 × 940 |
| Summary · rating loss | Session summary and rating change | `screens/v1-summary-loss-mobile.html` | 360 × 1080 |
| Summary · save progress prompt | Session summary and rating change | `screens/v1-summary-save-mobile.html`<br>`screens/v1-summary-save-desktop.html` | 360 × 940<br>1280 × 900 |
| Long text · Portuguese | Flows · long text, both languages, code on a small screen, offline | `screens/v1-flow-longtext-pt-mobile.html`<br>`screens/v1-flow-longtext-pt-desktop.html` | 360 × 900<br>1280 × 800 |
| English | Flows · long text, both languages, code on a small screen, offline | `screens/v1-flow-english-mobile.html` | 360 × 800 |
| Code on a small screen | Flows · long text, both languages, code on a small screen, offline | `screens/v1-flow-code-mobile.html` | 360 × 1000 |
| Offline · interrupted mid-question | Flows · long text, both languages, code on a small screen, offline | `screens/v1-flow-offline-1-mobile.html` | 360 × 840 |
| Offline · resumed | Flows · long text, both languages, code on a small screen, offline | `screens/v1-flow-offline-2-mobile.html` | 360 × 800 |
| Landing page | Landing page | `screens/v1-landing-mobile.html`<br>`screens/v1-landing-desktop.html` | 360 × 2320<br>1280 × 1460 |
| Onboarding · step 1 | Onboarding | `screens/v1-onboarding-1-mobile.html`<br>`screens/v1-onboarding-1-desktop.html` | 360 × 800<br>1280 × 800 |
| Onboarding · step 2 | Onboarding | `screens/v1-onboarding-2-mobile.html`<br>`screens/v1-onboarding-2-desktop.html` | 360 × 800<br>1280 × 800 |
| Onboarding · step 3 | Onboarding | `screens/v1-onboarding-3-mobile.html`<br>`screens/v1-onboarding-3-desktop.html` | 360 × 800<br>1280 × 800 |
| Onboarding · step 4 | Onboarding | `screens/v1-onboarding-4-mobile.html`<br>`screens/v1-onboarding-4-desktop.html` | 360 × 800<br>1280 × 800 |
| Home | Home | `screens/v1-home-mobile.html`<br>`screens/v1-home-desktop.html` | 360 × 940<br>1280 × 800 |
| Profile and stats | Profile and stats | `screens/v1-profile-mobile.html`<br>`screens/v1-profile-desktop.html` | 360 × 1460<br>1280 × 920 |
| Sign in | Sign in | `screens/v1-signin-mobile.html`<br>`screens/v1-signin-desktop.html` | 360 × 800<br>1280 × 800 |
| Settings | Settings | `screens/v1-settings-mobile.html`<br>`screens/v1-settings-desktop.html` | 360 × 1020<br>1280 × 900 |
| Sign in · link sent | Sign in | `screens/v1-signin-sent-mobile.html` | 360 × 800 |
| Settings · delete account | Settings | `screens/v1-settings-delete-mobile.html` | 360 × 1020 |
| First session · tap 1, pick an option | Flow · first session without an account | `screens/v1-flow-first-1-mobile.html` | 360 × 800 |
| First session · tap 2, answered | Flow · first session without an account | `screens/v1-flow-first-2-mobile.html` | 360 × 940 |
| System state · loading | System states | `screens/v1-state-loading-mobile.html`<br>`screens/v1-state-loading-desktop.html` | 360 × 800<br>1280 × 720 |
| System state · empty | System states | `screens/v1-state-empty-mobile.html`<br>`screens/v1-state-empty-desktop.html` | 360 × 800<br>1280 × 720 |
| System state · offline | System states | `screens/v1-state-offline-mobile.html`<br>`screens/v1-state-offline-desktop.html` | 360 × 800<br>1280 × 720 |
| System state · error | System states | `screens/v1-state-error-mobile.html`<br>`screens/v1-state-error-desktop.html` | 360 × 800<br>1280 × 720 |
| System state · 404 | System states | `screens/v1-state-404-mobile.html`<br>`screens/v1-state-404-desktop.html` | 360 × 800<br>1280 × 720 |
| System state · maintenance | System states | `screens/v1-state-maintenance-mobile.html`<br>`screens/v1-state-maintenance-desktop.html` | 360 × 800<br>1280 × 720 |
| Streak lifecycle | Streak lifecycle | `screens/v1-flow-streak-mobile.html` | 360 × 1240 |

### V2 · retention and mobile (behind feature flags)

| Screen | Group | File | Frame (px) |
| --- | --- | --- | --- |
| Review queue | Review queue | `screens/v2-review-mobile.html`<br>`screens/v2-review-desktop.html` | 360 × 860<br>1280 × 800 |
| True or false | New question types | `screens/v2-type-1-truefalse-mobile.html`<br>`screens/v2-type-1-truefalse-desktop.html` | 360 × 800<br>1280 × 800 |
| Predict the output | New question types | `screens/v2-type-2-predict-mobile.html`<br>`screens/v2-type-2-predict-desktop.html` | 360 × 820<br>1280 × 860 |
| Find the bug | New question types | `screens/v2-type-3-bug-mobile.html`<br>`screens/v2-type-3-bug-desktop.html` | 360 × 800<br>1280 × 800 |
| Fill in the blank | New question types | `screens/v2-type-4-blank-mobile.html`<br>`screens/v2-type-4-blank-desktop.html` | 360 × 800<br>1280 × 800 |
| Order the steps | New question types | `screens/v2-type-5-order-mobile.html`<br>`screens/v2-type-5-order-desktop.html` | 360 × 860<br>1280 × 800 |
| Exam mode · question | Exam mode | `screens/v2-exam-1-question-mobile.html`<br>`screens/v2-exam-1-question-desktop.html` | 360 × 860<br>1280 × 840 |
| Exam mode · results by topic | Exam mode | `screens/v2-exam-3-results-mobile.html`<br>`screens/v2-exam-3-results-desktop.html` | 360 × 960<br>1280 × 920 |
| Leagues | Leagues | `screens/v2-leagues-mobile.html`<br>`screens/v2-leagues-desktop.html` | 360 × 1080<br>1280 × 880 |
| Achievements | Achievements | `screens/v2-achievements-mobile.html`<br>`screens/v2-achievements-desktop.html` | 360 × 800<br>1280 × 800 |
| Out of lives | Lives | `screens/v2-lives-out-mobile.html`<br>`screens/v2-lives-out-desktop.html` | 360 × 800<br>1280 × 800 |
| Subject catalog | Subject catalog | `screens/v2-catalog-mobile.html`<br>`screens/v2-catalog-desktop.html` | 360 × 900<br>1280 × 800 |
| Review queue · empty | Review queue | `screens/v2-review-empty-mobile.html` | 360 × 800 |
| Exam mode · question navigator | Exam mode | `screens/v2-exam-2-navigator-mobile.html` | 360 × 860 |
| Achievement · unlock moment | Achievements | `screens/v2-achievements-unlock-mobile.html` | 360 × 800 |
| Lives in the session header | Lives | `screens/v2-lives-session-mobile.html` | 360 × 800 |
| Subject catalog · search | Subject catalog | `screens/v2-catalog-search-mobile.html` | 360 × 800 |
| Streak freeze | Streak freeze | `screens/v2-freeze-mobile.html` | 360 × 1000 |
| Push notifications | Notifications and email | `screens/v2-notifications-mobile.html` | 360 × 640 |
| Weekly progress email | Notifications and email | `screens/v2-email-weekly-email.html` | 720 × 760 |
| Splash screen | Mobile app shell | `screens/v2-shell-splash-mobile.html` | 360 × 800 |
| Safe-area layouts | Mobile app shell | `screens/v2-shell-safearea-board.html` | 1280 × 860 |
| Admin · question list | Admin · question review | `screens/v2-admin-1-list-desktop.html` | 1280 × 760 |
| Admin · edit, approve, retire | Admin · question review | `screens/v2-admin-2-edit-desktop.html` | 1280 × 820 |
| App icon set | Mobile app shell | `screens/v2-shell-icons-board.html` | 1280 × 1120 |
| Store screenshot 1 · Google Play 1080 × 1920 at 1/3 | Store screenshots | `screens/v2-store-1-play.html`<br>`screens/v2-store-1-ios.html` | 360 × 640<br>430 × 932 |
| Store screenshot 2 · Google Play 1080 × 1920 at 1/3 | Store screenshots | `screens/v2-store-2-play.html`<br>`screens/v2-store-2-ios.html` | 360 × 640<br>430 × 932 |
| Store screenshot 3 · Google Play 1080 × 1920 at 1/3 | Store screenshots | `screens/v2-store-3-play.html`<br>`screens/v2-store-3-ios.html` | 360 × 640<br>430 × 932 |
| Store screenshot 4 · Google Play 1080 × 1920 at 1/3 | Store screenshots | `screens/v2-store-4-play.html`<br>`screens/v2-store-4-ios.html` | 360 × 640<br>430 × 932 |

### V3 · money (behind feature flags)

| Screen | Group | File | Frame (px) |
| --- | --- | --- | --- |
| Pricing · monthly | Pricing | `screens/v3-pricing-mobile.html`<br>`screens/v3-pricing-desktop.html` | 360 × 1640<br>1280 × 660 |
| Paywall · daily limit reached | Paywall moments and the free limit | `screens/v3-paywall-1-limit-mobile.html`<br>`screens/v3-paywall-1-limit-desktop.html` | 360 × 860<br>1280 × 800 |
| Checkout · card | Checkout and account | `screens/v3-checkout-card-mobile.html`<br>`screens/v3-checkout-card-desktop.html` | 360 × 820<br>1280 × 760 |
| Checkout · Pix | Checkout and account | `screens/v3-checkout-pix-mobile.html`<br>`screens/v3-checkout-pix-desktop.html` | 360 × 820<br>1280 × 760 |
| Manage subscription | Checkout and account | `screens/v3-account-manage-mobile.html`<br>`screens/v3-account-manage-desktop.html` | 360 × 800<br>1280 × 640 |
| AI tutor chat | AI tutor chat and entry points | `screens/v3-tutor-chat-mobile.html`<br>`screens/v3-tutor-chat-desktop.html` | 360 × 800<br>1280 × 800 |
| Exam track home | Exam tracks | `screens/v3-tracks-mobile.html`<br>`screens/v3-tracks-desktop.html` | 360 × 1280<br>1280 × 900 |
| Write-code question | Write-code question | `screens/v3-writecode-mobile.html`<br>`screens/v3-writecode-desktop.html` | 360 × 1060<br>1280 × 800 |
| Referral | Referral | `screens/v3-referral-mobile.html`<br>`screens/v3-referral-desktop.html` | 360 × 860<br>1280 × 800 |
| Pricing · annual | Pricing | `screens/v3-pricing-annual-desktop.html` | 1280 × 660 |
| Paywall · locked feature tapped | Paywall moments and the free limit | `screens/v3-paywall-2-locked-mobile.html` | 360 × 940 |
| Paywall · end-of-session upsell | Paywall moments and the free limit | `screens/v3-paywall-3-upsell-mobile.html` | 360 × 960 |
| Checkout · success | Checkout and account | `screens/v3-checkout-success-mobile.html` | 360 × 800 |
| Checkout · payment failed | Checkout and account | `screens/v3-checkout-failure-mobile.html` | 360 × 800 |
| Cancel subscription · confirm | Checkout and account | `screens/v3-account-cancel-mobile.html` | 360 × 800 |
| Opt-in ad · restore a life | Opt-in ad offers | `screens/v3-adoffer-life-mobile.html` | 360 × 800 |
| Tutor entry · from a wrong answer | AI tutor chat and entry points | `screens/v3-tutor-entry-1-wrong-mobile.html` | 360 × 1020 |
| Tutor entry · from a topic | AI tutor chat and entry points | `screens/v3-tutor-entry-2-topic-mobile.html` | 360 × 940 |
| Tutor · message allowance used up | AI tutor chat and entry points | `screens/v3-tutor-out-mobile.html` | 360 × 800 |
| Beat the ad · challenge offered | Beat the ad, end to end | `screens/v3-beat-1-offer-mobile.html` | 360 × 800 |
| Beat the ad · challenge question | Beat the ad, end to end | `screens/v3-beat-2-question-mobile.html` | 360 × 800 |
| Beat the ad · win, double or nothing offered | Beat the ad, end to end | `screens/v3-beat-3-double-mobile.html` | 360 × 860 |
| Beat the ad · double won | Beat the ad, end to end | `screens/v3-beat-4-win-mobile.html` | 360 × 800 |
| Beat the ad · lost | Beat the ad, end to end | `screens/v3-beat-5-lose-mobile.html` | 360 × 800 |
| Beat the ad · ad break frame | Beat the ad, end to end | `screens/v3-beat-6-adbreak-mobile.html` | 360 × 800 |
| Streak repair · offer on the free plan | Streak repair | `screens/v3-repair-1-free-mobile.html` | 360 × 800 |
| Streak repair · offer on a paid plan | Streak repair | `screens/v3-repair-2-paid-mobile.html` | 360 × 800 |
| Streak repair · restored | Streak repair | `screens/v3-repair-3-restored-mobile.html` | 360 × 800 |

## Assets

| File | What it is |
| --- | --- |
| `assets/logo-wordmark-on-dark.svg` | caramelCase wordmark for dark backgrounds |
| `assets/logo-wordmark-on-light.svg` | caramelCase wordmark for light backgrounds |
| `assets/logo-wordmark-on-caramel.svg` | caramelCase wordmark for caramel backgrounds |
| `assets/logo-wordmark-mono.svg` | caramelCase wordmark, single colour (uses currentColor) |
| `assets/mel-wave.svg` | Mel, neutral and waving · 26 × 27 px sprite, scale by whole numbers |
| `assets/mel-head-wave.svg` | Mel, neutral and waving, head only · 21 × 14 px sprite |
| `assets/mel-celebrate.svg` | Mel celebrating · 26 × 27 px sprite, scale by whole numbers |
| `assets/mel-head-celebrate.svg` | Mel celebrating, head only · 21 × 14 px sprite |
| `assets/mel-encourage.svg` | Mel encouraging · 26 × 27 px sprite, scale by whole numbers |
| `assets/mel-head-encourage.svg` | Mel encouraging, head only · 21 × 14 px sprite |
| `assets/mel-think.svg` | Mel thinking · 26 × 27 px sprite, scale by whole numbers |
| `assets/mel-head-think.svg` | Mel thinking, head only · 21 × 14 px sprite |
| `assets/mel-sleep.svg` | Mel sleeping · 26 × 27 px sprite, scale by whole numbers |
| `assets/mel-head-sleep.svg` | Mel sleeping, head only · 21 × 14 px sprite |
| `assets/mel-mischief.svg` | Mel mischievous · 26 × 27 px sprite, scale by whole numbers |
| `assets/mel-head-mischief.svg` | Mel mischievous, head only · 21 × 14 px sprite |
| `assets/mel-study.svg` | Mel studying with glasses and a laptop · 26 × 27 px sprite, scale by whole numbers |
| `assets/mel-head-study.svg` | Mel studying with glasses and a laptop, head only · 21 × 14 px sprite |
| `assets/app-icon.svg` | caramelCase app icon |
| `assets/app-icon-square.svg` | caramelCase app icon, square for iOS and store uploads (the OS applies the mask) |
| `assets/app-icon-adaptive-foreground.svg` | Android adaptive icon, foreground layer (108 dp canvas, 66 dp safe zone) |
| `assets/app-icon-adaptive-background.svg` | Android adaptive icon, background layer |
| `assets/app-icon-mono.svg` | caramelCase app icon, monochrome (uses currentColor) for Android themed icons |
| `assets/favicon.svg` | caramelCase favicon |
| `assets/logo-lockup-on-dark.svg` | caramelCase icon and wordmark for dark backgrounds |

Export PNG app icons from `app-icon-square.svg` (iOS, stores) and the two adaptive layers (Android) at the sizes in `screens/v2-shell-icons-board.html`: Android 48, 72, 96, 144, 192 and 512 px; iOS 40, 58, 60, 80, 87, 120, 180 and 1024 px; web 16, 32, 48 and 192 px. Store screenshots are drawn at one third of the upload size (Google Play 1080 × 1920, App Store 1290 × 2796).

## Decisions made by the designer, to confirm

- Daily goal is counted in questions: 10, 20 or 30 a day. XP is a separate score. (Confirmed.)
- Streak freeze (V2): earned by meeting the goal 7 days in a row, at most 2 held, used automatically. Streak repair (V3): 48 hours after a loss; an opt-in ad on the free plan, one tap on paid plans. (Confirmed.)
- Code blocks stay dark in both themes.
- Light-theme filled buttons get a 1.5 px ink outline and an ink hard shadow.
- A rating loss is grey with a down arrow and a reassuring line; never red, never a shake.
- V1 navigation is Início, Perfil, Ajustes. From V2 it is Início, Revisão, Ligas, Perfil, with Ajustes reached from Perfil.
- Lives (V2): three lives, one refills every 30 minutes, review sessions do not cost lives.
- Leagues (V2): ten students per league, top three promoted, bottom three relegated; tiers named Bit, Byte, Kilobyte.
- At the free daily limit (V3) the student can still do today's review and open their profile.
- Paywall copy says paid plans remove the daily limit and start at R$ 15.
- Push notifications: at most one a day.
- A topic sheet with "Praticar" and "Perguntar ao Mel" is the tutor's entry point from a topic.

## Placeholders to fill

`[Benefício do plano]` on every pricing card, `[ANUAL]` yearly prices, `[RECOMPENSA]` for referrals, `[nome da prova]` on the exam track, `[seu-dominio]` in the referral link. Sample questions, per-option reasons, names and numbers are illustrative; check the computer-science content before it ships.

## Not designed

Things the brief does not ask for that the product will probably need. None of them is in the screens.

- Legal: terms, privacy policy and LGPD consent on the landing page and at sign-up; data export.
- The notification permission prompt and a time picker for the daily reminder.
- Home with the subject switcher open (the bottom sheet component exists, the screen state does not).
- A full topic page.
- Exam mode: submit confirmation, time-up state, and the answer-by-answer review after the report.
- Leagues: the end-of-week promotion or relegation moment.
- Lives: the moment a life is lost.
- Checkout: expired Pix code, yearly checkout, change-plan screen, receipts.
- Tutor: conversation history.
- Admin: sign-in, creating a question, bulk actions.
- Account: changing the e-mail address.
- Desktop versions of the states drawn only for phones, and a full English render of every screen.
- Sound and haptics.
