import { Suspense, lazy } from 'react';
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
  Outlet,
  useLocation,
} from 'react-router-dom';
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
import { ResetRequestPage } from '@/pages/reset/request';
import { ResetConfirmPage } from '@/pages/reset/confirm';
import { TermsOfServicePage } from '@/pages/legal/tos';
import { PrivacyPolicyPage } from '@/pages/legal/privacy';
import { BillingSuccessPage } from '@/pages/billing/success';
import { BillingCancelPage } from '@/pages/billing/cancel';
import { NotFoundPage } from '@/pages/NotFound';

// Pages privées - lazy loading pour code splitting
const DashboardPage = lazy(() =>
  import('@/pages/app/dashboard').then((module) => ({
    default: module.DashboardPage,
  }))
);
const HoroscopePage = lazy(() =>
  import('@/pages/app/horoscope').then((module) => ({
    default: module.HoroscopePage,
  }))
);
const ChatPage = lazy(() =>
  import('@/pages/app/chat').then((module) => ({
    default: module.ChatPage,
  }))
);
const AccountPage = lazy(() =>
  import('@/pages/app/account').then((module) => ({
    default: module.AccountPage,
  }))
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
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
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
            path: ROUTES.RESET.REQUEST,
            element: <ResetRequestPage />,
          },
          {
            path: ROUTES.RESET.CONFIRM,
            element: <ResetConfirmPage />,
          },
          {
            path: ROUTES.LEGAL.TOS,
            element: <TermsOfServicePage />,
          },
          {
            path: ROUTES.LEGAL.PRIVACY,
            element: <PrivacyPolicyPage />,
          },
          {
            path: ROUTES.BILLING.SUCCESS,
            element: <BillingSuccessPage />,
          },
          {
            path: ROUTES.BILLING.CANCEL,
            element: <BillingCancelPage />,
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
                path: 'horoscope',
                element: (
                  <Suspense fallback={<PageLoader />}>
                    <HoroscopePage />
                  </Suspense>
                ),
              },
              {
                path: 'chat',
                element: (
                  <Suspense fallback={<PageLoader />}>
                    <ChatPage />
                  </Suspense>
                ),
              },
              {
                path: 'account',
                element: (
                  <Suspense fallback={<PageLoader />}>
                    <AccountPage />
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
