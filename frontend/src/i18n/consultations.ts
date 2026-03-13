import type { AstrologyLang } from "./astrology"

const CONSULTATIONS_I18N: Record<string, Record<AstrologyLang, string>> = {
  page_title: {
    fr: "Consultations",
    en: "Consultations",
    es: "Consultas",
  },
  page_subtitle: {
    fr: "Créez des consultations thématiques ciblées avec nos astrologues.",
    en: "Create targeted thematic consultations with our astrologers.",
    es: "Cree consultas temáticas específicas con nuestros astrólogos.",
  },
  new_consultation_cta: {
    fr: "Nouvelle consultation",
    en: "New consultation",
    es: "Nueva consulta",
  },
  history_title: {
    fr: "Vos consultations passées",
    en: "Your past consultations",
    es: "Sus consultas pasadas",
  },
  no_history: {
    fr: "Aucune consultation passée",
    en: "No past consultations",
    es: "Sin consultas pasadas",
  },
  precheck_loading: {
    fr: "Analyse de votre profil en cours...",
    en: "Analyzing your profile...",
    es: "Analizando su perfil...",
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
  wizard_progress_aria: {
    fr: "Étapes de la consultation",
    en: "Consultation steps",
    es: "Pasos de la consulta",
  },
  step_type: {
    fr: "Type",
    en: "Type",
    es: "Tipo",
  },
  step_frame: {
    fr: "Cadrage",
    en: "Framing",
    es: "Encuadre",
  },
  step_collection: {
    fr: "Collecte",
    en: "Collection",
    es: "Recolección",
  },
  step_summary: {
    fr: "Résumé",
    en: "Summary",
    es: "Resumen",
  },
  frame_step_title: {
    fr: "Cadrez votre demande",
    en: "Frame your request",
    es: "Encuadre su solicitud",
  },
  collection_step_title: {
    fr: "Compléments nécessaires",
    en: "Additional information",
    es: "Información adicional",
  },
  summary_step_title: {
    fr: "Vérification finale",
    en: "Final verification",
    es: "Verificación final",
  },
  select_type: {
    fr: "Choisissez le type de consultation",
    en: "Choose consultation type",
    es: "Elija el tipo de consulta",
  },
  objective_label: {
    fr: "Objet de la consultation",
    en: "Consultation goal",
    es: "Objetivo de la consulta",
  },
  objective_placeholder: {
    fr: "Ex: comprendre la dynamique de ce rendez-vous",
    en: "E.g. understand the dynamic of this romantic meetup",
    es: "Ej: comprender la dinámica de esta cita",
  },
  enter_context: {
    fr: "Décrivez votre situation ou votre question",
    en: "Describe your situation or question",
    es: "Describa su situación o pregunta",
  },
  context_placeholder: {
    fr: "Ex : Je dois prendre une décision importante concernant...",
    en: "E.g.: I need to make an important decision about...",
    es: "Ej: Debo tomar una decisión importante sobre...",
  },
  context_max_length_hint: {
    fr: "caractères restants",
    en: "characters remaining",
    es: "caracteres restantes",
  },
  time_horizon_label: {
    fr: "Horizon temporel",
    en: "Time horizon",
    es: "Horizonte temporal",
  },
  time_horizon_placeholder: {
    fr: "Ex : cette semaine, ce mois-ci, avant l'entretien",
    en: "E.g. this week, this month, before the interview",
    es: "Ej: esta semana, este mes, antes de la entrevista",
  },
  time_horizon_hint: {
    fr: "Optionnel, utile pour cadrer la guidance.",
    en: "Optional, useful to frame the guidance.",
    es: "Opcional, útil para encuadrar la guía.",
  },
  is_interaction_label: {
    fr: "Cette consultation concerne une autre personne",
    en: "This consultation concerns another person",
    es: "Esta consulta se refiere a otra persona",
  },
  is_interaction_hint: {
    fr: "Cochez pour ajouter les données de naissance d'un tiers (ex: partenaire, collègue, recruteur).",
    en: "Check to add birth data for a third party (e.g., partner, colleague, recruiter).",
    es: "Marque para añadir los datos de nacimiento de un tercero (ej: pareja, colega, reclutador).",
  },
  other_person_title: {
    fr: "Informations sur l'autre personne",
    en: "Information about the other person",
    es: "Información sobre la otra persona",
  },
  other_person_hint: {
    fr: "Ces données sont utilisées uniquement pour cette consultation.",
    en: "This data is used only for this consultation.",
    es: "Estos datos se utilizan únicamente para esta consulta.",
  },
  birth_date_label: {
    fr: "Date de naissance",
    en: "Birth date",
    es: "Fecha de nacimiento",
  },
  birth_time_label: {
    fr: "Heure de naissance",
    en: "Birth time",
    es: "Hora de nacimiento",
  },
  unknown_time_label: {
    fr: "Heure inconnue",
    en: "Unknown time",
    es: "Hora desconocida",
  },
  birth_place_label: {
    fr: "Lieu de naissance",
    en: "Birth place",
    es: "Lugar de nacimiento",
  },
  birth_place_placeholder: {
    fr: "Ville, Pays",
    en: "City, Country",
    es: "Ciudad, País",
  },
  birth_city_label: {
    fr: "Ville de naissance",
    en: "Birth city",
    es: "Ciudad de nacimiento",
  },
  birth_city_placeholder: {
    fr: "Paris",
    en: "Paris",
    es: "Paris",
  },
  birth_country_label: {
    fr: "Pays de naissance",
    en: "Birth country",
    es: "País de nacimiento",
  },
  birth_country_placeholder: {
    fr: "France",
    en: "France",
    es: "Francia",
  },
  user_data_missing_hint: {
    fr: "Certaines de vos données de profil sont manquantes pour une précision optimale.",
    en: "Some of your profile data is missing for optimal precision.",
    es: "Faltan algunos datos de su perfil para una precisión óptima.",
  },
  complete_my_profile: {
    fr: "Compléter mon profil",
    en: "Complete my profile",
    es: "Completar mi perfil",
  },
  no_extra_data_needed: {
    fr: "Aucune donnée supplémentaire n'est requise.",
    en: "No extra data is required.",
    es: "No se requiere información adicional.",
  },
  expected_quality_title: {
    fr: "Qualité attendue",
    en: "Expected quality",
    es: "Calidad esperada",
  },
  precision_high: {
    fr: "Précision élevée",
    en: "High precision",
    es: "Precisión alta",
  },
  precision_medium: {
    fr: "Précision moyenne",
    en: "Medium precision",
    es: "Precisión media",
  },
  precision_limited: {
    fr: "Précision limitée",
    en: "Limited precision",
    es: "Precisión limitada",
  },
  precision_blocked: {
    fr: "Génération bloquée",
    en: "Generation blocked",
    es: "Generación bloqueada",
  },
  degraded_mode_info: {
    fr: "Mode dégradé",
    en: "Degraded mode",
    es: "Modo degradado",
  },
  user_no_birth_time: {
    fr: "Heure de naissance utilisateur manquante",
    en: "Missing user birth time",
    es: "Falta la hora de nacimiento del usuario",
  },
  other_no_birth_time: {
    fr: "Heure de naissance de l'autre personne manquante",
    en: "Missing other person birth time",
    es: "Falta la hora de nacimiento de la otra persona",
  },
  choose_astrologer_optional: {
    fr: "Choisissez votre astrologue (optionnel)",
    en: "Choose your astrologer (optional)",
    es: "Elija a su astrólogo (opcional)",
  },
  select_astrologer: {
    fr: "Sélectionnez un astrologue",
    en: "Select an astrologer",
    es: "Seleccione un astrólogo",
  },
  step_astrologer: {
    fr: "Astrologue",
    en: "Astrologer",
    es: "Astrólogo",
  },
  auto_astrologer: {
    fr: "Sélection automatique",
    en: "Automatic selection",
    es: "Selección automática",
  },
  loading: {
    fr: "Chargement...",
    en: "Loading...",
    es: "Cargando...",
  },
  loading_name: {
    fr: "Chargement du nom...",
    en: "Loading name...",
    es: "Cargando nombre...",
  },
  error_loading_astrologers: {
    fr: "Impossible de charger les astrologues.",
    en: "Unable to load astrologers.",
    es: "No se pueden cargar los astrólogos.",
  },
  type_label: {
    fr: "Type",
    en: "Type",
    es: "Tipo",
  },
  horizon_label: {
    fr: "Horizon",
    en: "Horizon",
    es: "Horizonte",
  },
  other_person_label: {
    fr: "Autre personne",
    en: "Other person",
    es: "Otra persona",
  },
  not_specified: {
    fr: "non précisé",
    en: "not specified",
    es: "no especificado",
  },
  blocked_reason_generic: {
    fr: "Certaines informations critiques sont manquantes pour générer cette consultation.",
    en: "Some critical information is missing to generate this consultation.",
    es: "Falta información crítica para generar esta consulta.",
  },
  precheck_not_available: {
    fr: "Analyse de qualité non disponible",
    en: "Quality analysis not available",
    es: "Análisis de calidad no disponible",
  },
  relation_user_only: {
    fr: "Analyse basée sur votre profil uniquement",
    en: "Analysis based on your profile only",
    es: "Análisis basado únicamente en su perfil",
  },
  timing_degraded: {
    fr: "Timing approximatif (heure de naissance manquante)",
    en: "Approximate timing (missing birth time)",
    es: "Tiempo aproximado (falta la hora de nacimiento)",
  },
  safeguard_reframed: {
    fr: "Réponse limitée aux aspects non sensibles",
    en: "Response limited to non-sensitive aspects",
    es: "Respuesta limitada a aspectos no sensibles",
  },
  safeguard_refused: {
    fr: "Sujet hors périmètre de conseil astrologique",
    en: "Subject outside the scope of astrological advice",
    es: "Tema fuera del alcance del asesoramiento astrológico",
  },
  nominal_mode_desc: {
    fr: "Toutes les données sont présentes pour une analyse optimale.",
    en: "All data is present for optimal analysis.",
    es: "Todos los datos están presentes para un análisis óptimo.",
  },
  birth_profile_not_found: {
    fr: "Profil natal non configuré",
    en: "Birth profile not configured",
    es: "Perfil natal no configurado",
  },
  safeguard_refusal_health: {
    fr: "Nous ne pouvons pas traiter les questions de santé physique.",
    en: "We cannot address physical health questions.",
    es: "No podemos abordar cuestiones de salud física.",
  },
  safeguard_refusal_death: {
    fr: "Les questions liées à la mort sont strictement exclues.",
    en: "Questions related to death are strictly excluded.",
    es: "Las cuestiones relacionadas con la muerte están estrictamente excluidas.",
  },
  safeguard_refusal_pregnancy: {
    fr: "Les questions de grossesse relèvent du domaine médical.",
    en: "Pregnancy questions belong to the medical field.",
    es: "Las cuestiones sobre el embarazo pertenecen al campo médico.",
  },
  safeguard_refusal_third_party_manipulation: {
    fr: "Nous refusons toute analyse visant à la manipulation d'autrui.",
    en: "We refuse any analysis aimed at manipulating others.",
    es: "Rechazamos cualquier análisis destinado a manipular a otros.",
  },
  cancel: {
    fr: "Annuler",
    en: "Cancel",
    es: "Cancelar",
  },
  previous: {
    fr: "Précédent",
    en: "Previous",
    es: "Anterior",
  },
  next: {
    fr: "Suivant",
    en: "Next",
    es: "Siguiente",
  },
  generate: {
    fr: "Générer la consultation",
    en: "Generate consultation",
    es: "Generar consulta",
  },
  generating: {
    fr: "Génération de votre consultation en cours...",
    en: "Generating your consultation...",
    es: "Generando su consulta...",
  },
  generation_timeout: {
    fr: "La génération prend trop de temps. Veuillez réessayer.",
    en: "Generation is taking too long. Please try again.",
    es: "La generación está tardando demasiado. Inténtelo de nuevo.",
  },
  error_generation: {
    fr: "La génération de la consultation a échoué.",
    en: "Consultation generation failed.",
    es: "La generación de la consulta falló.",
  },
  result_title: {
    fr: "Résultat de votre consultation",
    en: "Your consultation result",
    es: "Resultado de su consulta",
  },
  summary_label: {
    fr: "Résumé",
    en: "Summary",
    es: "Resumen",
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
  back_to_consultations: {
    fr: "Retour aux consultations",
    en: "Back to consultations",
    es: "Volver a consultas",
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
  objective_summary_label: {
    fr: "Objet",
    en: "Objective",
    es: "Objetivo",
  },
  time_horizon_summary_label: {
    fr: "Horizon temporel",
    en: "Time horizon",
    es: "Horizonte temporal",
  },
  interpretation_label: {
    fr: "Interprétation",
    en: "Interpretation",
    es: "Interpretación",
  },
}

export function t(key: string, lang: AstrologyLang): string {
  const entry = CONSULTATIONS_I18N[key]
  return entry?.[lang] ?? key
}
