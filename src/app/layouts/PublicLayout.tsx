import { Outlet, Link, useLocation } from 'react-router-dom';
import { ROUTES } from '@/shared/config/routes';

/**
 * Layout pour les routes publiques (/, /login, /signup, /legal/*)
 * Inclut une barre de navigation simple
 */
export function PublicLayout(): JSX.Element {
  const location = useLocation();
  const isHome = location.pathname === ROUTES.HOME;
  const isLogin = location.pathname === ROUTES.LOGIN;
  const isSignup = location.pathname === ROUTES.SIGNUP;

  return (
    <div
      style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}
    >
      {/* Navigation */}
      <nav
        style={{
          padding: '1rem',
          borderBottom: '1px solid #e0e0e0',
          backgroundColor: '#f9f9f9',
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            display: 'flex',
            gap: '1rem',
          }}
        >
          <Link
            to={ROUTES.HOME}
            style={{
              textDecoration: 'none',
              color: isHome ? '#007bff' : '#333',
              fontWeight: isHome ? 'bold' : 'normal',
            }}
          >
            Accueil
          </Link>
          {!isLogin && (
            <Link
              to={ROUTES.LOGIN}
              style={{
                textDecoration: 'none',
                color: isLogin ? '#007bff' : '#333',
                fontWeight: isLogin ? 'bold' : 'normal',
              }}
            >
              Connexion
            </Link>
          )}
          {!isSignup && (
            <Link
              to={ROUTES.SIGNUP}
              style={{
                textDecoration: 'none',
                color: isSignup ? '#007bff' : '#333',
                fontWeight: isSignup ? 'bold' : 'normal',
              }}
            >
              Inscription
            </Link>
          )}
        </div>
      </nav>

      {/* Contenu */}
      <main
        style={{
          flex: 1,
          padding: '2rem',
          maxWidth: '1200px',
          margin: '0 auto',
          width: '100%',
        }}
      >
        <Outlet />
      </main>
    </div>
  );
}
