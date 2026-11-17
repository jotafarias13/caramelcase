import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type IconButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  /** What the button does: an icon alone says nothing to a screen reader. */
  "aria-label": string;
};

// "Icon button" in design/README.md: 44 × 44, transparent.
export function IconButton({
  className,
  type = "button",
  ...props
}: IconButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex size-11 shrink-0 cursor-pointer items-center justify-center rounded-md",
        "bg-transparent text-fg-muted hover:bg-surface-raised active:bg-border",
        "disabled:cursor-not-allowed disabled:text-disabled-text",
        "[&_svg]:size-5 [&_svg]:shrink-0",
        className,
      )}
      {...props}
    />
  );
}
