import type { Lang } from './predictions';

export const LEVEL_LABELS: Record<string, { fr: string; en: string; color_hint: string }> = {
  "très_favorable": { fr: "Très favorable", en: "Very Favorable", color_hint: "success" },
  "favorable": { fr: "Favorable", en: "Favorable", color_hint: "success-light" },
  "stable": { fr: "Stable", en: "Stable", color_hint: "neutral" },
  "mitigé": { fr: "Mitigé", en: "Mixed", color_hint: "warning" },
  "exigeant": { fr: "Exigeant", en: "Challenging", color_hint: "danger" },
};

export const REGIME_LABELS: Record<string, { fr: string; en: string }> = {
  "progression": { fr: "Progression", en: "Momentum" },
  "fluidité": { fr: "Fluidité", en: "Flow" },
  "prudence": { fr: "Prudence", en: "Caution" },
  "pivot": { fr: "Pivot", en: "Turning Point" },
  "récupération": { fr: "Récupération", en: "Rest" },
  "retombée": { fr: "Retombée", en: "Wind Down" },
  "mise_en_route": { fr: "Mise en route", en: "Warm Up" },
  "recentrage": { fr: "Recentrage", en: "Refocus" },
};

export const CHANGE_TYPE_LABELS: Record<string, { fr: string; en: string }> = {
  "emergence": { fr: "Montée", en: "Rising" },
  "recomposition": { fr: "Virage", en: "Shift" },
  "attenuation": { fr: "Retombée", en: "Easing" },
};

export const DOMAIN_LABELS: Record<string, { fr: string; en: string; icon: string }> = {
  "pro_ambition": { fr: "Pro & Ambition", en: "Work & Ambition", icon: "Briefcase" },
  "relations_echanges": { fr: "Relations & échanges", en: "Relationships", icon: "Users" },
  "energie_bienetre": { fr: "Énergie & bien-être", en: "Energy & Wellbeing", icon: "Zap" },
  "argent_ressources": { fr: "Argent & ressources", en: "Money & Resources", icon: "DollarSign" },
  "vie_personnelle": { fr: "Vie personnelle", en: "Personal Life", icon: "Heart" },
};

export function getDomainLabel(key: string, lang: Lang): string {
  const entry = DOMAIN_LABELS[key];
  if (!entry) return key;
  return lang === 'fr' ? entry.fr : entry.en;
}

export function getLevelLabel(level: string, lang: Lang): string {
  const entry = LEVEL_LABELS[level];
  if (!entry) return level;
  return lang === 'fr' ? entry.fr : entry.en;
}

export function getRegimeLabel(regime: string, lang: Lang): string {
  const entry = REGIME_LABELS[regime];
  if (!entry) return regime;
  return lang === 'fr' ? entry.fr : entry.en;
}

export function getChangeTypeLabel(type: string, lang: Lang): string {
  const entry = CHANGE_TYPE_LABELS[type];
  if (!entry) return type;
  return lang === 'fr' ? entry.fr : entry.en;
}
