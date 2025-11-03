import { useMutation } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { accountService } from '@/shared/api/account.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { downloadBlob } from '@/features/horoscope/utils/downloadBlob';

/**
 * Interface du résultat du hook useExportZip
 */
export interface UseExportZipResult {
  /** Fonction pour exporter les données */
  exportZip: () => Promise<void>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
}

/**
 * Hook React Query pour exporter les données utilisateur au format ZIP
 * Protection double-clic intégrée (bloque si isPending)
 * Gestion d'erreurs réaliste (401, 500, NetworkError)
 * Support AbortController pour annulation
 */
export function useExportZip(): UseExportZipResult {
  const abortControllerRef = useRef<AbortController | null>(null);

  // Nettoyer l'AbortController au démontage
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const { mutateAsync, isPending, error } = useMutation<
    { blob: Blob; filename: string },
    Error
  >({
    mutationFn: async () => {
      // Créer un nouveau AbortController pour cette mutation
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        return await accountService.exportZip(controller.signal);
      } finally {
        // Nettoyer la référence après la mutation
        abortControllerRef.current = null;
      }
    },
    onSuccess: ({ blob, filename }) => {
      // Télécharger le blob (révoque automatiquement l'URL)
      downloadBlob(blob, filename);
      toast.success('Données exportées avec succès');
    },
    onError: (err) => {
      // Gestion erreurs réaliste
      if (err instanceof ApiError) {
        // 401 → laisse le wrapper déclencher l'unauthorized (redir login via callback global)
        if (err.status === 401) {
          // Pas de toast, le wrapper gère
          return;
        }

        // 500 → toast spécifique
        if (err.status === 500) {
          toast.error('Erreur serveur lors de l\'export');
          return;
        }

        // Autres erreurs API
        const message =
          err.message || 'Une erreur est survenue lors de l\'export.';
        toast.error(message);
      } else if (err instanceof NetworkError) {
        // NetworkError/timeout/offline → toast clair
        const message =
          err.reason === 'timeout' || err.reason === 'offline'
            ? 'Export indisponible, réessayez.'
            : 'Erreur réseau lors de l\'export.';
        toast.error(message);
      } else {
        // Erreur inconnue
        toast.error('Une erreur inattendue est survenue.');
      }

      // Journalisation légère : log request_id si présent (utile en support)
      if (err instanceof ApiError && err.requestId !== undefined) {
        console.error('[ExportZip] request_id:', err.requestId);
      }
    },
  });

  /**
   * Fonction pour exporter avec protection double-clic
   */
  const exportZip = async (): Promise<void> => {
    // Protection double-clic : bloquer un second appel tant que isPending est true
    if (isPending) {
      return;
    }

    // Les erreurs sont déjà gérées dans onError
    await mutateAsync();
  };

  return {
    exportZip,
    isPending,
    error: error ?? null,
  };
}
