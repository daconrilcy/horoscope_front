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
    fr: "Dating / Rendez-vous amoureux",
    en: "Dating / Romantic meetup",
    es: "Cita / Encuentro romántico",
  },
  type_pro: {
    fr: "Choix professionnel",
    en: "Professional choice",
    es: "Elección profesional",
  },
  type_event: {
    fr: "Événement important",
    en: "Important event",
    es: "Evento importante",
  },
  type_free: {
    fr: "Question libre",
    en: "Free question",
    es: "Pregunta libre",
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
  step_drawing: {
    fr: "Tirage",
    en: "Drawing",
    es: "Tirada",
  },
  step_validation: {
    fr: "Validation",
    en: "Validation",
    es: "Validación",
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
  select_drawing: {
    fr: "Souhaitez-vous un tirage ?",
    en: "Would you like a drawing?",
    es: "¿Desea una tirada?",
  },
  drawing_none: {
    fr: "Sans tirage",
    en: "No drawing",
    es: "Sin tirada",
  },
  drawing_tarot: {
    fr: "Tirage de cartes",
    en: "Card drawing",
    es: "Tirada de cartas",
  },
  drawing_runes: {
    fr: "Tirage de runes",
    en: "Rune drawing",
    es: "Tirada de runas",
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
    fr: "Récapitulatif",
    en: "Summary",
    es: "Resumen",
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
  drawing_completed: {
    fr: "Tirage effectué",
    en: "Drawing completed",
    es: "Tirada realizada",
  },
  loading_name: {
    fr: "Chargement...",
    en: "Loading...",
    es: "Cargando...",
  },
}

export function t(key: string, lang: AstrologyLang): string {
  const entry = CONSULTATIONS_I18N[key]
  return entry?.[lang] ?? key
}
