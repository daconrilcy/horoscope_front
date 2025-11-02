import React, { Component, type ReactNode } from 'react';
import { ApiError } from '@/shared/api/errors';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  requestId: string | undefined;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error | null, requestId?: string) => ReactNode;
  resetKeys?: readonly unknown[]; // Clés qui déclenchent un reset automatique
}

/**
 * ErrorBoundary pour capturer les erreurs 5xx et autres erreurs non gérées
 * Affiche le request_id si disponible dans l'erreur ApiError
 * Supporte resetKeys pour réinitialiser automatiquement lors d'un changement de route
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      requestId: undefined,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    const requestId = error instanceof ApiError ? error.requestId : undefined;
    return {
      hasError: true,
      error,
      requestId,
    };
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps): void {
    const { resetKeys } = this.props;
    const { hasError } = this.state;

    // Si resetKeys a changé et qu'il y a une erreur, réinitialiser
    if (hasError && resetKeys !== undefined && prevProps.resetKeys !== undefined) {
      const hasResetKeyChanged = resetKeys.some((key, index) => key !== prevProps.resetKeys?.[index]);
      if (hasResetKeyChanged) {
        this.setState({
          hasError: false,
          error: null,
          requestId: undefined,
        });
      }
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      requestId: undefined,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.state.requestId);
      }

      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>Une erreur est survenue</h2>
          <p>
            {this.state.error?.message || 'Une erreur inattendue s\'est produite.'}
          </p>
          {this.state.requestId && (
            <p style={{ fontSize: '0.875rem', color: '#666' }}>
              ID de requête : <code>{this.state.requestId}</code>
            </p>
          )}
          <button
            type="button"
            onClick={this.handleRetry}
            style={{
              marginTop: '1rem',
              padding: '0.5rem 1rem',
              cursor: 'pointer',
            }}
          >
            Réessayer
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

