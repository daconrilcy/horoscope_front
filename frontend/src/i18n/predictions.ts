import type { DayPeriodKey } from "../types/dayTimeline";

export type Lang = "fr" | "en";

export const PERIOD_LABELS: Record<DayPeriodKey, Record<Lang, string>> = {
  nuit: { fr: "Nuit", en: "Night" },
  matin: { fr: "Matin", en: "Morning" },
  apres_midi: { fr: "Après-midi", en: "Afternoon" },
  soiree: { fr: "Soirée", en: "Evening" },
};

export const CATEGORY_LABELS: Record<string, Record<Lang, string>> = {
  love: { fr: "Amour & Relations", en: "Love & Relationships" },
  work: { fr: "Travail", en: "Work" },
  career: { fr: "Carrière", en: "Career" },
  energy: { fr: "Énergie & Vitalité", en: "Energy & Vitality" },
  mood: { fr: "Humeur & Climat intérieur", en: "Mood & Inner Climate" },
  health: { fr: "Santé & Hygiène de vie", en: "Health & Routine" },
  money: { fr: "Argent & Ressources", en: "Money & Resources" },
  sex_intimacy: { fr: "Sexe & Intimité", en: "Sex & Intimacy" },
  family_home: { fr: "Famille & Foyer", en: "Family & Home" },
  social_network: { fr: "Vie sociale & Réseau", en: "Social Network" },
  communication: { fr: "Communication", en: "Communication" },
  pleasure_creativity: { fr: "Plaisir & Créativité", en: "Pleasure & Creativity" },
  amour: { fr: "Amour & Relations", en: "Love & Relationships" },
  travail: { fr: "Travail", en: "Work" },
  carriere: { fr: "Carrière", en: "Career" },
  energie: { fr: "Énergie & Vitalité", en: "Energy & Vitality" },
  vitalite: { fr: "Énergie & Vitalité", en: "Energy & Vitality" },
  humeur: { fr: "Humeur & Climat intérieur", en: "Mood & Inner Climate" },
  sante: { fr: "Santé & Hygiène de vie", en: "Health & Routine" },
  argent: { fr: "Argent & Ressources", en: "Money & Resources" },
  finances: { fr: "Argent & Ressources", en: "Money & Resources" },
  sexe_intimite: { fr: "Sexe & Intimité", en: "Sex & Intimacy" },
  famille_foyer: { fr: "Famille & Foyer", en: "Family & Home" },
  social_reseau: { fr: "Vie sociale & Réseau", en: "Social Network" },
};

export const NOTE_BAND_LABELS: Record<string, Record<Lang, string>> = {
  fragile: { fr: "Fragile", en: "Fragile" },
  tense: { fr: "Tendu", en: "Tense" },
  neutral: { fr: "Neutre", en: "Neutral" },
  favorable: { fr: "Porteur", en: "Favorable" },
  very_favorable: { fr: "Très favorable", en: "Very favorable" },
  tendu: { fr: "Tendu", en: "Tense" },
  neutre: { fr: "Neutre", en: "Neutral" },
  porteur: { fr: "Porteur", en: "Favorable" },
  "très favorable": { fr: "Très favorable", en: "Very favorable" },
};

export const TONE_LABELS: Record<string, Record<Lang, string>> = {
  positive: { fr: "Très porteuse", en: "Very positive" },
  mixed: { fr: "Contrastée", en: "Mixed" },
  neutral: { fr: "Équilibrée", en: "Balanced" },
  negative: { fr: "Exigeante", en: "Challenging" },
  steady: { fr: "Stable", en: "Steady" },
  push: { fr: "Dynamique", en: "Push" },
  careful: { fr: "Prudent", en: "Careful" },
  open: { fr: "Ouvert", en: "Open" },
};

export const PIVOT_LABELS: Record<string, Record<Lang, string>> = {
  low: { fr: "Mineur", en: "Minor" },
  medium: { fr: "Notable", en: "Notable" },
  high: { fr: "Majeur", en: "Major" },
  critical: { fr: "Critique", en: "Critical" },
};

export const TURNING_POINT_LABELS: Record<string, Record<Lang, string>> = {
  why: { fr: "Pourquoi ?", en: "Why?" },
  before_after: { fr: "Transition", en: "Transition" },
  implication: { fr: "Implication", en: "Implication" },
  emergence: { fr: "Émergence d'un nouveau climat", en: "Emergence of a new climate" },
  recomposition: { fr: "Recomposition des énergies", en: "Recomposition of energies" },
  attenuation: { fr: "Atténuation de l'intensité", en: "Attenuation of intensity" },
  implication_emergence: {
    fr: "De nouveaux thèmes prennent de la place dans le climat du moment.",
    en: "New themes are gaining importance in the current atmosphere.",
  },
  implication_recomposition: {
    fr: "Le centre de gravité de la journée se déplace vers d'autres priorités.",
    en: "The center of gravity of the day is shifting toward different priorities.",
  },
  implication_attenuation: {
    fr: "L'intensité retombe et le climat redevient plus calme.",
    en: "The intensity recedes and the atmosphere becomes calmer again.",
  },
  no_driver: { fr: "Évolution naturelle du cycle", en: "Natural evolution of the cycle" },
  cause_new_priority: {
    fr: "Une nouvelle priorité entre au premier plan",
    en: "A new priority moves into the foreground",
  },
  cause_priority_fades: {
    fr: "Une priorité se retire du premier plan",
    en: "A priority steps back from the foreground",
  },
  cause_priorities_rebalance: {
    fr: "Les priorités du moment se réorganisent",
    en: "The moment's priorities are rebalancing",
  },
  cause_returns_to_calm: {
    fr: "Le relief du moment s'apaise",
    en: "The moment is settling back down",
  },
  from: { fr: "De", en: "From" },
  to: { fr: "vers", en: "to" },
  and: { fr: "et", en: "and" },
  none: { fr: "calme", en: "calm" },
  global_movement: { fr: "Mouvement global", en: "Global movement" },
  local_variations: { fr: "Variations locales", en: "Local variations" },
  astrology_data: { fr: "Données astrologiques", en: "Astrological data" },
  quantified_change: { fr: "Variation mesurée", en: "Measured change" },
  orb: { fr: "Orbe", en: "Orb" },
  phase: { fr: "Phase", en: "Phase" },
  applying: { fr: "appliquante", en: "applying" },
  separating: { fr: "séparante", en: "separating" },
  houses: { fr: "Maisons", en: "Houses" },
  score_delta: { fr: "delta score", en: "score delta" },
  intensity_delta: { fr: "delta intensité", en: "intensity delta" },
  composite_delta: { fr: "variation globale", en: "global delta" },
  rank_delta: { fr: "delta rang", en: "rank delta" },
};

export const DRIVER_TYPE_LABELS: Record<string, Record<Lang, string>> = {
  // Taxonomy V2
  aspect_exact_to_angle: { fr: "Alignement angulaire exact", en: "Exact angular alignment" },
  aspect_exact_to_luminary: { fr: "Point culminant d'un luminaire", en: "Culmination of a luminary" },
  aspect_exact_to_personal: { fr: "Résonance avec votre thème natal", en: "Resonance with your natal chart" },
  aspect_enter_orb: { fr: "Entrée en orbe d'aspect", en: "Aspect orb opening" },
  aspect_exit_orb: { fr: "Sortie d'orbe d'aspect", en: "Aspect orb closing" },
  moon_sign_ingress: { fr: "Changement de signe de la Lune", en: "Moon sign change" },
  asc_sign_change: { fr: "Changement de signe à l'Ascendant", en: "Ascendant sign change" },
  planet_ingress: { fr: "Changement de signe planétaire", en: "Planetary sign change" },
  planetary_hour_change: { fr: "Changement d'heure planétaire", en: "Planetary hour change" },
  // Legacy codes
  exact: { fr: "Aspect exact", en: "Exact aspect" },
  ingress: { fr: "Changement de signe", en: "Sign ingress" },
  station: { fr: "Station planétaire", en: "Planetary station" },
  enter_orb: { fr: "Entrée en orbe", en: "Orb opening" },
  exit_orb: { fr: "Sortie d'orbe", en: "Orb closing" },
  generic_event: { fr: "Configuration céleste notable", en: "Notable celestial configuration" },
};

export const MOVEMENT_DIRECTION_LABELS: Record<string, Record<Lang, string>> = {
  rising: { fr: "en hausse", en: "rising" },
  falling: { fr: "en baisse", en: "falling" },
  recomposition: { fr: "en mutation", en: "shifting" },
};

export const INTENSITY_LEVEL_LABELS: Record<string, Record<Lang, string>> = {
  slight: { fr: "léger", en: "slight" },
  notable: { fr: "net", en: "notable" },
  marked: { fr: "marqué", en: "marked" },
};

export const CATEGORY_VARIATION_LABELS: Record<string, Record<Lang, string>> = {
  up: { fr: "progression", en: "increase" },
  down: { fr: "recul", en: "decrease" },
  stable: { fr: "stabilité", en: "stability" },
};

export const PREDICTION_UI_MESSAGES: Record<
  | "loading"
  | "error"
  | "retry"
  | "empty"
  | "setup_profile"
  | "best_window"
  | "dominant"
  | "timeline"
  | "pivot_badge"
  | "turning_points"
  | "impacts_label"
  | "no_major_aspect"
  | "aspect_shift_label"
  | "intensity"
  | "pending_summary"
  | "key_points_title"
  | "timeline_title"
  | "focus_title"
  | "domains_title"
  | "advice_title"
  | "advice_cta"
  | "day_mood_label",
  Record<Lang, string>
> = {
  loading: { fr: "Chargement de votre ciel du jour...", en: "Loading your forecast for today..." },
  error: { fr: "Impossible de charger votre horoscope du jour.", en: "Unable to load today's horoscope." },
  retry: { fr: "Réessayer", en: "Retry" },
  empty: { fr: "Aucune prédiction disponible pour le moment.", en: "No prediction is available right now." },
  setup_profile: { fr: "Configurer mon profil", en: "Set up my profile" },
  best_window: { fr: "Meilleur créneau", en: "Best window" },
  dominant: { fr: "Dominante", en: "Dominant" },
  timeline: { fr: "Chronologie du jour", en: "Today's timeline" },
  pivot_badge: { fr: "Changement", en: "Shift" },
  turning_points: { fr: "Moments clés du jour", en: "Key moments today" },
  impacts_label: { fr: "Impacts :", en: "Impacts:" },
  no_major_aspect: { fr: "Pas d'aspect majeur", en: "No major aspect" },
  aspect_shift_label: { fr: "Bascule", en: "Shift" },
  intensity: { fr: "Intensité", en: "Intensity" },
  pending_summary: { fr: "Calcul de votre tendance en cours...", en: "Calculating your daily trend..." },
  key_points_title: { fr: "Points clés du jour", en: "Key points" },
  timeline_title: { fr: "Moments de la journée", en: "Day timeline" },
  focus_title: { fr: "Focus du créneau", en: "Slot focus" },
  domains_title: { fr: "Domaines du jour", en: "Daily domains" },
  advice_title: { fr: "Conseil du jour", en: "Today's advice" },
  advice_cta: { fr: "Voir les moments clés", en: "View key moments" },
  day_mood_label: { fr: "Tonalité", en: "Mood" },
  see_details_cta: { fr: "Voir le détail", en: "See details" },
  no_detail_available: { fr: "Détails non disponibles pour ce créneau.", en: "Details not available for this slot." },
  focus_moment_default_title: { fr: "Moment de la journée", en: "Moment of the day" },
  optimize_day_cta: { fr: "Optimiser ma journée", en: "Optimize my day" },
};

/**
 * Helper to get a label with fallback.
 */
export function getLabel(
  dictionary: Record<string, Record<Lang, string>>,
  code: string,
  lang: Lang
): string {
  const entry = dictionary[code];
  if (!entry) return code;
  return entry[lang] || code;
}
