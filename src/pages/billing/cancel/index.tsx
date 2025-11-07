import { Link } from 'react-router-dom';
import { useTitle } from '@/shared/hooks/useTitle';
import { ROUTES } from '@/shared/config/routes';

/**
 * Page d'annulation après checkout Stripe
 * Affiche un message et propose de réessayer
 */
export function BillingCancelPage(): JSX.Element {
  useTitle('Paiement annulé');

  return (
    <main style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Paiement annulé</h1>
      <p style={{ marginBottom: '1.5rem', fontSize: '1.1rem' }}>
        Vous avez annulé le processus de paiement.
      </p>
      <p style={{ marginBottom: '2rem', color: '#6b7280' }}>
        Aucun paiement n'a été effectué. Vous pouvez réessayer à tout moment.
      </p>
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center',
          flexWrap: 'wrap',
        }}
      >
        <Link
          to={ROUTES.APP.DASHBOARD}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#007bff',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            display: 'inline-block',
          }}
        >
          Retour au tableau de bord
        </Link>
        <Link
          to={ROUTES.APP.ACCOUNT}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#6c757d',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            display: 'inline-block',
          }}
        >
          Gérer mon abonnement
        </Link>
      </div>
    </main>
  );
}
