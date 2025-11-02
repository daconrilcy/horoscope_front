import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  setToken: (token: string) => void;
  getToken: () => string | null;
  clearToken: () => void;
}

/**
 * Store Zustand pour la gestion du token JWT
 * Mémoire = source de vérité, localStorage sync en arrière-plan
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,

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
    }),
    {
      name: 'auth-storage',
      // Stocke uniquement le token, pas d'autres données sensibles
      partialize: (state) => ({ token: state.token }),
    }
  )
);

