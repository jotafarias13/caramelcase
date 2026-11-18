import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { cn } from "@/lib/utils";

const link =
  "inline-flex min-h-11 items-center underline underline-offset-3 hover:text-fg";

/**
 * "Privacidade · Termos": the links to the privacy policy and the terms,
 * in the landing page's footer, on sign-in and in Settings.
 */
export function LegalLinks({ className }: { className?: string }) {
  const { t } = useTranslation();
  return (
    <nav
      aria-label={t("legal.links_label")}
      className={cn(
        "flex items-center font-mono text-[12px] leading-4 text-fg-muted",
        className,
      )}
    >
      <Link to="/privacy" className={link}>
        {t("legal.privacy_link")}
      </Link>
      <span aria-hidden="true" className="px-2">
        ·
      </span>
      <Link to="/terms" className={link}>
        {t("legal.terms_link")}
      </Link>
    </nav>
  );
}
