import { Link } from 'react-router-dom';
import { useTitle } from '@/shared/hooks/useTitle';
import { ROUTES } from '@/shared/config/routes';

/**
 * Page 404 - Non trouvée
 */
export function NotFoundPage(): JSX.Element {
  useTitle('Horoscope - Page non trouvée');

  return (
    <div style={{ textAlign: 'center', padding: '3rem' }}>
      <h1>404</h1>
      <h2>Page non trouvée</h2>
      <p>La page que vous recherchez n'existe pas ou a été déplacée.</p>
      <div style={{ marginTop: '2rem' }}>
        <Link
          to={ROUTES.HOME}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#007bff',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
          }}
        >
          Retour à l'accueil
        </Link>
      </div>
    </div>
  );
}

