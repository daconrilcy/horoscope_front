import { useNavigate, useSearchParams } from 'react-router-dom';
import { ROUTES } from '@/shared/config/routes';
import { UpgradeButton } from '@/widgets/UpgradeButton/UpgradeButton';
import { PLANS } from '@/shared/config/plans';

/**
 * Page d'annulation après le checkout Stripe
 * Affiche un message d'annulation et propose de réessayer
 */
export function BillingCancelPage(): JSX.Element {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const sessionId = searchParams.get('session_id');

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        backgroundColor: '#f9fafb',
      }}
    >
      <div
        style={{
          maxWidth: '500px',
          width: '100%',
          textAlign: 'center',
          backgroundColor: '#ffffff',
          padding: '3rem',
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div
          style={{
            fontSize: '4rem',
            marginBottom: '1rem',
          }}
        >
          ❌
        </div>
        <h1
          style={{
            fontSize: '1.5rem',
            fontWeight: 600,
            marginBottom: '1rem',
            color: '#111827',
          }}
        >
          Paiement annulé
        </h1>
        <p
          style={{
            fontSize: '1rem',
            color: '#6b7280',
            marginBottom: '2rem',
          }}
        >
          Le paiement a été annulé. Vous pouvez réessayer à tout moment.
        </p>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            alignItems: 'center',
          }}
        >
          <UpgradeButton plan={PLANS.PLUS} variant="primary" />
          <button
            type="button"
            onClick={() => {
              void navigate(ROUTES.APP.DASHBOARD);
            }}
            style={{
              padding: '0.5rem 1rem',
              fontSize: '0.875rem',
              color: '#6b7280',
              backgroundColor: 'transparent',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f9fafb';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            Retour au tableau de bord
          </button>
        </div>
        {sessionId != null && (
          <p
            style={{
              fontSize: '0.875rem',
              color: '#9ca3af',
              marginTop: '1rem',
            }}
          >
            Session: {sessionId.slice(0, 16)}...
          </p>
        )}
      </div>
    </div>
  );
}

