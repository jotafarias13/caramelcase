import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@design/tokens.css";
import "./styles/index.css";
import { App } from "./app/App";
import { startMonitoring } from "./lib/monitoring";
import { initTheme } from "./lib/theme";

initTheme();
startMonitoring();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
