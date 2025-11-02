import { Outlet, Link, useLocation } from 'react-router-dom';
import { ROUTES } from '@/shared/config/routes';
import { useAuthStore } from '@/stores/authStore';

/**
 * Layout pour les routes privées (/app/*)
 * Inclut une barre de navigation avec lien de déconnexion
 */
export function PrivateLayout(): JSX.Element {
  const location = useLocation();
  const clearToken = useAuthStore((state) => state.clearToken);
  const isDashboard = location.pathname === ROUTES.APP.DASHBOARD;

  const handleLogout = (): void => {
    clearToken();
    window.location.href = ROUTES.LOGIN;
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Navigation */}
      <nav
        style={{
          padding: '1rem',
          borderBottom: '1px solid #e0e0e0',
          backgroundColor: '#f9f9f9',
        }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <Link
            to={ROUTES.APP.DASHBOARD}
            style={{
              textDecoration: 'none',
              color: isDashboard ? '#007bff' : '#333',
              fontWeight: isDashboard ? 'bold' : 'normal',
            }}
          >
            Dashboard
          </Link>
          <div style={{ marginLeft: 'auto' }}>
            <button
              type="button"
              onClick={handleLogout}
              style={{
                padding: '0.5rem 1rem',
                cursor: 'pointer',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
              }}
            >
              Déconnexion
            </button>
          </div>
        </div>
      </nav>

      {/* Contenu */}
      <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <Outlet />
      </main>
    </div>
  );
}

