import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UpgradeButton } from './UpgradeButton';
import { useCheckout } from '@/features/billing/hooks/useCheckout';
import { PLANS } from '@/shared/config/plans';
import React from 'react';

// Mock useCheckout
vi.mock('@/features/billing/hooks/useCheckout', () => ({
  useCheckout: vi.fn(),
}));

describe('UpgradeButton', () => {
  let queryClient: QueryClient;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let mockStartCheckout: ReturnType<typeof vi.fn<any, any>>;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();

    mockStartCheckout = vi.fn().mockResolvedValue(undefined);

    const mockUseCheckout = useCheckout as unknown as ReturnType<typeof vi.fn>;
    mockUseCheckout.mockReturnValue({
      startCheckout: mockStartCheckout,
      isPending: false,
      error: null,
    });
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait afficher le label par défaut depuis PLAN_LABELS si non fourni', () => {
    render(<UpgradeButton plan={PLANS.PLUS} />, { wrapper });

    expect(screen.getByText(/Passer au plan Plus/i)).toBeInTheDocument();
  });

  it('devrait afficher le label personnalisé si fourni', () => {
    render(<UpgradeButton plan={PLANS.PLUS} label="Plan Premium" />, {
      wrapper,
    });

    expect(
      screen.getByText(/Passer au plan Plan Premium/i)
    ).toBeInTheDocument();
  });

  it('devrait appeler startCheckout avec le plan au clic', async () => {
    render(<UpgradeButton plan={PLANS.PLUS} />, { wrapper });

    const button = screen.getByRole('button');
    button.click();

    await waitFor(() => {
      expect(mockStartCheckout).toHaveBeenCalledWith(PLANS.PLUS);
    });
  });

  it('devrait afficher "Chargement…" et se désactiver pendant la mutation', () => {
    (useCheckout as ReturnType<typeof vi.fn>).mockReturnValue({
      startCheckout: mockStartCheckout,
      isPending: true,
      error: null,
    });

    render(<UpgradeButton plan={PLANS.PLUS} />, { wrapper });

    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Chargement…');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
  });

  it('devrait avoir aria-busy={true} pendant la mutation', () => {
    (useCheckout as ReturnType<typeof vi.fn>).mockReturnValue({
      startCheckout: mockStartCheckout,
      isPending: true,
      error: null,
    });

    render(<UpgradeButton plan={PLANS.PLUS} />, { wrapper });

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-busy', 'true');
  });

  it('devrait avoir aria-label explicite', () => {
    render(<UpgradeButton plan={PLANS.PLUS} />, { wrapper });

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Passer au plan Plus');
  });

  it("devrait ignorer le double-clic (pas d'appel supplémentaire si isPending)", async () => {
    (useCheckout as ReturnType<typeof vi.fn>).mockReturnValue({
      startCheckout: mockStartCheckout,
      isPending: true,
      error: null,
    });

    render(<UpgradeButton plan={PLANS.PLUS} />, { wrapper });

    const button = screen.getByRole('button');
    button.click();
    button.click(); // Second clic (doit être ignoré)

    await waitFor(() => {
      expect(mockStartCheckout).not.toHaveBeenCalled();
    });
  });

  it('devrait appeler onBeforeCheckout et peut annuler si retourne false', async () => {
    const onBeforeCheckout = vi.fn().mockReturnValue(false);

    render(
      <UpgradeButton plan={PLANS.PLUS} onBeforeCheckout={onBeforeCheckout} />,
      {
        wrapper,
      }
    );

    const button = screen.getByRole('button');
    button.click();

    await waitFor(() => {
      expect(onBeforeCheckout).toHaveBeenCalled();
    });

    // Le checkout ne doit pas être appelé si onBeforeCheckout retourne false
    expect(mockStartCheckout).not.toHaveBeenCalled();
  });

  it('devrait appeler startCheckout si onBeforeCheckout ne retourne pas false', async () => {
    const onBeforeCheckout = vi.fn().mockReturnValue(true);

    render(
      <UpgradeButton plan={PLANS.PLUS} onBeforeCheckout={onBeforeCheckout} />,
      {
        wrapper,
      }
    );

    const button = screen.getByRole('button');
    button.click();

    await waitFor(() => {
      expect(onBeforeCheckout).toHaveBeenCalled();
      expect(mockStartCheckout).toHaveBeenCalledWith(PLANS.PLUS);
    });
  });

  it('devrait fonctionner avec plan PRO', () => {
    render(<UpgradeButton plan={PLANS.PRO} />, { wrapper });

    expect(screen.getByText(/Passer au plan Pro/i)).toBeInTheDocument();
  });

  it('devrait supporter la variante secondary', () => {
    render(<UpgradeButton plan={PLANS.PLUS} variant="secondary" />, {
      wrapper,
    });

    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });
});
