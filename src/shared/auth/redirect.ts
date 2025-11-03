/**
 * Helper pour validation sécurisée des redirections internes
 * Anti open-redirect : bloque routes externes
 */

/**
 * Valide et retourne une route de redirection sécurisée (interne uniquement)
 * @param path Route de redirection à valider (peut être undefined)
 * @returns Route sécurisée interne ou `/app/dashboard` par défaut
 */
export function safeInternalRedirect(path?: string): string {
  // Si pas de path, retourner dashboard par défaut
  if (path == null || path === '') {
    return '/app/dashboard';
  }

  // Bloquer les routes externes (commençant par // ou http:// ou https://)
  if (
    path.startsWith('//') ||
    path.startsWith('http://') ||
    path.startsWith('https://')
  ) {
    return '/app/dashboard';
  }

  // Vérifier que la route commence par / (route interne)
  if (!path.startsWith('/')) {
    return '/app/dashboard';
  }

  // Route valide interne
  return path;
}
