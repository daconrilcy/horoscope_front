import { PaywallGate } from '@/features/billing/PaywallGate';
import { FEATURES } from '@/shared/config/features';
import { useCheckout } from '@/features/billing/hooks/useCheckout';
import { useTodayPremium } from './hooks/useTodayPremium';

/**
 * Props pour le composant TodayPremiumCard
 */
export interface TodayPremiumCardProps {
  /** ID du thème natal */
  chartId: string | null;
}

/**
 * Composant interne qui déclenche la query
 * Critique : cette query n'est déclenchée QUE si PaywallGate autorise
 */
function TodayPremiumContent({ chartId }: { chartId: string | null }) {
  const { data, isLoading, isError, error, refetch } = useTodayPremium(chartId);

  if (!chartId) {
    return null;
  }

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Chargement de l'horoscope premium...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div
        style={{
          padding: '1rem',
          backgroundColor: '#fee2e2',
          borderRadius: '0.5rem',
        }}
      >
        <p style={{ margin: 0 }}>
          Erreur lors du chargement de l'horoscope premium.
        </p>
        {error && (
          <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem' }}>
            {error.message}
          </p>
        )}
        <button type="button" onClick={refetch} style={{ marginTop: '0.5rem' }}>
          Réessayer
        </button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div
      style={{
        marginTop: '2rem',
        padding: '1.5rem',
        backgroundColor: '#fff3cd',
        borderRadius: '8px',
        border: '2px solid #ffc107',
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: '1rem' }}>
        <span style={{ fontSize: '1.25rem' }}>⭐</span> Horoscope premium du
        jour
      </h2>
      <div style={{ whiteSpace: 'pre-wrap' }}>{data.content}</div>
      {data.premium_insights && (
        <div
          style={{
            marginTop: '1rem',
            padding: '1rem',
            backgroundColor: '#fff',
            borderRadius: '4px',
          }}
        >
          <h3 style={{ marginTop: 0 }}>Insights premium</h3>
          <div style={{ whiteSpace: 'pre-wrap' }}>{data.premium_insights}</div>
        </div>
      )}
      {data.generated_at && (
        <p style={{ fontSize: '0.875rem', color: '#666', marginTop: '1rem' }}>
          Généré le {new Date(data.generated_at).toLocaleString('fr-FR')}
        </p>
      )}
    </div>
  );
}

/**
 * Card pour afficher l'horoscope Today Premium
 * Enveloppée dans PaywallGate pour gérer l'accès
 * Query déclenchée uniquement à l'intérieur du PaywallGate
 */
export function TodayPremiumCard({
  chartId,
}: TodayPremiumCardProps): JSX.Element {
  const { startCheckout } = useCheckout();

  if (!chartId) {
    return <></>;
  }

  return (
    <PaywallGate
      feature={FEATURES.HORO_TODAY_PREMIUM}
      onUpgrade={() => void startCheckout('plus')}
    >
      <TodayPremiumContent chartId={chartId} />
    </PaywallGate>
  );
}
