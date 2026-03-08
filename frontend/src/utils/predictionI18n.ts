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
  provisional_calibration: {
    fr: "Calibration provisoire : les notes peuvent rester peu contrastées tant que le référentiel local n'est pas entièrement calibré.",
    en: "Provisional calibration: scores may stay close together until the local reference is fully calibrated.",
  },
};

export function getCategoryLabel(code: string, lang: Lang): string {
  return getLabel(CATEGORY_LABELS, code, lang);
}

export function getNoteBand(note: number, lang: Lang) {
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
  const categoryLabel = getCategoryLabel(canonical, lang);
  const fallbackLabel =
    categoryLabel === canonical
      ? canonical
          .split("_")
          .filter(Boolean)
          .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
          .join(" ")
      : categoryLabel;

  return {
    label: fallbackLabel,
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

export function humanizeTurningPointSummary(
  summary: string | null | undefined,
  lang: Lang,
): string | null {
  if (!summary) return null;

  const normalized = summary.trim().toLowerCase();
  const labels: Record<string, Record<Lang, string>> = {
    delta_note: {
      fr: "Le climat change nettement sur ce créneau.",
      en: "The mood shifts noticeably during this window.",
    },
    top3_change: {
      fr: "Les priorités du jour changent de dominante.",
      en: "The day's dominant themes are shifting.",
    },
    high_priority_event: {
      fr: "Un événement astrologique marqué mérite votre attention.",
      en: "A strong astrological event deserves your attention.",
    },
  };

  return labels[normalized]?.[lang] ?? summary;
}

export function humanizePredictionDriverLabel(
  driver: { label?: string | null; event_type?: string | null; body?: unknown; target?: unknown; aspect?: unknown },
  lang: Lang,
): string {
  if (driver.label && driver.label.trim()) {
    return driver.label;
  }

  const eventType = typeof driver.event_type === "string" ? driver.event_type : "";
  const body = typeof driver.body === "string" ? driver.body : null;
  const target = typeof driver.target === "string" ? driver.target : null;
  const aspect = typeof driver.aspect === "string" ? driver.aspect : null;

  if (eventType === "exact" && body && aspect && target) {
    return lang === "fr"
      ? `Aspect exact : ${body} ${aspect} ${target}`
      : `Exact aspect: ${body} ${aspect} ${target}`;
  }

  if (eventType === "planetary_hour_change") {
    return lang === "fr" ? "Changement d'heure planétaire" : "Planetary hour change";
  }

  const eventLabels: Record<string, Record<Lang, string>> = {
    exact: { fr: "Aspect exact", en: "Exact aspect" },
    ingress: { fr: "Changement de signe", en: "Sign ingress" },
    station: { fr: "Station planétaire", en: "Planetary station" },
  };

  if (eventLabels[eventType]) {
    return eventLabels[eventType][lang];
  }

  return eventType || (lang === "fr" ? "Signal astrologique" : "Astrological signal");
}

export function buildTimelineFallbackSummary(
  dominantCategories: string[],
  toneCode: string,
  lang: Lang,
): string {
  const labels = dominantCategories.slice(0, 3).map((code) => getCategoryLabel(code, lang));
  const tone = getToneLabel(toneCode, lang).toLowerCase();
  const joined = labels.join(", ");

  if (!joined) {
    return lang === "fr" ? `Climat ${tone}.` : `${tone} atmosphere.`;
  }

  return lang === "fr"
    ? `Climat ${tone}, accent sur ${joined}.`
    : `${tone} atmosphere, with focus on ${joined}.`;
}
