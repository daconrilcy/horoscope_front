import { Navigate } from 'react-router-dom';
import { DevTerminalConsole } from '@/widgets/DevTerminalConsole/DevTerminalConsole';
import { ROUTES } from '@/shared/config/routes';

/**
 * Page de développement pour le simulateur Stripe Terminal
 * Accessible uniquement en mode développement
 */
export function DevTerminalPage(): JSX.Element {
  // Rediriger vers le dashboard si pas en dev
  if (!import.meta.env.DEV) {
    return <Navigate to={ROUTES.APP.DASHBOARD} replace />;
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#121212', padding: '1rem' }}>
      <DevTerminalConsole />
    </div>
  );
}
