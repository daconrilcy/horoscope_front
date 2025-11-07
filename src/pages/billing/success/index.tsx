import { useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTitle } from '@/shared/hooks/useTitle';
import { billingService } from '@/shared/api/billing.service';
import { ROUTES } from '@/shared/config/routes';
import { ApiError } from '@/shared/api/errors';

/**
 * Page de succès après checkout Stripe
 * Valide le session_id et affiche le résultat
 */
export function BillingSuccessPage(): JSX.Element {
  useTitle('Paiement réussi');
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const sessionId = searchParams.get('session_id');

  // Requête pour vérifier la session
  const {
    data: sessionData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['billing', 'verify-session', sessionId],
    queryFn: () => {
      if (sessionId == null || sessionId.trim() === '') {
        throw new Error("session_id manquant dans l'URL");
      }
      return billingService.verifyCheckoutSession(sessionId);
    },
    enabled: sessionId != null && sessionId.trim() !== '',
    retry: false,
    staleTime: 0, // Toujours revalider
  });

  // Revalidation automatique du plan après succès
  useEffect(() => {
    if (sessionData?.status === 'paid') {
      // Invalider les queries liées au plan/billing pour forcer la revalidation
      void queryClient.invalidateQueries({ queryKey: ['plan'] });
      void queryClient.invalidateQueries({ queryKey: ['billing'] });
      void queryClient.invalidateQueries({ queryKey: ['paywall'] });
    }
  }, [sessionData, queryClient]);

  const handleRetry = (): void => {
    void refetch();
  };

  // État de chargement
  if (isLoading) {
    return (
      <main style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Validation en cours...</h1>
        <p>Vérification de votre paiement...</p>
      </main>
    );
  }

  // Erreur : session_id manquant
  if (sessionId == null || sessionId.trim() === '') {
    return (
      <main style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Erreur</h1>
        <p style={{ color: '#dc3545', marginBottom: '1.5rem' }}>
          Aucun identifiant de session trouvé dans l'URL.
        </p>
        <Link
          to={ROUTES.APP.DASHBOARD}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#007bff',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            display: 'inline-block',
          }}
        >
          Retour au tableau de bord
        </Link>
      </main>
    );
  }

  // Erreur API
  if (error) {
    const isApiError = error instanceof ApiError;
    const isNotFound = isApiError && error.status === 404;
    const isUnauthorized = isApiError && error.status === 401;

    return (
      <main style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Erreur de validation</h1>
        <p style={{ color: '#dc3545', marginBottom: '1.5rem' }}>
          {isNotFound
            ? 'Session introuvable ou expirée.'
            : isUnauthorized
              ? 'Session expirée. Veuillez vous reconnecter.'
              : error instanceof Error
                ? error.message
                : 'Une erreur est survenue lors de la validation.'}
        </p>
        <div
          style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
        >
          <button
            type="button"
            onClick={handleRetry}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Réessayer
          </button>
          <Link
            to={ROUTES.APP.DASHBOARD}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#6c757d',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontWeight: 600,
              display: 'inline-block',
            }}
          >
            Retour au tableau de bord
          </Link>
        </div>
      </main>
    );
  }

  // Succès
  if (sessionData?.status === 'paid') {
    return (
      <main style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Paiement réussi !</h1>
        <p
          style={{
            color: '#28a745',
            marginBottom: '1.5rem',
            fontSize: '1.1rem',
          }}
        >
          Votre abonnement a été activé avec succès.
        </p>
        {sessionData.plan && (
          <p style={{ marginBottom: '1.5rem' }}>
            Plan : <strong>{sessionData.plan}</strong>
          </p>
        )}
        <Link
          to={ROUTES.APP.DASHBOARD}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#28a745',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            display: 'inline-block',
          }}
        >
          Accéder au tableau de bord
        </Link>
      </main>
    );
  }

  // Statut unpaid ou expired
  return (
    <main style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Paiement non finalisé</h1>
      <p style={{ color: '#ffc107', marginBottom: '1.5rem' }}>
        {sessionData?.status === 'expired'
          ? 'La session de paiement a expiré.'
          : "Le paiement n'a pas été finalisé."}
      </p>
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center',
          flexWrap: 'wrap',
        }}
      >
        <button
          type="button"
          onClick={handleRetry}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Réessayer la validation
        </button>
        <Link
          to={ROUTES.APP.DASHBOARD}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#6c757d',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            display: 'inline-block',
          }}
        >
          Retour au tableau de bord
        </Link>
      </div>
    </main>
  );
}
