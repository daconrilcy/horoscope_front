export type Lang = "fr" | "en";

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
  | "intensity"
  | "pending_summary",
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
  pivot_badge: { fr: "Pivot", en: "Pivot" },
  turning_points: { fr: "Points de bascule", en: "Turning points" },
  intensity: { fr: "Intensité", en: "Intensity" },
  pending_summary: { fr: "Calcul de votre tendance en cours...", en: "Calculating your daily trend..." },
};
