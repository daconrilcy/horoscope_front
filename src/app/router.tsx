import { Suspense, lazy } from 'react';
import { createBrowserRouter, RouterProvider, Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { AppProviders } from './AppProviders';
import { UpgradeBanner } from '@/widgets/UpgradeBanner/UpgradeBanner';
import { PublicLayout } from './layouts/PublicLayout';
import { PrivateLayout } from './layouts/PrivateLayout';
import { ScrollRestoration } from './ScrollRestoration';
import { ROUTES } from '@/shared/config/routes';

// Pages publiques
import { HomePage } from '@/pages/home';
import { LoginPage } from '@/pages/login';
import { SignupPage } from '@/pages/signup';
import { TermsOfServicePage } from '@/pages/legal/tos';
import { PrivacyPolicyPage } from '@/pages/legal/privacy';
import { NotFoundPage } from '@/pages/NotFound';

// Pages privées - lazy loading pour code splitting
const DashboardPage = lazy(() =>
  import('@/pages/app/dashboard').then((module) => ({ default: module.DashboardPage }))
);

/**
 * Loader simple pour Suspense
 */
function PageLoader(): JSX.Element {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <p>Chargement...</p>
    </div>
  );
}

/**
 * RouteGuard : protège les routes privées en vérifiant la présence du token
 * Attend l'hydratation du store avant de décider pour éviter les redirections intempestives
 */
function RouteGuard(): JSX.Element {
  const token = useAuthStore((state) => state.token);
  const hasHydrated = useAuthStore((state) => state._hasHydrated);
  const location = useLocation();

  // Attendre l'hydratation avant de décider
  if (!hasHydrated) {
    // Afficher un loader pendant l'hydratation
    return <PageLoader />;
  }

  // Rediriger si pas de token après hydratation
  if (token === null || token === '') {
    // Stocker la route d'origine pour redirectAfterLogin
    const currentPath = location.pathname + location.search;
    if (currentPath !== ROUTES.LOGIN) {
      sessionStorage.setItem('redirectAfterLogin', currentPath);
    }
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  return <Outlet />;
}

/**
 * Composant pour envelopper l'app avec providers et bannière
 */
function AppShell(): JSX.Element {
  return (
    <AppProviders>
      <UpgradeBanner />
      <ScrollRestoration />
      <Outlet />
    </AppProviders>
  );
}

/**
 * Configuration des routes avec Data Router
 */
const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      {
        element: <PublicLayout />,
        children: [
          {
            path: ROUTES.HOME,
            element: <HomePage />,
          },
          {
            path: ROUTES.LOGIN,
            element: <LoginPage />,
          },
          {
            path: ROUTES.SIGNUP,
            element: <SignupPage />,
          },
          {
            path: ROUTES.LEGAL.TOS,
            element: <TermsOfServicePage />,
          },
          {
            path: ROUTES.LEGAL.PRIVACY,
            element: <PrivacyPolicyPage />,
          },
        ],
      },
      {
        path: ROUTES.APP.BASE,
        element: <RouteGuard />,
        children: [
          {
            element: <PrivateLayout />,
            children: [
              {
                path: 'dashboard',
                element: (
                  <Suspense fallback={<PageLoader />}>
                    <DashboardPage />
                  </Suspense>
                ),
              },
              {
                path: '*',
                element: <Navigate to={ROUTES.APP.DASHBOARD} replace />,
              },
            ],
          },
        ],
      },
      {
        path: ROUTES.NOT_FOUND,
        element: <NotFoundPage />,
      },
    ],
  },
]);

/**
 * Router principal avec Data Router (createBrowserRouter + RouterProvider)
 */
export function Router(): JSX.Element {
  return <RouterProvider router={router} />;
}
