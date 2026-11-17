// Makes t() check its keys against pt-BR.json at compile time.
import "i18next";
import type ptBR from "./pt-BR.json";

declare module "i18next" {
  interface CustomTypeOptions {
    defaultNS: "translation";
    resources: { translation: typeof ptBR };
  }
}
