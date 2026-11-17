import wordmarkOnDark from "@design/assets/logo-wordmark-on-dark.svg";
import wordmarkOnLight from "@design/assets/logo-wordmark-on-light.svg";
import {
  CircleCheck,
  CircleX,
  Flame,
  LoaderCircle,
  TrendingUp,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Mel } from "@/components/Mel";
import { Button } from "@/components/ui/button";
import { SegmentedControl } from "@/components/ui/segmented-control";
import { getThemeChoice, setThemeChoice, type ThemeChoice } from "@/lib/theme";
import { cn } from "@/lib/utils";

// Milestone 1's sample page: it proves that the design tokens, the Tailwind
// theme, shadcn/ui and the /api proxy work together in both themes. The
// landing page replaces it in milestone 6, when copy moves to i18n files.

type ApiState = "checking" | "ok" | "down";

function useApiHealth(): ApiState {
  const [state, setState] = useState<ApiState>("checking");

  useEffect(() => {
    let cancelled = false;
    fetch("/api/v1/health")
      .then((response) => response.ok)
      .catch(() => false)
      .then((ok) => {
        if (!cancelled) setState(ok ? "ok" : "down");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}

const apiBadges = {
  checking: {
    label: "API: verificando…",
    Icon: LoaderCircle,
    className: "bg-warning-tint text-warning-text",
  },
  ok: {
    label: "API: no ar",
    Icon: CircleCheck,
    className: "bg-correct-tint text-correct-text",
  },
  down: {
    label: "API: fora do ar",
    Icon: CircleX,
    className: "bg-wrong-tint text-wrong-text",
  },
};

function ApiBadge() {
  const { label, Icon, className } = apiBadges[useApiHealth()];
  return (
    <span
      role="status"
      className={cn(
        "inline-flex items-center gap-1 rounded-sm px-2 py-0.5",
        "font-mono text-[11px] leading-4 font-bold",
        className,
      )}
    >
      <Icon aria-hidden="true" className="size-3" />
      {label}
    </span>
  );
}

const themeOptions: { value: ThemeChoice; label: string }[] = [
  { value: "system", label: "Sistema" },
  { value: "light", label: "Claro" },
  { value: "dark", label: "Escuro" },
];

const statChip =
  "inline-flex h-8 items-center gap-1.5 rounded-tile px-2.5 font-mono text-[14px] font-extrabold tabular-nums [&_svg]:size-[15px]";

function CodeSample() {
  const lines = [
    <>
      <span className="text-syn-keyword">int</span>{" "}
      <span className="text-syn-function">soma</span>(
      <span className="text-syn-keyword">int</span> a,{" "}
      <span className="text-syn-keyword">int</span> b) {"{"}
    </>,
    <>
      {"    "}
      <span className="text-syn-keyword">return</span> a + b;{" "}
      <span className="text-syn-comment">{"// 2 + 3 = 5"}</span>
    </>,
    <>{"}"}</>,
  ];
  return (
    <div className="overflow-hidden rounded-lg border border-code-border bg-code-bg">
      <div className="flex justify-between border-b border-ink-line px-3 py-[7px] font-mono text-[11px] leading-4 text-ink-muted">
        <span>c</span>
        <span>{lines.length} linhas</span>
      </div>
      <pre className="m-0 overflow-x-auto py-3 font-mono text-code text-ink-text [font-variant-ligatures:none]">
        {lines.map((line, index) => (
          <div key={index} className="flex">
            <span className="w-[34px] shrink-0 pr-2.5 text-right text-ink-subtle select-none">
              {index + 1}
            </span>
            <code className="pr-3">{line}</code>
          </div>
        ))}
      </pre>
    </div>
  );
}

export function SamplePage() {
  const [themeChoice, setChoice] = useState<ThemeChoice>(getThemeChoice);

  function chooseTheme(choice: ThemeChoice) {
    setThemeChoice(choice);
    setChoice(choice);
  }

  return (
    <main className="mx-auto flex max-w-[640px] flex-col gap-6 px-gutter py-6 md:px-6">
      <header className="flex items-center justify-between gap-4">
        <img
          src={wordmarkOnDark}
          alt="caramelCase"
          className="hidden h-7 w-auto dark:block"
        />
        <img
          src={wordmarkOnLight}
          alt="caramelCase"
          className="h-7 w-auto dark:hidden"
        />
        <ApiBadge />
      </header>

      <section className="flex items-center gap-4">
        <Mel pose="wave" scale={4} />
        <div className="flex flex-col gap-1">
          <h1 className="text-title">Base pronta</h1>
          <p className="text-body-sm text-fg-muted">
            Página de amostra do marco 1: tokens, tipografia e componentes do
            design, nos dois temas.
          </p>
        </div>
      </section>

      <SegmentedControl
        label="Tema"
        value={themeChoice}
        options={themeOptions}
        onChange={chooseTheme}
      />

      <section className="mr-1.5 flex flex-col gap-3 rounded-card bg-brand p-4 text-brand-fg shadow-step-xl">
        <span className="font-mono text-label-mono lowercase">
          meta de hoje
        </span>
        <h2 className="text-heading">0 de 10 questões</h2>
        <Button variant="onCaramel" className="self-start">
          Começar
        </Button>
      </section>

      <section className="flex flex-wrap items-center gap-3 pr-1.5 pb-1.5">
        <Button>Verificar</Button>
        <Button variant="secondary">Pular</Button>
        <Button variant="danger">Excluir conta</Button>
        <Button variant="ghost">Agora não</Button>
        <Button loading>Verificando…</Button>
        <Button disabled>Indisponível</Button>
      </section>

      <section className="flex flex-wrap items-center gap-2">
        <span className={cn(statChip, "bg-streak text-streak-fg")}>
          <Flame aria-hidden="true" />7
        </span>
        <span className={cn(statChip, "bg-xp text-xp-fg")}>
          <Zap aria-hidden="true" />
          +12 XP
        </span>
        <span className={cn(statChip, "bg-rating text-rating-fg")}>
          <TrendingUp aria-hidden="true" />
          1032
        </span>
        <span className="text-caption text-fg-subtle">
          sequência, XP e rating
        </span>
      </section>

      <CodeSample />
    </main>
  );
}
