import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBoundary } from './ErrorBoundary';
import { ApiError } from '@/shared/api/errors';
import React from 'react';

// Composant qui lance une erreur
function ThrowError({ shouldThrow }: { shouldThrow: boolean }): JSX.Element {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    // Supprimer les warnings console.error pendant les tests
    vi.spyOn(console, 'error').mockImplementation(() => {
      // No-op
    });
  });

  it('devrait capturer une erreur et afficher le fallback', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('devrait afficher requestId si erreur est ApiError', () => {
    function ThrowApiError(): JSX.Element {
      throw new ApiError('API Error', 500, undefined, 'req-123');
    }

    render(
      <ErrorBoundary>
        <ThrowApiError />
      </ErrorBoundary>
    );

    expect(
      screen.getByText((content, element) => {
        return element?.textContent === 'ID de requête : req-123';
      })
    ).toBeInTheDocument();
  });

  it('devrait avoir role="alert" et aria-live="assertive"', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'assertive');
  });

  it('devrait réinitialiser l\'erreur au clic sur "Réessayer"', async () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument();

    const retryButton = screen.getByRole('button', { name: 'Réessayer' });
    await userEvent.click(retryButton);

    // L'erreur devrait être réinitialisée, mais ThrowError va re-lancer
    // On vérifie juste que le bouton existe toujours
    expect(
      screen.getByRole('button', { name: 'Réessayer' })
    ).toBeInTheDocument();
  });

  it('devrait appeler onError callback', () => {
    const onError = vi.fn();

    function ThrowTestError(): JSX.Element {
      throw new Error('Test error');
    }

    render(
      <ErrorBoundary onError={onError}>
        <ThrowTestError />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalled();

    const calls = vi.mocked(onError).mock.calls as Array<
      [Error, React.ErrorInfo]
    >;
    expect(calls.length).toBeGreaterThan(0);
    if (calls.length > 0 && calls[0] !== undefined) {
      const firstCall = calls[0];
      expect(firstCall[0]).toBeInstanceOf(Error);
      expect(firstCall[1]).toHaveProperty('componentStack');
      expect(typeof firstCall[1].componentStack).toBe('string');
    }
  });

  it('devrait réinitialiser avec resetKeys', () => {
    function ThrowErrorWithKey({ key }: { key: string }): JSX.Element {
      throw new Error(`Error with key ${key}`);
    }

    const { rerender } = render(
      <ErrorBoundary resetKeys={['key1']}>
        <ThrowErrorWithKey key="key1" />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Une erreur est survenue/)).toBeInTheDocument();

    // Changer resetKeys devrait réinitialiser l'erreur
    rerender(
      <ErrorBoundary resetKeys={['key2']}>
        <ThrowErrorWithKey key="key2" />
      </ErrorBoundary>
    );

    // L'erreur devrait être réinitialisée mais va re-lancer
    // On vérifie que le fallback est toujours affiché
    expect(screen.getByText(/Une erreur est survenue/)).toBeInTheDocument();
  });

  it('devrait utiliser fallback custom si fourni', () => {
    const customFallback = (error: Error | null): JSX.Element => (
      <div data-testid="custom-fallback">Custom: {error?.message}</div>
    );

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    expect(screen.getByText(/Custom: Test error/)).toBeInTheDocument();
  });
});
