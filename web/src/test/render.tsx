import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { MemoryRouter } from "react-router";
import type { Locale } from "@/api/types";
import { AppProviders } from "@/app/providers";
import { AppRoutes } from "@/app/routes";
import { Toaster } from "@/components/ui/toaster";
import { initI18n } from "@/i18n";
import { world } from "./fixtures";
import type { Routes } from "./mock-api";
import { stubApi } from "./stub-api";

type Options = {
  /** API answers on top of fixtures.ts's world. */
  routes?: Routes;
  /** The interface language; Portuguese unless a test says otherwise. */
  locale?: Locale;
};

function testQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, networkMode: "always" },
      mutations: { networkMode: "always" },
    },
  });
}

function setUp({ routes, locale = "pt-BR" }: Options) {
  initI18n(locale);
  return {
    api: stubApi(world(routes)),
    user: userEvent.setup(),
    queryClient: testQueryClient(),
  };
}

/**
 * The whole app at an address, against the mock API: what a student sees
 * after opening that link. Pages load lazily, so find things with
 * `await screen.findBy...`.
 */
export function renderApp(path: string, options: Options = {}) {
  const { api, user, queryClient } = setUp(options);
  const view = render(
    <AppProviders queryClient={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>
      <Toaster />
    </AppProviders>,
  );
  return { ...view, api, user, queryClient };
}

/** One component with the app's providers and a router around it. */
export function renderWithProviders(ui: ReactNode, options: Options = {}) {
  const { api, user, queryClient } = setUp(options);
  const view = render(
    <AppProviders queryClient={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
      <Toaster />
    </AppProviders>,
  );
  return { ...view, api, user, queryClient };
}
