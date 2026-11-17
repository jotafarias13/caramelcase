import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

// "Card" in design/README.md: the plain surface most sections sit on.
export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3 rounded-card border border-border bg-surface p-4",
        className,
      )}
      {...props}
    />
  );
}

// "Caramel card": the goal card and other moments that ask for one action.
// Its button is <Button variant="onCaramel">. Leave 6 px of room on the
// right and bottom for the hard shadow.
export function CaramelCard({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3.5 rounded-card bg-brand p-4 text-brand-fg shadow-step-xl",
        className,
      )}
      {...props}
    />
  );
}
