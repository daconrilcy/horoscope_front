import { usePaywallStore } from '@/stores/paywallStore';

/**
 * Bannière d'upgrade affichée en cas de 402 (plan insuffisant) ou 429 (quota dépassé)
 * CTA vers checkout pour upgrade
 */
export function UpgradeBanner(): JSX.Element | null {
  const { visible, reason, upgradeUrl, hidePaywall } = usePaywallStore();

  if (!visible) {
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
    // TODO: Intégrer avec le hook useCheckout ou fonction similaire
    if (upgradeUrl) {
      window.location.href = upgradeUrl;
    } else {
      // Fallback vers la page de checkout
      // TODO: Utiliser react-router quand disponible
      window.location.href = '/checkout';
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
          onClick={hidePaywall}
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

