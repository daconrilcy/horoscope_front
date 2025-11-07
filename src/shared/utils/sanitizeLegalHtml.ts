/**
 * Sanitization minimale pour le HTML légal (TOS/Privacy)
 * Retire les éléments dangereux (scripts, iframes, objets, etc.) et les attributs on*
 */

/**
 * Sanitise le HTML légal en retirant les éléments dangereux
 * @param input HTML brut à sanitizer
 * @returns HTML sanitizé
 */
export function sanitizeLegalHtml(input: string): string {
  if (!input || typeof input !== 'string') {
    return '';
  }

  let sanitized = input;

  // Retire les scripts (toutes variantes : inline, externe, avec attributs)
  sanitized = sanitized.replace(/<script[\s\S]*?<\/script>/gi, '');

  // Retire iframes, objects, embeds (éléments qui peuvent charger du contenu externe)
  sanitized = sanitized.replace(/<\/?(iframe|object|embed)\b[\s\S]*?>/gi, '');

  // Retire les liens CSS externes (<link rel="stylesheet">)
  sanitized = sanitized.replace(
    /<link\b[^>]*rel=["']?stylesheet["']?[^>]*>/gi,
    ''
  );

  // Retire tous les attributs on* (onclick, onload, onerror, etc.)
  // Format: onXXX="..." ou onXXX='...'
  sanitized = sanitized.replace(/\son\w+="[^"]*"/gi, '');
  sanitized = sanitized.replace(/\son\w+='[^']*'/gi, '');

  // Neutralise javascript: dans href et src
  // Remplace javascript:... par # pour éviter l'exécution
  // Gère les cas avec espaces après javascript: et guillemets simples/doubles
  sanitized = sanitized.replace(
    /\b(href|src)\s*=\s*(["'])\s*javascript\s*:[\s\S]*?\2/gi,
    '$1="#"'
  );

  return sanitized;
}
