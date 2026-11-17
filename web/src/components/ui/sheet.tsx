import { X } from "lucide-react";
import { Dialog } from "radix-ui";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { IconButton } from "./icon-button";

type SheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  /**
   * "sheet" rises from the bottom edge, "modal" sits in the middle, and
   * "responsive" is a sheet on phones and a modal from 1280 px.
   */
  placement?: "sheet" | "modal" | "responsive";
  /** The label of the close button; leave out on a destructive question. */
  closeLabel?: string;
  /** The 40 × 4 handle on top of a sheet. */
  handle?: boolean;
  children: ReactNode;
  className?: string;
};

const sheetClasses = [
  "inset-x-0 bottom-0 rounded-t-xl border-t-[1.5px] px-4 pt-5",
  "pb-[calc(24px+env(safe-area-inset-bottom))]",
];
const modalClasses = [
  "top-1/2 left-1/2 w-[calc(100%-32px)] max-w-[480px] -translate-x-1/2 -translate-y-1/2",
  "rounded-xl border-[1.5px] p-6",
];
// The same two, with the modal's classes behind the lg: breakpoint.
const responsiveClasses = [
  "max-lg:inset-x-0 max-lg:bottom-0 max-lg:rounded-t-xl max-lg:border-t-[1.5px]",
  "max-lg:px-4 max-lg:pt-5 max-lg:pb-[calc(24px+env(safe-area-inset-bottom))]",
  "lg:top-1/2 lg:left-1/2 lg:w-full lg:max-w-[480px] lg:-translate-x-1/2 lg:-translate-y-1/2",
  "lg:rounded-xl lg:border-[1.5px] lg:p-6",
];

// "Modal" and "Bottom sheet" in design/README.md, on Radix Dialog: focus is
// trapped, Esc closes, and focus goes back to what opened it.
export function Sheet({
  open,
  onOpenChange,
  title,
  description,
  placement = "responsive",
  closeLabel,
  handle = false,
  children,
  className,
}: SheetProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 animate-[fade-in_var(--dur-overlay-in)_var(--ease-standard)] bg-overlay" />
        <Dialog.Content
          // Without a description Radix asks for this to be explicit.
          {...(description ? {} : { "aria-describedby": undefined })}
          className={cn(
            "fixed z-50 flex max-h-[calc(100dvh-24px)] flex-col gap-4 overflow-y-auto",
            "border-border-strong bg-surface text-fg shadow-overlay",
            "animate-[rise-in_var(--dur-overlay-in)_var(--ease-standard)]",
            placement === "sheet" && sheetClasses,
            placement === "modal" && modalClasses,
            placement === "responsive" && responsiveClasses,
            className,
          )}
        >
          {handle && (
            <div
              aria-hidden="true"
              className="-mt-1 h-1 w-10 shrink-0 self-center rounded-full bg-border-strong"
            />
          )}
          <div className="flex items-start gap-3">
            <div className="flex min-w-0 grow flex-col gap-2">
              <Dialog.Title className="text-[20px] leading-[26px] font-bold">
                {title}
              </Dialog.Title>
              {description && (
                <Dialog.Description className="text-[15px] leading-[22px] text-fg-muted">
                  {description}
                </Dialog.Description>
              )}
            </div>
            {closeLabel && (
              <Dialog.Close asChild>
                <IconButton aria-label={closeLabel} className="-mt-2 -mr-2">
                  <X aria-hidden="true" />
                </IconButton>
              </Dialog.Close>
            )}
          </div>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
