import { lazy, Suspense, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Route, Routes, useLocation } from "react-router";
import { LoadingScreen, NotFoundScreen } from "@/components/StateScreen";
import { LandingPage } from "@/features/landing/LandingPage";
import { AppShell } from "./AppShell";
import { RequireUser } from "./RequireUser";

// The landing page is in the first bundle: it is what a search visitor
// lands on, and the build renders it to static HTML. Everything else loads
// when its route is opened.
const SignInPage = lazy(() => import("@/features/auth/SignInPage"));
const AuthCallbackPage = lazy(() => import("@/features/auth/AuthCallbackPage"));
const OnboardingPage = lazy(
  () => import("@/features/onboarding/OnboardingPage"),
);
const HomePage = lazy(() => import("@/features/home/HomePage"));
const SubjectsPage = lazy(() => import("@/features/catalog/SubjectsPage"));
const ProfilePage = lazy(() => import("@/features/profile/ProfilePage"));
const SettingsPage = lazy(() => import("@/features/settings/SettingsPage"));
const SessionPage = lazy(() => import("@/features/session/SessionPage"));
const SummaryPage = lazy(() => import("@/features/summary/SummaryPage"));
const PrivacyPage = lazy(() => import("@/features/legal/PrivacyPage"));
const TermsPage = lazy(() => import("@/features/legal/TermsPage"));

// Flagged routes (/review, /exam, /leagues, /pricing, /tutor, /admin) are
// added in milestones 9 and 10, each as
//   <Route path="/review" element={<Flagged flag="review_queue"><ReviewPage /></Flagged>} />
// with ReviewPage a lazy import: see ./Flagged.tsx.

/** The landing page has a title for search results; the app has its name. */
function useDocumentTitle() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const title = pathname === "/" ? t("landing.meta_title") : t("common.brand");
  useEffect(() => {
    document.title = title;
  }, [title]);
}

export function AppRoutes() {
  useDocumentTitle();
  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />

        <Route element={<RequireUser />}>
          <Route path="/start" element={<OnboardingPage />} />
          <Route path="/session/:id" element={<SessionPage />} />
          <Route path="/session/:id/summary" element={<SummaryPage />} />
          <Route element={<AppShell />}>
            <Route path="/home" element={<HomePage />} />
            <Route path="/subjects" element={<SubjectsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundScreen />} />
      </Routes>
    </Suspense>
  );
}
