// Exports the PNG icons of the web app from the SVG files of the design
// handoff, at the web sizes design/README.md lists ("Assets"). The PNGs
// are committed; run this again only when the design's icon changes:
//
//   npm run icons
//
// Chromium does the drawing (Playwright is already a dev dependency), so
// there is no image library to install.
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "@playwright/test";

const assets = path.resolve(import.meta.dirname, "../../design/assets");
const out = path.resolve(import.meta.dirname, "../public/icons");

/** Layers are drawn on top of each other, each filling the square. */
const icons = [
  { file: "favicon-16.png", size: 16, layers: ["favicon.svg"] },
  { file: "favicon-32.png", size: 32, layers: ["favicon.svg"] },
  { file: "favicon-48.png", size: 48, layers: ["favicon.svg"] },
  { file: "icon-192.png", size: 192, layers: ["app-icon.svg"] },
  { file: "icon-512.png", size: 512, layers: ["app-icon.svg"] },
  // iOS masks the square itself.
  { file: "apple-touch-icon.png", size: 180, layers: ["app-icon-square.svg"] },
  // "maskable": Android crops it to its own shape, so the drawing keeps to
  // the safe zone of the adaptive layers.
  {
    file: "icon-maskable-512.png",
    size: 512,
    layers: [
      "app-icon-adaptive-background.svg",
      "app-icon-adaptive-foreground.svg",
    ],
  },
];

function dataUrl(name) {
  const svg = readFileSync(path.join(assets, name));
  return `data:image/svg+xml;base64,${svg.toString("base64")}`;
}

const browser = await chromium.launch();
const page = await browser.newPage();
for (const icon of icons) {
  await page.setViewportSize({ width: icon.size, height: icon.size });
  const images = icon.layers
    .map(
      (layer) =>
        `<img src="${dataUrl(layer)}" style="position:absolute;inset:0;width:100%;height:100%">`,
    )
    .join("");
  await page.setContent(`<body style="margin:0">${images}</body>`);
  await page.waitForLoadState("load");
  const png = await page.screenshot({ omitBackground: true });
  writeFileSync(path.join(out, icon.file), png);
  console.log(`${icon.file}  ${icon.size} × ${icon.size}`);
}
await browser.close();
