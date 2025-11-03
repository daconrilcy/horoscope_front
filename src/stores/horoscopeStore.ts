import { create } from 'zustand';
import {
  readPersistedCharts,
  writePersistedCharts,
  clearPersistedCharts,
  type ChartEntry,
} from '@/shared/auth/charts';

interface HoroscopeState {
  recentCharts: ChartEntry[];
  hasHydrated: boolean;
  hydrateFromStorage: () => void;
  addChart: (chartId: string, label?: string) => void;
  getCharts: () => ChartEntry[];
  clearCharts: () => void;
}

const MAX_CHARTS = 10;

/**
 * Store Zustand pour la gestion des charts horoscope
 * Mémoire = source de vérité, localStorage sert uniquement d'appoint pour rehydrate au boot
 * hasHydrated permet de savoir si l'hydratation depuis localStorage est terminée
 * LRU anti-doublon : si chartId existe, le remonter en tête (pas dupliquer)
 * Cap 10 FIFO : si > 10, supprimer le plus ancien
 */
export const useHoroscopeStore = create<HoroscopeState>()((set, get) => ({
  recentCharts: [],
  hasHydrated: false,

  hydrateFromStorage: (): void => {
    const charts = readPersistedCharts();
    set({ recentCharts: charts, hasHydrated: true });
  },

  addChart: (chartId: string, label?: string): void => {
    const currentCharts = get().recentCharts;
    const now = new Date().toISOString();

    // Rechercher si le chartId existe déjà
    const existingIndex = currentCharts.findIndex(
      (entry) => entry.chartId === chartId
    );

    let newCharts: ChartEntry[];

    if (existingIndex !== -1) {
      // LRU : remonter en tête l'élément existant
      const existingEntry = currentCharts[existingIndex];
      // Mettre à jour label si fourni (peut changer)
      const updatedEntry: ChartEntry = {
        ...existingEntry,
        label: label ?? existingEntry.label,
      };
      newCharts = [
        updatedEntry,
        ...currentCharts.filter((_, index) => index !== existingIndex),
      ];
    } else {
      // Ajouter en tête
      const newEntry: ChartEntry = {
        chartId,
        label,
        createdAt: now,
      };
      newCharts = [newEntry, ...currentCharts];
    }

    // FIFO : limiter à MAX_CHARTS (conserver les plus récents)
    if (newCharts.length > MAX_CHARTS) {
      newCharts = newCharts.slice(0, MAX_CHARTS);
    }

    // Persister
    writePersistedCharts(newCharts);
    set({ recentCharts: newCharts });
  },

  getCharts: (): ChartEntry[] => {
    return get().recentCharts;
  },

  clearCharts: (): void => {
    clearPersistedCharts();
    set({ recentCharts: [] });
  },
}));
