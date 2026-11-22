import { House, Settings, User, type LucideIcon } from "lucide-react";
import { Suspense } from "react";
import { useTranslation } from "react-i18next";
import { NavLink, Outlet } from "react-router";
import { LoadingState } from "@/components/StateScreen";
import { UserChips } from "@/components/UserChips";
import { Wordmark } from "@/components/Wordmark";
import { cn } from "@/lib/utils";

type Destination = {
  to: string;
  label: "nav.home" | "nav.profile" | "nav.settings";
  Icon: LucideIcon;
};

// V1 navigation. Revisão and Ligas join it with their flags (milestone 9).
const home: Destination = { to: "/home", label: "nav.home", Icon: House };
const profile: Destination = {
  to: "/profile",
  label: "nav.profile",
  Icon: User,
};
const settings: Destination = {
  to: "/settings",
  label: "nav.settings",
  Icon: Settings,
};

function SidebarItem({ to, label, Icon }: Destination) {
  const { t } = useTranslation();
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cn(
          "group flex h-11 items-center gap-3 rounded-md px-3 text-[15px]",
          isActive
            ? "bg-brand font-bold text-brand-fg shadow-brand"
            : "font-medium text-fg hover:bg-surface-raised",
        )
      }
    >
      <Icon
        aria-hidden="true"
        strokeWidth={2.25}
        className="size-5 shrink-0 text-fg-muted group-aria-[current=page]:text-brand-fg"
      />
      <span className="grow">{t(label)}</span>
    </NavLink>
  );
}

/** From 1280 px: 248 px wide, on the left. */
function Sidebar() {
  const { t } = useTranslation();
  return (
    <nav
      aria-label={t("nav.main")}
      className="sticky top-0 hidden h-dvh w-sidebar shrink-0 flex-col gap-5 border-r border-border bg-surface pt-6 pr-3.5 pb-5 pl-3 lg:flex"
    >
      <div className="px-2">
        <Wordmark className="text-[20px] leading-[26px]" />
      </div>
      <div className="flex flex-col gap-1.5">
        <SidebarItem {...home} />
        <SidebarItem {...profile} />
      </div>
      <div className="grow" />
      <UserChips shownOn="desktop" className="px-2" />
      <div className="h-px bg-border" />
      <SidebarItem {...settings} />
    </nav>
  );
}

function TabBarItem({ to, label, Icon }: Destination) {
  const { t } = useTranslation();
  return (
    <NavLink
      to={to}
      className="group flex min-h-13 flex-col items-center justify-center gap-[3px] rounded-md"
    >
      <span
        className={cn(
          "flex h-7 w-12 items-center justify-center rounded-tile text-fg-muted",
          "group-active:bg-surface-raised",
          "group-aria-[current=page]:bg-brand group-aria-[current=page]:text-brand-fg",
        )}
      >
        <Icon aria-hidden="true" strokeWidth={2.25} className="size-5" />
      </span>
      <span className="text-[11px] leading-[14px] font-medium text-fg-muted group-aria-[current=page]:font-bold group-aria-[current=page]:text-fg">
        {t(label)}
      </span>
    </NavLink>
  );
}

/** Below 1280 px: along the bottom edge, above the home indicator. */
function TabBar() {
  const { t } = useTranslation();
  return (
    <nav
      aria-label={t("nav.main")}
      className="sticky bottom-0 z-30 grid grid-cols-3 border-t border-border bg-surface px-2 pt-1.5 pb-[calc(20px+env(safe-area-inset-bottom))] lg:hidden"
    >
      <TabBarItem {...home} />
      <TabBarItem {...profile} />
      <TabBarItem {...settings} />
    </nav>
  );
}

/**
 * The frame of Home, Profile, Settings and the catalog: navigation plus a
 * column for the screen. Sessions, onboarding and sign-in do not use it.
 */
export function AppShell() {
  return (
    <div className="flex min-h-dvh flex-col lg:flex-row">
      <Sidebar />
      <main
        className={cn(
          "flex min-w-0 grow flex-col gap-4 px-4 pb-5",
          "pt-[calc(16px+env(safe-area-inset-top))]",
          "md:mx-auto md:w-full md:max-w-[688px] md:px-6",
          "lg:mx-0 lg:max-w-[1120px] lg:gap-6 lg:px-10 lg:pt-8 lg:pb-10",
        )}
      >
        <Suspense fallback={<LoadingState />}>
          <Outlet />
        </Suspense>
      </main>
      <TabBar />
    </div>
  );
}
