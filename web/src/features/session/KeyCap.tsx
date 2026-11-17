import type { ReactNode } from "react";

/** A key on the keyboard, in the desktop hints: "1", "Enter". */
export function KeyCap({ children }: { children: ReactNode }) {
  return (
    <kbd className="rounded-xs border border-border-strong px-1.5 py-px font-mono text-[11px] leading-4 text-fg">
      {children}
    </kbd>
  );
}
