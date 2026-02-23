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
}

export function t(key: string, lang: AstrologyLang): string {
  const entry = ASTROLOGERS_I18N[key]
  return entry?.[lang] ?? key
}
