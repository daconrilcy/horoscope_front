import type { AstrologyLang } from "./astrology"

const ASTROLOGERS_I18N: Record<string, Record<AstrologyLang, string>> = {
  page_title: {
    fr: "Nos Astrologues",
    en: "Our Astrologers",
    es: "Nuestros Astrólogos",
  },
  page_subtitle: {
    fr: "Choisissez l'astrologue qui vous correspond pour démarrer une conversation.",
    en: "Choose the astrologer that suits you to start a conversation.",
    es: "Elija el astrólogo que le corresponda para iniciar una conversación.",
  },
  loading: {
    fr: "Chargement...",
    en: "Loading...",
    es: "Cargando...",
  },
  error_loading: {
    fr: "Erreur lors du chargement des astrologues.",
    en: "Error loading astrologers.",
    es: "Error al cargar los astrólogos.",
  },
  error_loading_description: {
    fr: "Le profil de cet astrologue n'a pas pu être chargé. Veuillez réessayer.",
    en: "This astrologer's profile could not be loaded. Please try again.",
    es: "No se pudo cargar el perfil de este astrólogo. Inténtelo de nuevo.",
  },
  empty_state: {
    fr: "Aucun astrologue disponible",
    en: "No astrologers available",
    es: "No hay astrólogos disponibles",
  },
  back_to_catalogue: {
    fr: "Retour au catalogue",
    en: "Back to catalogue",
    es: "Volver al catálogo",
  },
  start_conversation: {
    fr: "Démarrer une conversation",
    en: "Start a conversation",
    es: "Iniciar una conversación",
  },
  years_experience: {
    fr: "ans d'expérience",
    en: "years of experience",
    es: "años de experiencia",
  },
  specialties: {
    fr: "Spécialités",
    en: "Specialties",
    es: "Especialidades",
  },
  languages: {
    fr: "Langues",
    en: "Languages",
    es: "Idiomas",
  },
  about: {
    fr: "À propos",
    en: "About",
    es: "Acerca de",
  },
  profile_not_found: {
    fr: "Astrologue introuvable",
    en: "Astrologer not found",
    es: "Astrólogo no encontrado",
  },
  profile_not_found_description: {
    fr: "L'astrologue demandé n'existe pas ou n'est plus disponible.",
    en: "The requested astrologer does not exist or is no longer available.",
    es: "El astrólogo solicitado no existe o ya no está disponible.",
  },
  view_profile_aria: {
    fr: "Voir le profil de",
    en: "View profile of",
    es: "Ver perfil de",
  },
  avatar_alt: {
    fr: "Avatar de",
    en: "Avatar of",
    es: "Avatar de",
  },
  provider_type_ai: {
    fr: "Astrologue IA",
    en: "AI astrologer",
    es: "Astrólogo IA",
  },
  provider_type_real: {
    fr: "Astrologue réel",
    en: "Human astrologer",
    es: "Astrólogo real",
  },
  your_astrologer: {
    fr: "Votre Astrologue",
    en: "Your Astrologer",
    es: "Su Astrólogo",
  },
  online: {
    fr: "En ligne",
    en: "Online",
    es: "En línea",
  },
  this_conversation: {
    fr: "Cette conversation",
    en: "This conversation",
    es: "Esta conversación",
  },
  default_bio: {
    fr: "Votre guide céleste personnel, connecté à votre thème natal pour des conseils personnalisés.",
    en: "Your personal celestial guide, connected to your birth chart for personalized advice.",
    es: "Tu guía celestial personal, conectado a tu carta natal para consejos personalizados.",
  },
  aria_star: {
    fr: "étoile",
    en: "star",
    es: "estrella",
  },
  aria_error: {
    fr: "erreur",
    en: "error",
    es: "error",
  },
  aria_not_found: {
    fr: "introuvable",
    en: "not found",
    es: "no encontrado",
  },
  chat_no_conversation: {
    fr: "Aucune conversation",
    en: "No conversation",
    es: "Sin conversación",
  },
  chat_no_conversation_description: {
    fr: "Commencez une nouvelle conversation avec votre astrologue pour recevoir des conseils personnalisés basés sur votre thème natal.",
    en: "Start a new conversation with your astrologer to receive personalized advice based on your birth chart.",
    es: "Comience una nueva conversación con su astrólogo para recibir consejos personalizados basados en su carta natal.",
  },
  chat_no_conversation_with_astrologer: {
    fr: "Commencez une conversation avec {name} pour recevoir des conseils personnalisés basés sur votre thème natal.",
    en: "Start a conversation with {name} to receive personalized advice based on your birth chart.",
    es: "Comience una conversación con {name} para recibir consejos personalizados basados en su carta natal.",
  },
  choose_astrologer: {
    fr: "Choisir un astrologue",
    en: "Choose an astrologer",
    es: "Elegir un astrólogo",
  },
  chat_not_found: {
    fr: "Conversation introuvable",
    en: "Conversation not found",
    es: "Conversación no encontrada",
  },
  chat_not_found_description: {
    fr: "La conversation #{id} n'existe pas ou a été supprimée.",
    en: "Conversation #{id} does not exist or has been deleted.",
    es: "La conversación #{id} no existe o ha sido eliminada.",
  },
  back_to_conversations: {
    fr: "Retour aux conversations",
    en: "Back to conversations",
    es: "Volver a las conversaciones",
  },
  aria_chat_bubble: {
    fr: "bulle de conversation",
    en: "chat bubble",
    es: "burbuja de conversación",
  },
  aria_search: {
    fr: "loupe de recherche",
    en: "search magnifier",
    es: "lupa de búsqueda",
  },
  chat_back_to_list: {
    fr: "Retour à la liste",
    en: "Back to list",
    es: "Volver a la lista",
  },
  chat_back: {
    fr: "Retour",
    en: "Back",
    es: "Volver",
  },
  chat_empty_title: {
    fr: "Commencez une conversation avec votre astrologue.",
    en: "Start a conversation with your astrologer.",
    es: "Comience una conversación con su astrólogo.",
  },
  chat_empty_subtitle: {
    fr: "Posez votre question sur votre thème natal, vos transits ou votre guidance du jour.",
    en: "Ask about your birth chart, transits, or daily guidance.",
    es: "Pregunte sobre su carta natal, tránsitos o guía del día.",
  },
  chat_error_prefix: {
    fr: "Erreur",
    en: "Error",
    es: "Error",
  },
  chat_retry: {
    fr: "Réessayer",
    en: "Retry",
    es: "Reintentar",
  },
  chat_quota_exhausted: {
    fr: "Votre quota quotidien est épuisé. Revenez demain ou changez de plan.",
    en: "Your daily quota is exhausted. Come back tomorrow or change your plan.",
    es: "Su cuota diaria está agotada. Vuelva mañana o cambie su plan.",
  },
  chat_placeholder: {
    fr: "Posez votre question aux astres...",
    en: "Ask the stars your question...",
    es: "Haga su pregunta a las estrellas...",
  },
  chat_send: {
    fr: "Envoyer",
    en: "Send",
    es: "Enviar",
  },
  chat_input_aria: {
    fr: "Message",
    en: "Message",
    es: "Mensaje",
  },
  chat_resume_conversation: {
    fr: "Reprendre la conversation",
    en: "Resume conversation",
    es: "Reanudar conversación",
  },
  chat_page_title: {
    fr: "Chat astrologique",
    en: "Astrology chat",
    es: "Chat astrológico",
  },
  chat_threads_title: {
    fr: "Discussions",
    en: "Threads",
    es: "Conversaciones",
  },
  chat_window_title: {
    fr: "Conversation en cours",
    en: "Active conversation",
    es: "Conversación activa",
  },
  chat_window_subtitle: {
    fr: "Retrouvez vos échanges astrologiques et poursuivez la discussion.",
    en: "Continue your astrology conversation from where you left off.",
    es: "Retome su conversación astrológica donde la dejó.",
  },
  conversations_title: {
    fr: "Conversations",
    en: "Conversations",
    es: "Conversaciones",
  },
  conversations_search: {
    fr: "Rechercher...",
    en: "Search...",
    es: "Buscar...",
  },
  conversations_error: {
    fr: "Erreur de chargement",
    en: "Loading error",
    es: "Error de carga",
  },
  conversations_no_results: {
    fr: "Aucun résultat",
    en: "No results",
    es: "Sin resultados",
  },
  conversation_new: {
    fr: "Nouvelle conversation",
    en: "New conversation",
    es: "Nueva conversación",
  },
  message_you: {
    fr: "Vous",
    en: "You",
    es: "Usted",
  },
  message_astrologer: {
    fr: "Astrologue",
    en: "Astrologer",
    es: "Astrólogo",
  },
  typing_label: {
    fr: "L'astrologue écrit...",
    en: "The astrologer is typing...",
    es: "El astrólogo está escribiendo...",
  },
  new_conversation: {
    fr: "Nouvelle discussion",
    en: "New conversation",
    es: "Nueva conversación",
  },
  chat_empty_state_title: {
    fr: "Bienvenue dans vos discussions",
    en: "Welcome to your conversations",
    es: "Bienvenido a sus conversaciones",
  },
  chat_empty_state_description: {
    fr: "Démarrez une discussion avec l'astrologue de votre choix pour recevoir des conseils personnalisés basés sur votre thème natal.",
    en: "Start a conversation with the astrologer of your choice to receive personalized advice based on your birth chart.",
    es: "Inicie una conversación con el astrólogo de su elección para recibir consejos personalizados basados en su carta natal.",
  },
  chat_empty_state_cta: {
    fr: "Démarrer ma première discussion",
    en: "Start my first conversation",
    es: "Iniciar mi primera conversación",
  },
  close: {
    fr: "Fermer",
    en: "Close",
    es: "Cerrar",
  },
  chat_opening_message: {
    fr: "Bonjour, que puis-je faire pour vous ?",
    en: "Hello, how can I help you?",
    es: "Hola, ¿en qué puedo ayudarle?",
  },
  ideal_for_prefix: {
    fr: "Idéal pour :",
    en: "Ideal for:",
    es: "Ideal para:",
  },
  consultations_count: {
    fr: "consultations",
    en: "consultations",
    es: "consultas",
  },
  average_rating_label: {
    fr: "note moyenne",
    en: "average rating",
    es: "calificación promedio",
  },
  mission_title: {
    fr: "Ma Mission",
    en: "My Mission",
    es: "Mi Misión",
  },
  method_title: {
    fr: "Ma Méthode",
    en: "My Method",
    es: "Mi Método",
  },
  specialties_title: {
    fr: "Expertises & Spécialités",
    en: "Expertise & Specialties",
    es: "Pericia y Especialidades",
  },
  reviews_title: {
    fr: "Avis",
    en: "Reviews from clients",
    es: "Opiniones de sus consultantes",
  },
  reviews_count: {
    fr: "avis",
    en: "reviews",
    es: "opiniones",
  },
  your_rating_title: {
    fr: "Votre note",
    en: "Your rating",
    es: "Su calificación",
  },
  review_form_title: {
    fr: "Ajouter un avis",
    en: "Add a review",
    es: "Añadir una reseña",
  },
  review_form_placeholder: {
    fr: "Décrivez votre expérience avec cet astrologue...",
    en: "Describe your experience with this astrologer...",
    es: "Describa su experiencia con este astrólogo...",
  },
  review_form_publish: {
    fr: "Publier l'avis",
    en: "Publish review",
    es: "Publicar la reseña",
  },
  review_form_min_length: {
    fr: "Merci d'écrire au moins 10 caractères pour publier un avis.",
    en: "Please write at least 10 characters to publish a review.",
    es: "Escriba al menos 10 caracteres para publicar una reseña.",
  },
  review_add_button: {
    fr: "Rédiger un avis",
    en: "Write a review",
    es: "Escribir una reseña",
  },
  rate_action: {
    fr: "Noter cet astrologue",
    en: "Rate this astrologer",
    es: "Calificar a este astrólogo",
  },
  cta_chat_new: {
    fr: "Démarrer un chat",
    en: "Start a chat",
    es: "Iniciar un chat",
  },
  cta_chat_resume: {
    fr: "Reprendre le chat",
    en: "Resume chat",
    es: "Reanudar el chat",
  },
  cta_natal_new: {
    fr: "Demander mon interprétation",
    en: "Request my interpretation",
    es: "Solicitar mi interpretación",
  },
  cta_natal_view: {
    fr: "Voir mon interprétation",
    en: "View my interpretation",
    es: "Ver mi interpretación",
  },
  cta_consultation: {
    fr: "Lancer une consultation",
    en: "Start a consultation",
    es: "Iniciar una consulta",
  },
  method_step_1: {
    fr: "Analyse du thème",
    en: "Chart Analysis",
    es: "Análisis del tema",
  },
  method_step_2: {
    fr: "Identification des cycles",
    en: "Cycle Identification",
    es: "Identificación de ciclos",
  },
  method_step_3: {
    fr: "Synthèse & Guidance",
    en: "Synthesis & Guidance",
    es: "Síntesis y Guía",
  },
  method_step_4: {
    fr: "Plan d'action",
    en: "Action Plan",
    es: "Plan de acción",
  },
}

export function tAstrologers(key: string, lang: AstrologyLang): string {
  const entry = ASTROLOGERS_I18N[key]
  return entry?.[lang] ?? key
}
