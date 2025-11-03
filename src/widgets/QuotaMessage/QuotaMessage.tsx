/**
 * Props pour le composant QuotaMessage
 */
export interface QuotaMessageProps {
  /** Nombre de secondes avant retry (si 429) */
  retryAfter?: number;
  /** URL d'upgrade (si disponible) */
  upgradeUrl?: string;
  /** Callback appelé lors du clic sur le bouton upgrade */
  onUpgrade?: () => void;
}

/**
 * Composant pour afficher un message de quota dépassé (429)
 * Affiche un message avec optionnellement un compte à rebours et un CTA upgrade
 */
export function QuotaMessage({
  retryAfter,
  upgradeUrl,
  onUpgrade,
}: QuotaMessageProps): JSX.Element {
  const handleUpgrade = (): void => {
    if (onUpgrade) {
      onUpgrade();
    } else if (upgradeUrl) {
      window.location.href = upgradeUrl;
    }
  };

  return (
    <div
      role="alert"
      style={{
        backgroundColor: '#fef3c7',
        border: '1px solid #fbbf24',
        borderRadius: '0.5rem',
        padding: '1rem',
        margin: '1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
      }}
    >
      <div>
        <p style={{ margin: 0, fontWeight: 500 }}>
          Quota atteint aujourd'hui. Vous avez atteint la limite de votre plan.
        </p>
        {retryAfter !== undefined && retryAfter > 0 && (
          <p
            style={{
              margin: '0.5rem 0 0 0',
              fontSize: '0.875rem',
              color: '#666',
            }}
          >
            Vous pourrez réessayer dans {retryAfter} seconde
            {retryAfter > 1 ? 's' : ''}.
          </p>
        )}
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
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
      </div>
    </div>
  );
}
