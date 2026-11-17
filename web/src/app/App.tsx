import { BrowserRouter } from "react-router";
import { Toaster } from "@/components/ui/toaster";
import { AppProviders } from "./providers";
import { AppRoutes } from "./routes";

export function App() {
  return (
    <AppProviders>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
      <Toaster />
    </AppProviders>
  );
}
