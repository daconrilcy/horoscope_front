import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useHoroscopeStore } from './horoscopeStore';
import * as chartsHelpers from '@/shared/auth/charts';

describe('horoscopeStore - Hydratation', () => {
  beforeEach(() => {
    // Reset store et localStorage
    useHoroscopeStore.setState({
      recentCharts: [],
      hasHydrated: false,
    });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(chartsHelpers, 'readPersistedCharts').mockReturnValue([]);
  });

  it('devrait initialiser hasHydrated à false', () => {
    const state = useHoroscopeStore.getState();
    expect(state.hasHydrated).toBe(false);
  });

  it('devrait hydrater depuis localStorage via hydrateFromStorage', () => {
    const mockCharts = [
      {
        chartId: 'chart-1',
        label: 'Test 1',
        createdAt: '2024-01-01T12:00:00Z',
      },
    ];
    vi.spyOn(chartsHelpers, 'readPersistedCharts').mockReturnValue(mockCharts);

    useHoroscopeStore.getState().hydrateFromStorage();

    const state = useHoroscopeStore.getState();
    expect(state.recentCharts).toEqual(mockCharts);
    expect(state.hasHydrated).toBe(true);
  });

  it('devrait mettre hasHydrated à true même si pas de charts', () => {
    vi.spyOn(chartsHelpers, 'readPersistedCharts').mockReturnValue([]);

    useHoroscopeStore.getState().hydrateFromStorage();

    const state = useHoroscopeStore.getState();
    expect(state.recentCharts).toEqual([]);
    expect(state.hasHydrated).toBe(true);
  });
});

describe('horoscopeStore - AddChart', () => {
  beforeEach(() => {
    useHoroscopeStore.setState({
      recentCharts: [],
      hasHydrated: true,
    });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(chartsHelpers, 'writePersistedCharts').mockImplementation(
      () => {}
    );
  });

  it('devrait ajouter un chart en tête', () => {
    const chartId = 'chart-1';
    const label = 'Test Chart';

    useHoroscopeStore.getState().addChart(chartId, label);

    const state = useHoroscopeStore.getState();
    expect(state.recentCharts).toHaveLength(1);
    expect(state.recentCharts[0].chartId).toBe(chartId);
    expect(state.recentCharts[0].label).toBe(label);
    expect(chartsHelpers.writePersistedCharts).toHaveBeenCalled();
  });

  it('devrait mettre à jour label si chart existe déjà (LRU anti-doublon)', () => {
    const chartId = 'chart-1';

    // Ajouter une première fois
    useHoroscopeStore.getState().addChart(chartId, 'Label 1');
    const state1 = useHoroscopeStore.getState();
    expect(state1.recentCharts).toHaveLength(1);

    // Ajouter une deuxième fois avec label différent
    useHoroscopeStore.getState().addChart(chartId, 'Label 2');
    const state2 = useHoroscopeStore.getState();

    // Doit toujours avoir 1 chart, mais avec le nouveau label
    expect(state2.recentCharts).toHaveLength(1);
    expect(state2.recentCharts[0].chartId).toBe(chartId);
    expect(state2.recentCharts[0].label).toBe('Label 2');
  });

  it('devrait remonter en tête si chart existe déjà (LRU)', () => {
    // Ajouter 3 charts
    useHoroscopeStore.getState().addChart('chart-1', 'Chart 1');
    useHoroscopeStore.getState().addChart('chart-2', 'Chart 2');
    useHoroscopeStore.getState().addChart('chart-3', 'Chart 3');

    const state1 = useHoroscopeStore.getState();
    expect(state1.recentCharts).toHaveLength(3);
    expect(state1.recentCharts[0].chartId).toBe('chart-3');

    // Rajouter chart-1, il doit remonter en tête
    useHoroscopeStore.getState().addChart('chart-1', 'Chart 1');
    const state2 = useHoroscopeStore.getState();

    expect(state2.recentCharts).toHaveLength(3);
    expect(state2.recentCharts[0].chartId).toBe('chart-1');
    expect(state2.recentCharts[1].chartId).toBe('chart-3');
    expect(state2.recentCharts[2].chartId).toBe('chart-2');
  });

  it('devrait limiter à 10 charts et supprimer le plus ancien (FIFO)', () => {
    // Ajouter 11 charts
    for (let i = 1; i <= 11; i++) {
      useHoroscopeStore.getState().addChart(`chart-${i}`, `Chart ${i}`);
    }

    const state = useHoroscopeStore.getState();
    expect(state.recentCharts).toHaveLength(10);
    expect(state.recentCharts[0].chartId).toBe('chart-11');
    expect(state.recentCharts[9].chartId).toBe('chart-2');
    // chart-1 doit être supprimé (le plus ancien)
    expect(state.recentCharts.some((c) => c.chartId === 'chart-1')).toBe(false);
  });

  it('devrait gérer chartId sans label', () => {
    const chartId = 'chart-1';

    useHoroscopeStore.getState().addChart(chartId);

    const state = useHoroscopeStore.getState();
    expect(state.recentCharts).toHaveLength(1);
    expect(state.recentCharts[0].chartId).toBe(chartId);
    expect(state.recentCharts[0].label).toBeUndefined();
  });
});

describe('horoscopeStore - GetCharts', () => {
  beforeEach(() => {
    useHoroscopeStore.setState({
      recentCharts: [],
      hasHydrated: true,
    });
    vi.clearAllMocks();
  });

  it('devrait retourner les charts', () => {
    const charts = [
      {
        chartId: 'chart-1',
        label: 'Chart 1',
        createdAt: '2024-01-01T12:00:00Z',
      },
      {
        chartId: 'chart-2',
        createdAt: '2024-01-02T12:00:00Z',
      },
    ];

    useHoroscopeStore.setState({ recentCharts: charts });

    const result = useHoroscopeStore.getState().getCharts();
    expect(result).toEqual(charts);
  });
});

describe('horoscopeStore - ClearCharts', () => {
  beforeEach(() => {
    useHoroscopeStore.setState({
      recentCharts: [
        {
          chartId: 'chart-1',
          label: 'Chart 1',
          createdAt: '2024-01-01T12:00:00Z',
        },
      ],
      hasHydrated: true,
    });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(chartsHelpers, 'clearPersistedCharts').mockImplementation(
      () => {}
    );
  });

  it('devrait vider les charts', () => {
    useHoroscopeStore.getState().clearCharts();

    const state = useHoroscopeStore.getState();
    expect(state.recentCharts).toEqual([]);
    expect(chartsHelpers.clearPersistedCharts).toHaveBeenCalled();
  });
});
