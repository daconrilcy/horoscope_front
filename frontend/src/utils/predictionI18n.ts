import {
  CATEGORY_LABELS,
  NOTE_BAND_LABELS,
  TONE_LABELS,
  PIVOT_LABELS,
  type Lang,
  getLabel,
} from "../i18n/predictions";
import { detectLang } from "../i18n/astrology";

export function getPredictionLang(): Lang {
  const lang = detectLang();
  return lang === "en" ? "en" : "fr";
}

const CATEGORY_ICONS: Record<string, string> = {
  love: "❤️",
  work: "💼",
  career: "🚀",
  energy: "⚡",
  mood: "🧠",
  health: "🍎",
  money: "💰",
  finances: "💸",
  sex_intimacy: "🔥",
  family_home: "🏠",
  social_network: "🤝",
  communication: "💬",
  pleasure_creativity: "🎨",
};

const TONE_COLORS: Record<string, string> = {
  positive: "var(--primary)",
  mixed: "var(--text-2)",
  neutral: "var(--text-2)",
  negative: "var(--warning)",
  // Legacy
  steady: "var(--text-2)",
  push: "var(--primary)",
  careful: "var(--warning)",
  open: "var(--success)",
};

const MESSAGES: Record<string, Record<Lang, string>> = {
  loading: { fr: "Chargement de votre ciel du jour...", en: "Loading your daily sky..." },
  error: { fr: "Impossible de charger votre horoscope.", en: "Unable to load your horoscope." },
  retry: { fr: "Réessayer", en: "Retry" },
  empty: { fr: "Aucune prédiction disponible.", en: "No predictions available yet." },
  setup_profile: { fr: "Configurer mon profil", en: "Setup my profile" },
  best_window: { fr: "Meilleur créneau", en: "Best window" },
  dominant: { fr: "Dominante", en: "Dominant" },
  timeline: { fr: "Chronologie du jour", en: "Daily Timeline" },
  turning_points: { fr: "Points de bascule", en: "Turning Points" },
  intensity: { fr: "Intensité", en: "Intensity" },
  pivot_badge: { fr: "Pivot", en: "Pivot" },
  pending_summary: { fr: "Calcul de votre tendance...", en: "Computing your trend..." },
};

export function getCategoryLabel(code: string, lang: Lang): string {
  return getLabel(CATEGORY_LABELS, code, lang);
}

export function getNoteBand(note: number, lang: Lang) {
  let key = "neutral";
  let colorVar = "var(--text-2)";

  if (note <= 5) {
    key = "fragile";
    colorVar = "var(--danger)";
  } else if (note <= 9) {
    key = "tendu"; // Use localized keys
    if (lang === "en") key = "tense";
    // Actually our dictionary uses 'fragile', 'tendu', etc. as keys
    // Let's stick to dictionary keys
    key = note <= 5 ? "fragile" : note <= 9 ? "tendu" : note <= 12 ? "neutre" : note <= 16 ? "porteur" : "très favorable";
    
    // Remap key to canonical for color? No, we use thresholds
  }

  const bandKey = note <= 5 ? "fragile" : note <= 9 ? "tendu" : note <= 12 ? "neutre" : note <= 16 ? "porteur" : "très favorable";
  
  const colors: Record<string, string> = {
    fragile: "var(--danger)",
    tendu: "var(--warning)",
    neutre: "var(--text-2)",
    porteur: "var(--success)",
    "très favorable": "var(--primary)",
  };

  // Canonical keys for tests if needed
  const canonicalMap: Record<string, string> = {
    fragile: "fragile",
    tendu: "tense",
    neutre: "neutral",
    porteur: "favorable",
    "très favorable": "very_favorable"
  };

  return {
    key: canonicalMap[bandKey],
    label: getLabel(NOTE_BAND_LABELS, bandKey, lang),
    colorVar: colors[bandKey],
  };
}

export function getCategoryMeta(code: string, lang: Lang) {
  const normalized = code.toLowerCase().trim();
  // Handle legacy FR codes
  const legacyMap: Record<string, string> = {
    amour: "love",
    travail: "work",
    sante: "health",
    argent: "money",
    vitalite: "energy",
  };
  const canonical = legacyMap[normalized] || normalized;

  return {
    label: getCategoryLabel(canonical, lang),
    icon: CATEGORY_ICONS[canonical] || "✨",
  };
}

export function getToneLabel(tone: string | null | undefined, lang: Lang): string {
  if (!tone) return getLabel(TONE_LABELS, "neutral", lang);
  return getLabel(TONE_LABELS, tone, lang);
}

export function getToneColor(tone: string | null | undefined): string {
  if (!tone) return TONE_COLORS.neutral;
  return TONE_COLORS[tone] || "var(--text-2)";
}

export function getPivotSeverityLabel(severity: number, lang: Lang): string {
  let key = "low";
  if (severity > 0.75) key = "critical";
  else if (severity > 0.5) key = "high";
  else if (severity > 0.25) key = "medium";
  return getLabel(PIVOT_LABELS, key, lang);
}

export function getPredictionMessage(key: string, lang: Lang): string {
  const entry = MESSAGES[key];
  if (!entry) return key;
  return entry[lang] || key;
}
