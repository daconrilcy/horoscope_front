import { useTitle } from '@/shared/hooks/useTitle';

/**
 * Page Dashboard (privée)
 * Préparée pour lazy loading
 */
export function DashboardPage(): JSX.Element {
  useTitle('Horoscope - Dashboard');

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Bienvenue sur votre tableau de bord</p>
      <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
        <p>Contenu du dashboard à venir...</p>
      </div>
    </div>
  );
}

