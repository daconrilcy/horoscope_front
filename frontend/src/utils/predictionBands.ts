export function getNoteBand(note: number): { label: string; colorVar: string } {
  if (note <= 5) return { label: "fragile", colorVar: "var(--danger)" };
  if (note <= 9) return { label: "tendu", colorVar: "var(--warning)" };
  if (note <= 12) return { label: "neutre", colorVar: "var(--text-2)" };
  if (note <= 16) return { label: "porteur", colorVar: "var(--success)" };
  return { label: "très favorable", colorVar: "var(--primary)" };
}

function humanizeCategoryCode(code: string): string {
  if (!code) {
    return "General";
  }

  return code
    .split(/[_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export const TONE_LABELS: Record<string, string> = {
  steady: "Stable",
  push: "Dynamique",
  careful: "Vigilance",
  open: "Ouverture",
  mixed: "Mitigé",
};

export const TONE_COLORS: Record<string, string> = {
  steady: "var(--text-2)",
  push: "var(--primary)",
  careful: "var(--warning)",
  open: "var(--success)",
  mixed: "var(--text-2)",
};

export const CATEGORY_META: Record<string, { label: string; icon: string }> = {
  love: { label: "Amour", icon: "❤️" },
  work: { label: "Travail", icon: "💼" },
  energy: { label: "Énergie", icon: "⚡" },
  social: { label: "Social", icon: "🤝" },
  mood: { label: "Mental", icon: "🧠" },
};

export function getCategoryMeta(code: string): { label: string; icon: string } {
  return CATEGORY_META[code] ?? { label: humanizeCategoryCode(code), icon: "✨" };
}
