import React, { type ReactNode, useMemo, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster, toast as sonnerToast } from 'sonner';
import { configureHttp } from '@/shared/api/client';
import { env } from '@/shared/config/env';
import { ErrorBoundary } from '@/shared/ui/ErrorBoundary';
import { NetworkError } from '@/shared/api/errors';
import { useAuthStore } from '@/stores/authStore';
import { eventBus } from '@/shared/api/eventBus';

interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Fonction helper pour détecter si une erreur est une NetworkError
 */
function isNetworkError(error: unknown): boolean {
  return error instanceof NetworkError;
}

/**
 * QueryClient avec configuration "safe by default"
 * - Retry uniquement sur NetworkError (max 2 fois)
 * - StaleTime 30s pour limiter le flicker
 */
function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: (failureCount, error) => {
          // Retry uniquement sur NetworkError, max 1 fois (background errors)
          return isNetworkError(error) && failureCount < 1;
        },
        staleTime: 30_000, // 30 secondes
        refetchOnWindowFocus: false, // Évite de spammer l'API
      },
      mutations: {
        retry: false, // Pas de retry par défaut sur les mutations
      },
    },
  });
}

/**
 * Helpers pour unifier les usages de toast
 */
export const toast = {
  success: (message: string) => {
    sonnerToast.success(message);
  },
  error: (message: string) => {
    sonnerToast.error(message);
  },
  info: (message: string) => {
    sonnerToast.info(message);
  },
  warning: (message: string) => {
    sonnerToast.warning(message);
  },
};

/**
 * Providers pour l'application
 * Configure le client HTTP, React Query, Toaster et ErrorBoundary
 */
export function AppProviders({ children }: AppProvidersProps): JSX.Element {
  const navigate = useNavigate();
  const location = useLocation();
  const hydrateFromStorage = useAuthStore((state) => state.hydrateFromStorage);

  // Créer QueryClient une seule fois (singleton)
  const queryClient = useMemo(() => createQueryClient(), []);

  // Hydratation unique au boot (une seule fois)
  React.useEffect(() => {
    hydrateFromStorage();
  }, [hydrateFromStorage]);

  // Configuration du client HTTP avec callback onUnauthorized
  React.useEffect(() => {
    const handleUnauthorized = (): void => {
      // Ne pas rediriger si déjà sur /login
      if (location.pathname === '/login') {
        return;
      }

      // Stocker la route d'origine pour redirectAfterLogin
      const currentPath = location.pathname + location.search;
      if (currentPath !== '/login') {
        sessionStorage.setItem('redirectAfterLogin', currentPath);
        // Rediriger vers /login
        void navigate('/login', { replace: true });
      }
    };

    configureHttp({
      baseURL: env.VITE_API_BASE_URL,
      onUnauthorized: handleUnauthorized,
    });
  }, [navigate, location]);

  // Écouter auth:unauthorized pour toast et post_login_redirect
  useEffect(() => {
    const unsubscribe = eventBus.on('auth:unauthorized', () => {
      // Ne pas toaster si déjà sur /login
      if (location.pathname !== '/login') {
        // Stocker post_login_redirect avant redirection
        const currentPath = location.pathname + location.search;
        sessionStorage.setItem('post_login_redirect', currentPath);
        // Afficher toast unique
        toast.warning('Session expirée');
        // Rediriger vers /login
        void navigate('/login', { replace: true });
      }
    });

    return unsubscribe;
  }, [navigate, location]);

  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary resetKeys={[location.pathname]}>
        {children}
        <Toaster richColors position="top-right" />
      </ErrorBoundary>
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}

/**
 * Hook pour récupérer la route de redirection après login
 */
export function useRedirectAfterLogin(): string | null {
  const redirectPath = sessionStorage.getItem('redirectAfterLogin') ?? null;
  React.useEffect(() => {
    if (redirectPath !== null && redirectPath !== '') {
      sessionStorage.removeItem('redirectAfterLogin');
    }
  }, [redirectPath]);
  return redirectPath;
}
