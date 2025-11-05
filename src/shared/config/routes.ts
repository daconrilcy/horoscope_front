/**
 * Routes centralisées de l'application
 * Évite les strings en dur et facilite la maintenance
 */

export const ROUTES = {
  // Routes publiques
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  RESET: {
    REQUEST: '/reset/request',
    CONFIRM: '/reset/confirm',
  },
  LEGAL: {
    BASE: '/legal',
    TOS: '/legal/tos',
    PRIVACY: '/legal/privacy',
  },
  BILLING: {
    SUCCESS: '/billing/success',
    CANCEL: '/billing/cancel',
  },

  // Routes privées
  APP: {
    BASE: '/app',
    DASHBOARD: '/app/dashboard',
    HOROSCOPE: '/app/horoscope',
    CHAT: '/app/chat',
    ACCOUNT: '/app/account',
  },

  // Route 404
  NOT_FOUND: '*',
} as const;

/**
 * Type pour les routes publiques
 */
export type PublicRoute =
  | typeof ROUTES.HOME
  | typeof ROUTES.LOGIN
  | typeof ROUTES.SIGNUP
  | typeof ROUTES.LEGAL.TOS
  | typeof ROUTES.LEGAL.PRIVACY;

/**
 * Type pour les routes privées
 */
export type PrivateRoute =
  | typeof ROUTES.APP.DASHBOARD
  | typeof ROUTES.APP.HOROSCOPE
  | typeof ROUTES.APP.CHAT
  | typeof ROUTES.APP.ACCOUNT;
