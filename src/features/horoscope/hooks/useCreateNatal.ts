import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  horoscopeService,
  type CreateNatalInput,
} from '@/shared/api/horoscope.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { useHoroscopeStore } from '@/stores/horoscopeStore';

/**
 * Interface du résultat du hook useCreateNatal
 */
export interface UseCreateNatalResult {
  /** Fonction pour créer un thème natal */
  createNatal: (input: CreateNatalInput) => Promise<string | undefined>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
  /** Détails d'erreur 422 par champ */
  fieldErrors: Record<string, string[]>;
}

/**
 * Hook React Query pour créer un thème natal
 * Protection double-clic intégrée
 * Gestion d'erreurs réaliste (422 avec détails, 401, 5xx, NetworkError)
 * Invalidation automatique des queries today après création
 */
export function useCreateNatal(): UseCreateNatalResult {
  const queryClient = useQueryClient();
  const addChart = useHoroscopeStore((state) => state.addChart);

  const { mutateAsync, isPending, error } = useMutation<
    { chart_id: string },
    Error,
    CreateNatalInput
  >({
    mutationFn: async (input) => {
      return await horoscopeService.createNatal(input);
    },
    onSuccess: (data, variables) => {
      // Ajouter au store
      addChart(data.chart_id, variables.name);

      // Invalider les queries today pour ce chart
      void queryClient.invalidateQueries({
        queryKey: ['horo', 'today', data.chart_id],
      });

      toast.success('Thème natal créé avec succès');
    },
    onError: (err) => {
      // Gestion erreurs
      if (err instanceof ApiError) {
        // 401 → laisse le wrapper déclencher l'unauthorized (redir login)
        // 422 → détails gérés ci-dessous
        if (err.status !== 401 && err.status !== 422) {
          toast.error(
            err.message || 'Une erreur est survenue lors de la création'
          );
        }
      } else if (err instanceof NetworkError) {
        toast.error('Erreur réseau, réessayez');
      } else {
        toast.error('Une erreur inattendue est survenue');
      }
    },
  });

  /**
   * Fonction pour créer un thème natal avec protection double-clic
   */
  const createNatal = async (
    input: CreateNatalInput
  ): Promise<string | undefined> => {
    // Protection double-clic : bloquer un second appel tant que isPending
    if (isPending) {
      return undefined;
    }

    // Les erreurs sont déjà gérées dans onError
    const result = await mutateAsync(input);
    return result.chart_id;
  };

  // Extraire les erreurs de champs depuis l'erreur
  let fieldErrors: Record<string, string[]> = {};
  if (error instanceof ApiError && error.status === 422) {
    // Les details sont déjà dans error.details
    if (
      typeof error.details === 'object' &&
      error.details !== null &&
      !Array.isArray(error.details)
    ) {
      fieldErrors = error.details as Record<string, string[]>;
    }
  }

  return {
    createNatal,
    isPending,
    error: error ?? null,
    fieldErrors,
  };
}
