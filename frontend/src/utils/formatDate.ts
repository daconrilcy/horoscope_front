import type { AstrologyLang } from "../i18n/astrology"

/**
 * Formate une date ISO en chaîne lisible (date uniquement).
 * Utilise le paramètre lang pour l'affichage localisé (contexte astrologique).
 * @param dateString - Chaîne de date ISO (ex: "2024-02-22" ou "2024-02-22T10:00:00Z")
 * @param lang - Langue cible pour le formatage (défaut: "fr")
 * @param fallback - Valeur retournée si la date est invalide (défaut: "—")
 * @returns Date formatée (ex: "22/02/2024") ou fallback si invalide
 * @see formatDateTime pour le formatage date+heure (utilise locale navigateur)
 */
export function formatDate(
  dateString: string,
  lang: AstrologyLang = "fr",
  fallback = "—"
): string {
  try {
    const date = new Date(dateString)
    if (Number.isNaN(date.getTime())) {
      return fallback
    }
    return date.toLocaleDateString(lang)
  } catch {
    return fallback
  }
}

/**
 * Formate une date ISO en chaîne lisible avec date et heure.
 * Utilise le locale du navigateur (undefined) pour un affichage localisé automatique.
 * @param value - Chaîne de date ISO (ex: "2024-02-22T10:00:00Z")
 * @param fallback - Valeur retournée si la date est invalide (défaut: "—")
 * @returns Date formatée (ex: "22 févr. 2024, 11:00") ou fallback si invalide
 * @see formatDate pour le formatage date uniquement avec paramètre lang explicite
 */
export function formatDateTime(value: string, fallback = "—"): string {
  try {
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) {
      return fallback
    }
    return date.toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    })
  } catch {
    return fallback
  }
}
