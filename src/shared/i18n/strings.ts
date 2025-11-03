/**
 * Module i18n pour centraliser les labels et CTA
 * Prêt pour internationalisation future
 */

/**
 * Labels pour la page Home
 */
export const HOME_STRINGS = {
  TITLE: 'Horoscope & Conseils Personnalisés',
  DESCRIPTION:
    'Découvrez votre horoscope personnalisé et recevez des conseils adaptés à votre profil astrologique',
  SIGNUP_CTA: "S'inscrire",
  SIGNUP_ARIA: "S'inscrire pour créer un compte",
  LOGIN_CTA: 'Se connecter',
  LOGIN_ARIA: 'Se connecter à votre compte',
  TOS_LINK: "Conditions d'utilisation",
  TOS_ARIA: "Consulter les conditions d'utilisation",
  PRIVACY_LINK: 'Politique de confidentialité',
  PRIVACY_ARIA: 'Consulter la politique de confidentialité',
} as const;

/**
 * Labels pour la page Dashboard
 */
export const DASHBOARD_STRINGS = {
  TITLE: 'Tableau de bord',
  AUTH_CARD_TITLE: 'Mon compte',
  AUTH_EMAIL_LABEL: 'Email :',
  AUTH_EMAIL_NOT_AVAILABLE: 'Non disponible',
  AUTH_LOGOUT_CTA: 'Se déconnecter',
  AUTH_LOGOUT_ARIA: 'Se déconnecter',
  PLAN_SECTION_TITLE: 'Mon offre',
  PLAN_LOADING: 'Chargement du plan...',
  QUOTA_SECTION_TITLE: 'État des quotas',
  QUICK_CARDS_TITLE: 'Accès rapide',
  HOROSCOPE_CARD_TITLE: 'Horoscope',
  HOROSCOPE_CREATE_CTA: 'Créer mon thème natal',
  HOROSCOPE_VIEW_TODAY_CTA: 'Voir Today',
  HOROSCOPE_LAST_CHART_LABEL: 'Dernier thème :',
  HOROSCOPE_NO_NAME: 'Sans nom',
  CHAT_CARD_TITLE: 'Chat',
  CHAT_CTA: "Discuter avec l'IA",
  CHAT_PLUS_REQUIRED: 'Plus requis',
  CHAT_ARIA: 'Accéder au chat',
  ACCOUNT_CARD_TITLE: 'Compte',
  ACCOUNT_CTA: 'Export & Paramètres',
  ACCOUNT_ARIA: 'Gérer mon compte',
} as const;

/**
 * Labels généraux
 */
export const COMMON_STRINGS = {
  LOADING: 'Chargement...',
  ERROR: 'Une erreur est survenue',
  RETRY: 'Réessayer',
  CANCEL: 'Annuler',
  CONFIRM: 'Confirmer',
} as const;
