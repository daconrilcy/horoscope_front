import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PrivacyPolicyPage } from './index';
import { usePrivacy } from '@/features/legal/hooks/usePrivacy';
import { ApiError, NetworkError } from '@/shared/api/errors';
import React from 'react';

// Mock usePrivacy
vi.mock('@/features/legal/hooks/usePrivacy', () => ({
  usePrivacy: vi.fn(),
}));

// Mock sanitizeLegalHtml
vi.mock('@/shared/utils/sanitizeLegalHtml', () => ({
  sanitizeLegalHtml: (html: string) => html, // Pas de sanitization dans les tests
}));

// Mock env
vi.mock('@/shared/config/env', () => ({
  env: {
    VITE_API_BASE_URL: 'https://api.example.com',
  },
}));

// Mock window.print
const mockPrint = vi.fn();
Object.defineProperty(window, 'print', {
  value: mockPrint,
  writable: true,
});

describe('PrivacyPolicyPage', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
    mockPrint.mockClear();
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait afficher le loader pendant le chargement', () => {
    vi.mocked(usePrivacy).mockReturnValue({
      html: undefined,
      meta: {},
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    expect(
      screen.getByText(/Chargement de la politique de confidentialité/i)
    ).toBeInTheDocument();
  });

  it('devrait afficher le contenu HTML après chargement', async () => {
    const mockHtml =
      '<div><h2>Collecte de données</h2><p>Nous collectons vos données...</p></div>';

    vi.mocked(usePrivacy).mockReturnValue({
      html: mockHtml,
      meta: {},
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Collecte de données')).toBeInTheDocument();
      expect(
        screen.getByText('Nous collectons vos données...')
      ).toBeInTheDocument();
    });
  });

  it('devrait afficher le titre h1', () => {
    vi.mocked(usePrivacy).mockReturnValue({
      html: '<div>Content</div>',
      meta: {},
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    expect(
      screen.getByRole('heading', { name: 'Politique de confidentialité' })
    ).toBeInTheDocument();
  });

  it('devrait afficher la structure ARIA article', () => {
    vi.mocked(usePrivacy).mockReturnValue({
      html: '<div>Content</div>',
      meta: {},
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    const article = screen.getByRole('article', {
      name: 'Politique de confidentialité',
    });
    expect(article).toBeInTheDocument();
  });

  it('devrait afficher le bouton Imprimer', () => {
    vi.mocked(usePrivacy).mockReturnValue({
      html: '<div>Content</div>',
      meta: {},
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    const printButton = screen.getByRole('button', { name: /imprimer/i });
    expect(printButton).toBeInTheDocument();
  });

  it('devrait appeler window.print au clic sur le bouton Imprimer', () => {
    vi.mocked(usePrivacy).mockReturnValue({
      html: '<div>Content</div>',
      meta: {},
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    const printButton = screen.getByRole('button', { name: /imprimer/i });
    printButton.click();

    expect(mockPrint).toHaveBeenCalledTimes(1);
  });

  it('devrait afficher erreur ApiError avec bouton Réessayer', () => {
    const mockError = new ApiError('Not found', 404, undefined, 'req-456');
    const mockRefetch = vi.fn();

    vi.mocked(usePrivacy).mockReturnValue({
      html: undefined,
      meta: {},
      isLoading: false,
      isError: true,
      error: mockError,
      refetch: mockRefetch,
    });

    render(<PrivacyPolicyPage />, { wrapper });

    expect(screen.getByText(/Erreur de chargement/i)).toBeInTheDocument();
    expect(screen.getByText(/Erreur 404/i)).toBeInTheDocument();
    expect(screen.getByText(/ID de requête : req-456/i)).toBeInTheDocument();

    const retryButton = screen.getByRole('button', { name: /réessayer/i });
    expect(retryButton).toBeInTheDocument();

    retryButton.click();
    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });

  it('devrait afficher erreur NetworkError', () => {
    const mockError = new NetworkError('offline', 'Network error: offline');

    vi.mocked(usePrivacy).mockReturnValue({
      html: undefined,
      meta: {},
      isLoading: false,
      isError: true,
      error: mockError,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    expect(screen.getByText(/Erreur réseau/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Vérifiez votre connexion internet/i)
    ).toBeInTheDocument();
  });

  it('devrait afficher lien mailto de contact', () => {
    const mockError = new ApiError('Error', 500);

    vi.mocked(usePrivacy).mockReturnValue({
      html: undefined,
      meta: {},
      isLoading: false,
      isError: true,
      error: mockError,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    const contactLink = screen.getByRole('link', {
      name: /contacter le support/i,
    });
    expect(contactLink).toBeInTheDocument();
    expect(contactLink).toHaveAttribute('href', 'mailto:support@horoscope.com');
  });

  it('devrait afficher la date de mise à jour', () => {
    vi.mocked(usePrivacy).mockReturnValue({
      html: '<div>Content</div>',
      meta: {},
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    expect(screen.getByText(/Dernière mise à jour/i)).toBeInTheDocument();
  });

  it('devrait sécuriser les liens externes', async () => {
    const mockHtml =
      '<div><a href="https://example.com">Lien externe</a><a href="/relative">Lien interne</a></div>';

    vi.mocked(usePrivacy).mockReturnValue({
      html: mockHtml,
      meta: {},
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<PrivacyPolicyPage />, { wrapper });

    await waitFor(() => {
      const externalLink = screen.getByText('Lien externe').closest('a');
      expect(externalLink).toHaveAttribute('target', '_blank');
      expect(externalLink).toHaveAttribute(
        'rel',
        expect.stringContaining('noopener')
      );
    });
  });
});
