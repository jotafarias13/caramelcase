import { CircleCheck, CircleX, Info, WifiOff, X } from "lucide-react";
import { useSyncExternalStore } from "react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import { IconButton } from "./icon-button";
import {
  dismissToast,
  getToasts,
  subscribeToasts,
  type ToastKind,
} from "./toast-store";

const icons: Record<ToastKind, { Icon: typeof Info; className: string }> = {
  success: { Icon: CircleCheck, className: "text-correct-text" },
  error: { Icon: CircleX, className: "text-wrong-text" },
  offline: { Icon: WifiOff, className: "text-warning-text" },
  info: { Icon: Info, className: "text-info-text" },
};

// "Toast" in design/README.md. Rendered once, by the app; sits above the
// tab bar on phones.
export function Toaster() {
  const { t } = useTranslation();
  const toasts = useSyncExternalStore(subscribeToasts, getToasts, getToasts);

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-[calc(96px+env(safe-area-inset-bottom))] z-[60] flex flex-col items-center gap-2 px-3 lg:bottom-6">
      {toasts.map((toast) => {
        const { Icon, className } = icons[toast.kind];
        return (
          <div
            key={toast.id}
            role="status"
            className={cn(
              "pointer-events-auto flex min-h-14 w-full max-w-[360px] items-center gap-2.5 pl-3.5",
              "rounded-lg border-[1.5px] border-border-strong bg-surface shadow-overlay",
              "animate-[toast-in_var(--dur-toast-in)_ease-out]",
            )}
          >
            <Icon
              aria-hidden="true"
              className={cn("size-5 shrink-0", className)}
            />
            <span className="grow py-2 text-[14px] leading-5 font-medium text-fg">
              {toast.message}
            </span>
            {toast.action && (
              <button
                type="button"
                onClick={toast.action.onClick}
                className="min-h-touch cursor-pointer px-1 text-[14px] leading-5 font-bold text-action-text"
              >
                {toast.action.label}
              </button>
            )}
            <IconButton
              aria-label={t("common.close")}
              onClick={() => dismissToast(toast.id)}
            >
              <X aria-hidden="true" />
            </IconButton>
          </div>
        );
      })}
    </div>
  );
}
