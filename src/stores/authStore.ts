import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  _hasHydrated: boolean;
  setToken: (token: string) => void;
  getToken: () => string | null;
  clearToken: () => void;
  setHasHydrated: (hasHydrated: boolean) => void;
}

/**
 * Store Zustand pour la gestion du token JWT
 * Mémoire = source de vérité, localStorage sync en arrière-plan
 * _hasHydrated permet de savoir si l'hydratation depuis localStorage est terminée
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      _hasHydrated: false,

      setToken: (token: string) => {
        set({ token });
        // Sync localStorage en arrière-plan (via persist middleware)
      },

      getToken: () => {
        return get().token;
      },

      clearToken: () => {
        set({ token: null });
        // Purge localStorage (via persist middleware)
        // Pour forcer un rechargement complet, on peut ajouter window.location.reload()
        // mais on le laisse au composant qui appelle clearToken() pour éviter de l'imposer ici
      },

      setHasHydrated: (hasHydrated: boolean) => {
        set({ _hasHydrated: hasHydrated });
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      // Stocke uniquement le token, pas d'autres données sensibles
      partialize: (state) => ({ token: state.token }),
      onRehydrateStorage: () => (state) => {
        // Appelé après l'hydratation
        state?.setHasHydrated(true);
      },
    }
  )
);

