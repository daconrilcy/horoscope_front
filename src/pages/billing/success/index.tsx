import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { ROUTES } from '@/shared/config/routes';
import { toast } from '@/app/AppProviders';

/**
 * Page de succès après le checkout Stripe
 * Valide le session_id, revalide le plan utilisateur, et redirige vers le dashboard
 */
export function BillingSuccessPage(): JSX.Element {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Si pas de session_id, rediriger immédiatement
    if (sessionId == null || sessionId.trim() === '') {
      console.warn('[BillingSuccess] No session_id in URL, redirecting to dashboard');
      void navigate(ROUTES.APP.DASHBOARD, { replace: true });
      return;
    }

    // Fonction pour revalider et rediriger
    const revalidateAndRedirect = async (): Promise<void> => {
      try {
        // Revalider le plan et le paywall pour mettre à jour l'état
        await queryClient.invalidateQueries({ queryKey: ['plan'] });
        await queryClient.invalidateQueries({ queryKey: ['paywall'] });

        // Attendre un peu pour que l'utilisateur voie le message de succès
        await new Promise((resolve) => setTimeout(resolve, 2500));

        // Rediriger vers le dashboard
        void navigate(ROUTES.APP.DASHBOARD, { replace: true });
      } catch (error) {
        console.error('[BillingSuccess] Revalidation failed:', error);
        // Même en cas d'erreur, rediriger vers le dashboard
        void navigate(ROUTES.APP.DASHBOARD, { replace: true });
      }
    };

    void revalidateAndRedirect();
  }, [sessionId, navigate, queryClient]);

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        backgroundColor: '#f9fafb',
      }}
    >
      <div
        style={{
          maxWidth: '500px',
          width: '100%',
          textAlign: 'center',
          backgroundColor: '#ffffff',
          padding: '3rem',
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div
          style={{
            fontSize: '4rem',
            marginBottom: '1rem',
          }}
        >
          ✅
        </div>
        <h1
          style={{
            fontSize: '1.5rem',
            fontWeight: 600,
            marginBottom: '1rem',
            color: '#111827',
          }}
        >
          Paiement réussi !
        </h1>
        <p
          style={{
            fontSize: '1rem',
            color: '#6b7280',
            marginBottom: '2rem',
          }}
        >
          Votre abonnement a été activé avec succès. Vous allez être redirigé vers votre tableau de bord.
        </p>
        {sessionId != null && (
          <p
            style={{
              fontSize: '0.875rem',
              color: '#9ca3af',
              marginTop: '1rem',
            }}
          >
            Session: {sessionId.slice(0, 16)}...
          </p>
        )}
      </div>
    </div>
  );
}

