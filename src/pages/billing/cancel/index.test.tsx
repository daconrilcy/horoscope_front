import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, useNavigate, useSearchParams } from 'react-router-dom';
import { BillingCancelPage } from './index';
import { PLANS } from '@/shared/config/plans';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
    useSearchParams: vi.fn(),
  };
});

// Mock UpgradeButton
vi.mock('@/widgets/UpgradeButton/UpgradeButton', () => ({
  UpgradeButton: ({ plan, variant }: { plan: typeof PLANS.PLUS; variant: string }) => (
    <button data-testid="upgrade-button" data-plan={plan} data-variant={variant}>
      Upgrade to {plan}
    </button>
  ),
}));

describe('BillingCancelPage', () => {
  let mockNavigate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockNavigate = vi.fn();
    vi.clearAllMocks();
    vi.mocked(useNavigate).mockReturnValue(mockNavigate);
  });

  const wrapper = ({
    children,
    searchParams = new URLSearchParams(),
  }: {
    children: React.ReactNode;
    searchParams?: URLSearchParams;
  }): JSX.Element => {
    vi.mocked(useSearchParams).mockReturnValue([searchParams, vi.fn()]);
    return <MemoryRouter>{children}</MemoryRouter>;
  };

  it('devrait afficher le message d\'annulation avec session_id', () => {
    const searchParams = new URLSearchParams({ session_id: 'cs_test_1234567890' });
    render(<BillingCancelPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    expect(screen.getByText('Paiement annulé')).toBeInTheDocument();
    expect(screen.getByText(/Session: cs_test_12345678/)).toBeInTheDocument();
  });

  it('devrait afficher le bouton UpgradeButton', () => {
    const searchParams = new URLSearchParams({ session_id: 'cs_test_1234567890' });
    render(<BillingCancelPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    const upgradeButton = screen.getByTestId('upgrade-button');
    expect(upgradeButton).toBeInTheDocument();
    expect(upgradeButton).toHaveAttribute('data-plan', PLANS.PLUS);
    expect(upgradeButton).toHaveAttribute('data-variant', 'primary');
  });

  it('devrait avoir un bouton pour retourner au dashboard', () => {
    const searchParams = new URLSearchParams({ session_id: 'cs_test_1234567890' });
    render(<BillingCancelPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    const backButton = screen.getByText('Retour au tableau de bord');
    expect(backButton).toBeInTheDocument();
  });

  it('devrait naviguer vers le dashboard quand on clique sur le bouton retour', () => {
    const searchParams = new URLSearchParams({ session_id: 'cs_test_1234567890' });
    render(<BillingCancelPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    const backButton = screen.getByText('Retour au tableau de bord');
    backButton.click();

    expect(mockNavigate).toHaveBeenCalledWith('/app/dashboard');
  });

  it('devrait fonctionner sans session_id', () => {
    const searchParams = new URLSearchParams();
    render(<BillingCancelPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    expect(screen.getByText('Paiement annulé')).toBeInTheDocument();
    expect(screen.queryByText(/Session:/)).not.toBeInTheDocument();
  });
});

