import { useState, useEffect } from 'react';
import { useTitle } from '@/shared/hooks/useTitle';
import { useQueryClient } from '@tanstack/react-query';
import { NatalForm } from '@/features/horoscope/NatalForm';
import { TodayCard } from '@/features/horoscope/TodayCard';
import { TodayPremiumCard } from '@/features/horoscope/TodayPremiumCard';
import { useDownloadPdf } from '@/features/horoscope/hooks/useDownloadPdf';

/**
 * Page Horoscope (privée)
 * Sections : form natal, today, premium, export PDF
 */
function HoroscopePage(): JSX.Element {
  useTitle('Horoscope');
  const queryClient = useQueryClient();

  const [currentChart, setCurrentChart] = useState<string | null>(null);
  const { downloadPdf, isPending: isPdfPending } = useDownloadPdf();

  // Post-checkout : revalidation des queries premium au retour de Stripe
  useEffect(() => {
    void queryClient.invalidateQueries({ queryKey: ['horo', 'today-premium'] });
  }, [queryClient]);

  const handleDownloadPdf = async (): Promise<void> => {
    if (currentChart) {
      await downloadPdf(currentChart);
    }
  };

  return (
    <div>
      <h1>Horoscope</h1>
      <p>Créez et consultez vos horoscopes personnalisés</p>

      {/* Section 1 : Formulaire de création */}
      <section>
        <NatalForm
          onSuccess={(chartId) => {
            setCurrentChart(chartId);
          }}
        />
      </section>

      {/* Section 2 : Today (free) */}
      {currentChart && (
        <section>
          <TodayCard chartId={currentChart} />
        </section>
      )}

      {/* Section 3 : Today Premium */}
      {currentChart && (
        <section>
          <TodayPremiumCard chartId={currentChart} />
        </section>
      )}

      {/* Bouton Export PDF */}
      {currentChart && (
        <section style={{ marginTop: '2rem' }}>
          <button
            type="button"
            onClick={() => {
              void handleDownloadPdf();
            }}
            disabled={isPdfPending}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isPdfPending ? 'not-allowed' : 'pointer',
              fontSize: '1rem',
            }}
          >
            {isPdfPending ? 'Téléchargement...' : 'Exporter le PDF'}
          </button>
        </section>
      )}
    </div>
  );
}

export { HoroscopePage };
