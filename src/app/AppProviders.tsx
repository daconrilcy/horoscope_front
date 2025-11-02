import React, { type ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { configureHttp } from '@/shared/api/client';
import { env } from '@/shared/config/env';
import { ErrorBoundary } from '@/shared/ui/ErrorBoundary';

interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Providers pour l'application
 * Configure le client HTTP et monte ErrorBoundary
 */
export function AppProviders({ children }: AppProvidersProps): JSX.Element {
  const navigate = useNavigate();
  const location = useLocation();

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

  return (
    <ErrorBoundary>
      {children}
    </ErrorBoundary>
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

