// Interface text belongs in src/i18n/pt-BR.json and en.json. This rule
// fails on text written straight into a component: JSX text, a string as a
// JSX child, and a string in an attribute that people read or hear.

const READ_ATTRIBUTES = new Set([
  "alt",
  "aria-description",
  "aria-label",
  "aria-placeholder",
  "aria-roledescription",
  "aria-valuetext",
  "helper",
  "label",
  "placeholder",
  "title",
]);

/** Text with a letter in it; "·", "/" and numbers alone are layout. */
function isCopy(text) {
  return /\p{L}/u.test(text);
}

/** The literal text of an expression, or null when it is not a literal. */
function literalText(node) {
  if (node.type === "Literal" && typeof node.value === "string") {
    return node.value;
  }
  if (node.type === "TemplateLiteral") {
    return node.quasis.map((quasi) => quasi.value.cooked ?? "").join("");
  }
  return null;
}

export default {
  meta: {
    type: "problem",
    docs: { description: "Interface text must come from the i18n files" },
    schema: [],
    messages: {
      text: 'Text "{{text}}" is written into the component. Put it in src/i18n/pt-BR.json and en.json and use t().',
    },
  },
  create(context) {
    function check(node, text) {
      if (text !== null && isCopy(text)) {
        const short = text.trim().replace(/\s+/g, " ").slice(0, 40);
        context.report({ node, messageId: "text", data: { text: short } });
      }
    }

    return {
      JSXText(node) {
        check(node, node.value);
      },
      JSXExpressionContainer(node) {
        const parent = node.parent;
        const isChild =
          parent.type === "JSXElement" || parent.type === "JSXFragment";
        if (isChild) check(node, literalText(node.expression));
      },
      JSXAttribute(node) {
        const name = node.name.name;
        if (typeof name !== "string" || !READ_ATTRIBUTES.has(name)) return;
        if (!node.value) return;
        if (node.value.type === "Literal") {
          check(node, String(node.value.value));
        } else if (node.value.type === "JSXExpressionContainer") {
          check(node, literalText(node.value.expression));
        }
      },
    };
  },
};
