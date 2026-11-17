// Prints a design mockup one element per line, without the coordinates of
// SVG shapes: icons are named by data-lucide and Mel by aria-label and
// viewBox, so the path data is never built from. Everything else is kept.
//
//   node shots/print-mockup.mjs v1-home-mobile [more names...]
import { readFileSync } from "node:fs";
import path from "node:path";

const screens = path.resolve(import.meta.dirname, "../../design/screens");

for (const name of process.argv.slice(2)) {
  const file = path.join(screens, name.replace(/\.html$/, "") + ".html");
  const html = readFileSync(file, "utf8")
    // An svg keeps its own tag (name, size, colour) and loses its children.
    .replace(/(<svg\b[^>]*>)[\s\S]*?(<\/svg>)/g, "$1$2")
    .replace(/></g, ">\n<");
  console.log(`===== ${name}\n${html}`);
}
