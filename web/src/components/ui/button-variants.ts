import { cva } from "class-variance-authority";

// States and sizes follow "Button" in design/README.md.
const pressShift = "active:translate-x-0.5 active:translate-y-0.5";

export const buttonVariants = cva(
  [
    "inline-flex shrink-0 cursor-pointer items-center justify-center gap-2",
    "rounded-lg font-sans font-bold whitespace-nowrap",
    "transition-[translate,box-shadow,background-color] duration-press ease-linear",
    "disabled:cursor-not-allowed disabled:translate-none disabled:shadow-none",
    "[&_svg]:size-[18px] [&_svg]:shrink-0",
  ],
  {
    variants: {
      variant: {
        primary: [
          "[border:var(--btn-border)] bg-action text-action-fg shadow-step-lg",
          "hover:bg-action-hover active:bg-action-pressed",
          "active:shadow-[2px_2px_0_var(--action-shadow)]",
          "disabled:border-transparent disabled:bg-disabled disabled:text-disabled-text",
          // Loading is not disabled to the eye: the fill stays (Verificando…).
          "aria-busy:disabled:[border:var(--btn-border)] aria-busy:disabled:bg-action",
          "aria-busy:disabled:text-action-fg aria-busy:disabled:shadow-step-lg",
          "aria-busy:disabled:cursor-progress",
          pressShift,
        ],
        secondary: [
          "border-[1.5px] border-border-strong bg-surface text-fg shadow-step-md",
          "hover:bg-surface-raised active:shadow-[1px_1px_0_var(--shadow-hard)]",
          "disabled:border-transparent disabled:bg-disabled disabled:text-disabled-text",
          pressShift,
        ],
        ghost: [
          "border-[1.5px] border-transparent bg-transparent text-action-text",
          "hover:bg-surface-raised active:bg-border",
          "disabled:bg-transparent disabled:text-disabled-text",
        ],
        danger: [
          "[border:var(--btn-border)] bg-wrong text-wrong-fg",
          "shadow-[4px_4px_0_var(--wrong-shadow)]",
          "hover:bg-wrong-hover active:bg-wrong-pressed",
          "active:shadow-[2px_2px_0_var(--wrong-shadow)]",
          "disabled:border-transparent disabled:bg-disabled disabled:text-disabled-text",
          pressShift,
        ],
        // The button that sits on a caramel card.
        onCaramel: [
          "bg-ink text-brand-cream shadow-[4px_4px_0_var(--brand-deep)]",
          "hover:bg-ink-raised active:shadow-[2px_2px_0_var(--brand-deep)]",
          pressShift,
        ],
      },
      size: {
        lg: "h-13 px-[22px] text-button",
        md: "h-11 px-[18px] text-[15px] leading-5",
        sm: "h-9 px-3.5 text-[14px] leading-5",
      },
    },
    defaultVariants: { variant: "primary", size: "lg" },
  },
);
