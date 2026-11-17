import { Dialog } from "radix-ui";
import { useRef } from "react";
import { useTranslation } from "react-i18next";
import { Mel } from "@/components/Mel";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type SaveProgressPromptProps = {
  open: boolean;
  onSave: () => void;
  onDismiss: () => void;
};

// v1-summary-save: a bottom sheet on phones and a 440 px modal from
// 1280 px. Built on Radix Dialog like components/ui/sheet.tsx, which has no
// place for Mel beside the title and spaces title and text differently.
export function SaveProgressPrompt({
  open,
  onSave,
  onDismiss,
}: SaveProgressPromptProps) {
  const { t } = useTranslation();
  const content = useRef<HTMLDivElement>(null);
  return (
    <Dialog.Root open={open} onOpenChange={(next) => !next && onDismiss()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 animate-[fade-in_var(--dur-overlay-in)_var(--ease-standard)] bg-overlay" />
        <Dialog.Content
          ref={content}
          // Focus goes to the dialog itself, so a screen reader reads the
          // question first and no button looks chosen before a tap.
          onOpenAutoFocus={(event) => {
            event.preventDefault();
            content.current?.focus();
          }}
          className={cn(
            "fixed z-50 flex flex-col gap-4 border-border-strong bg-surface text-fg outline-none",
            "animate-[rise-in_var(--dur-overlay-in)_var(--ease-standard)]",
            // Phones: a sheet on the bottom edge.
            "inset-x-0 bottom-0 rounded-t-xl border-t-[1.5px] px-4 pt-5 pb-[calc(24px+env(safe-area-inset-bottom))]",
            // From 1280 px: a modal in the middle.
            "lg:inset-x-auto lg:top-1/2 lg:bottom-auto lg:left-1/2 lg:w-[440px] lg:-translate-x-1/2 lg:-translate-y-1/2",
            "lg:gap-[18px] lg:rounded-xl lg:border-[1.5px] lg:p-6 lg:shadow-overlay",
          )}
        >
          <div className="flex items-center gap-3">
            <Mel pose="wave" head scale={4} />
            <div className="flex min-w-0 flex-col gap-1">
              <Dialog.Title className="text-[20px] leading-[26px] font-bold">
                {t("summary.save_title")}
              </Dialog.Title>
              <Dialog.Description className="text-[14px] leading-5 text-fg-muted">
                {t("summary.save_body")}
              </Dialog.Description>
            </div>
          </div>
          <div className="flex flex-col gap-2.5 pr-1">
            <Button className="w-full" onClick={onSave}>
              {t("summary.save_action")}
            </Button>
            <Button
              variant="ghost"
              size="md"
              className="w-full"
              onClick={onDismiss}
            >
              {t("summary.save_later")}
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
