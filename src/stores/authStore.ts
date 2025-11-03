import { create } from 'zustand';
import type { QueryClient } from '@tanstack/react-query';
import {
  readPersistedToken,
  writePersistedToken,
  clearPersistedToken,
} from '@/shared/auth/token';

export type UserRef = { id: string; email: string };

interface AuthState {
  token: string | null;
  userRef?: UserRef;
  hasHydrated: boolean;
  redirectAfterLogin?: string;
  hydrateFromStorage: () => void;
  login: (token: string, userRef?: UserRef) => void;
  logout: (queryClient?: QueryClient) => void;
  setRedirectAfterLogin: (path?: string) => void;
  getToken: () => string | null;
}

/**
 * Store Zustand pour la gestion du token JWT
 * Mémoire = source de vérité, localStorage sert uniquement d'appoint pour rehydrate au boot
 * hasHydrated permet de savoir si l'hydratation depuis localStorage est terminée
 */
export const useAuthStore = create<AuthState>()((set, get) => ({
  token: null,
  userRef: undefined,
  hasHydrated: false,
  redirectAfterLogin: undefined,

  hydrateFromStorage: (): void => {
    const token = readPersistedToken();
    if (token != null && token !== '') {
      set({ token, hasHydrated: true });
    } else {
      set({ hasHydrated: true });
    }
  },

  login: (token: string, userRef?: UserRef): void => {
    writePersistedToken(token);
    set({ token, userRef });
  },

  logout: (queryClient?: QueryClient): void => {
    clearPersistedToken();
    set({ token: null, userRef: undefined, redirectAfterLogin: undefined });
    // Purge React Query cache si queryClient fourni
    if (queryClient != null) {
      queryClient.clear();
    }
  },

  setRedirectAfterLogin: (path?: string): void => {
    set({ redirectAfterLogin: path });
  },

  getToken: (): string | null => {
    return get().token;
  },
}));
