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

interface LockedTeaserCopy {
  teaser: { fr: string; en: string; es: string }
  lead: { fr: string; en: string; es: string }
  body: { fr: string; en: string; es: string }
}

export const HOROSCOPE_LOCKED_COPY: Record<TeaserKey, LockedTeaserCopy> = {
  domainRanking: {
    teaser: {
      fr: "Découvrez vos domaines d'énergie prioritaires ce jour et comment les naviguer...",
      en: "Discover your priority energy domains for today and how to navigate them...",
      es: "Descubre tus dominios de energía prioritarios hoy y cómo navegarlos...",
    },
    lead: {
      fr: "Dans Basic, ce bloc hiérarchise les zones de vie qui prennent le plus de poids dans votre journée, avec une lecture plus claire de ce qui mérite d'être soutenu, ralenti ou protégé dès les premières heures.",
      en: "In Basic, this block ranks the life areas carrying the most weight in your day and clarifies what deserves support, restraint, or protection first.",
      es: "En Basic, este bloque jerarquiza las áreas de vida que más peso tienen en tu día y aclara qué conviene apoyar, frenar o proteger primero.",
    },
    body: {
      fr: "Le texte complet détaille les écarts entre vos secteurs porteurs et vos zones plus sensibles, afin de vous aider à arbitrer vos priorités avec plus de finesse. Vous y retrouvez une synthèse plus ample, plus incarnée et plus utile pour savoir où investir votre énergie sans vous disperser.",
      en: "The full text details the gap between your strongest sectors and your more sensitive areas so you can set priorities with more nuance and clarity.",
      es: "El texto completo detalla la diferencia entre tus sectores más fuertes y tus zonas más sensibles para ayudarte a priorizar con más matices y claridad.",
    },
  },
  dayTimeline: {
    teaser: {
      fr: "Vos meilleures fenêtres temporelles pour agir, vous reposer et décider...",
      en: "Your best time windows to act, rest and decide...",
      es: "Tus mejores ventanas de tiempo para actuar, descansar y decidir...",
    },
    lead: {
      fr: "Avec Basic, cette section déroule la journée comme une séquence lisible, en distinguant les moments de lancement, de consolidation, de vigilance et d'apaisement selon votre climat astrologique personnel.",
      en: "With Basic, this section maps the day as a readable sequence, separating moments to launch, consolidate, stay cautious, or slow down.",
      es: "Con Basic, esta sección desarrolla el día como una secuencia legible y distingue los momentos para iniciar, consolidar, vigilar o bajar el ritmo.",
    },
    body: {
      fr: "La version complète donne davantage de matière sur le bon tempo à adopter selon les heures, avec des conseils plus concrets pour décider, temporiser ou préserver votre énergie. Elle transforme la simple chronologie en véritable ligne de conduite pour la journée.",
      en: "The full version gives more concrete guidance about pacing your decisions and preserving your energy throughout the day.",
      es: "La versión completa aporta una guía más concreta sobre el ritmo adecuado para decidir y preservar tu energía a lo largo del día.",
    },
  },
  turningPoint: {
    teaser: {
      fr: "Un tournant astrologique particulier est prévu ce jour — découvrez lequel...",
      en: "A particular astrological turning point is expected today — discover it...",
      es: "Un punto de inflexión astrológico particular está previsto hoy — descúbrelo...",
    },
    lead: {
      fr: "Dans Basic, le moment clé ne se limite pas à un signal bref : il explique la bascule du jour, ce qu'elle déplace dans votre ressenti et dans quelles conditions elle devient une opportunité plutôt qu'une friction.",
      en: "In Basic, the key moment goes beyond a short signal and explains the day's pivot, what it shifts, and when it becomes an opportunity rather than friction.",
      es: "En Basic, el momento clave va más allá de una señal breve y explica el giro del día, lo que mueve y cuándo puede convertirse en oportunidad en lugar de fricción.",
    },
    body: {
      fr: "Vous obtenez une lecture plus développée du point d'inflexion, avec davantage de contexte sur son intensité, sa durée probable et la meilleure manière de l'aborder sans réagir trop vite. Cela vous permet d'anticiper au lieu de subir.",
      en: "You get a fuller reading of the turning point, including its likely intensity, duration, and the best way to approach it.",
      es: "Obtienes una lectura más amplia del punto de inflexión, incluida su intensidad probable, su duración y la mejor manera de afrontarlo.",
    },
  },
  bestWindow: {
    teaser: {
      fr: "La fenêtre idéale de votre journée, révélée par votre thème personnel...",
      en: "Your ideal time window, revealed by your personal chart...",
      es: "Tu ventana de tiempo ideal, revelada por tu tema personal...",
    },
    lead: {
      fr: "Avec l'abonnement Basic, l'opportunité du jour est interprétée comme un créneau réellement exploitable, avec plus de détails sur ce que vous pouvez y initier, sécuriser ou faire avancer avec fluidité.",
      en: "With the Basic subscription, the day's opportunity is interpreted as a truly actionable window with more detail on what to initiate or secure.",
      es: "Con la suscripción Basic, la oportunidad del día se interpreta como una ventana realmente accionable, con más detalle sobre lo que puedes iniciar o consolidar.",
    },
    body: {
      fr: "Le texte complet précise pourquoi cette fenêtre est favorable, quel type d'action elle soutient le mieux et comment en tirer parti sans en attendre trop. Vous disposez ainsi d'un conseil plus concret pour transformer une simple indication en mouvement utile.",
      en: "The full text explains why this window is favorable, what type of action it supports, and how to use it without overreaching.",
      es: "El texto completo explica por qué esta ventana es favorable, qué tipo de acción sostiene mejor y cómo aprovecharla sin excederte.",
    },
  },
  astroFoundation: {
    teaser: {
      fr: "Les mouvements planétaires qui influencent votre journée en profondeur...",
      en: "The planetary movements deeply influencing your day...",
      es: "Los movimientos planetarios que influyen profundamente en tu día...",
    },
    lead: {
      fr: "Dans Basic, les fondements astrologiques traduisent les configurations planétaires du jour en lecture compréhensible, avec plus de contexte sur les tensions, appuis et résonances qui structurent votre climat intérieur.",
      en: "In Basic, the astrological foundations translate daily planetary patterns into a clearer reading of tensions, supports, and resonances.",
      es: "En Basic, los fundamentos astrológicos traducen las configuraciones planetarias del día en una lectura más clara de tensiones, apoyos y resonancias.",
    },
    body: {
      fr: "La version complète relie davantage les aspects du jour à votre expérience concrète, pour expliquer pourquoi certaines dynamiques se font sentir plus nettement dans vos choix, vos réactions ou votre niveau de disponibilité. Elle apporte une profondeur d'analyse absente de la version découverte.",
      en: "The full version connects the day's aspects to your concrete experience and adds more depth than the discovery tier.",
      es: "La versión completa conecta los aspectos del día con tu experiencia concreta y aporta una profundidad ausente en la versión de descubrimiento.",
    },
  },
  dailyAdvice: {
    teaser: {
      fr: "Votre conseil personnalisé du jour, aligné à votre thème natal...",
      en: "Your personalized daily advice, aligned with your natal chart...",
      es: "Tu consejo personalizado del día, alineado con tu tema natal...",
    },
    lead: {
      fr: "Avec Basic, le conseil du jour prend la forme d'une recommandation plus développée, articulée autour de votre humeur dominante, de vos marges de manœuvre réelles et de l'attitude la plus juste pour traverser la journée.",
      en: "With Basic, the daily advice becomes a fuller recommendation shaped by your dominant mood and your real room to maneuver.",
      es: "Con Basic, el consejo del día se convierte en una recomendación más desarrollada, basada en tu clima dominante y tu margen real de acción.",
    },
    body: {
      fr: "Le texte complet ne se contente pas d'une formule courte : il propose une ligne directrice plus riche, plus nuancée et plus actionnable, afin de vous aider à poser un geste simple mais pertinent au bon moment. C'est cette profondeur qui transforme l'horoscope en guide quotidien.",
      en: "The full text goes beyond a short formula and offers a richer, more actionable guideline for the right moment.",
      es: "El texto completo va más allá de una fórmula breve y ofrece una guía más rica y accionable para el momento adecuado.",
    },
  },
}

export function getHoroscopeTeaser(key: TeaserKey, lang: Lang): string {
  const entry = HOROSCOPE_LOCKED_COPY[key]?.teaser
  if (!entry) return ''
  if (lang === 'fr') return entry.fr
  return entry.en
}

export function getHoroscopeLockedLead(key: TeaserKey, lang: Lang): string {
  const entry = HOROSCOPE_LOCKED_COPY[key]?.lead
  if (!entry) return ''
  if (lang === 'fr') return entry.fr
  return entry.en
}

export function getHoroscopeLockedBody(key: TeaserKey, lang: Lang): string {
  const entry = HOROSCOPE_LOCKED_COPY[key]?.body
  if (!entry) return ''
  if (lang === 'fr') return entry.fr
  return entry.en
}

export function getHoroscopeUpgradeHeroMessage(lang: Lang): string {
  if (lang === 'fr') return "Passez à Basic pour obtenir un horoscope du jour plus riche et plus détaillé."
  return "Upgrade to Basic for a richer and more detailed daily horoscope."
}

export function getHoroscopeUpgradeCtaLabel(lang: Lang): string {
  if (lang === 'fr') return "Obtenez un horoscope du jour plus riche"
  return "Get a richer daily horoscope"
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
