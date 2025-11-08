import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, useNavigate, useSearchParams } from 'react-router-dom';
import { BillingSuccessPage } from './index';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
    useSearchParams: vi.fn(),
  };
});

// Mock toast
vi.mock('@/app/AppProviders', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
    warning: vi.fn(),
  },
}));

describe('BillingSuccessPage', () => {
  let queryClient: QueryClient;
  let mockNavigate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    mockNavigate = vi.fn();
    vi.clearAllMocks();
    vi.mocked(useNavigate).mockReturnValue(mockNavigate);
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const wrapper = ({
    children,
    searchParams = new URLSearchParams(),
  }: {
    children: React.ReactNode;
    searchParams?: URLSearchParams;
  }): JSX.Element => {
    vi.mocked(useSearchParams).mockReturnValue([searchParams, vi.fn()]);
    return (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>{children}</MemoryRouter>
      </QueryClientProvider>
    );
  };

  it('devrait afficher le message de succès avec session_id', async () => {
    const searchParams = new URLSearchParams({ session_id: 'cs_test_1234567890' });
    render(<BillingSuccessPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    expect(screen.getByText('Paiement réussi !')).toBeInTheDocument();
    expect(screen.getByText(/Session: cs_test_12345678/)).toBeInTheDocument();
  });

  it('devrait rediriger vers le dashboard après un délai si session_id présent', async () => {
    const searchParams = new URLSearchParams({ session_id: 'cs_test_1234567890' });
    render(<BillingSuccessPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    // Avancer le temps de 2500ms pour déclencher le setTimeout
    await vi.advanceTimersByTimeAsync(2500);
    // Exécuter les promesses en attente
    await vi.runAllTimersAsync();

    expect(mockNavigate).toHaveBeenCalledWith('/app/dashboard', { replace: true });
  });

  it('devrait rediriger immédiatement si pas de session_id', async () => {
    const searchParams = new URLSearchParams();
    render(<BillingSuccessPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    // Exécuter les promesses en attente
    await vi.runAllTimersAsync();

    expect(mockNavigate).toHaveBeenCalledWith('/app/dashboard', { replace: true });
  });

  it('devrait revalider les queries plan et paywall', async () => {
    const searchParams = new URLSearchParams({ session_id: 'cs_test_1234567890' });
    const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries');

    render(<BillingSuccessPage />, {
      wrapper: ({ children }) => wrapper({ children, searchParams }),
    });

    // Exécuter les promesses en attente
    await vi.runAllTimersAsync();

    expect(invalidateQueriesSpy).toHaveBeenCalledWith({ queryKey: ['plan'] });
    expect(invalidateQueriesSpy).toHaveBeenCalledWith({ queryKey: ['paywall'] });
  });
});

