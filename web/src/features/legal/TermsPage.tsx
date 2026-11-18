import { useTranslation } from "react-i18next";
import { LegalDocument } from "./LegalDocument";

// The sections of legal.terms in the translation files, in order.
const sections = [
  "service",
  "account",
  "conduct",
  "content",
  "price",
  "liability",
  "ending",
  "law",
  "contact",
] as const;

/** /terms: the terms of use, with placeholder legal text. */
export default function TermsPage() {
  const { t } = useTranslation();
  return (
    <LegalDocument
      title={t("legal.terms.title")}
      intro={t("legal.terms.intro")}
      sections={sections.map((section) => ({
        title: t(`legal.terms.${section}_title`),
        body: t(`legal.terms.${section}_body`),
      }))}
    />
  );
}
