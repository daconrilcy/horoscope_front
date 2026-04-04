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
  "work": { fr: "Travail", en: "Work", icon: "Briefcase" },
  "career": { fr: "Carrière", en: "Career", icon: "Briefcase" },
  "love": { fr: "Amour & Relations", en: "Love & Relationships", icon: "Heart" },
  "health": { fr: "Santé & Hygiène de vie", en: "Health & Routine", icon: "Sparkles" },
  "energy": { fr: "Énergie & Vitalité", en: "Energy & Vitality", icon: "Zap" },
  "mood": { fr: "Humeur & Climat intérieur", en: "Mood & Inner Climate", icon: "Sparkles" },
  "money": { fr: "Argent & Ressources", en: "Money & Resources", icon: "DollarSign" },
  "social_network": { fr: "Vie sociale & Réseau", en: "Social Network", icon: "Users" },
  "communication": { fr: "Communication", en: "Communication", icon: "Users" },
  "pleasure_creativity": { fr: "Plaisir & Créativité", en: "Pleasure & Creativity", icon: "Sparkles" },
};

export type TeaserKey = 'domainRanking' | 'dayTimeline' | 'turningPoint' | 'bestWindow' | 'astroFoundation' | 'dailyAdvice'

export const HOROSCOPE_TEASERS: Record<TeaserKey, { fr: string; en: string; es: string }> = {
  domainRanking: {
    fr: "Découvrez vos domaines d'énergie prioritaires ce jour et comment les naviguer...",
    en: "Discover your priority energy domains for today and how to navigate them...",
    es: "Descubre tus dominios de energía prioritarios hoy y cómo navegarlos...",
  },
  dayTimeline: {
    fr: "Vos meilleures fenêtres temporelles pour agir, vous reposer et décider...",
    en: "Your best time windows to act, rest and decide...",
    es: "Tus mejores ventanas de tiempo para actuar, descansar y decidir...",
  },
  turningPoint: {
    fr: "Un tournant astrologique particulier est prévu ce jour — découvrez lequel...",
    en: "A particular astrological turning point is expected today — discover it...",
    es: "Un punto de inflexión astrológico particular está previsto hoy — descúbrelo...",
  },
  bestWindow: {
    fr: "La fenêtre idéale de votre journée, révélée par votre thème personnel...",
    en: "Your ideal time window, revealed by your personal chart...",
    es: "Tu ventana de tiempo ideal, revelada por tu tema personal...",
  },
  astroFoundation: {
    fr: "Les mouvements planétaires qui influencent votre journée en profondeur...",
    en: "The planetary movements deeply influencing your day...",
    es: "Los movimientos planetarios que influyen profundamente en tu día...",
  },
  dailyAdvice: {
    fr: "Votre conseil personnalisé du jour, aligné à votre thème natal...",
    en: "Your personalized daily advice, aligned with your natal chart...",
    es: "Tu consejo personalizado del día, alineado con tu tema natal...",
  },
}

export function getHoroscopeTeaser(key: TeaserKey, lang: Lang): string {
  const entry = HOROSCOPE_TEASERS[key]
  if (!entry) return ''
  if (lang === 'fr') return entry.fr
  if (lang === 'es') return entry.es
  return entry.en
}

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
