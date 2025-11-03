import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InlineError } from './InlineError';
import { ApiError } from '@/shared/api/errors';

describe('InlineError', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('devrait afficher une erreur string', () => {
    render(<InlineError error="Erreur de test" />);

    expect(screen.getByText('Erreur de test')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveAttribute('aria-live', 'assertive');
  });

  it('devrait afficher une erreur Error', () => {
    const error = new Error('Erreur de test');
    render(<InlineError error={error} />);

    expect(screen.getByText('Erreur de test')).toBeInTheDocument();
  });

  it('devrait afficher requestId si ApiError', () => {
    const error = new ApiError('Erreur API', 500, undefined, 'req-123');
    render(<InlineError error={error} />);

    expect(screen.getByText('Erreur API')).toBeInTheDocument();
    expect(screen.getByText(/Request ID: req-123/)).toBeInTheDocument();
  });

  it('devrait afficher un bouton "Réessayer" si retry fourni', async () => {
    const retry = vi.fn();
    render(<InlineError error="Erreur" retry={retry} />);

    const button = screen.getByRole('button', { name: 'Réessayer' });
    expect(button).toBeInTheDocument();

    await userEvent.click(button);
    expect(retry).toHaveBeenCalledTimes(1);
  });

  it('devrait être dismissible si dismissible=true', async () => {
    const onDismiss = vi.fn();
    render(
      <InlineError error="Erreur" dismissible={true} onDismiss={onDismiss} />
    );

    const dismissButton = screen.getByRole('button', {
      name: "Fermer l'erreur",
    });
    expect(dismissButton).toBeInTheDocument();

    await userEvent.click(dismissButton);
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('devrait fermer avec ESC si dismissible', async () => {
    const onDismiss = vi.fn();
    render(
      <InlineError error="Erreur" dismissible={true} onDismiss={onDismiss} />
    );

    await userEvent.keyboard('{Escape}');
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('ne devrait pas afficher bouton dismiss si dismissible=false', () => {
    render(<InlineError error="Erreur" dismissible={false} />);

    expect(
      screen.queryByRole('button', { name: "Fermer l'erreur" })
    ).not.toBeInTheDocument();
  });
});
