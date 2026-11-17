import { X } from "lucide-react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router";
import { IconButton } from "@/components/ui/icon-button";
import { cn } from "@/lib/utils";

/**
 * Close goes back to wherever the student came from; opened from a link
 * with nothing before it, to Home.
 */
function useClose(): () => void {
  const navigate = useNavigate();
  const location = useLocation();
  return () => {
    if (location.key === "default") navigate("/home");
    else navigate(-1);
  };
}

function CloseButton() {
  const { t } = useTranslation();
  const close = useClose();
  return (
    <IconButton
      aria-label={t("common.close")}
      onClick={close}
      className="[&_svg]:size-[22px]"
    >
      <X />
    </IconButton>
  );
}

/**
 * The frame of v1-signin and v1-signin-sent. Phones: a close button above
 * the content. From 1280 px: a 440 px card in the middle of the window,
 * with the close button in its corner.
 */
export function AuthFrame({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col lg:items-center lg:justify-center lg:p-10">
      <div
        className={cn(
          "relative flex w-full flex-col md:mx-auto md:max-w-[688px]",
          "lg:mx-0 lg:w-[440px] lg:max-w-none",
          "lg:rounded-xl lg:border lg:border-border lg:bg-surface lg:p-8 lg:shadow-step-xl",
        )}
      >
        <div className="flex items-center px-2 pt-[calc(8px+env(safe-area-inset-top))] md:px-4 lg:absolute lg:top-2 lg:right-2 lg:p-0">
          <CloseButton />
        </div>
        <div className="flex flex-col gap-4 px-4 pt-2 pb-[calc(24px+env(safe-area-inset-bottom))] md:px-6 lg:p-0">
          {children}
        </div>
      </div>
    </div>
  );
}

/** Mel, the title and the line under it. */
export function AuthIntro({
  mel,
  title,
  body,
}: {
  mel: ReactNode;
  title: string;
  body: string;
}) {
  return (
    <>
      {mel}
      <h1 className="text-[24px] leading-[30px] font-bold tracking-[-0.01em] text-balance">
        {title}
      </h1>
      <p className="text-[15px] leading-[22px] text-fg-muted">{body}</p>
    </>
  );
}
