import { useTranslation } from "react-i18next";
import { LegalDocument } from "./LegalDocument";

// The sections of legal.privacy in the translation files, in order.
const sections = [
  "who",
  "data",
  "use",
  "device",
  "sharing",
  "retention",
  "rights",
  "basis",
  "changes",
] as const;

/** /privacy: the privacy policy, with placeholder legal text. */
export default function PrivacyPage() {
  const { t } = useTranslation();
  return (
    <LegalDocument
      title={t("legal.privacy.title")}
      intro={t("legal.privacy.intro")}
      sections={sections.map((section) => ({
        title: t(`legal.privacy.${section}_title`),
        body: t(`legal.privacy.${section}_body`),
      }))}
    />
  );
}
