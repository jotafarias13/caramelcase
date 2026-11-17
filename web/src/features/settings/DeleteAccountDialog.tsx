import { AlertDialog } from "radix-ui";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type DeleteAccountDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  pending: boolean;
};

/**
 * "Excluir sua conta?" (v1-settings-delete). A destructive confirmation:
 * an alert dialog with the safe choice first and no close button
 * (design/README.md, "Modal"). Esc and "Cancelar" close it; a tap on the
 * backdrop does not.
 */
export function DeleteAccountDialog({
  open,
  onOpenChange,
  onConfirm,
  pending,
}: DeleteAccountDialogProps) {
  const { t } = useTranslation();
  return (
    <AlertDialog.Root open={open} onOpenChange={onOpenChange}>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="fixed inset-0 z-50 animate-[fade-in_var(--dur-overlay-in)_var(--ease-standard)] bg-overlay" />
        <AlertDialog.Content
          className={cn(
            "fixed top-1/2 left-1/2 z-50 w-[calc(100%-32px)] max-w-[480px] -translate-x-1/2 -translate-y-1/2",
            "flex flex-col gap-2.5 rounded-xl border-[1.5px] border-border-strong bg-surface p-6",
            "text-fg shadow-overlay animate-[rise-in_var(--dur-overlay-in)_var(--ease-standard)]",
          )}
        >
          <AlertDialog.Title className="text-[20px] leading-[26px] font-bold">
            {t("settings.delete_title")}
          </AlertDialog.Title>
          <AlertDialog.Description className="text-[15px] leading-[22px] text-fg-muted">
            {t("settings.delete_body")}
          </AlertDialog.Description>
          <div className="mt-2.5 flex flex-wrap items-center justify-end gap-3 pr-1">
            <AlertDialog.Cancel asChild>
              <Button variant="secondary" size="md" disabled={pending}>
                {t("common.cancel")}
              </Button>
            </AlertDialog.Cancel>
            {/* Not AlertDialog.Action, which closes the dialog at once: it
                stays open, with a spinner, while the request runs. */}
            <Button
              variant="danger"
              size="md"
              loading={pending}
              onClick={onConfirm}
            >
              {t("settings.delete_account")}
            </Button>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
}
