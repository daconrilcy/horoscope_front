import { useCheckout } from '@/features/billing/hooks/useCheckout';
import { PLAN_LABELS, type BillingPlan } from '@/shared/config/plans';

/**
 * Props pour le composant UpgradeButton
 */
export interface UpgradeButtonProps {
  /** Plan de facturation (plus | pro) */
  plan: BillingPlan;
  /** Label personnalisé (défaut depuis PLAN_LABELS) */
  label?: string;
  /** Variante du bouton */
  variant?: 'primary' | 'secondary';
  /** Callback optionnel appelé avant checkout (peut annuler si retourne false) */
  onBeforeCheckout?: () => boolean | void;
}

/**
 * Composant réutilisable pour bouton upgrade vers un plan de facturation
 * Utilise useCheckout() pour créer session Stripe et rediriger
 * Gère l'état pending avec disabled et aria-busy
 */
export function UpgradeButton({
  plan,
  label,
  variant = 'primary',
  onBeforeCheckout,
}: UpgradeButtonProps): JSX.Element {
  const { startCheckout, isPending } = useCheckout();

  // Label par défaut depuis PLAN_LABELS
  const buttonLabel = label ?? PLAN_LABELS[plan];
  const displayLabel = isPending
    ? 'Chargement…'
    : `Passer au plan ${buttonLabel}`;

  const handleClick = (): void => {
    // Ignore les clics si pending
    if (isPending) {
      return;
    }

    // Appeler onBeforeCheckout si fourni (peut annuler si retourne false)
    if (onBeforeCheckout?.() === false) {
      return;
    }

    // Démarrer le checkout
    void startCheckout(plan);
  };

  const baseStyle: React.CSSProperties = {
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '0.25rem',
    cursor: isPending ? 'not-allowed' : 'pointer',
    fontWeight: 500,
    transition: 'opacity 0.2s',
    opacity: isPending ? 0.7 : 1,
  };

  const variantStyles: Record<'primary' | 'secondary', React.CSSProperties> = {
    primary: {
      backgroundColor: '#f59e0b',
      color: 'white',
    },
    secondary: {
      backgroundColor: 'transparent',
      color: '#f59e0b',
      border: '1px solid #f59e0b',
    },
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isPending}
      aria-busy={isPending}
      aria-label={`Passer au plan ${buttonLabel}`}
      title={`Passer au plan ${buttonLabel} pour accéder à plus de fonctionnalités`}
      style={{
        ...baseStyle,
        ...variantStyles[variant],
      }}
    >
      {displayLabel}
    </button>
  );
}
