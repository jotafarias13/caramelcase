// The list of toasts on screen. Kept outside React so that any code can
// show one: toast({ kind: "success", message: t("...") }).
export type ToastKind = "success" | "error" | "offline" | "info";

export type Toast = {
  id: number;
  kind: ToastKind;
  message: string;
  action?: { label: string; onClick: () => void };
};

const STAY_MS = 4000;

let toasts: Toast[] = [];
let nextId = 1;
const listeners = new Set<() => void>();

function emit(next: Toast[]) {
  toasts = next;
  listeners.forEach((listener) => listener());
}

export function subscribeToasts(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function getToasts(): Toast[] {
  return toasts;
}

export function dismissToast(id: number): void {
  emit(toasts.filter((toast) => toast.id !== id));
}

/** Show a toast; it leaves by itself after four seconds. */
export function toast(options: Omit<Toast, "id">): number {
  const id = nextId++;
  emit([...toasts, { ...options, id }]);
  setTimeout(() => dismissToast(id), STAY_MS);
  return id;
}

/** For tests. */
export function clearToasts(): void {
  emit([]);
}
