import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { test, type Browser } from "@playwright/test";
import { world } from "../src/test/fixtures";
import { createMockApi, NetworkFailure } from "../src/test/mock-api";
import type { Scene } from "./scene";
import { scenes } from "./scenes";

const screensDir = path.resolve(import.meta.dirname, "../../design/screens");
const outDir = path.resolve(import.meta.dirname, "out");
const themes = ["dark", "light"] as const;
type Theme = (typeof themes)[number];
type Frame = { width: number; height: number };

/** Every mockup starts with a comment that gives its frame in pixels. */
function frameOf(mockup: string): Frame {
  const html = readFileSync(path.join(screensDir, `${mockup}.html`), "utf8");
  const size = /frame (\d+) × (\d+) px/.exec(html);
  if (!size) throw new Error(`${mockup}: no frame size in the file`);
  return { width: Number(size[1]), height: Number(size[2]) };
}

async function shootMockup(
  browser: Browser,
  scene: Scene,
  theme: Theme,
  frame: Frame,
): Promise<Buffer> {
  const context = await browser.newContext({ viewport: frame });
  const page = await context.newPage();
  const file = path.join(screensDir, `${scene.mockup}.html`);
  await page.goto(pathToFileURL(file).href);
  await page.evaluate((value) => {
    document.documentElement.setAttribute("data-theme", value);
  }, theme);
  await page.evaluate(() => document.fonts.ready.then(() => true));
  const shot = await page.screenshot({ fullPage: true });
  await context.close();
  return shot;
}

async function shootApp(
  browser: Browser,
  scene: Scene,
  theme: Theme,
  frame: Frame,
  baseURL: string,
): Promise<Buffer> {
  const locale = scene.locale ?? "pt-BR";
  const context = await browser.newContext({
    viewport: frame,
    baseURL,
    locale,
    // The fixtures' user lives in this process's timezone.
    timezoneId: Intl.DateTimeFormat().resolvedOptions().timeZone,
    reducedMotion: "reduce",
    // An account set to "system" follows this.
    colorScheme: theme,
  });
  await context.addInitScript(
    (entries) => {
      for (const [key, value] of Object.entries(entries)) {
        localStorage.setItem(key, value);
      }
    },
    {
      "caramelcase.theme": theme,
      "caramelcase.locale": locale,
      ...scene.storage,
    },
  );

  const api = createMockApi(world(scene.routes));
  await context.route("**/api/v1/**", async (route) => {
    const request = route.request();
    try {
      const answer = await api.handle(
        request.method(),
        request.url(),
        request.postDataJSON(),
      );
      await route.fulfill({
        status: answer.status,
        contentType: "application/json",
        body: answer.body === undefined ? "" : JSON.stringify(answer.body),
      });
    } catch (error) {
      if (!(error instanceof NetworkFailure)) throw error;
      await route.abort("internetdisconnected");
    }
  });

  const page = await context.newPage();
  if (scene.now) await page.clock.setFixedTime(new Date(scene.now));
  await page.goto(scene.path);
  // A scene with a request left pending never goes idle: wait a little.
  await page
    .waitForLoadState("networkidle", { timeout: 4000 })
    .catch(() => undefined);
  await scene.prepare?.(page);
  await page.evaluate(() => document.fonts.ready.then(() => true));
  await page.waitForTimeout(300);
  const shot = await page.screenshot({
    fullPage: true,
    animations: "disabled",
  });
  await context.close();
  return shot;
}

type Comparison = {
  /** Share of pixels whose colour differs clearly, from 0 to 1. */
  differing: number;
  mockupSize: string;
  appSize: string;
  side: Buffer;
  diff: Buffer;
};

/** Both shots side by side, and the app with its differing pixels marked. */
async function compare(
  browser: Browser,
  mockup: Buffer,
  app: Buffer,
): Promise<Comparison> {
  const page = await browser.newPage();
  const urls = [mockup, app].map(
    (png) => `data:image/png;base64,${png.toString("base64")}`,
  );
  const result = await page.evaluate(async ([mockupUrl, appUrl]) => {
    function load(src: string): Promise<HTMLImageElement> {
      return new Promise((resolve) => {
        const image = new Image();
        image.onload = () => resolve(image);
        image.src = src;
      });
    }
    const [left, right] = await Promise.all([load(mockupUrl), load(appUrl)]);
    const width = Math.max(left.width, right.width);
    const height = Math.max(left.height, right.height);

    function canvasOf(image: HTMLImageElement) {
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext("2d")!;
      context.drawImage(image, 0, 0);
      return { canvas, context };
    }
    const a = canvasOf(left);
    const b = canvasOf(right);
    const pixelsA = a.context.getImageData(0, 0, width, height).data;
    const marked = b.context.getImageData(0, 0, width, height);
    const pixelsB = marked.data;

    let differing = 0;
    for (let i = 0; i < pixelsA.length; i += 4) {
      const distance =
        Math.abs(pixelsA[i] - pixelsB[i]) +
        Math.abs(pixelsA[i + 1] - pixelsB[i + 1]) +
        Math.abs(pixelsA[i + 2] - pixelsB[i + 2]) +
        Math.abs(pixelsA[i + 3] - pixelsB[i + 3]);
      if (distance > 60) {
        differing += 1;
        pixelsB.set([255, 0, 255, 255], i);
      } else {
        // Dim what matches, so the marks stand out.
        pixelsB[i + 3] = 90;
      }
    }
    b.context.putImageData(marked, 0, 0);

    const side = document.createElement("canvas");
    side.width = width * 2 + 24;
    side.height = height;
    const sideContext = side.getContext("2d")!;
    sideContext.fillStyle = "#808080";
    sideContext.fillRect(0, 0, side.width, side.height);
    sideContext.drawImage(left, 0, 0);
    sideContext.drawImage(right, width + 24, 0);

    return {
      differing: differing / (width * height),
      mockupSize: `${left.width}×${left.height}`,
      appSize: `${right.width}×${right.height}`,
      side: side.toDataURL("image/png"),
      diff: b.canvas.toDataURL("image/png"),
    };
  }, urls);
  await page.close();

  const toBuffer = (dataUrl: string) =>
    Buffer.from(dataUrl.slice(dataUrl.indexOf(",") + 1), "base64");
  return {
    ...result,
    side: toBuffer(result.side),
    diff: toBuffer(result.diff),
  };
}

mkdirSync(outDir, { recursive: true });

for (const scene of scenes) {
  for (const theme of themes) {
    test(`${scene.mockup} ${theme}`, async ({ browser, baseURL }) => {
      const frame = frameOf(scene.mockup);
      const [mockup, app] = await Promise.all([
        shootMockup(browser, scene, theme, frame),
        shootApp(browser, scene, theme, frame, baseURL!),
      ]);
      const result = await compare(browser, mockup, app);

      const base = path.join(outDir, `${scene.mockup}-${theme}`);
      writeFileSync(`${base}.mockup.png`, mockup);
      writeFileSync(`${base}.app.png`, app);
      writeFileSync(`${base}.side.png`, result.side);
      writeFileSync(`${base}.diff.png`, result.diff);
      console.log(
        `${scene.mockup} ${theme}: ${(result.differing * 100).toFixed(1)}% of pixels differ` +
          ` (mockup ${result.mockupSize}, app ${result.appSize})`,
      );
    });
  }
}
