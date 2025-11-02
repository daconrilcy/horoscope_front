/**
 * Helpers pour la gestion du token JWT dans localStorage
 * Source de vérité = mémoire (Zustand), localStorage sert uniquement d'appoint pour rehydrate au boot
 */

const STORAGE_KEY = 'APP_AUTH_TOKEN';

/**
 * Lit le token depuis localStorage
 * @returns Token ou null si absent/invalide
 */
export function readPersistedToken(): string | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored == null || stored === '') {
      return null;
    }

    // Essayer de parser comme JSON
    try {
      const parsed: unknown = JSON.parse(stored);
      // Si c'est un objet avec token, extraire le token
      if (typeof parsed === 'object' && parsed !== null && 'token' in parsed) {
        const tokenValue = (parsed as { token: unknown }).token;
        return typeof tokenValue === 'string' ? tokenValue : null;
      }
      // Si c'est directement une string, la retourner
      if (typeof parsed === 'string') {
        return parsed;
      }
      // Sinon, retourner null (format inconnu)
      return null;
    } catch {
      // Si le parsing JSON échoue, ce n'est pas un format valide
      // Retourner null pour éviter de retourner des données invalides
      return null;
    }
  } catch {
    // Fallback en cas d'erreur (localStorage bloqué, etc.)
    return null;
  }
}

/**
 * Stocke le token dans localStorage
 * @param token Token JWT à persister
 */
export function writePersistedToken(token: string): void {
  try {
    // Stocker comme JSON stringifié pour cohérence avec Zustand persist
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ token }));
  } catch {
    // Ignorer les erreurs (localStorage plein, etc.)
  }
}

/**
 * Purge le token de localStorage
 */
export function clearPersistedToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignorer les erreurs
  }
}

