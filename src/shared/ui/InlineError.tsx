import { useEffect, useCallback } from 'react';
import { ApiError } from '@/shared/api/errors';

/**
 * Props pour le composant InlineError
 */
export interface InlineErrorProps {
  /** Erreur à afficher (string, Error, ou ApiError) */
  error: string | Error | ApiError;
  /** Callback appelé lors du clic sur "Réessayer" */
  retry?: () => void;
  /** Indique si l'erreur peut être masquée */
  dismissible?: boolean;
  /** Callback appelé lors du masquage */
  onDismiss?: () => void;
}

/**
 * Composant pour afficher une erreur inline avec option retry et dismiss
 * Affiche le requestId si l'erreur est un ApiError
 */
export function InlineError({
  error,
  retry,
  dismissible = false,
  onDismiss,
}: InlineErrorProps): JSX.Element {
  // Extraire le message
  const message =
    typeof error === 'string'
      ? error
      : error instanceof Error
        ? error.message
        : 'Une erreur est survenue';

  // Extraire requestId si ApiError
  const requestId = error instanceof ApiError ? error.requestId : undefined;

  // Gestion ESC pour fermer
  useEffect(() => {
    if (!dismissible || !onDismiss) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        onDismiss();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [dismissible, onDismiss]);

  const handleDismiss = useCallback((): void => {
    if (onDismiss) {
      onDismiss();
    }
  }, [onDismiss]);

  return (
    <div
      role="alert"
      aria-live="assertive"
      style={{
        padding: '1rem',
        backgroundColor: '#fee2e2',
        border: '1px solid #fca5a5',
        borderRadius: '0.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        <div style={{ flex: 1 }}>
          <p style={{ margin: 0, color: '#991b1b', fontWeight: 500 }}>
            {message}
          </p>
          {requestId && (
            <small
              style={{
                display: 'block',
                marginTop: '0.5rem',
                fontSize: '0.75rem',
                color: '#7f1d1d',
                fontFamily: 'monospace',
              }}
            >
              Request ID: {requestId}
            </small>
          )}
        </div>
        {dismissible && onDismiss && (
          <button
            type="button"
            onClick={handleDismiss}
            aria-label="Fermer l'erreur"
            style={{
              padding: '0.25rem',
              backgroundColor: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: '#991b1b',
              fontSize: '1.25rem',
              lineHeight: 1,
              marginLeft: '0.5rem',
            }}
          >
            ×
          </button>
        )}
      </div>

      {retry && (
        <div>
          <button
            type="button"
            onClick={retry}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer',
              fontWeight: 500,
            }}
          >
            Réessayer
          </button>
        </div>
      )}
    </div>
  );
}
