import { useMutation } from '@tanstack/react-query';
import { horoscopeService } from '@/shared/api/horoscope.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { downloadBlob } from '../utils/downloadBlob';

/**
 * Interface du résultat du hook useDownloadPdf
 */
export interface UseDownloadPdfResult {
  /** Fonction pour télécharger le PDF */
  downloadPdf: (chartId: string) => Promise<void>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
}

/**
 * Hook React Query pour télécharger le PDF d'un thème natal
 * Protection double-clic intégrée
 * Gestion d'erreurs réaliste (404, 500, NetworkError)
 */
export function useDownloadPdf(): UseDownloadPdfResult {
  const { mutateAsync, isPending, error } = useMutation<
    { blob: Blob; filename: string },
    Error,
    string
  >({
    mutationFn: async (chartId) => {
      return await horoscopeService.getNatalPdfStream(chartId);
    },
    onSuccess: ({ blob, filename }) => {
      downloadBlob(blob, filename);
      toast.success('PDF téléchargé avec succès');
    },
    onError: (err) => {
      // Gestion erreurs
      if (err instanceof ApiError) {
        if (err.status === 404) {
          toast.error('Thème natal introuvable');
        } else {
          toast.error('Erreur lors du téléchargement du PDF');
        }
      } else if (err instanceof NetworkError) {
        toast.error('Erreur réseau, réessayez');
      } else {
        toast.error('Une erreur inattendue est survenue');
      }
    },
  });

  /**
   * Fonction pour télécharger le PDF avec protection double-clic
   */
  const downloadPdf = async (chartId: string): Promise<void> => {
    // Protection double-clic : bloquer un second appel tant que isPending
    if (isPending) {
      return;
    }

    // Les erreurs sont déjà gérées dans onError
    await mutateAsync(chartId);
  };

  return {
    downloadPdf,
    isPending,
    error: error ?? null,
  };
}
