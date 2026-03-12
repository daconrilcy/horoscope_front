import {
  CATEGORY_LABELS,
  NOTE_BAND_LABELS,
  TONE_LABELS,
  PIVOT_LABELS,
  TURNING_POINT_LABELS,
  DRIVER_TYPE_LABELS,
  MOVEMENT_DIRECTION_LABELS,
  INTENSITY_LEVEL_LABELS,
  CATEGORY_VARIATION_LABELS,
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
  turning_points: { fr: "Moments clés du jour", en: "Key moments today" },
  impacts_label: { fr: "Impacts :", en: "Impacts:" },
  no_major_aspect: { fr: "Pas d'aspect majeur", en: "No major aspect" },
  aspect_shift_label: { fr: "Bascule", en: "Shift" },
  intensity: { fr: "Intensité", en: "Intensity" },
  pivot_badge: { fr: "Changement", en: "Shift" },
  refresh: { fr: "Actualiser", en: "Refresh" },
  pending_summary: { fr: "Calcul de votre tendance...", en: "Computing your trend..." },
  provisional_calibration: {
    fr: "Lecture provisoire : ces scores restent indicatifs tant que l'historique de calibration n'est pas complet.",
    en: "Provisional reading: these scores remain indicative until calibration history is complete.",
  },
  // Agenda du jour (ex-fenêtres décisionnelles)
  decision_windows_title: { fr: "Agenda du jour", en: "Daily Agenda" },
  window_type_favorable: { fr: "Fenêtre favorable", en: "Favorable window" },
  window_type_prudence: { fr: "Prudence", en: "Caution" },
  window_type_pivot: { fr: "Transition à surveiller", en: "Watch for a shift" },
  window_msg_favorable: {
    fr: "Bon créneau pour lancer une action ou prendre une décision.",
    en: "Good window to take action or make a decision.",
  },
  window_msg_prudence: {
    fr: "Gardez une marge de manœuvre, évitez les engagements irréversibles.",
    en: "Keep some flexibility, avoid irreversible commitments.",
  },
  window_msg_pivot: {
    fr: "Le rythme change sur ce créneau : observez avant d'agir.",
    en: "The tempo is shifting here: observe before acting.",
  },
};

const ASPECT_LABELS: Record<string, Record<Lang, string>> = {
  conjunction: { fr: "conjonction", en: "conjunction" },
  opposition: { fr: "opposition", en: "opposition" },
  square: { fr: "carré", en: "square" },
  trine: { fr: "trigone", en: "trine" },
  sextile: { fr: "sextile", en: "sextile" },
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
      fr: "Des aspects majeurs demandent votre attention.",
      en: "Major aspects deserve your attention.",
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
    // Legacy codes
    exact: { fr: "Aspect exact", en: "Exact aspect" },
    ingress: { fr: "Changement de signe", en: "Sign ingress" },
    station: { fr: "Station planétaire", en: "Planetary station" },
    // Taxonomy V2 codes (event_detector.py)
    aspect_exact_to_angle: { fr: "Aspect exact (Asc/MC)", en: "Exact aspect (Asc/MC)" },
    aspect_exact_to_luminary: { fr: "Aspect exact (Soleil/Lune)", en: "Exact aspect (Sun/Moon)" },
    aspect_exact_to_personal: { fr: "Aspect exact", en: "Exact aspect" },
    aspect_enter_orb: { fr: "Entrée en orbe d'aspect", en: "Aspect orb opening" },
    aspect_exit_orb: { fr: "Sortie d'orbe d'aspect", en: "Aspect orb closing" },
    enter_orb: { fr: "Entrée en orbe", en: "Orb opening" },
    exit_orb: { fr: "Sortie d'orbe", en: "Orb closing" },
    moon_sign_ingress: { fr: "Changement de signe de la Lune", en: "Moon sign change" },
    asc_sign_change: { fr: "Changement de signe à l'Ascendant", en: "Ascendant sign change" },
  };

  if (eventLabels[eventType]) {
    return eventLabels[eventType][lang];
  }

  return lang === "fr" ? "Signal astrologique" : "Astrological signal";
}

function formatSignedValue(value: number, lang: Lang, digits = 2): string {
  const formatted = value.toLocaleString(lang === "fr" ? "fr-FR" : "en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return value > 0 ? `+${formatted}` : formatted;
}

function formatUnsignedValue(value: number, lang: Lang, digits = 2): string {
  return value.toLocaleString(lang === "fr" ? "fr-FR" : "en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function humanizePrimaryDriver(
  driver:
    | {
        event_type: string;
        body?: string;
        target?: string;
        aspect?: string;
        orb_deg?: number | null;
        phase?: string | null;
        metadata?: Record<string, unknown>;
      }
    | null
    | undefined,
  lang: Lang,
): { headline: string; details: string | null } | null {
  if (!driver) return null;

  const body = driver.body?.trim();
  const target = driver.target?.trim();
  const aspect = driver.aspect?.trim().toLowerCase();
  const localizedAspect = aspect ? getLabel(ASPECT_LABELS, aspect, lang) : null;

  const headline =
    body && target && localizedAspect
      ? `${body} ${localizedAspect} ${target}`
      : getLabel(DRIVER_TYPE_LABELS, driver.event_type, lang);

  const details: string[] = [];
  if (typeof driver.orb_deg === "number") {
    details.push(
      `${getLabel(TURNING_POINT_LABELS, "orb", lang)} ${formatUnsignedValue(driver.orb_deg, lang)}°`,
    );
  }

  if (driver.phase) {
    details.push(
      `${getLabel(TURNING_POINT_LABELS, "phase", lang)} ${getLabel(TURNING_POINT_LABELS, driver.phase, lang)}`,
    );
  }

  const fromHouse = driver.metadata?.natal_house_transited;
  const toHouse = driver.metadata?.natal_house_target;
  if (typeof fromHouse === "number" || typeof toHouse === "number") {
    details.push(
      `${getLabel(TURNING_POINT_LABELS, "houses", lang)} ${fromHouse ?? "?"} -> ${toHouse ?? "?"}`,
    );
  }

  return {
    headline,
    details: details.length > 0 ? details.join(" · ") : null,
  };
}

export function humanizeTurningPointSemantic(
  tp: {
    change_type?: string;
    impacted_categories?: string[];
    previous_categories?: string[];
    next_categories?: string[];
    primary_driver?: any;
  },
  lang: Lang
) {
  const labels = TURNING_POINT_LABELS;
  const changeLabel = getLabel(labels, tp.change_type || "recomposition", lang);

  const prev = tp.previous_categories?.slice(0, 3) || [];
  const next = tp.next_categories?.slice(0, 3) || [];
  const retained = prev.filter((category) => next.includes(category));
  const entered = next.filter((category) => !prev.includes(category));
  const removed = prev.filter((category) => !next.includes(category));

  const formatCats = (cats: string[]) => {
    if (cats.length === 0) return getLabel(labels, "none", lang);
    return cats
      .map((code) => getCategoryLabel(code, lang).toLowerCase())
      .join(` ${getLabel(labels, "and", lang)} `);
  };

  const previousLabel = formatCats(prev);
  const nextLabel = formatCats(next);
  const retainedLabel = formatCats(retained);
  const enteredLabel = formatCats(entered);
  const removedLabel = formatCats(removed);

  const driverLabel = tp.primary_driver
    ? humanizePrimaryDriver(tp.primary_driver, lang)?.headline ||
      getLabel(DRIVER_TYPE_LABELS, tp.primary_driver.event_type, lang)
    : next.length === 0 && prev.length > 0
      ? getLabel(labels, "cause_returns_to_calm", lang)
      : entered.length > 0 && removed.length === 0
        ? getLabel(labels, "cause_new_priority", lang)
        : removed.length > 0 && entered.length === 0
          ? getLabel(labels, "cause_priority_fades", lang)
          : entered.length > 0 && removed.length > 0
            ? getLabel(labels, "cause_priorities_rebalance", lang)
            : getLabel(labels, "no_driver", lang);

  const transitionLabel = (() => {
    if (next.length === 0 && prev.length > 0) {
      return lang === "fr"
        ? `${previousLabel} laisse place à un climat plus calme.`
        : `${previousLabel} gives way to a calmer atmosphere.`;
    }

    if (entered.length > 0 && removed.length === 0 && retained.length > 0) {
      return lang === "fr"
        ? `${enteredLabel} rejoint ${retainedLabel} au premier plan.`
        : `${enteredLabel} joins ${retainedLabel} in the foreground.`;
    }

    if (removed.length > 0 && entered.length === 0 && retained.length > 0) {
      return lang === "fr"
        ? `${removedLabel} quitte le premier plan et le climat se recentre sur ${retainedLabel}.`
        : `${removedLabel} leaves the foreground and the focus narrows to ${retainedLabel}.`;
    }

    if (entered.length > 0 && removed.length > 0 && retained.length > 0) {
      return lang === "fr"
        ? `${enteredLabel} prend le relais de ${removedLabel}, avec ${retainedLabel} comme fil conducteur.`
        : `${enteredLabel} takes over from ${removedLabel}, with ${retainedLabel} as the common thread.`;
    }

    if (entered.length > 0 && removed.length > 0) {
      return lang === "fr"
        ? `${removedLabel} cède la place à ${enteredLabel}.`
        : `${removedLabel} gives way to ${enteredLabel}.`;
    }

    return `${getLabel(labels, "from", lang)} ${previousLabel} ${getLabel(labels, "to", lang)} ${nextLabel}`;
  })();

  const implication = (() => {
    if (next.length === 0 && prev.length > 0) {
      return lang === "fr"
        ? `Le relief retombe et le climat cesse de se structurer autour de ${previousLabel}.`
        : `The momentum fades and the atmosphere stops organizing itself around ${previousLabel}.`;
    }

    if (entered.length > 0 && removed.length === 0 && retained.length > 0) {
      return lang === "fr"
        ? `Le climat s'ouvre davantage à ${enteredLabel}, aux côtés de ${retainedLabel}.`
        : `The atmosphere opens up more to ${enteredLabel}, alongside ${retainedLabel}.`;
    }

    if (removed.length > 0 && entered.length === 0 && retained.length > 0) {
      return lang === "fr"
        ? `Le focus se resserre sur ${retainedLabel}, tandis que ${removedLabel} recule.`
        : `The focus narrows to ${retainedLabel}, while ${removedLabel} recedes.`;
    }

    if (entered.length > 0 && removed.length > 0 && retained.length > 0) {
      return lang === "fr"
        ? `Le focus glisse de ${removedLabel} vers ${enteredLabel}, avec ${retainedLabel} en fil conducteur.`
        : `The focus shifts from ${removedLabel} to ${enteredLabel}, with ${retainedLabel} as the common thread.`;
    }

    return getLabel(labels, `implication_${tp.change_type || "recomposition"}`, lang);
  })();

  return {
    title: changeLabel,
    cause: driverLabel,
    transition: transitionLabel,
    implication,
  };
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

export function humanizeMovement(
  movement: { direction: string; strength: number; delta_composite: number } | null | undefined,
  lang: Lang,
) {
  if (!movement) return null;

  const direction = getLabel(MOVEMENT_DIRECTION_LABELS, movement.direction, lang);
  
  // Strength Mapping (AC2)
  let intensity = getLabel(INTENSITY_LEVEL_LABELS, "slight", lang);
  if (movement.strength > 7) intensity = getLabel(INTENSITY_LEVEL_LABELS, "marked", lang);
  else if (movement.strength > 3) intensity = getLabel(INTENSITY_LEVEL_LABELS, "notable", lang);

  const isRising = movement.direction === "rising";
  const isFalling = movement.direction === "falling";

  if (lang === "fr") {
    if (isRising || isFalling) {
      return `Mouvement global ${direction} (${intensity}).`;
    }
    return `Mouvement global ${direction}.`;
  } else {
    if (isRising || isFalling) {
      return `Global movement is ${direction} (${intensity}).`;
    }
    return `Global movement is ${direction}.`;
  }
}

export function quantifyMovement(
  movement:
    | {
        previous_composite?: number;
        next_composite?: number;
        delta_composite: number;
      }
    | null
    | undefined,
  lang: Lang,
): string | null {
  if (!movement) return null;
  if (
    typeof movement.previous_composite === "number" &&
    typeof movement.next_composite === "number"
  ) {
    return `${getLabel(TURNING_POINT_LABELS, "composite_delta", lang)} ${formatSignedValue(movement.delta_composite, lang)} (${formatUnsignedValue(movement.previous_composite, lang)} -> ${formatUnsignedValue(movement.next_composite, lang)})`;
  }

  return `${getLabel(TURNING_POINT_LABELS, "composite_delta", lang)} ${formatSignedValue(movement.delta_composite, lang)}`;
}

export function humanizeCategoryDelta(
  delta: { code: string; direction: string; delta_intensity: number },
  lang: Lang,
) {
  const cat = getCategoryMeta(delta.code, lang);
  const dir = getLabel(CATEGORY_VARIATION_LABELS, delta.direction, lang);
  
  if (lang === "fr") {
    return `${cat.icon} ${dir} sur ${cat.label.toLowerCase()}`;
  }
  return `${cat.icon} ${cat.label} ${dir}`;
}

export function quantifyCategoryDelta(
  delta: { delta_score?: number; delta_intensity: number; delta_rank?: number | null },
  lang: Lang,
): string {
  const deltaScore = delta.delta_score;
  const hasMeaningfulScore = typeof deltaScore === "number" && Math.abs(deltaScore) >= 0.05;
  const scorePart =
    hasMeaningfulScore
      ? `${getLabel(TURNING_POINT_LABELS, "score_delta", lang)} ${formatSignedValue(deltaScore, lang)} · `
      : "";
  const rankPart =
    typeof delta.delta_rank === "number" && delta.delta_rank !== 0
      ? `${getLabel(TURNING_POINT_LABELS, "rank_delta", lang)} ${formatSignedValue(delta.delta_rank, lang, 0)} · `
      : "";

  if (lang === "fr") {
    return `${scorePart}${rankPart}${getLabel(TURNING_POINT_LABELS, "intensity_delta", lang)} ${formatSignedValue(delta.delta_intensity, lang)}`;
  }
  return `${scorePart}${rankPart}${getLabel(TURNING_POINT_LABELS, "intensity_delta", lang)} ${formatSignedValue(delta.delta_intensity, lang)}`;
}
