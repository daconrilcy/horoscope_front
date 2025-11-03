import { usePlan } from '@/features/billing/hooks/usePlan';
import { PortalButton } from '@/widgets/PortalButton/PortalButton';
import { UpgradeButton } from '@/widgets/UpgradeButton/UpgradeButton';
import { PLANS, PLAN_LABELS } from '@/shared/config/plans';

/**
 * Props pour le composant PlanBanner
 */
export interface PlanBannerProps {
  /** Callback appelé lors du clic sur upgrade */
  onUpgrade?: () => void;
}

/**
 * Bannière affichant le plan actuel avec CTA Portal/Upgrade
 * Plan dérivé via sentinelles (usePlan)
 */
export function PlanBanner({
  onUpgrade,
}: PlanBannerProps = {}): JSX.Element | null {
  const { plan, isLoading } = usePlan();

  if (isLoading) {
    return (
      <div
        style={{
          padding: '1rem',
          backgroundColor: '#f9fafb',
          borderRadius: '0.5rem',
          border: '1px solid #e5e7eb',
        }}
      >
        <p style={{ margin: 0, color: '#6b7280' }}>Chargement du plan...</p>
      </div>
    );
  }

  const planLabel =
    plan === 'free'
      ? 'Gratuit'
      : plan === 'plus'
        ? PLAN_LABELS.plus
        : PLAN_LABELS.pro;

  return (
    <div
      style={{
        padding: '1.5rem',
        backgroundColor: '#f9fafb',
        borderRadius: '0.5rem',
        border: '1px solid #e5e7eb',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
      }}
    >
      <div>
        <h3
          style={{
            margin: '0 0 0.5rem 0',
            fontSize: '1.125rem',
            fontWeight: 600,
          }}
        >
          Votre plan actuel
        </h3>
        <p style={{ margin: 0, fontSize: '1rem', color: '#374151' }}>
          Plan : <strong>{planLabel}</strong>
        </p>
      </div>

      <div
        style={{
          display: 'flex',
          gap: '0.75rem',
          flexWrap: 'wrap',
        }}
      >
        {plan === 'free' && (
          <>
            <UpgradeButton
              plan={PLANS.PLUS}
              onBeforeCheckout={
                onUpgrade !== undefined
                  ? (): boolean => {
                      onUpgrade();
                      return true;
                    }
                  : undefined
              }
            />
            <UpgradeButton
              plan={PLANS.PRO}
              onBeforeCheckout={
                onUpgrade !== undefined
                  ? (): boolean => {
                      onUpgrade();
                      return true;
                    }
                  : undefined
              }
            />
          </>
        )}

        {(plan === 'plus' || plan === 'pro') && (
          <PortalButton label="Gérer mon abonnement" variant="primary" />
        )}
      </div>
    </div>
  );
}
