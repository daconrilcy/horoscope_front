import { useEffect } from 'react';
import { useTitle } from '@/shared/hooks/useTitle';
import { useQueryClient } from '@tanstack/react-query';
import { UpgradeButton } from '@/widgets/UpgradeButton/UpgradeButton';
import { PortalButton } from '@/widgets/PortalButton/PortalButton';
import { PLANS } from '@/shared/config/plans';

/**
 * Page Dashboard (privée)
 * Préparée pour lazy loading
 */
export function DashboardPage(): JSX.Element {
  useTitle('Horoscope - Dashboard');
  const queryClient = useQueryClient();

  // Post-checkout : revalidation des queries paywall au retour de Stripe
  // Ne pas déduire l'état du plan localement : laisser les webhooks faire foi
  useEffect(() => {
    void queryClient.invalidateQueries({ queryKey: ['paywall'] });
  }, [queryClient]);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Bienvenue sur votre tableau de bord</p>

      {/* Section "Mon offre" */}
      <div
        style={{
          marginTop: '2rem',
          padding: '1.5rem',
          backgroundColor: '#f9f9f9',
          borderRadius: '8px',
          border: '1px solid #e0e0e0',
        }}
      >
        <h2 style={{ marginTop: 0, marginBottom: '1rem' }}>Mon offre</h2>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          <div>
            <p style={{ marginBottom: '0.5rem' }}>
              Passez à un plan supérieur pour accéder à plus de fonctionnalités
            </p>
            <div
              style={{
                display: 'flex',
                gap: '1rem',
                flexWrap: 'wrap',
              }}
            >
              <UpgradeButton plan={PLANS.PLUS} />
              <UpgradeButton plan={PLANS.PRO} />
            </div>
          </div>
          <div style={{ borderTop: '1px solid #e0e0e0', paddingTop: '1rem' }}>
            <p style={{ marginBottom: '0.5rem' }}>
              Gérer votre abonnement existant
            </p>
            <PortalButton />
          </div>
        </div>
      </div>

      <div
        style={{
          marginTop: '2rem',
          padding: '1rem',
          backgroundColor: '#f9f9f9',
          borderRadius: '4px',
        }}
      >
        <p>Contenu du dashboard à venir...</p>
      </div>
    </div>
  );
}
