/**
 * Version de l'application (git SHA ou version package)
 * Utilisé pour X-Client-Version dans les headers HTTP
 */

// En dev, générer un hash court basé sur timestamp
// En prod, utiliser le git SHA injecté à la build time
export const CLIENT_VERSION: string =
  (import.meta.env.VITE_CLIENT_VERSION as string | undefined) ||
  `dev-${Date.now().toString(36).slice(-8)}`;

// Source identifiée dans les logs backend
export const REQUEST_SOURCE: string = 'frontend';
