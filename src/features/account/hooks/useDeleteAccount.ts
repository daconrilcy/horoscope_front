import { useMutation, useQueryClient, type QueryClient } from '@tanstack/react-query';
import { accountService } from '@/shared/api/account.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { useAuthStore } from '@/stores/authStore';
import { useChatStore } from '@/stores/chatStore';
import { useHoroscopeStore } from '@/stores/horoscopeStore';
import { usePaywallStore } from '@/stores/paywallStore';
import { clearChatHistory } from '@/shared/auth/chatHistory';
import { clearPersistedCharts } from '@/shared/auth/charts';
import { clearPersistedToken } from '@/shared/auth/token';

/**
 * Interface du résultat du hook useDeleteAccount
 */
export interface UseDeleteAccountResult {
  /** Fonction pour supprimer le compte */
  deleteAccount: () => Promise<void>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
}

/**
 * Logout "dur" : purge complète des stores, localStorage et caches
 */
function performHardLogout(queryClient: QueryClient): void {
  try {
    // Logout via authStore (purge token + userRef)
    const logout = useAuthStore.getState().logout;
    logout(queryClient);

    // Purge React Query cache
    queryClient.clear();

    // Purge stores Zustand
    const chatStore = useChatStore.getState();
    // Note: clearMessages() existe mais ne purge que pour un chartId
    // On purge plutôt via localStorage directement
    chatStore.byChart = {};

    const horoscopeStore = useHoroscopeStore.getState();
    horoscopeStore.clearCharts();

    const paywallStore = usePaywallStore.getState();
    paywallStore.hidePaywall();

    // Purge localStorage clés projet
    clearChatHistory();
    clearPersistedCharts();
    clearPersistedToken();
  } catch (error) {
    // Log l'erreur mais continue la purge
    console.error('[DeleteAccount] Erreur lors de la purge:', error);
  }
}

/**
 * Hook React Query pour supprimer le compte utilisateur
 * Protection double-clic intégrée (bloque si isPending)
 * Gestion d'erreurs réaliste (401, 409, 500, NetworkError)
 * Logout "dur" avec purge complète après succès
 */
export function useDeleteAccount(): UseDeleteAccountResult {
  const queryClient = useQueryClient();

  const { mutateAsync, isPending, error } = useMutation<void, Error>({
    mutationFn: async () => {
      return await accountService.deleteAccount();
    },
    onSuccess: () => {
      try {
        // Logout "dur" : purge complète
        performHardLogout(queryClient);

        // Toast de succès
        toast.success('Compte supprimé avec succès');

        // Redirection vers / après purge (garantie même si purge échoue partiellement)
        // Utiliser window.location.assign pour forcer un reload complet
        window.location.assign('/');
      } catch (error) {
        // Si la purge échoue partiellement, forcer quand même la redirection
        console.error('[DeleteAccount] Erreur lors du logout dur:', error);
        window.location.assign('/');
      }
    },
    onError: (err) => {
      // Gestion erreurs réaliste
      if (err instanceof ApiError) {
        // 401 → laisse le wrapper déclencher l'unauthorized (redir login via callback global)
        if (err.status === 401) {
          // Pas de toast, le wrapper gère
          return;
        }

        // 409 → toast métier spécifique (pas de logout)
        if (err.status === 409) {
          const message =
            err.message ||
            'Suppression impossible pour le moment (opérations en cours)';
          toast.error(message);
          return;
        }

        // 500 → toast spécifique
        if (err.status === 500) {
          toast.error('Erreur serveur lors de la suppression');
          return;
        }

        // Autres erreurs API
        const message =
          err.message || 'Une erreur est survenue lors de la suppression.';
        toast.error(message);
      } else if (err instanceof NetworkError) {
        // NetworkError/timeout/offline → toast clair
        const message =
          err.reason === 'timeout' || err.reason === 'offline'
            ? 'Service indisponible, réessayez.'
            : 'Erreur réseau lors de la suppression.';
        toast.error(message);
      } else {
        // Erreur inconnue
        toast.error('Une erreur inattendue est survenue.');
      }

      // Journalisation légère : log request_id si présent (utile en support)
      if (err instanceof ApiError && err.requestId !== undefined) {
        console.error('[DeleteAccount] request_id:', err.requestId);
      }
    },
  });

  /**
   * Fonction pour supprimer avec protection double-clic
   */
  const deleteAccount = async (): Promise<void> => {
    // Protection double-clic : bloquer un second appel tant que isPending est true
    if (isPending) {
      return;
    }

    // Les erreurs sont déjà gérées dans onError
    await mutateAsync();
  };

  return {
    deleteAccount,
    isPending,
    error: error ?? null,
  };
}
