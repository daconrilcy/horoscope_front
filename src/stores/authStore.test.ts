import { describe, it, expect, beforeEach, vi } from 'vitest';
import { QueryClient } from '@tanstack/react-query';
import { useAuthStore } from './authStore';
import * as tokenHelpers from '@/shared/auth/token';

describe('authStore - Hydratation', () => {
  beforeEach(() => {
    // Reset store et localStorage
    useAuthStore.setState({ token: null, hasHydrated: false, userRef: undefined, redirectAfterLogin: undefined });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(tokenHelpers, 'readPersistedToken').mockReturnValue(null);
  });

  it('devrait initialiser hasHydrated à false', () => {
    const state = useAuthStore.getState();
    expect(state.hasHydrated).toBe(false);
  });

  it('devrait hydrater depuis localStorage via hydrateFromStorage', () => {
    vi.spyOn(tokenHelpers, 'readPersistedToken').mockReturnValue('test-token');
    
    useAuthStore.getState().hydrateFromStorage();
    
    const state = useAuthStore.getState();
    expect(state.token).toBe('test-token');
    expect(state.hasHydrated).toBe(true);
  });

  it('devrait mettre hasHydrated à true même si pas de token', () => {
    vi.spyOn(tokenHelpers, 'readPersistedToken').mockReturnValue(null);
    
    useAuthStore.getState().hydrateFromStorage();
    
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.hasHydrated).toBe(true);
  });
});

describe('authStore - Login', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, hasHydrated: false, userRef: undefined });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(tokenHelpers, 'writePersistedToken').mockImplementation(() => {});
  });

  it('devrait stocker token et userRef via login', () => {
    const token = 'test-token';
    const userRef = { id: '123', email: 'test@example.com' };
    
    useAuthStore.getState().login(token, userRef);
    
    const state = useAuthStore.getState();
    expect(state.token).toBe(token);
    expect(state.userRef).toEqual(userRef);
    expect(tokenHelpers.writePersistedToken).toHaveBeenCalledWith(token);
  });

  it('devrait stocker token sans userRef via login', () => {
    const token = 'test-token';
    
    useAuthStore.getState().login(token);
    
    const state = useAuthStore.getState();
    expect(state.token).toBe(token);
    expect(state.userRef).toBeUndefined();
  });
});

describe('authStore - Logout', () => {
  beforeEach(() => {
    useAuthStore.setState({ 
      token: 'test-token', 
      hasHydrated: true, 
      userRef: { id: '123', email: 'test@example.com' },
      redirectAfterLogin: '/app/dashboard',
    });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(tokenHelpers, 'clearPersistedToken').mockImplementation(() => {});
  });

  it('devrait purger token, userRef et redirectAfterLogin via logout', () => {
    const queryClient = new QueryClient();
    const clearSpy = vi.spyOn(queryClient, 'clear');
    
    useAuthStore.getState().logout(queryClient);
    
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.userRef).toBeUndefined();
    expect(state.redirectAfterLogin).toBeUndefined();
    expect(tokenHelpers.clearPersistedToken).toHaveBeenCalled();
    expect(clearSpy).toHaveBeenCalled();
  });

  it('devrait purger sans queryClient si non fourni', () => {
    useAuthStore.getState().logout();
    
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.userRef).toBeUndefined();
    expect(tokenHelpers.clearPersistedToken).toHaveBeenCalled();
  });
});

describe('authStore - RedirectAfterLogin', () => {
  beforeEach(() => {
    useAuthStore.setState({ redirectAfterLogin: undefined });
    vi.clearAllMocks();
  });

  it('devrait stocker redirectAfterLogin via setRedirectAfterLogin', () => {
    const path = '/app/dashboard';
    
    useAuthStore.getState().setRedirectAfterLogin(path);
    
    const state = useAuthStore.getState();
    expect(state.redirectAfterLogin).toBe(path);
  });

  it('devrait effacer redirectAfterLogin si path undefined', () => {
    useAuthStore.setState({ redirectAfterLogin: '/app/dashboard' });
    
    useAuthStore.getState().setRedirectAfterLogin(undefined);
    
    const state = useAuthStore.getState();
    expect(state.redirectAfterLogin).toBeUndefined();
  });
});

