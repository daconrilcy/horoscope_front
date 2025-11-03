import { usePortal } from '@/features/billing/hooks/usePortal';
import { useAuthStore } from '@/stores/authStore';

/**
 * Props pour le composant PortalButton
 */
export interface PortalButtonProps {
  /** Label personnalisé (défaut "Gérer mon abonnement") */
  label?: string;
  /** Variante du bouton */
  variant?: 'primary' | 'secondary';
}

/**
 * Composant pour accéder au portal Stripe (gestion abonnements)
 * Utilise usePortal() pour créer session portal et rediriger
 * Nécessite JWT (désactivé si pas de token)
 * Gère l'état pending avec disabled et aria-busy
 */
export function PortalButton({
  label = 'Gérer mon abonnement',
  variant = 'secondary',
}: PortalButtonProps = {}): JSX.Element {
  const { openPortal, isPending } = usePortal();
  const token = useAuthStore((state) => state.getToken());
  const hasToken = token !== null && token !== '';

  const displayLabel = isPending ? 'Chargement…' : label;

  const handleClick = (): void => {
    // Ignore les clics si pending ou pas de token
    if (isPending || !hasToken) {
      return;
    }

    // Ouvrir le portal
    void openPortal();
  };

  const baseStyle: React.CSSProperties = {
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '0.25rem',
    cursor: isPending || !hasToken ? 'not-allowed' : 'pointer',
    fontWeight: 500,
    transition: 'opacity 0.2s',
    opacity: isPending || !hasToken ? 0.7 : 1,
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

  const disabledTooltip = !hasToken
    ? "Connecte-toi pour gérer l'abonnement"
    : undefined;

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isPending || !hasToken}
      aria-busy={isPending}
      aria-label={label}
      title={disabledTooltip ?? label}
      style={{
        ...baseStyle,
        ...variantStyles[variant],
      }}
    >
      {displayLabel}
    </button>
  );
}
