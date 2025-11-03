import { useTitle } from '@/shared/hooks/useTitle';

/**
 * Page Politique de confidentialité (placeholder)
 */
export function PrivacyPolicyPage(): JSX.Element {
  useTitle('Horoscope - Politique de confidentialité');

  return (
    <div>
      <h1>Politique de confidentialité</h1>
      <p>Page de la politique de confidentialité (à implémenter)</p>
      <div style={{ marginTop: '2rem' }}>
        <p>Le contenu de la politique de confidentialité sera intégré ici.</p>
      </div>
    </div>
  );
}
