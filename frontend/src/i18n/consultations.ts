import type { AstrologyLang } from "./astrology"

const CONSULTATIONS_I18N: Record<string, Record<AstrologyLang, string>> = {
  page_title: {
    fr: "Consultations",
    en: "Consultations",
    es: "Consultas",
  },
  page_subtitle: {
    fr: "Créez des consultations thématiques pour obtenir des guidances personnalisées.",
    en: "Create thematic consultations to get personalized guidance.",
    es: "Cree consultas temáticas para obtener orientación personalizada.",
  },
  start_consultation: {
    fr: "Nouvelle consultation",
    en: "New consultation",
    es: "Nueva consulta",
  },
  history_title: {
    fr: "Historique",
    en: "History",
    es: "Historial",
  },
  no_history: {
    fr: "Aucune consultation passée",
    en: "No past consultations",
    es: "Sin consultas pasadas",
  },
  type_dating: {
    fr: "Dating / Rendez-vous amoureux (Legacy)",
    en: "Dating / Romantic meetup (Legacy)",
    es: "Cita / Encuentro romántico (Legacy)",
  },
  type_pro: {
    fr: "Choix professionnel (Legacy)",
    en: "Professional choice (Legacy)",
    es: "Elección profesional (Legacy)",
  },
  type_event: {
    fr: "Événement important (Legacy)",
    en: "Important event (Legacy)",
    es: "Evento importante (Legacy)",
  },
  type_free: {
    fr: "Question libre (Legacy)",
    en: "Free question (Legacy)",
    es: "Pregunta libre (Legacy)",
  },
  type_period_label: {
    fr: "Période & Climat",
    en: "Period & Climate",
    es: "Periodo y Clima",
  },
  type_period_promise: {
    fr: "Comprenez les énergies qui influencent votre vie sur une période donnée.",
    en: "Understand the energies influencing your life over a given period.",
    es: "Comprenda las energías que influyen en su vida en un periodo determinado.",
  },
  type_work_label: {
    fr: "Carrière & Travail",
    en: "Career & Work",
    es: "Carrera y Trabajo",
  },
  type_work_promise: {
    fr: "Optimisez vos choix professionnels et saisissez les opportunités.",
    en: "Optimize your professional choices and seize opportunities.",
    es: "Optimice sus elecciones profesionales y aproveche las oportunidades.",
  },
  type_orientation_label: {
    fr: "Orientation & Mission",
    en: "Orientation & Mission",
    es: "Orientación y Misión",
  },
  type_orientation_promise: {
    fr: "Redonnez du sens à votre parcours et alignez-vous avec votre mission de vie.",
    en: "Find meaning in your path and align with your life mission.",
    es: "Encuentre sentido a su camino y alinéese con su misión de vida.",
  },
  type_relation_label: {
    fr: "Relations & Synastrie",
    en: "Relationships & Synastry",
    es: "Relaciones y Sinastría",
  },
  type_relation_promise: {
    fr: "Explorez la dynamique de vos relations personnelles ou professionnelles.",
    en: "Explore the dynamics of your personal or professional relationships.",
    es: "Explore la dinámica de sus relaciones personales o profesionales.",
  },
  type_timing_label: {
    fr: "Élection & Timing",
    en: "Election & Timing",
    es: "Elección y Timing",
  },
  type_timing_promise: {
    fr: "Identifiez le moment idéal pour agir et lancer vos projets.",
    en: "Identify the ideal moment to act and launch your projects.",
    es: "Identifique el momento ideal para actuar y lanzar sus proyectos.",
  },
  step_type: {
    fr: "Type",
    en: "Type",
    es: "Tipo",
  },
  step_astrologer: {
    fr: "Astrologue",
    en: "Astrologer",
    es: "Astrólogo",
  },
  step_validation: {
    fr: "Demande",
    en: "Request",
    es: "Solicitud",
  },
  select_type: {
    fr: "Choisissez le type de consultation",
    en: "Choose consultation type",
    es: "Elija el tipo de consulta",
  },
  select_astrologer: {
    fr: "Choisissez votre astrologue",
    en: "Choose your astrologer",
    es: "Elija su astrólogo",
  },
  auto_astrologer: {
    fr: "Laisser choisir automatiquement",
    en: "Let choose automatically",
    es: "Dejar elegir automáticamente",
  },
  enter_context: {
    fr: "Décrivez votre situation ou question",
    en: "Describe your situation or question",
    es: "Describa su situación o pregunta",
  },
  context_placeholder: {
    fr: "Ex: Je dois prendre une décision importante concernant...",
    en: "E.g.: I need to make an important decision about...",
    es: "Ej.: Debo tomar una decisión importante sobre...",
  },
  summary_title: {
    fr: "Votre demande ciblée",
    en: "Your targeted request",
    es: "Su solicitud enfocada",
  },
  objective_label: {
    fr: "Objet de la consultation",
    en: "Consultation goal",
    es: "Objetivo de la consulta",
  },
  objective_placeholder: {
    fr: "Ex: comprendre la dynamique de ce rendez-vous amoureux",
    en: "E.g. understand the dynamic of this romantic meetup",
    es: "Ej.: comprender la dinámica de esta cita romántica",
  },
  time_horizon_label: {
    fr: "Horizon temporel",
    en: "Time horizon",
    es: "Horizonte temporal",
  },
  time_horizon_placeholder: {
    fr: "Ex: cette semaine, ce mois-ci, avant l'entretien",
    en: "E.g. this week, this month, before the interview",
    es: "Ej.: esta semana, este mes, antes de la entrevista",
  },
  time_horizon_hint: {
    fr: "Optionnel, utile pour cadrer la guidance.",
    en: "Optional, useful to frame the guidance.",
    es: "Opcional, útil para encuadrar la orientación.",
  },
  objective_summary_label: {
    fr: "Objectif",
    en: "Goal",
    es: "Objetivo",
  },
  time_horizon_summary_label: {
    fr: "Horizon",
    en: "Horizon",
    es: "Horizonte",
  },
  generate: {
    fr: "Générer la consultation",
    en: "Generate consultation",
    es: "Generar consulta",
  },
  generating: {
    fr: "Génération en cours...",
    en: "Generating...",
    es: "Generando...",
  },
  next: {
    fr: "Suivant",
    en: "Next",
    es: "Siguiente",
  },
  previous: {
    fr: "Précédent",
    en: "Previous",
    es: "Anterior",
  },
  cancel: {
    fr: "Annuler",
    en: "Cancel",
    es: "Cancelar",
  },
  result_title: {
    fr: "Résultat de votre consultation",
    en: "Your consultation result",
    es: "Resultado de su consulta",
  },
  interpretation: {
    fr: "Interprétation",
    en: "Interpretation",
    es: "Interpretación",
  },
  open_in_chat: {
    fr: "Ouvrir dans le chat",
    en: "Open in chat",
    es: "Abrir en el chat",
  },
  save: {
    fr: "Sauvegarder",
    en: "Save",
    es: "Guardar",
  },
  saved: {
    fr: "Sauvegardé",
    en: "Saved",
    es: "Guardado",
  },
  back_to_consultations: {
    fr: "Retour aux consultations",
    en: "Back to consultations",
    es: "Volver a consultas",
  },
  error_generation: {
    fr: "Erreur lors de la génération. Veuillez réessayer.",
    en: "Error during generation. Please try again.",
    es: "Error durante la generación. Por favor, inténtelo de nuevo.",
  },
  loading: {
    fr: "Chargement...",
    en: "Loading...",
    es: "Cargando...",
  },
  error_loading_astrologers: {
    fr: "Erreur lors du chargement des astrologues.",
    en: "Error loading astrologers.",
    es: "Error al cargar los astrólogos.",
  },
  interpretation_label: {
    fr: "Interprétation",
    en: "Interpretation",
    es: "Interpretación",
  },
  wizard_progress_aria: {
    fr: "Étapes de la consultation",
    en: "Consultation steps",
    es: "Pasos de la consulta",
  },
  context_max_length_hint: {
    fr: "caractères restants",
    en: "characters remaining",
    es: "caracteres restantes",
  },
  loading_name: {
    fr: "Chargement...",
    en: "Loading...",
    es: "Cargando...",
  },
  objective_dating: {
    fr: "relation/amour",
    en: "romantic relationship/love",
    es: "relación/amor",
  },
  objective_pro: {
    fr: "décision ou évolution professionnelle",
    en: "professional decision or evolution",
    es: "decisión o evolución profesional",
  },
  objective_event: {
    fr: "événement spécifique",
    en: "specific event",
    es: "evento específico",
  },
  objective_free: {
    fr: "guidance libre",
    en: "free guidance",
    es: "orientación libre",
  },
  objective_period: {
    fr: "comprendre le climat d'une période",
    en: "understand the climate of a period",
    es: "comprender el clima de un periodo",
  },
  objective_work: {
    fr: "étudier une situation professionnelle",
    en: "study a professional situation",
    es: "estudiar una situación profesional",
  },
  objective_orientation: {
    fr: "trouver son orientation de vie",
    en: "find one's life direction",
    es: "encontrar su dirección de vida",
  },
  objective_relation: {
    fr: "analyser une dynamique relationnelle",
    en: "analyze relational dynamics",
    es: "analizar la dinámica relacional",
  },
  objective_timing: {
    fr: "choisir le bon moment pour agir",
    en: "choose the right time to act",
    es: "elegir el momento adecuado para actuar",
  },
  key_points_label: {
    fr: "Points clés",
    en: "Key points",
    es: "Puntos clave",
  },
  actionable_advice_label: {
    fr: "Conseils",
    en: "Advice",
    es: "Consejos",
  },
}

export function t(key: string, lang: AstrologyLang): string {
  const entry = CONSULTATIONS_I18N[key]
  return entry?.[lang] ?? key
}
