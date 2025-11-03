import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PortalButton } from './PortalButton';
import { usePortal } from '@/features/billing/hooks/usePortal';
import React from 'react';

// Mock usePortal
vi.mock('@/features/billing/hooks/usePortal', () => ({
  usePortal: vi.fn(),
}));

// Mock useAuthStore
const mockAuthStore = {
  token: 'test-token',
  getToken: vi.fn(() => 'test-token'),
};

vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(
    (selector: (state: typeof mockAuthStore) => string | null) =>
      selector(mockAuthStore)
  ),
}));

describe('PortalButton', () => {
  let queryClient: QueryClient;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let mockOpenPortal: ReturnType<typeof vi.fn<any, any>>;

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

    mockOpenPortal = vi.fn().mockResolvedValue(undefined);

    const mockUsePortal = usePortal as unknown as ReturnType<typeof vi.fn>;
    mockUsePortal.mockReturnValue({
      openPortal: mockOpenPortal,
      isPending: false,
      error: null,
    });

    // Par défaut, token présent (utilisateur connecté)
    mockAuthStore.token = 'test-token';
    mockAuthStore.getToken = vi.fn(() => 'test-token');
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait afficher le label par défaut "Gérer mon abonnement"', () => {
    render(<PortalButton />, { wrapper });

    expect(screen.getByText('Gérer mon abonnement')).toBeInTheDocument();
  });

  it('devrait afficher le label personnalisé si fourni', () => {
    render(<PortalButton label="Mon abonnement" />, { wrapper });

    expect(screen.getByText('Mon abonnement')).toBeInTheDocument();
  });

  it('devrait appeler openPortal au clic si token présent', async () => {
    render(<PortalButton />, { wrapper });

    const button = screen.getByRole('button');
    button.click();

    await waitFor(() => {
      expect(mockOpenPortal).toHaveBeenCalled();
    });
  });

  it('devrait être désactivé si pas de JWT', () => {
    mockAuthStore.token = null;
    mockAuthStore.getToken = vi.fn(() => null);

    render(<PortalButton />, { wrapper });

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute(
      'title',
      "Connecte-toi pour gérer l'abonnement"
    );
  });

  it('devrait avoir title="Connecte-toi pour gérer l\'abonnement" si pas de JWT', () => {
    mockAuthStore.token = null;
    mockAuthStore.getToken = vi.fn(() => null);

    render(<PortalButton />, { wrapper });

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute(
      'title',
      "Connecte-toi pour gérer l'abonnement"
    );
  });

  it('devrait ne pas appeler openPortal si pas de JWT', async () => {
    mockAuthStore.token = null;
    mockAuthStore.getToken = vi.fn(() => null);

    render(<PortalButton />, { wrapper });

    const button = screen.getByRole('button');
    button.click();

    await waitFor(() => {
      expect(mockOpenPortal).not.toHaveBeenCalled();
    });
  });

  it('devrait afficher "Chargement…" et se désactiver pendant la mutation', () => {
    (usePortal as ReturnType<typeof vi.fn>).mockReturnValue({
      openPortal: mockOpenPortal,
      isPending: true,
      error: null,
    });

    render(<PortalButton />, { wrapper });

    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Chargement…');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
  });

  it('devrait avoir aria-busy={true} pendant la mutation', () => {
    (usePortal as ReturnType<typeof vi.fn>).mockReturnValue({
      openPortal: mockOpenPortal,
      isPending: true,
      error: null,
    });

    render(<PortalButton />, { wrapper });

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-busy', 'true');
  });

  it("devrait ignorer le double-clic (pas d'appel supplémentaire si isPending)", async () => {
    (usePortal as ReturnType<typeof vi.fn>).mockReturnValue({
      openPortal: mockOpenPortal,
      isPending: true,
      error: null,
    });

    render(<PortalButton />, { wrapper });

    const button = screen.getByRole('button');
    button.click();
    button.click(); // Second clic (doit être ignoré)

    await waitFor(() => {
      expect(mockOpenPortal).not.toHaveBeenCalled();
    });
  });

  it('devrait supporter la variante primary', () => {
    render(<PortalButton variant="primary" />, { wrapper });

    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });
});
