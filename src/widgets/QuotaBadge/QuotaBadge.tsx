import { useState, useEffect } from 'react';
import { useMultiPaywall } from '@/features/billing/hooks/useMultiPaywall';
import { FEATURES } from '@/shared/config/features';
import { InlineError } from '@/shared/ui/InlineError';

/**
 * Props pour le composant QuotaBadge
 */
export interface QuotaBadgeProps {
  /** Features à vérifier (défaut: features principales) */
  features?: string[];
  /** Afficher le compte à rebours si retry_after disponible */
  showRetryAfter?: boolean;
}

/**
 * Composant badge pour afficher l'état des quotas
 * Affiche des états simples basés sur allowed/reason (pas "restant/limite" si API ne le fournit pas)
 */
export function QuotaBadge({
  features = [FEATURES.CHAT_MSG_PER_DAY, FEATURES.HORO_TODAY_PREMIUM],
  showRetryAfter = true,
}: QuotaBadgeProps): JSX.Element | null {
  const { results, isLoadingAny, isErrorAny } = useMultiPaywall(features);

  // Trouver la première décision qui bloque (rate ou plan)
  const blockingResult = results.find((r) => r.data && !r.data.allowed);

  // Trouver retry_after maximum parmi les résultats
  const maxRetryAfter = results.reduce((max, r) => {
    if (r.retryAfter !== undefined && r.retryAfter > max) {
      return r.retryAfter;
    }
    return max;
  }, 0);

  // État pour le compte à rebours
  const [countdown, setCountdown] = useState<number | null>(
    maxRetryAfter > 0 && showRetryAfter ? maxRetryAfter : null
  );

  // Compte à rebours
  useEffect(() => {
    if (countdown === null || countdown <= 0) {
      return;
    }

    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev === null || prev <= 0) {
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [countdown]);

  // Réinitialiser countdown si retryAfter change
  useEffect(() => {
    if (maxRetryAfter > 0 && showRetryAfter) {
      setCountdown(maxRetryAfter);
    }
  }, [maxRetryAfter, showRetryAfter]);

  // Loading state
  if (isLoadingAny) {
    return (
      <div
        role="status"
        aria-live="polite"
        style={{
          display: 'inline-block',
          padding: '0.25rem 0.5rem',
          backgroundColor: '#f3f4f6',
          borderRadius: '0.25rem',
          fontSize: '0.875rem',
          color: '#6b7280',
        }}
      >
        Chargement...
      </div>
    );
  }

  // Error state
  if (isErrorAny) {
    const error = results.find((r) => r.error)?.error;
    if (error) {
      return <InlineError error={error} dismissible={false} />;
    }
    return null;
  }

  // Si toutes les features sont autorisées
  const allAllowed = results.every((r) => r.isAllowed);
  if (allAllowed) {
    return (
      <div
        role="status"
        aria-live="polite"
        style={{
          display: 'inline-block',
          padding: '0.25rem 0.5rem',
          backgroundColor: '#d1fae5',
          borderRadius: '0.25rem',
          fontSize: '0.875rem',
          color: '#065f46',
          fontWeight: 500,
        }}
      >
        OK aujourd'hui
      </div>
    );
  }

  // Si bloqué par quota (rate)
  if (blockingResult?.reason === 'rate') {
    return (
      <div
        role="status"
        aria-live="polite"
        style={{
          display: 'inline-block',
          padding: '0.25rem 0.5rem',
          backgroundColor: '#fee2e2',
          borderRadius: '0.25rem',
          fontSize: '0.875rem',
          color: '#991b1b',
          fontWeight: 500,
        }}
      >
        Quota atteint
        {showRetryAfter && countdown !== null && countdown > 0 && (
          <span style={{ marginLeft: '0.5rem' }}>
            (réessayez dans {countdown}s)
          </span>
        )}
      </div>
    );
  }

  // Si bloqué par plan (plan)
  if (blockingResult?.reason === 'plan') {
    return (
      <div
        role="status"
        aria-live="polite"
        style={{
          display: 'inline-block',
          padding: '0.25rem 0.5rem',
          backgroundColor: '#fef3c7',
          borderRadius: '0.25rem',
          fontSize: '0.875rem',
          color: '#92400e',
          fontWeight: 500,
        }}
      >
        Fonctionnalité Plus/Pro
      </div>
    );
  }

  return null;
}
