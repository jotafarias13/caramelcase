import { useId, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";
import { errorKind } from "@/api/client";
import {
  useDeleteAccount,
  useLogout,
  useMe,
  usePatchSettings,
} from "@/api/queries";
import type { Locale, Me, ThemeSetting } from "@/api/types";
import { LoadingState } from "@/components/StateScreen";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { Card } from "@/components/ui/card";
import { SegmentedControl } from "@/components/ui/segmented-control";
import { Switch } from "@/components/ui/switch";
import { toast } from "@/components/ui/toast-store";
import { locales } from "@/i18n";
import { useFlag } from "@/lib/flags";
import { useChangeLocale, useChangeTheme } from "@/lib/preferences";
import { getThemeChoice } from "@/lib/theme";
import { LegalLinks } from "@/features/legal/LegalLinks";
import { DeleteAccountDialog } from "./DeleteAccountDialog";

const themes: ThemeSetting[] = ["light", "dark", "system"];

// Everything the API keeps about the user (LGPD's right of access).
const EXPORT_URL = "/api/v1/me/export";
const EXPORT_FILE_NAME = "caramelcase-data.json";

/**
 * Says that a change did not reach the account. Called after the control
 * went back, so the message is in the language now on screen.
 */
function useSaveFailed() {
  const { t } = useTranslation();
  return (error: unknown, message: string = t("settings.save_failed")) => {
    if (errorKind(error) === "offline") {
      toast({ kind: "offline", message: t("states.offline_title") });
    } else {
      toast({ kind: "error", message });
    }
  };
}

export default function SettingsPage() {
  const me = useMe();
  // RequireUser has loaded the user before any page renders.
  if (!me.data) return <LoadingState />;
  return <Settings me={me.data} />;
}

/** Every change applies at once; there is no save button. */
function Settings({ me }: { me: Me }) {
  const { t } = useTranslation();
  const reminders = useFlag("reminders");

  return (
    <>
      <h1 className="text-[24px] leading-[30px] font-bold tracking-[-0.01em] text-balance lg:text-[30px] lg:leading-9">
        {t("settings.title")}
      </h1>
      <div className="flex flex-col gap-4 lg:max-w-[640px]">
        <LanguageCard />
        <ThemeCard me={me} />
        <Card>
          <h2 className="text-[18px] leading-6 font-bold text-fg">
            {t("settings.session")}
          </h2>
          <SettingSwitch
            me={me}
            field="show_option_reasons"
            label={t("settings.explain_options")}
            description={t("settings.explain_options_body")}
          />
        </Card>
        {/* Hidden until reminders exist (docs/DECISIONS.md). */}
        {reminders && (
          <Card>
            <h2 className="text-[18px] leading-6 font-bold text-fg">
              {t("settings.notifications")}
            </h2>
            <SettingSwitch
              me={me}
              field="daily_reminder"
              label={t("settings.daily_reminder")}
              description={t("settings.daily_reminder_body")}
            />
          </Card>
        )}
        <AccountCard me={me} />
        <LegalLinks />
      </div>
    </>
  );
}

function LanguageCard() {
  const { t, i18n } = useTranslation();
  const saveFailed = useSaveFailed();
  const changeLocale = useChangeLocale((error) => saveFailed(error));

  return (
    <Card>
      <h2 className="text-[18px] leading-6 font-bold text-fg">
        {t("common.language")}
      </h2>
      <SegmentedControl
        label={t("common.language")}
        value={i18n.language as Locale}
        options={locales.map((locale) => ({
          value: locale,
          label: t(`common.languages.${locale}`),
        }))}
        onChange={changeLocale}
      />
    </Card>
  );
}

function ThemeCard({ me }: { me: Me }) {
  const { t } = useTranslation();
  const saveFailed = useSaveFailed();
  // The account's choice, which the device follows (RequireUser).
  const [theme, setTheme] = useState<ThemeSetting>(me.settings.theme);
  const changeTheme = useChangeTheme((error) => {
    // The device went back to what it had; so does the control.
    setTheme(getThemeChoice());
    saveFailed(error);
  });

  return (
    <Card>
      <h2 className="text-[18px] leading-6 font-bold text-fg">
        {t("settings.theme")}
      </h2>
      <SegmentedControl
        label={t("settings.theme")}
        value={theme}
        options={themes.map((value) => ({
          value,
          label: t(`settings.themes.${value}`),
        }))}
        onChange={(next) => {
          setTheme(next);
          changeTheme(next);
        }}
      />
    </Card>
  );
}

type SettingSwitchProps = {
  me: Me;
  field: "show_option_reasons" | "daily_reminder";
  label: string;
  description: string;
};

/**
 * A switch saved to the account at once. While the request runs it shows
 * the new value; if the request fails it shows the account's value again.
 */
function SettingSwitch({ me, field, label, description }: SettingSwitchProps) {
  const id = useId();
  const patch = usePatchSettings();
  const saveFailed = useSaveFailed();
  const saving = patch.isPending ? patch.variables[field] : null;
  const checked = saving ?? me.settings[field];

  return (
    <div className="flex min-h-11 items-center justify-between gap-3.5">
      <div className="flex min-w-0 flex-col gap-0.5">
        <label
          htmlFor={id}
          className="cursor-pointer text-[15px] leading-5 font-semibold text-fg"
        >
          {label}
        </label>
        <span
          id={`${id}-description`}
          className="text-[13px] leading-[18px] text-fg-muted"
        >
          {description}
        </span>
      </div>
      <Switch
        id={id}
        aria-describedby={`${id}-description`}
        checked={checked}
        onCheckedChange={(value) =>
          patch.mutate({ [field]: value }, { onError: (e) => saveFailed(e) })
        }
      />
    </div>
  );
}

/**
 * The email, "Sair" and "Excluir conta". A guest has no email and nothing
 * to sign out of: the row offers sign-in instead, which keeps the guest's
 * progress. Deleting is there for both, since a guest's data is erased
 * the same way.
 */
function AccountCard({ me }: { me: Me }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const logout = useLogout();
  const deleteAccount = useDeleteAccount();
  const saveFailed = useSaveFailed();
  const [confirming, setConfirming] = useState(false);

  function signOut() {
    logout.mutate(undefined, {
      onSuccess: () => navigate("/"),
      onError: (error) => saveFailed(error, t("settings.sign_out_failed")),
    });
  }

  function confirmDelete() {
    deleteAccount.mutate(undefined, {
      onSuccess: () => navigate("/"),
      onError: (error) => {
        // Closed first: while it is open, the rest of the page, the toast
        // included, is hidden from screen readers.
        setConfirming(false);
        saveFailed(error, t("settings.delete_failed"));
      },
    });
  }

  return (
    <Card>
      <h2 className="text-[18px] leading-6 font-bold text-fg">
        {t("settings.account")}
      </h2>
      <div className="flex flex-wrap items-center justify-between gap-3 pr-[3px]">
        {me.is_guest ? (
          <>
            <span className="text-[15px] leading-5 font-medium text-fg">
              {t("settings.guest")}
            </span>
            <Link
              to="/signin"
              className={buttonVariants({ variant: "secondary", size: "md" })}
            >
              {t("settings.sign_in")}
            </Link>
          </>
        ) : (
          <>
            <span className="min-w-0 text-[15px] leading-5 font-medium break-all text-fg">
              {me.email}
            </span>
            <Button
              variant="secondary"
              size="md"
              loading={logout.isPending}
              onClick={signOut}
            >
              {t("settings.sign_out")}
            </Button>
          </>
        )}
      </div>
      <div className="h-px bg-border" />
      <div className="flex flex-col">
        {/* A plain download of GET /me/export, with the session cookie. */}
        <a
          href={EXPORT_URL}
          download={EXPORT_FILE_NAME}
          className="flex min-h-11 w-max items-center text-[14px] leading-5 font-semibold text-fg underline underline-offset-3"
        >
          {t("settings.download_data")}
        </a>
        <span className="text-[13px] leading-[18px] text-fg-muted">
          {t("settings.download_data_body")}
        </span>
      </div>
      <div className="flex flex-col">
        <button
          type="button"
          onClick={() => setConfirming(true)}
          className="flex min-h-11 w-max cursor-pointer items-center gap-1.5 text-[14px] leading-5 font-semibold text-wrong-text underline underline-offset-3"
        >
          {t("settings.delete_account")}
        </button>
        <span className="text-[13px] leading-[18px] text-fg-muted">
          {t("settings.delete_account_body")}
        </span>
      </div>
      <DeleteAccountDialog
        open={confirming}
        onOpenChange={(open) => !deleteAccount.isPending && setConfirming(open)}
        onConfirm={confirmDelete}
        pending={deleteAccount.isPending}
      />
    </Card>
  );
}
