import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTitle } from '@/shared/hooks/useTitle';
import { useAuthStore } from '@/stores/authStore';
import { ROUTES } from '@/shared/config/routes';

/**
 * Page d'accueil publique
 * Redirige automatiquement vers le dashboard si l'utilisateur est authentifié
 */
export function HomePage(): JSX.Element {
  useTitle('Accueil');
  const navigate = useNavigate();
  const token = useAuthStore((state) => state.token);
  const hasHydrated = useAuthStore((state) => state.hasHydrated);

  // Redirection automatique si authentifié (après hydratation pour éviter le flicker)
  useEffect(() => {
    if (hasHydrated && token !== null && token !== '') {
      void navigate(ROUTES.APP.DASHBOARD, { replace: true });
    }
  }, [hasHydrated, token, navigate]);

  // Si en cours d'hydratation ou déjà authentifié, ne rien afficher (évite le flicker)
  if (!hasHydrated || (token !== null && token !== '')) {
    return (
      <div
        aria-busy="true"
        aria-live="polite"
        style={{ padding: '2rem', textAlign: 'center' }}
      />
    );
  }

  return (
    <main>
      <h1>Horoscope & Conseils Personnalisés</h1>
      <p>
        Découvrez votre horoscope personnalisé et recevez des conseils adaptés à
        votre profil astrologique
      </p>
      <div
        style={{
          marginTop: '2rem',
          display: 'flex',
          gap: '1rem',
          flexWrap: 'wrap',
        }}
      >
        <Link
          to={ROUTES.SIGNUP}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#28a745',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: 600,
          }}
          aria-label="S'inscrire pour créer un compte"
        >
          S'inscrire
        </Link>
        <Link
          to={ROUTES.LOGIN}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#007bff',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: 600,
          }}
          aria-label="Se connecter à votre compte"
        >
          Se connecter
        </Link>
      </div>
      <nav
        style={{
          marginTop: '3rem',
          paddingTop: '2rem',
          borderTop: '1px solid #e0e0e0',
          fontSize: '0.875rem',
          color: '#6b7280',
        }}
        aria-label="Liens légaux"
      >
        <div
          style={{
            display: 'flex',
            gap: '1.5rem',
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
        >
          <Link
            to={ROUTES.LEGAL.TOS}
            style={{
              color: '#6b7280',
              textDecoration: 'none',
            }}
            aria-label="Consulter les conditions d'utilisation"
          >
            Conditions d'utilisation
          </Link>
          <Link
            to={ROUTES.LEGAL.PRIVACY}
            style={{
              color: '#6b7280',
              textDecoration: 'none',
            }}
            aria-label="Consulter la politique de confidentialité"
          >
            Politique de confidentialité
          </Link>
        </div>
      </nav>
    </main>
  );
}
