import { useToday } from './hooks/useToday';

/**
 * Props pour le composant TodayCard
 */
export interface TodayCardProps {
  /** ID du thème natal */
  chartId: string | null;
}

/**
 * Card pour afficher l'horoscope Today (free)
 * Loading/error/retry states
 */
export function TodayCard({ chartId }: TodayCardProps): JSX.Element | null {
  const { data, isLoading, isError, error, refetch } = useToday(chartId);

  if (!chartId) {
    return null;
  }

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Chargement de l'horoscope...</p>
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
        <p style={{ margin: 0 }}>Erreur lors du chargement de l'horoscope.</p>
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
        backgroundColor: '#f9f9f9',
        borderRadius: '8px',
        border: '1px solid #e0e0e0',
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: '1rem' }}>Horoscope du jour</h2>
      <div style={{ whiteSpace: 'pre-wrap' }}>{data.content}</div>
      {data.generated_at && (
        <p style={{ fontSize: '0.875rem', color: '#666', marginTop: '1rem' }}>
          Généré le {new Date(data.generated_at).toLocaleString('fr-FR')}
        </p>
      )}
    </div>
  );
}
