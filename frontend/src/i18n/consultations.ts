import type { AstrologyLang } from "./astrology"
import type { AppLocale } from "./types"

export type ConsultationsTranslation = { t: (key: string) => string };

const CONSULTATIONS_I18N: Record<string, Record<AstrologyLang, string>> = {
  back_to_dashboard: {
    fr: "Retour au tableau de bord",
    en: "Back to dashboard",
    es: "Volver al tablero de mando",
  },
  // ... (rest of the file remains same, but I must provide full content)
  loading_catalogue: {
    fr: "Chargement du catalogue...",
    en: "Loading catalogue...",
    es: "Cargando catálogo...",
  },
  catalogue_error: {
    fr: "Impossible de charger le catalogue, affichage des types par défaut.",
    en: "Could not load catalogue, showing default types.",
    es: "No se pudo cargar el catalogue, mostrando tipos predeterminados.",
  },
  choose_consultation: {
    fr: "Choisir",
    en: "Choose",
    es: "Elegir",
  },
  no_preference_title: {
    fr: "Je n’ai pas de préférence",
    en: "I have no preference",
    es: "No tengo preferencia",
  },
  no_preference_subtitle: {
    fr: "Laissez-vous guider et définissez votre besoin à l'étape suivante.",
    en: "Let us guide you and define your needs in the next step.",
    es: "Déjanos guiarte y define tus necesidades en el siguiente paso.",
  },
  start_now: {
    fr: "Commencer",
    en: "Start",
    es: "Comenzar",
  },
  page_title: {
    fr: "Choisissez votre consultation",
    en: "Choose your consultation",
    es: "Elija su consulta",
  },
  page_subtitle: {
    fr: "Nous analysons votre thème natal pour éclairer différents aspects de votre vie. Dans quel domaine souhaitez-vous un éclairage ?",
    en: "We analyze your natal chart to shed light on different aspects of your life. Which area would you like guidance on?",
    es: "Analizamos su carta natal para iluminar distintos aspects de su vida. ¿Sobre qué ámbito desea orientación?",
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
    fr: "Où j’en suis en ce moment",
    en: "Where I am right now",
    es: "Dónde estoy en este momento",
  },
  type_period_promise: {
    fr: "Faites le point sur la période que vous traversez et les dynamiques qui vous influencent.",
    en: "Take stock of the period you are going through and the dynamics influencing you.",
    es: "Haga balance del período que atraviesa y de las dinámicas que le influyen.",
  },
  type_work_label: {
    fr: "Ma vie pro & mes décisions",
    en: "My work life & decisions",
    es: "Mi vida profesional y mis decisiones",
  },
  type_work_promise: {
    fr: "Éclairez vos choix professionnels, vos opportunités et vos prochaines étapes.",
    en: "Clarify your professional choices, opportunities, and next steps.",
    es: "Aclare sus decisiones profesionales, sus oportunidades y sus próximos pasos.",
  },
  type_orientation_label: {
    fr: "Ce qui me correspond vraiment",
    en: "What truly suits me",
    es: "Lo que realmente me corresponde",
  },
  type_orientation_promise: {
    fr: "Mieux comprendre vos forces, vos aspirations et la direction qui vous ressemble.",
    en: "Better understand your strengths, aspirations, and the direction that fits you.",
    es: "Comprenda mejor sus fortalezas, aspiraciones y la dirección que le corresponde.",
  },
  type_relation_label: {
    fr: "Cette relation est-elle faite pour moi ?",
    en: "Is this relationship right for me?",
    es: "¿Esta relación está hecha para mí?",
  },
  type_relation_promise: {
    fr: "Explorez la dynamique d’une relation amoureuse, personnelle ou professionnelle.",
    en: "Explore the dynamics of a romantic, personal, or professional relationship.",
    es: "Explore la dinámica de una relación amorosa, personal o profesional.",
  },
  type_timing_label: {
    fr: "Est-ce le bon moment ?",
    en: "Is it the right time?",
    es: "¿Es el buen momento?",
  },
  type_timing_promise: {
    fr: "Identifiez les périodes les plus favorables pour agir, lancer ou décider.",
    en: "Identify the most favorable periods to act, launch, or decide.",
    es: "Identifique los períodos más favorables para actuar, lanzar o decidir.",
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
    fr: "faire le point sur ma période actuelle",
    en: "take stock of my current period",
    es: "hacer balance de mi período actual",
  },
  objective_work: {
    fr: "éclairer une décision ou une situation professionnelle",
    en: "clarify a professional decision or situation",
    es: "aclarar una decisión o situación profesional",
  },
  objective_orientation: {
    fr: "mieux comprendre ce qui me correspond",
    en: "better understand what truly suits me",
    es: "comprender mejor lo que realmente me corresponde",
  },
  objective_relation: {
    fr: "comprendre la dynamique d’une relation",
    en: "understand the dynamics of a relationship",
    es: "comprender la dinámica de una relación",
  },
  objective_timing: {
    fr: "vérifier si c’est le bon moment pour agir",
    en: "check whether this is the right time to act",
    es: "verificar si es el buen momento para actuar",
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
  save_to_contacts_label: {
    fr: "Enregistrer dans mes contacts",
    en: "Save to my contacts",
    es: "Guardar en mis contactos",
  },
  nickname_label: {
    fr: "Pseudonyme (pour vos contacts)",
    en: "Nickname (for your contacts)",
    es: "Pseudónimo (para sus contactos)",
  },
  nickname_placeholder: {
    fr: "Ex: Mon partenaire, Recruteur A...",
    en: "E.g. My partner, Recruiter A...",
    es: "Ej: Mi pareja, Reclutador A...",
  },
  pseudonym_warning: {
    fr: "Attention : Pour votre vie privée, n'utilisez pas de nom complet ou d'information permettant d'identifier directement la personne.",
    en: "Warning: For your privacy, do not use full names or information that directly identifies the person.",
    es: "Atención: Por su privacidad, no utilice nombres completos o información que identifique directamente a la persona.",
  },
  existing_contact_label: {
    fr: "Utiliser un contact enregistré",
    en: "Use an existing contact",
    es: "Utilizar un contacto guardado",
  },
  select_contact_placeholder: {
    fr: "-- Choisir un contact --",
    en: "-- Choose a contact --",
    es: "-- Elegir un contacto --",
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
  step_form: {
    fr: "Ma question",
    en: "My question",
    es: "Mi pregunta",
  },
  form_step_title: {
    fr: "Formulez votre demande",
    en: "Formulate your request",
    es: "Formule su solicitud",
  },
  add_third_party_label: {
    fr: "Cette consultation concerne aussi une autre personne",
    en: "This consultation also concerns another person",
    es: "Esta consulta también concierne a otra persona",
  },
  add_third_party_hint: {
    fr: "Optionnel — ajoutez les données natales d'un proche pour enrichir l'analyse.",
    en: "Optional — add a person's birth data to enrich the analysis.",
    es: "Opcional — añada los datos natales de alguien para enriquecer el análisis.",
  },
  select_astrologer_step_title: {
    fr: "Choisissez votre astrologue",
    en: "Choose your astrologer",
    es: "Elija su astrólogo",
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
  retry_loading_astrologers: {
    fr: "Réessayer",
    en: "Retry",
    es: "Reintentar",
  },
  no_astrologers_available: {
    fr: "Aucun astrologue spécifique n'est disponible pour le moment.",
    en: "No specific astrologer is available at the moment.",
    es: "No hay astrólogo específico disponible por el momento.",
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
    es: "La generación está tardando demasiado. Inténtelo de nouveau.",
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

export function tConsultations(key: string, lang: AppLocale): string {
  const entry = CONSULTATIONS_I18N[key]
  return entry?.[lang as AstrologyLang] ?? key
}
