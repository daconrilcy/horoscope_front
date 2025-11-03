import { useQuery } from '@tanstack/react-query';
import { legalService, type LegalContent } from '@/shared/api/legal.service';
import { NetworkError } from '@/shared/api/errors';

/**
 * Interface du résultat du hook usePrivacy
 */
export interface UsePrivacyResult {
  /** HTML sanitizé */
  html: string | undefined;
  /** Métadonnées (ETag, Last-Modified, Version) */
  meta: {
    etag?: string;
    lastModified?: string;
    version?: string;
  };
  /** Indique si la query est en cours */
  isLoading: boolean;
  /** Indique s'il y a une erreur */
  isError: boolean;
  /** Erreur de la query */
  error: Error | null;
  /** Fonction pour refetch manuel */
  refetch: () => void;
}

/**
 * Hook React Query pour récupérer la Politique de confidentialité
 * staleTime: 24h (1 jour)
 * gcTime: 7j (1 semaine)
 * retry: 1 uniquement sur NetworkError (pas sur 4xx)
 */
export function usePrivacy(): UsePrivacyResult {
  const { data, isLoading, isError, error, refetch } = useQuery<
    LegalContent,
    Error
  >({
    queryKey: ['legal', 'privacy'],
    queryFn: async () => {
      // Pour l'instant, pas de gestion ETag conditionnel (complexe à gérer)
      // On récupère toujours le contenu
      // TODO: Ajouter support If-None-Match/If-Modified-Since si nécessaire
      return await legalService.getPrivacy();
    },
    staleTime: 24 * 60 * 60 * 1000, // 1 jour
    gcTime: 7 * 24 * 60 * 60 * 1000, // 1 semaine (ancien cacheTime)
    retry: (failureCount, error) => {
      // Retry 1 uniquement sur NetworkError (pas sur ApiError 4xx/5xx)
      if (error instanceof NetworkError) {
        return failureCount < 1;
      }
      return false;
    },
    refetchOnWindowFocus: false, // Évite de spammer l'endpoint
  });

  const safeRefetch = (): void => {
    void refetch();
  };

  return {
    html: data?.html,
    meta: {
      etag: data?.etag,
      lastModified: data?.lastModified,
      version: data?.version,
    },
    isLoading,
    isError,
    error: error ?? null,
    refetch: safeRefetch,
  };
}
