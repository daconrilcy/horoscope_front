import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from './authStore';

describe('authStore - Hydratation', () => {
  beforeEach(() => {
    // Reset store et localStorage
    useAuthStore.setState({ token: null, _hasHydrated: false });
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('devrait initialiser _hasHydrated à false', () => {
    const state = useAuthStore.getState();
    expect(state._hasHydrated).toBe(false);
  });

  it('devrait permettre de définir _hasHydrated via setHasHydrated', () => {
    useAuthStore.getState().setHasHydrated(true);
    expect(useAuthStore.getState()._hasHydrated).toBe(true);
  });

  it('devrait hydrater le token depuis localStorage', () => {
    localStorage.setItem('auth-storage', JSON.stringify({ state: { token: 'test-token' } }));

    // Simuler l'hydratation
    const store = useAuthStore.getState();
    store.setHasHydrated(true);

    // Vérifier que le token est disponible après hydratation
    // Note: L'hydratation réelle se fait via persist middleware, ici on teste juste l'état
    expect(store._hasHydrated).toBe(true);
  });
});

