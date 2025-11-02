import { Link } from 'react-router-dom';
import { useTitle } from '@/shared/hooks/useTitle';
import { ROUTES } from '@/shared/config/routes';

/**
 * Page d'accueil publique
 */
export function HomePage(): JSX.Element {
  useTitle('Horoscope - Accueil');

  return (
    <div>
      <h1>Bienvenue sur Horoscope</h1>
      <p>Découvrez votre horoscope personnalisé</p>
      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
        <Link
          to={ROUTES.LOGIN}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#007bff',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
          }}
        >
          Se connecter
        </Link>
        <Link
          to={ROUTES.SIGNUP}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#28a745',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
          }}
        >
          S'inscrire
        </Link>
      </div>
    </div>
  );
}

