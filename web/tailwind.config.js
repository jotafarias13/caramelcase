// Tailwind reads the design handoff's theme unchanged. src/styles/index.css
// loads this file through @config.
import caramel from "../design/tailwind.theme.js";

export default {
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: { extend: caramel },
};
