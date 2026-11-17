import { existsSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import type { Plugin } from "vite";
import { VitePWA } from "vite-plugin-pwa";
import { defineConfig } from "vitest/config";

const designDir = path.resolve(import.meta.dirname, "../design");
const prerenderEntry = path.resolve(
  import.meta.dirname,
  "dist-ssr/prerender.js",
);

function escapeAttribute(text: string): string {
  return text.replace(/&/g, "&amp;").replace(/"/g, "&quot;");
}

/**
 * Puts the landing page into index.html as static HTML. `npm run build`
 * first builds src/prerender.tsx for Node (into dist-ssr/), then builds the
 * app; this plugin runs in the second build, calls the first one's render()
 * and writes its result into the page.
 */
function landingPrerender(): Plugin {
  return {
    name: "landing-prerender",
    apply: (_config, env) => env.command === "build" && !env.isSsrBuild,
    async transformIndexHtml(html) {
      if (!existsSync(prerenderEntry)) {
        throw new Error(
          "dist-ssr/prerender.js is missing: build with `npm run build`.",
        );
      }
      const { render } = await import(pathToFileURL(prerenderEntry).href);
      const page = render();
      return html
        .replace('<div id="root"></div>', `<div id="root">${page.html}</div>`)
        .replace(
          "<title>caramelCase</title>",
          `<title>${page.title}</title>\n    <meta name="description" content="${escapeAttribute(page.description)}" />`,
        );
    },
  };
}

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    landingPrerender(),
    // Installable app. The service worker keeps the app shell only: the
    // built HTML, scripts, styles and images. It never answers for /api,
    // so questions, answers and progress always come from the server.
    VitePWA({
      registerType: "autoUpdate",
      injectRegister: "script-defer",
      manifest: {
        name: "caramelCase",
        short_name: "caramelCase",
        description: "Ciência da computação em sessões de cinco minutos.",
        lang: "pt-BR",
        start_url: "/home",
        scope: "/",
        display: "standalone",
        // --bg and --bg of the dark theme (design/tokens.css): the splash
        // screen and the status bar before the app paints.
        background_color: "#1B2140",
        theme_color: "#1B2140",
        icons: [
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
          {
            src: "/icons/icon-maskable-512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{html,js,css,svg,png}"],
        // Any address of the single-page app is index.html.
        navigateFallback: "/index.html",
        navigateFallbackDenylist: [/^\/api\//],
        cleanupOutdatedCaches: true,
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "src"),
      // The design handoff is consumed in place, never copied into web/.
      "@design": designDir,
    },
  },
  server: {
    port: 5173,
    fs: { allow: [import.meta.dirname, designDir] },
    proxy: {
      "/api": {
        target: process.env.API_PROXY_TARGET ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    // shots/ is Playwright's, run by npm run shots.
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
