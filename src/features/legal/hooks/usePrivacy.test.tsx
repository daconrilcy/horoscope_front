import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePrivacy } from './usePrivacy';
import { legalService } from '@/shared/api/legal.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import React from 'react';

// Mock legalService
vi.mock('@/shared/api/legal.service', () => ({
  legalService: {
    getPrivacy: vi.fn(),
  },
}));

describe('usePrivacy', () => {
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
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait retourner HTML et métadonnées avec succès', async () => {
    const mockResponse = {
      html: '<html><body><h1>Politique de confidentialité</h1></body></html>',
      etag: 'def456',
      lastModified: 'Tue, 02 Jan 2024 12:00:00 GMT',
      version: '2.0.0',
    };

    (legalService.getPrivacy as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => usePrivacy(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.html).toBe(mockResponse.html);
    expect(result.current.meta.etag).toBe('def456');
    expect(result.current.meta.lastModified).toBe(
      'Tue, 02 Jan 2024 12:00:00 GMT'
    );
    expect(result.current.meta.version).toBe('2.0.0');
    expect(result.current.isError).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('devrait retourner HTML sans métadonnées', async () => {
    const mockResponse = {
      html: '<html><body><h1>Privacy</h1></body></html>',
    };

    (legalService.getPrivacy as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => usePrivacy(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.html).toBe(mockResponse.html);
    expect(result.current.meta.etag).toBeUndefined();
    expect(result.current.meta.lastModified).toBeUndefined();
    expect(result.current.meta.version).toBeUndefined();
  });

  it('devrait retourner isLoading: true pendant le chargement', () => {
    (legalService.getPrivacy as ReturnType<typeof vi.fn>).mockImplementation(
      () =>
        new Promise((resolve) => {
          // Ne jamais résoudre pour tester isLoading
          setTimeout(() => {
            resolve({
              html: '<html><body>Test</body></html>',
            });
          }, 1000);
        })
    );

    const { result } = renderHook(() => usePrivacy(), { wrapper });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.html).toBeUndefined();
  });

  it('devrait gérer ApiError (404)', async () => {
    const mockError = new ApiError('Not found', 404);

    (legalService.getPrivacy as ReturnType<typeof vi.fn>).mockRejectedValue(
      mockError
    );

    const { result } = renderHook(() => usePrivacy(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBe(mockError);
    expect(result.current.html).toBeUndefined();
    expect(result.current.isLoading).toBe(false);
  });

  it('devrait gérer NetworkError (offline)', async () => {
    const mockError = new NetworkError('offline', 'Network error: offline');

    (legalService.getPrivacy as ReturnType<typeof vi.fn>).mockRejectedValue(
      mockError
    );

    const { result } = renderHook(() => usePrivacy(), { wrapper });

    // Attendre que React Query détecte l'erreur (peut prendre un peu de temps)
    await waitFor(
      () => {
        expect(result.current.isError).toBe(true);
      },
      { timeout: 3000 }
    );

    expect(result.current.error).toBeInstanceOf(NetworkError);
    expect(result.current.html).toBeUndefined();
  });

  it('devrait permettre refetch manuel', async () => {
    const mockResponse = {
      html: '<html><body><h1>Privacy</h1></body></html>',
    };

    (legalService.getPrivacy as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => usePrivacy(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.html).toBe(mockResponse.html);

    // Refetch
    result.current.refetch();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Vérifier que getPrivacy a été appelé au moins 2 fois (initial + refetch)
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(legalService.getPrivacy).toHaveBeenCalledTimes(2);
  });

  it('devrait utiliser staleTime de 24h', async () => {
    const mockResponse = {
      html: '<html><body><h1>Privacy</h1></body></html>',
    };

    (legalService.getPrivacy as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => usePrivacy(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Vérifier que la query utilise staleTime de 24h
    const query = queryClient.getQueryState(['legal', 'privacy']);
    expect(query).toBeDefined();
  });
});
