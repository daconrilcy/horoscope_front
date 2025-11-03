import { usePaywallStore } from '@/stores/paywallStore';
import type { PaywallReason } from '@/shared/api/types';

/**
 * Props pour le composant UpgradeBanner
 */
export interface UpgradeBannerProps {
  /** Callback appelé lors du clic sur le bouton upgrade */
  onUpgrade?: () => void;
  /** URL d'upgrade (si disponible) */
  upgradeUrl?: string;
  /** Raison du blocage (si pas fourni, utilise le store) */
  reason?: PaywallReason;
  /** Callback pour masquer la bannière (si pas fourni, utilise le store) */
  onHide?: () => void;
}

/**
 * Bannière d'upgrade affichée en cas de 402 (plan insuffisant)
 * CTA vers checkout pour upgrade
 * Peut être utilisée directement avec le store ou avec des props
 */
export function UpgradeBanner({
  onUpgrade,
  upgradeUrl: propsUpgradeUrl,
  reason: propsReason,
  onHide,
}: UpgradeBannerProps = {}): JSX.Element | null {
  const store = usePaywallStore();
  const {
    visible,
    reason: storeReason,
    upgradeUrl: storeUpgradeUrl,
    hidePaywall,
  } = store;

  // Utiliser props ou store selon ce qui est fourni
  const reason = propsReason ?? storeReason;
  const upgradeUrl = propsUpgradeUrl ?? storeUpgradeUrl;

  // Si utilisé avec props uniquement, toujours visible
  // Sinon, vérifier le store
  if (!propsReason && !visible) {
    return null;
  }

  const getMessage = (): string => {
    if (reason === 'plan') {
      return 'Cette fonctionnalité nécessite un plan supérieur.';
    }
    if (reason === 'rate') {
      return 'Vous avez atteint la limite de votre plan. Passez à un plan supérieur pour continuer.';
    }
    return 'Cette fonctionnalité nécessite un upgrade.';
  };

  const handleUpgrade = (): void => {
    if (onUpgrade) {
      onUpgrade();
    } else if (upgradeUrl) {
      window.location.href = upgradeUrl;
    } else {
      // Fallback vers la page de checkout
      // TODO: Utiliser react-router quand disponible
      window.location.href = '/checkout';
    }
  };

  const handleHide = (): void => {
    if (onHide) {
      onHide();
    } else {
      hidePaywall();
    }
  };

  return (
    <div
      style={{
        backgroundColor: '#fef3c7',
        border: '1px solid #fbbf24',
        borderRadius: '0.5rem',
        padding: '1rem',
        margin: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '1rem',
      }}
    >
      <div style={{ flex: 1 }}>
        <p style={{ margin: 0, fontWeight: 500 }}>{getMessage()}</p>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button
          type="button"
          onClick={handleUpgrade}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#f59e0b',
            color: 'white',
            border: 'none',
            borderRadius: '0.25rem',
            cursor: 'pointer',
            fontWeight: 500,
          }}
        >
          Upgrade
        </button>
        <button
          type="button"
          onClick={handleHide}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: 'transparent',
            border: '1px solid #d1d5db',
            borderRadius: '0.25rem',
            cursor: 'pointer',
          }}
        >
          Fermer
        </button>
      </div>
    </div>
  );
}
