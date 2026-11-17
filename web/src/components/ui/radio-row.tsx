import { RadioGroup } from "radix-ui";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type RadioRowsProps<Value extends string> = {
  /** Names the group for screen readers. */
  label: string;
  value: Value | null;
  onChange: (value: Value) => void;
  children: ReactNode;
  className?: string;
};

/** The group around RadioRow items; the arrow keys move between them. */
export function RadioRows<Value extends string>({
  label,
  value,
  onChange,
  children,
  className,
}: RadioRowsProps<Value>) {
  return (
    <RadioGroup.Root
      aria-label={label}
      // "" keeps the group controlled while nothing is chosen.
      value={value ?? ""}
      onValueChange={(next) => onChange(next as Value)}
      className={cn("flex flex-col gap-2.5 pr-[3px]", className)}
    >
      {children}
    </RadioGroup.Root>
  );
}

type RadioRowProps = {
  value: string;
  title: string;
  /** A second, smaller line. */
  sub?: string;
  /** Sits before the title: a subject's badge, for example. */
  leading?: ReactNode;
  disabled?: boolean;
};

// "Radio row" in design/README.md.
export function RadioRow({
  value,
  title,
  sub,
  leading,
  disabled,
}: RadioRowProps) {
  return (
    <RadioGroup.Item
      value={value}
      disabled={disabled}
      className={cn(
        "group flex min-h-14 w-full cursor-pointer items-center gap-3 rounded-lg px-3.5 py-2 text-left",
        "border-[1.5px] border-border-strong bg-surface text-fg shadow-step-md",
        "transition-[translate,box-shadow] duration-press ease-linear",
        "hover:bg-surface-raised active:translate-x-0.5 active:translate-y-0.5",
        "active:shadow-[1px_1px_0_var(--shadow-hard)]",
        "data-[state=checked]:border-2 data-[state=checked]:border-action-border",
        "data-[state=checked]:bg-action-tint data-[state=checked]:shadow-selected",
        "disabled:cursor-not-allowed disabled:border-border disabled:bg-bg disabled:shadow-none",
      )}
    >
      {leading}
      <span className="flex min-w-0 grow flex-col gap-0.5">
        <span className="text-[16px] leading-[22px] font-medium group-data-[state=checked]:font-bold">
          {title}
        </span>
        {sub && (
          <span className="text-[13px] leading-[18px] text-fg-muted">
            {sub}
          </span>
        )}
      </span>
      {/* The mockups draw the ring as a 20 px icon: a 17 px circle in it. */}
      <span
        aria-hidden="true"
        className="flex size-5 shrink-0 items-center justify-center"
      >
        <span
          className={cn(
            "flex size-[17px] items-center justify-center rounded-full",
            "border-2 border-border-strong group-data-[state=checked]:border-action-text",
          )}
        >
          <span className="hidden size-2 rounded-full bg-action-text group-data-[state=checked]:block" />
        </span>
      </span>
    </RadioGroup.Item>
  );
}
