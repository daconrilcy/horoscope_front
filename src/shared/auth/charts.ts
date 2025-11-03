/**
 * Helpers pour la gestion des charts récents dans localStorage
 * Source de vérité = mémoire (Zustand), localStorage sert uniquement d'appoint pour rehydrate au boot
 */

const STORAGE_KEY = 'HORO_RECENT_CHARTS';

export interface ChartEntry {
  chartId: string;
  label?: string;
  createdAt: string; // ISO datetime
}

/**
 * Lit les charts depuis localStorage
 * @returns Array de ChartEntry ou tableau vide si absent/invalide
 */
export function readPersistedCharts(): ChartEntry[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored == null || stored === '') {
      return [];
    }

    // Essayer de parser comme JSON
    try {
      const parsed: unknown = JSON.parse(stored);
      // Vérifier que c'est un array
      if (Array.isArray(parsed)) {
        // Vérifier que chaque élément a la structure correcte
        const validEntries: ChartEntry[] = [];
        for (const entry of parsed) {
          if (typeof entry === 'object' && entry !== null) {
            const typedEntry = entry as Record<string, unknown>;
            if (
              'chartId' in typedEntry &&
              typeof typedEntry.chartId === 'string' &&
              'createdAt' in typedEntry &&
              typeof typedEntry.createdAt === 'string'
            ) {
              validEntries.push({
                chartId: typedEntry.chartId,
                label:
                  'label' in typedEntry && typeof typedEntry.label === 'string'
                    ? typedEntry.label
                    : undefined,
                createdAt: typedEntry.createdAt,
              });
            }
          }
        }
        return validEntries;
      }
      // Sinon, retourner tableau vide
      return [];
    } catch {
      // Si le parsing JSON échoue, retourner tableau vide
      return [];
    }
  } catch {
    // Fallback en cas d'erreur (localStorage bloqué, etc.)
    return [];
  }
}

/**
 * Stocke les charts dans localStorage
 * @param charts Array de ChartEntry à persister
 */
export function writePersistedCharts(charts: ChartEntry[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(charts));
  } catch {
    // Ignorer les erreurs (localStorage plein, etc.)
  }
}

/**
 * Purge les charts de localStorage
 */
export function clearPersistedCharts(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignorer les erreurs
  }
}
