import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { AppProviders } from './AppProviders';
import { UpgradeBanner } from '@/widgets/UpgradeBanner/UpgradeBanner';

/**
 * RouteGuard : protège les routes privées en vérifiant la présence du token
 */
function RouteGuard({ children }: { children: React.ReactNode }): JSX.Element {
  const token = useAuthStore((state) => state.token);

  if (token === null || token === '') {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

/**
 * Placeholder pour les pages (à créer plus tard)
 */
function LoginPage(): JSX.Element {
  return (
    <div>
      <h1>Login</h1>
      <p>Page de connexion</p>
    </div>
  );
}

function SignupPage(): JSX.Element {
  return (
    <div>
      <h1>Signup</h1>
      <p>Page d'inscription</p>
    </div>
  );
}

function HomePage(): JSX.Element {
  return (
    <div>
      <h1>Horoscope</h1>
      <p>Page d'accueil</p>
    </div>
  );
}

function DashboardPage(): JSX.Element {
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Tableau de bord</p>
    </div>
  );
}

/**
 * Router principal avec React Router v6
 */
export function Router(): JSX.Element {
  return (
    <BrowserRouter>
      <AppProviders>
        <UpgradeBanner />
        <Routes>
          {/* Routes publiques */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          
          {/* Routes privées */}
          <Route
            path="/app/*"
            element={
              <RouteGuard>
                <Routes>
                  <Route path="dashboard" element={<DashboardPage />} />
                  <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
                </Routes>
              </RouteGuard>
            }
          />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppProviders>
    </BrowserRouter>
  );
}
