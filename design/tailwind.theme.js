/** caramelCase · Tailwind theme extension (Tailwind 3 syntax).
 *  Every value points at a CSS custom property from tokens.css, so both themes work with one class set.
 *
 *  tailwind.config.js:
 *    const caramel = require('./design/tailwind.theme.js')
 *    module.exports = { darkMode: ['selector', '[data-theme="dark"]'], theme: { extend: caramel } }
 *  and import './design/tokens.css' once in the app entry.
 *
 *  Colours are plain var() references, so opacity modifiers such as bg-action/50 do not apply.
 *  Use the tint tokens (action-tint, correct-tint, ...) instead.
 */
module.exports = {
  screens: { sm: '360px', md: '768px', lg: '1280px' },
  colors: {
    // shadcn/ui names
    background: 'var(--background)', foreground: 'var(--foreground)',
    card: { DEFAULT: 'var(--card)', foreground: 'var(--card-foreground)' },
    popover: { DEFAULT: 'var(--popover)', foreground: 'var(--popover-foreground)' },
    primary: { DEFAULT: 'var(--primary)', foreground: 'var(--primary-foreground)' },
    secondary: { DEFAULT: 'var(--secondary)', foreground: 'var(--secondary-foreground)' },
    muted: { DEFAULT: 'var(--muted)', foreground: 'var(--muted-foreground)' },
    accent: { DEFAULT: 'var(--accent)', foreground: 'var(--accent-foreground)' },
    destructive: { DEFAULT: 'var(--destructive)', foreground: 'var(--destructive-foreground)' },
    input: 'var(--input)', ring: 'var(--ring)',
    // caramelCase names
    bg: { DEFAULT: 'var(--bg)', well: 'var(--bg-well)' },
    surface: { DEFAULT: 'var(--surface)', raised: 'var(--surface-raised)' },
    border: { DEFAULT: 'var(--border)', strong: 'var(--border-strong)' },
    fg: { DEFAULT: 'var(--text)', muted: 'var(--text-muted)', subtle: 'var(--text-subtle)' },
    brand: { DEFAULT: 'var(--brand)', text: 'var(--brand-text)', deep: 'var(--brand-deep)', cream: 'var(--brand-cream)', pale: 'var(--brand-pale)', fg: 'var(--on-brand)' },
    action: { DEFAULT: 'var(--action)', hover: 'var(--action-hover)', pressed: 'var(--action-pressed)', shadow: 'var(--action-shadow)', text: 'var(--action-text)', tint: 'var(--action-tint)', border: 'var(--action-border)', fg: 'var(--on-action)' },
    correct: { DEFAULT: 'var(--correct)', text: 'var(--correct-text)', tint: 'var(--correct-tint)', border: 'var(--correct-border)', fg: 'var(--on-correct)' },
    wrong: { DEFAULT: 'var(--wrong)', hover: 'var(--wrong-hover)', pressed: 'var(--wrong-pressed)', shadow: 'var(--wrong-shadow)', text: 'var(--wrong-text)', tint: 'var(--wrong-tint)', border: 'var(--wrong-border)', fg: 'var(--on-wrong)' },
    warning: { DEFAULT: 'var(--warning)', text: 'var(--warning-text)', tint: 'var(--warning-tint)', border: 'var(--warning-border)' },
    info: { DEFAULT: 'var(--info)', text: 'var(--info-text)', tint: 'var(--info-tint)', border: 'var(--info-border)', fg: 'var(--on-info)' },
    streak: { DEFAULT: 'var(--streak)', text: 'var(--streak-text)', fg: 'var(--on-streak)' },
    xp: { DEFAULT: 'var(--xp)', text: 'var(--xp-text)', gain: 'var(--xp-gain)', fg: 'var(--on-xp)' },
    rating: { DEFAULT: 'var(--rating)', text: 'var(--rating-text)', fg: 'var(--on-rating)' },
    ink: { DEFAULT: 'var(--ink)', raised: 'var(--ink-raised)', line: 'var(--ink-line)', selected: 'var(--ink-selected)', text: 'var(--ink-text)', muted: 'var(--ink-muted)', subtle: 'var(--ink-subtle)', 24: 'var(--ink-24)' },
    code: { bg: 'var(--code-bg)', border: 'var(--code-border)' },
    syn: { keyword: 'var(--syn-keyword)', function: 'var(--syn-function)', number: 'var(--syn-number)', string: 'var(--syn-string)', comment: 'var(--syn-comment)' },
    disabled: { DEFAULT: 'var(--disabled-bg)', text: 'var(--disabled-text)' },
    overlay: 'var(--overlay)', focus: 'var(--focus-ring)',
    white: 'var(--white)', transparent: 'transparent', current: 'currentColor',
  },
  fontFamily: { sans: ['var(--font-sans)'], mono: ['var(--font-mono)'] },
  fontSize: {
    'display': ['var(--text-display)', { lineHeight: 'var(--leading-display)', fontWeight: 'var(--weight-display)' }],
    'title': ['var(--text-title)', { lineHeight: 'var(--leading-title)', fontWeight: 'var(--weight-title)' }],
    'question': ['var(--text-question)', { lineHeight: 'var(--leading-question)', fontWeight: 'var(--weight-question)' }],
    'heading': ['var(--text-heading)', { lineHeight: 'var(--leading-heading)', fontWeight: 'var(--weight-heading)' }],
    'body': ['var(--text-body)', { lineHeight: 'var(--leading-body)', fontWeight: 'var(--weight-body)' }],
    'body-sm': ['var(--text-body-sm)', { lineHeight: 'var(--leading-body-sm)', fontWeight: 'var(--weight-body-sm)' }],
    'caption': ['var(--text-caption)', { lineHeight: 'var(--leading-caption)', fontWeight: 'var(--weight-caption)' }],
    'button': ['var(--text-button)', { lineHeight: 'var(--leading-button)', fontWeight: 'var(--weight-button)' }],
    'label-mono': ['var(--text-label-mono)', { lineHeight: 'var(--leading-label-mono)', fontWeight: 'var(--weight-label-mono)' }],
    'code': ['var(--text-code)', { lineHeight: 'var(--leading-code)', fontWeight: 'var(--weight-code)' }],
    'code-lg': ['var(--text-code-lg)', { lineHeight: 'var(--leading-code-lg)', fontWeight: 'var(--weight-code-lg)' }],
    'stat-mono': ['var(--text-stat-mono)', { lineHeight: 'var(--leading-stat-mono)', fontWeight: 'var(--weight-stat-mono)' }],
  },
  borderRadius: { px: 'var(--radius-px)', xs: 'var(--radius-xs)', sm: 'var(--radius-sm)', tile: 'var(--radius-tile)', md: 'var(--radius-md)', lg: 'var(--radius-lg)', bubble: 'var(--radius-bubble)', card: 'var(--radius-card)', xl: 'var(--radius-xl)', 'full': 'var(--radius-full)' },
  boxShadow: {
    'step-sm': 'var(--shadow-step-sm)', 'step-md': 'var(--shadow-step-md)', 'step-lg': 'var(--shadow-step-lg)', 'step-xl': 'var(--shadow-step-xl)',
    selected: 'var(--shadow-selected)', brand: 'var(--shadow-brand)', overlay: 'var(--shadow-overlay)',
  },
  spacing: { gutter: 'var(--gutter-mobile)', touch: 'var(--touch-min)', sidebar: 'var(--sidebar-width)' }, // Tailwind's default 4 px scale already matches --space-*
  maxWidth: { content: 'var(--content-max)' },
  minHeight: { touch: 'var(--touch-min)' }, minWidth: { touch: 'var(--touch-min)' },
  outlineWidth: { focus: 'var(--focus-width)' }, outlineOffset: { focus: 'var(--focus-offset)' }, outlineColor: { focus: 'var(--focus-ring)' },
  transitionDuration: {
    press: 'var(--dur-press)', select: 'var(--dur-select)', 'reveal-hold': 'var(--dur-reveal-hold)', 'reveal-sweep': 'var(--dur-reveal-sweep)', 'reveal-panel': 'var(--dur-reveal-panel)',
    xp: 'var(--dur-xp)', rating: 'var(--dur-rating)', streak: 'var(--dur-streak)', 'level-up': 'var(--dur-level-up)',
    'overlay-in': 'var(--dur-overlay-in)', 'overlay-out': 'var(--dur-overlay-out)', 'toast-in': 'var(--dur-toast-in)', 'toast-out': 'var(--dur-toast-out)',
  },
  transitionTimingFunction: { standard: 'var(--ease-standard)', 'pixel-5': 'var(--ease-pixel-5)', 'pixel-6': 'var(--ease-pixel-6)' },
}
