import { useTitle } from '@/shared/hooks/useTitle';

/**
 * Page Conditions d'utilisation (placeholder)
 */
export function TermsOfServicePage(): JSX.Element {
  useTitle('Horoscope - Conditions d\'utilisation');

  return (
    <div>
      <h1>Conditions d'utilisation</h1>
      <p>Page des conditions d'utilisation (à implémenter)</p>
      <div style={{ marginTop: '2rem' }}>
        <p>Le contenu des conditions d'utilisation sera intégré ici.</p>
      </div>
    </div>
  );
}

